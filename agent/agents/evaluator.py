"""Evaluator Agent: Assesses content quality and provides approval/rejection."""

import re
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import GenerationSpec, ValidationResult
from llm_client import llm_client
from prompts.system_prompts import EVALUATOR_SYSTEM_PROMPT
from prompts.templates import EVALUATOR_PROMPT_TEMPLATE
from utils.validator import validate_generation_spec

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """Agent responsible for evaluating blog post quality and providing approval."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client
        self.system_prompt = EVALUATOR_SYSTEM_PROMPT

    async def evaluate_draft(self, draft: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """
        Evaluate the blog post draft against quality standards.

        Args:
            draft: Draft content and metadata
            spec: Generation specifications

        Returns:
            Evaluation result with approval status and feedback
        """
        logger.info(f"Evaluator agent assessing draft: {draft.get('word_count', 0)} words, iteration {draft.get('iteration', 1)}")

        try:
            # Basic validation checks first
            basic_checks = self._perform_basic_validation(draft, spec)

            if not basic_checks['passed']:
                return {
                    "approved": False,
                    "feedback": basic_checks['feedback'],
                    "validation_details": basic_checks
                }

            # Advanced evaluation using LLM
            prompt = EVALUATOR_PROMPT_TEMPLATE.substitute(
                draft_content=draft['content'],
                min_words=spec.min_words,
                max_words=spec.max_words,
                current_words=draft.get('word_count', 0)
            )

            response = await self.llm_client.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ], temperature=0.1)  # Low temperature for consistent evaluation

            # Parse evaluation response
            evaluation = self._parse_evaluation_response(response)

            result = {
                "approved": evaluation['approved'],
                "feedback": evaluation['feedback'],
                "validation_details": basic_checks,
                "llm_evaluation": evaluation
            }

            logger.info(f"Evaluation result: {'APPROVED' if evaluation['approved'] else 'REJECTED'}")

            return result

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                "approved": False,
                "feedback": f"Evaluation failed: {str(e)}",
                "error": str(e)
            }

    def _perform_basic_validation(self, draft: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """Perform basic structural validation."""
        content = draft.get('content', '')
        word_count = draft.get('word_count', 0)

        checks = {
            "structure": self._check_structure(content),
            "word_count": self._check_word_count(word_count, spec),
            "markdown": self._check_markdown_formatting(content)
            # Removed frontmatter check since frontmatter is added later
        }

        passed = all(checks.values())
        feedback_parts = []

        if not checks["word_count"]:
            feedback_parts.append(f"Word count ({word_count}) not in range {spec.min_words}-{spec.max_words}")
        if not checks["structure"]:
            feedback_parts.append("Missing proper introduction, body, or conclusion sections")
        if not checks["markdown"]:
            feedback_parts.append("Markdown formatting issues detected")

        return {
            "passed": passed,
            "checks": checks,
            "feedback": "; ".join(feedback_parts) if feedback_parts else "All basic checks passed"
        }

    def _check_structure(self, content: str) -> bool:
        """Check if content has proper introduction, body, and conclusion."""
        # Look for at least H1 title, some paragraphs, and sections
        has_h1 = bool(re.search(r'^#\s+', content.strip(), re.MULTILINE))
        has_sections = len(re.findall(r'^##\s+', content, re.MULTILINE)) >= 2
        has_content_length = len(content.split()) >= 100

        return has_h1 and has_sections and has_content_length

    def _check_word_count(self, word_count: int, spec: GenerationSpec) -> bool:
        """Check if word count is within acceptable range."""
        return spec.min_words <= word_count <= spec.max_words

    def _check_markdown_formatting(self, content: str) -> bool:
        """Check basic markdown formatting."""
        # Check for proper headers and basic markdown structure
        has_proper_headers = bool(re.search(r'^#+\s+', content, re.MULTILINE))
        # Links are optional in blog posts, so only check for basic formatting
        return has_proper_headers

    def _check_frontmatter(self, content: str) -> bool:
        """Check if frontmatter is properly formatted."""
        lines = content.strip().split('\n')
        return len(lines) >= 3 and lines[0] == '---' and '---' in lines[1:]

    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM evaluation response."""
        response_upper = response.upper()

        if response_upper.startswith('APPROVED'):
            return {
                "approved": True,
                "feedback": "Content meets quality standards"
            }
        elif response_upper.startswith('REJECTED'):
            # Extract feedback after "REJECTED"
            feedback = response.split('\n', 1)[1] if '\n' in response else "Content needs improvement"
            return {
                "approved": False,
                "feedback": feedback.strip()
            }
        else:
            # Fallback parsing
            return {
                "approved": False,
                "feedback": "Unable to determine approval status from evaluation response"
            }
