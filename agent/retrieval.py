"""
Semantic retrieval system with RAG capabilities.

Handles query expansion, multi-query retrieval, re-ranking, and context assembly.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from .config import config
    from .models import Document, ResearchBrief, LLMMesssage
    from .llm_client import llm_client
    from .vector_store import vector_store
except ImportError:
    from config import config
    from models import Document, ResearchBrief, LLMMesssage
    from llm_client import llm_client
    from vector_store import vector_store

logger = logging.getLogger(__name__)


async def expand_query(query: str, llm_client_instance=None) -> List[str]:
    """
    Generate multiple related search queries for better retrieval.

    Args:
        query: Original query
        llm_client_instance: LLM client instance (optional)

    Returns:
        List of expanded queries including original
    """
    if llm_client_instance is None:
        llm_client_instance = llm_client

    expansion_prompt = f"""
Generate 3-4 different search queries that would help find relevant information about: "{query}"

Focus on:
- Related subtopics
- Different phrasings
- Long-tail keywords
- Semantic variations

Return only the queries, one per line, no numbering or bullets.

Example for "machine learning optimization":
What are the best algorithms for ML model optimization?
How to improve machine learning model performance?
Techniques for optimizing neural network training
ML hyperparameter tuning methods
"""

    try:
        response = await llm_client_instance.generate(expansion_prompt, temperature=0.3)
        expanded_queries = [q.strip() for q in response.split('\n') if q.strip()]

        # Include original query and limit to 4 total
        queries = [query] + expanded_queries[:3]
        return queries

    except Exception as e:
        logger.warning(f"Query expansion failed: {e}")
        return [query]  # Fallback to original query


async def retrieve_relevant_context(
    query: str,
    top_k: int = None,
    expand_queries: bool = True,
    filters: Optional[Dict[str, Any]] = None,
    search_all_ingested: bool = True
) -> List[Document]:
    """
    Retrieve relevant context from the entire ingested knowledge base.

    Searches across all ingested content including blog posts and RSS articles
    to provide comprehensive context for blog post generation.

    Args:
        query: Search query
        top_k: Number of results to return
        expand_queries: Whether to expand query with multiple formulations
        filters: Optional metadata filters
        search_all_ingested: Always search entire database (kept for backward compatibility)

    Returns:
        List of relevant documents from all ingested sources
    """
    if top_k is None:
        top_k = config.top_k_retrieval

    try:
        # Query expansion for better retrieval
        if expand_queries:
            queries = await expand_query(query)
            logger.info(f"Expanded query into {len(queries)} variations")
        else:
            queries = [query]

        # Perform multi-query retrieval
        all_results = []
        for q in queries:
            try:
                results = vector_store.similarity_search(q, top_k=top_k, filters=filters)
                all_results.extend(results)
                logger.debug(f"Query '{q[:50]}...' returned {len(results)} results")
            except Exception as e:
                logger.warning(f"Query failed: {q[:50]}...: {e}")
                continue

        if not all_results:
            logger.warning("No results found for any queries")
            return []

        # Remove duplicates based on content
        unique_results = _deduplicate_results(all_results)

        # Re-rank results by relevance
        reranked_results = _rerank_results(unique_results, query)

        # Return top results
        final_results = reranked_results[:top_k]

        logger.info(f"Retrieved {len(final_results)} unique, reranked results")

        return final_results

    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        return []


def _deduplicate_results(results: List[Document]) -> List[Document]:
    """Remove duplicate results based on content similarity."""
    seen_content = set()
    unique_results = []

    for doc in results:
        # Simple deduplication based on first 200 characters
        content_hash = hash(doc.page_content[:200])

        if content_hash not in seen_content:
            unique_results.append(doc)
            seen_content.add(content_hash)

    logger.debug(f"Deduplicated {len(results)} -> {len(unique_results)} results")
    return unique_results


def _rerank_results(results: List[Document], original_query: str) -> List[Document]:
    """
    Re-rank results by enhanced relevance scoring.

    Considers multiple factors:
    - Semantic similarity score
    - Recency (newer posts get slight boost)
    - Query term frequency in content
    - Content quality indicators
    """
    for doc in results:
        base_score = doc.metadata.get("relevance_score", 0)

        # Recency boost (newer posts slightly preferred)
        recency_boost = 0
        if doc.metadata.get("date"):
            try:
                from datetime import datetime
                post_date = datetime.fromisoformat(doc.metadata["date"])
                days_old = (datetime.now(post_date.tzinfo) - post_date).days

                # Boost recent posts (within 1 year: +0.1, within 1 month: +0.05)
                if days_old < 30:
                    recency_boost = 0.05
                elif days_old < 365:
                    recency_boost = 0.02
            except:
                pass

        # Keyword frequency boost
        query_terms = original_query.lower().split()
        content_lower = doc.page_content.lower()
        keyword_matches = sum(1 for term in query_terms if term in content_lower)
        keyword_boost = min(keyword_matches * 0.02, 0.1)  # Max 0.1 boost

        # Length quality (prefer substantial content)
        content_length = len(doc.page_content.split())
        length_boost = max(0, min(0.05, (content_length - 50) / 1000))  # Boost for 50-1000 words

        # Calculate final score
        final_score = (
            base_score +
            recency_boost +
            keyword_boost +
            length_boost
        )

        doc.metadata["final_score"] = final_score

    # Sort by final score descending
    results.sort(key=lambda x: x.metadata["final_score"], reverse=True)

    return results


async def assemble_context_window(results: List[Document], max_tokens: int = 4000) -> str:
    """
    Assemble retrieved documents into a coherent context window.

    Args:
        results: List of retrieved documents
        max_tokens: Maximum context length in tokens

    Returns:
        Assembled context string
    """
    if not results:
        return "No relevant context found."

    # Estimate token usage (rough approximation)
    ESTIMATED_CHARS_PER_TOKEN = 4
    max_chars = max_tokens * ESTIMATED_CHARS_PER_TOKEN

    context_parts = []
    included_sources = set()
    total_chars = 0

    for doc in results:
        # Add source header if not already included
        source = doc.metadata.get("title", doc.metadata.get("source_file", "Unknown"))

        if source not in included_sources:
            header = f"\n## From: {source}\n"
            if total_chars + len(header) > max_chars:
                break

            # Add date if available
            if doc.metadata.get("date"):
                try:
                    from datetime import datetime
                    post_date = datetime.fromisoformat(doc.metadata["date"]).strftime("%B %Y")
                    header = f"\n## From: {source} ({post_date})\n"
                except:
                    pass

            context_parts.append(header)
            total_chars += len(header)
            included_sources.add(source)

        # Add content chunk
        content = doc.page_content.strip()
        if total_chars + len(content) > max_chars:
            # Truncate content to fit
            remaining_chars = max_chars - total_chars - 50  # Leave room for truncation marker
            if remaining_chars > 100:  # Only include if meaningful
                truncated_content = content[:remaining_chars] + "...\n"
                context_parts.append(truncated_content)
            break

        context_parts.append(content)
        total_chars += len(content)

        # Add separator
        if total_chars < max_chars:
            separator = "\n\n---\n\n"
            if total_chars + len(separator) < max_chars:
                context_parts.append(separator)
                total_chars += len(separator)

    # Join parts
    context = "".join(context_parts).strip()

    # Add summary statistics
    stats = f"\n\n--- Context assembled from {len(included_sources)} sources, {total_chars} characters ---"
    if total_chars + len(stats) < max_chars * 1.1:  # 10% overhead allowed
        context += stats

    logger.info(f"Assembled context: {len(included_sources)} sources, {total_chars} characters")

    return context


async def gather_context_for_topic(
    topic: str,
    spec: Dict[str, Any] = None,
    max_context_tokens: int = 3000
) -> ResearchBrief:
    """
    Gather comprehensive context for a blog post topic.

    Args:
        topic: Blog post topic
        spec: Generation specification
        max_context_tokens: Maximum context length

    Returns:
        Research brief with gathered context
    """
    logger.info(f"Gathering context for topic: {topic}")

    # Build search query from topic and spec
    search_query = topic
    if spec and spec.get("keywords"):
        keywords = spec["keywords"][:2]  # Use top 2 keywords
        search_query += f" {' '.join(keywords)}"

    # Retrieve relevant context
    context_docs = await retrieve_relevant_context(
        search_query,
        top_k=10,  # Get more for research
        expand_queries=True
    )

    if not context_docs:
        return ResearchBrief(
            context_documents=[],
            relevant_facts=["No relevant context found in knowledge base."],
            recommended_focus=[f"General overview of {topic}"]
        )

    # Assemble context for research
    context_window = await assemble_context_window(context_docs, max_context_tokens)

    # Use LLM to synthesize research brief
    research_prompt = f"""
Analyze the following context about "{topic}" and provide a structured research brief:

CONTEXT:
{context_window}

Provide your response in this JSON-like format:

KEY_THEMES: List the main themes and concepts found in the context
RELEVANT_FACTS: Key facts, statistics, or findings from the existing content
RELATED_TOPICS: Topics covered in related blog posts
GAPS_IDENTIFIED: Areas not well covered in existing content
RECOMMENDED_FOCUS: Suggested areas to focus on in the new post

Be specific and actionable.
"""

    try:
        response = await llm_client.generate(research_prompt, temperature=0.2)

        # Parse response into ResearchBrief
        brief = ResearchBrief(context_documents=context_docs)

        # Simple parsing (could be improved with better NLP)
        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('KEY_THEMES:'):
                current_section = 'themes'
            elif line.startswith('RELEVANT_FACTS:'):
                current_section = 'facts'
            elif line.startswith('RELATED_TOPICS:'):
                current_section = 'topics'
            elif line.startswith('GAPS_IDENTIFIED:'):
                current_section = 'gaps'
            elif line.startswith('RECOMMENDED_FOCUS:'):
                current_section = 'focus'
            elif current_section and line.startswith('-'):
                content = line[1:].strip()
                if current_section == 'themes':
                    brief.key_themes.append(content)
                elif current_section == 'facts':
                    brief.relevant_facts.append(content)
                elif current_section == 'topics':
                    brief.related_topics.append(content)
                elif current_section == 'gaps':
                    brief.gaps_identified.append(content)
                elif current_section == 'focus':
                    brief.recommended_focus.append(content)

        logger.info(f"Generated research brief with {len(brief.key_themes)} themes, {len(brief.relevant_facts)} facts")

        return brief

    except Exception as e:
        logger.warning(f"Failed to generate structured research brief: {e}")

        # Fallback to basic brief
        return ResearchBrief(
            key_themes=[topic],
            relevant_facts=["Context available from knowledge base"],
            context_documents=context_docs,
            recommended_focus=["Comprehensive coverage of the topic"]
        )
