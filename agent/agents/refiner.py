"""Refiner Agent: Iteratively improves blog post drafts."""

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
from prompts.system_prompts import REFFINER_SYSTEM_PROMPT
from prompts.templates import REFINER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class RefinerAgent:
    """Agent responsible for refining and improving blog post drafts."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client
        self.system_prompt = REFFINER_SYSTEM_PROMPT

    async def refine_draft(self, draft: Dict[str, Any], spec: GenerationSpec, feedback: str = None) -> Dict[str, Any]:
        """
        Refine the blog post draft to improve quality and engagement.

        Args:
            draft: Current draft content and metadata
            spec: Generation specifications
            feedback: Optional feedback from evaluator for targeted improvements

        Returns:
            Refined draft with improvements
        """
        logger.info(f"Refiner agent improving draft iteration {draft.get('iteration', 1)}")

        try:
            # Extract content body and frontmatter
            content = draft['content']
            frontmatter = ""
            content_body = content

            if content.startswith('---'):
                # Separate frontmatter from content
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[0] + '---' + parts[1] + '---\n\n'
                    content_body = parts[2].strip()

            # Prepare refinement prompt with content body only
            prompt = REFINER_PROMPT_TEMPLATE.substitute(
                draft_content=content_body,
                length=spec.max_words,
                min_words=spec.min_words,
                max_words=spec.max_words,
                style=spec.style,
                tone=spec.tone,
                categories=', '.join(spec.categories) if spec.categories else "",
                tags=', '.join(spec.tags) if spec.tags else ""
            )

            # Add specific feedback if provided
            if feedback:
                prompt += f"\n\nSPECIFIC FEEDBACK TO ADDRESS:\n{feedback}\n\nIMPORTANT: Stay within {spec.min_words}-{spec.max_words} word range. Only fix the specific issues mentioned, don't add unnecessary content or change the structure drastically."
            else:
                prompt += f"\n\nIMPORTANT: Stay within {spec.min_words}-{spec.max_words} word range. Make improvements while respecting word count limits and maintaining the original structure."

            # Refine the content body only
            response = await self.llm_client.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ], temperature=0.3)  # Lower temperature for more controlled refinement

            # Combine frontmatter back with refined content
            full_content = frontmatter + response if frontmatter else response

            # Extract word count from content body only (exclude frontmatter)
            word_count = len(response.split())

            refined_draft = {
                "content": full_content,
                "word_count": word_count,
                "topic": draft['topic'],
                "spec": spec.dict(),
                "iteration": draft.get('iteration', 1) + 1
            }

            logger.info(f"Refined draft: iteration {refined_draft['iteration']}, {word_count} words")

            return refined_draft

        except Exception as e:
            logger.error(f"Refinement failed: {e}")
            # Return original draft if refinement fails
            return {
                "error": f"Refinement failed: {str(e)}",
                **draft
            }
