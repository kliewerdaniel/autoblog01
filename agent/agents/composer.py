"""Composer Agent: Creates initial blog post drafts."""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import GenerationSpec
from llm_client import llm_client
from prompts.system_prompts import COMPOSER_SYSTEM_PROMPT
from prompts.templates import COMPOSER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class ComposerAgent:
    """Agent responsible for creating initial blog post drafts."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client
        self.system_prompt = COMPOSER_SYSTEM_PROMPT

    def _clean_frontmatter_from_response(self, response: str) -> str:
        """
        Clean any accidental frontmatter-like content from the LLM response.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned response containing only the markdown body
        """
        lines = response.strip().split('\n')

        # If response starts with --- and contains frontmatter-like content, find where it ends
        if lines and lines[0] == '---':
            # Look for the closing ---
            in_frontmatter = True
            cleaned_lines = []
            for line in lines[1:]:
                if line.strip() == '---':
                    in_frontmatter = False
                    continue
                if not in_frontmatter:
                    cleaned_lines.append(line)

            if cleaned_lines:
                return '\n'.join(cleaned_lines).lstrip()

        # If no frontmatter detected, return as-is but ensure it starts with #
        if lines and not lines[0].startswith('# '):
            # If first non-empty line isn't H1, prepend one
            first_content_line = next((line for line in lines if line.strip()), "")
            if first_content_line and not first_content_line.startswith('# '):
                # If it has a title that looks like it should be H1
                if first_content_line and not first_content_line.startswith('#'):
                    return f"# {first_content_line}\n\n" + '\n'.join(lines[1:])

        return response.strip()

    async def compose_draft(self, topic: str, retriever_output: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """
        Create an initial blog post draft based on retriever context.

        Args:
            topic: The blog post topic
            retriever_output: Output from the Retriever agent
            spec: Generation specifications

        Returns:
            Dictionary containing the draft content and metadata
        """
        logger.info(f"Composer agent creating initial draft for: {topic}")

        try:
            # Format excerpts for the prompt
            excerpts_formatted = "\n".join([
                f"- {excerpt}" for excerpt in retriever_output.get('excerpts', [])
            ])

            # Calculate word counts based on length if not present
            if not hasattr(spec, 'max_words') or spec.max_words == 0:
                word_counts = {'short': (600, 1000), 'medium': (1000, 1500), 'long': (1500, 2500)}
                min_words, max_words = word_counts.get(spec.length, (1000, 1500))
                if not hasattr(spec, 'min_words'):
                    spec.min_words = min_words
                if not hasattr(spec, 'max_words'):
                    spec.max_words = max_words

            # Prepare prompt variables
            prompt = COMPOSER_PROMPT_TEMPLATE.substitute(
                topic=topic,
                summary=retriever_output.get('summary', 'No summary available'),
                excerpts=excerpts_formatted,
                style=spec.style,
                length=getattr(spec, 'max_words', 1500),  # Target the max word count
                min_words=getattr(spec, 'min_words', 1000),
                max_words=getattr(spec, 'max_words', 1500),
                tone=spec.tone,
                categories=', '.join(spec.categories) if spec.categories else "",
                tags=', '.join(spec.tags) if spec.tags else ""
            )

            # Generate the draft content (body only, frontmatter will be added later)
            response = await self.llm_client.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ], temperature=0.7)  # Higher temperature for creative writing

            # Clean the response to remove any accidental frontmatter
            full_content = self._clean_frontmatter_from_response(response)

            # Extract word count from content only (exclude frontmatter)
            content_word_count = len(response.split())

            draft_output = {
                "content": full_content,
                "word_count": content_word_count,
                "topic": topic,
                "spec": spec.dict(),
                "iteration": 1
            }

            logger.info(f"Initial draft created: {content_word_count} words")

            return draft_output

        except Exception as e:
            logger.error(f"Composition failed: {e}")
            return {
                "error": str(e),
                "topic": topic,
                "spec": spec.dict() if spec else {}
            }
