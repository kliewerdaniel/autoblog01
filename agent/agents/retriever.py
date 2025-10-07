"""Retriever Agent: Searches the local vector database for relevant entries."""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import Document, GenerationSpec
from llm_client import llm_client
from retrieval import retrieve_relevant_context, assemble_context_window
from config import config
from prompts.system_prompts import RETRIEVER_SYSTEM_PROMPT
from prompts.templates import RETRIEVER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class RetrieverAgent:
    """Agent responsible for searching the knowledge base and synthesizing context."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client
        self.system_prompt = RETRIEVER_SYSTEM_PROMPT

    async def search_and_synthesize(self, topic: str, spec: GenerationSpec, top_k: int = 5) -> Dict[str, Any]:
        """
        Search the entire ingested knowledge base and synthesize relevant context.

        Retrieves from all sources: blog posts, RSS articles, and any other ingested content
        to provide comprehensive context for blog post generation.

        Args:
            topic: The search topic
            spec: Generation specification
            top_k: Number of results to retrieve

        Returns:
            Dictionary with summary and excerpts
        """
        logger.info(f"Retriever agent searching entire knowledge base for: {topic}")

        try:
            # Retrieve relevant documents from ALL ingested sources
            context_docs = await retrieve_relevant_context(
                topic,
                top_k=top_k,
                expand_queries=True
            )

            if not context_docs:
                logger.info("No relevant context found in entire knowledge base")
                return {
                    "summary": f"No relevant context found for '{topic}'",
                    "excerpts": [],
                    "source_count": 0
                }

            # Log sources found for transparency
            sources = set()
            for doc in context_docs:
                source_type = doc.metadata.get("source_type", "blog_post")
                title = doc.metadata.get("title", "Unknown")
                sources.add(f"{source_type}: {title}")

            logger.info(f"Retrieved context from {len(context_docs)} documents spanning {len(sources)} sources: {', '.join(list(sources)[:5])}{'...' if len(sources) > 5 else ''}")

            # Assemble context window
            context_window = await assemble_context_window(context_docs, max_tokens=2000)

            # Synthesize summary and key excerpts
            synthesis_prompt = RETRIEVER_PROMPT_TEMPLATE.substitute(
                topic=topic,
                context=context_window,
                excerpt_limit=5
            )

            response = await self.llm_client.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": synthesis_prompt}
            ], temperature=0.2)

            # Parse response into summary and excerpts
            parsed = self._parse_synthesis_response(response)

            return {
                "summary": parsed["summary"],
                "excerpts": parsed["excerpts"],
                "source_count": len(context_docs)
            }

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {
                "summary": f"Error retrieving context for '{topic}': {str(e)}",
                "excerpts": [],
                "source_count": 0
            }

    def _parse_synthesis_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into summary and excerpts."""
        # Simple parsing - look for SUMMARY and EXCERPTS sections
        summary = ""
        excerpts = []

        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if 'SUMMARY:' in line.upper() or 'CONCISE SUMMARY:' in line.upper():
                current_section = 'summary'
                # Extract summary text after the colon
                if ':' in line:
                    summary_part = line.split(':', 1)[1].strip()
                    if summary_part:
                        summary = summary_part
            elif 'EXCERPTS:' in line.upper() or 'RELEVANT EXCERPTS:' in line.upper():
                current_section = 'excerpts'
            elif current_section == 'summary' and not line.upper().startswith('EXCERPTS'):
                summary += line + ' '
            elif current_section == 'excerpts' and (line.startswith('-') or line.startswith('*')):
                excerpt = line[1:].strip()
                if excerpt:
                    excerpts.append(excerpt)

        # If parsing failed, use the whole response as summary
        if not summary and not excerpts:
            summary = response

        return {
            "summary": summary.strip(),
            "excerpts": excerpts[:5]  # Limit to 5 excerpts
        }
