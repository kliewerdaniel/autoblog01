"""Agentic Workflow Orchestrator for Blog Post Generation."""

import asyncio
import sys
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import GenerationSpec
from agents import RetrieverAgent, ComposerAgent, RefinerAgent, EvaluatorAgent, IngestorAgent
from config import config

logger = logging.getLogger(__name__)


@dataclass
class WorkflowResult:
    """Result of the agentic workflow."""
    success: bool
    final_content: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    iterations: int = 0
    approval_status: str = "pending"
    error: Optional[str] = None


class BlogGenerationOrchestrator:
    """Orchestrates the multi-agent blog post generation workflow."""

    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.config = {**config.__dict__, **(config_override or {})}
        self.max_iterations = self.config.get('max_refinement_iterations', 5)

        # Initialize agents
        self.retriever = RetrieverAgent()
        self.composer = ComposerAgent()
        self.refiner = RefinerAgent()
        self.evaluator = EvaluatorAgent()
        self.ingestor = IngestorAgent()

    async def generate_blog_post(self, topic: str, spec_data: Dict[str, Any]) -> WorkflowResult:
        """
        Execute the complete agentic workflow to generate a blog post.

        Args:
            topic: The blog post topic
            spec_data: Generation specifications

        Returns:
            Workflow result with final content and metadata
        """
        logger.info(f"Starting agentic workflow for topic: {topic}")

        try:
            # Calculate word counts based on length
            word_counts = {'short': (600, 1000), 'medium': (1000, 1500), 'long': (1500, 2500)}
            min_words, max_words = word_counts.get(spec_data.get('length', 'medium'), (1000, 1500))

            # Add word count fields to spec_data
            spec_data['min_words'] = spec_data.get('min_words', min_words)
            spec_data['max_words'] = spec_data.get('max_words', max_words)

            # Convert spec data to GenerationSpec object
            spec = GenerationSpec(**spec_data)

            # Phase 1: Retrieval
            logger.info("Phase 1: Retrieving context from knowledge base")
            retriever_output = await self.retriever.search_and_synthesize(
                topic, spec, top_k=self.config.get('top_k_retrieval', 5)
            )

            if not retriever_output.get('summary'):
                return WorkflowResult(
                    success=False,
                    error="Failed to retrieve relevant context"
                )

            # Phase 2: Composition
            logger.info("Phase 2: Composing initial draft")
            draft = await self.composer.compose_draft(topic, retriever_output, spec)

            if 'error' in draft:
                return WorkflowResult(
                    success=False,
                    error=f"Composition failed: {draft['error']}"
                )

            # Phase 3: Iterative Refinement
            logger.info("Phase 3: Iterative refinement and evaluation")
            final_draft = await self._iterative_refinement_loop(draft, spec)

            if not final_draft:
                # Fallback: Return the last draft if no approval achieved after max iterations
                logger.warning(f"No draft approved after {self.max_iterations} iterations, falling back to last iteration")
                final_draft = draft  # Use initial draft if no iterations succeeded

            # Phase 4: Ingestion
            logger.info("Phase 4: Ingesting final content")
            ingestion_result = await self.ingestor.ingest_final_content(final_draft, spec_data)

            if not ingestion_result.get('success', False):
                return WorkflowResult(
                    success=False,
                    error=f"Ingestion failed: {ingestion_result.get('error', 'Unknown error')}",
                    iterations=final_draft.get('iteration', 1)
                )

            # Success!
            return WorkflowResult(
                success=True,
                final_content=final_draft,
                file_path=ingestion_result.get('file_path'),
                iterations=final_draft.get('iteration', 1),
                approval_status="approved"
            )

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return WorkflowResult(
                success=False,
                error=str(e)
            )

    async def _iterative_refinement_loop(self, initial_draft: Dict[str, Any], spec: GenerationSpec) -> Optional[Dict[str, Any]]:
        """
        Iteratively refine the draft until it passes evaluation or hits max iterations.

        Args:
            initial_draft: The initial draft from composer
            spec: Generation specifications

        Returns:
            Final approved draft or None if failed
        """
        current_draft = initial_draft
        feedback = None

        for iteration in range(self.max_iterations):
            logger.info(f"Refinement iteration {iteration + 1}/{self.max_iterations}")

            # Refine the draft (skip for first iteration if feedback is None)
            if feedback and iteration > 0:
                current_draft = await self.refiner.refine_draft(current_draft, spec, feedback)

                if 'error' in current_draft:
                    logger.warning(f"Refinement failed: {current_draft['error']}")
                    # Continue with previous draft

            # Evaluate the current draft
            evaluation = await self.evaluator.evaluate_draft(current_draft, spec)

            if evaluation.get('approved', False):
                logger.info(f"Draft approved on iteration {iteration + 1}")
                return current_draft

            # Extract feedback for next iteration
            feedback = evaluation.get('feedback', 'Content needs improvement')
            logger.info(f"Draft rejected: {feedback}")

            # Brief pause between iterations
            await asyncio.sleep(0.1)

        logger.warning("Maximum iterations reached without approval")
        # Return the last draft as fallback
        return current_draft
