"""
Researcher Agent: Analyzes knowledge base and synthesizes research briefs.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import ResearchBrief, Document
from llm_client import llm_client
from retrieval import gather_context_for_topic
from config import config
from prompts.system_prompts import RESEARCHER_SYSTEM_PROMPT
from prompts.templates import render_researcher_prompt

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """Agent responsible for analyzing existing content and creating research briefs."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client
        self.system_prompt = RESEARCHER_SYSTEM_PROMPT

    async def research_topic(self, topic: str, spec: Dict[str, Any]) -> ResearchBrief:
        """
        Perform comprehensive research on a topic.

        Args:
            topic: The blog post topic to research
            spec: Generation specifications

        Returns:
            Research brief with findings and recommendations
        """
        logger.info(f"Researcher agent starting research on: {topic}")

        try:
            # Gather relevant context from knowledge base
            brief = await gather_context_for_topic(topic, spec)

            # Enhance the research brief with LLM analysis if needed
            if not brief.key_themes:  # If basic parsing didn't yield good results
                enhanced_brief = await self._enhance_research_with_llm(topic, brief, spec)
                return enhanced_brief

            logger.info(f"Research complete - found {len(brief.key_themes)} themes, {len(brief.relevant_facts)} facts")

            return brief

        except Exception as e:
            logger.error(f"Research failed for topic '{topic}': {e}")
            # Return basic brief on error
            return ResearchBrief(
                key_themes=[topic],
                relevant_facts=["Research context unavailable"],
                recommended_focus=[f"General coverage of {topic}"]
            )

    async def _enhance_research_with_llm(
        self,
        topic: str,
        basic_brief: ResearchBrief,
        spec: Dict[str, Any]
    ) -> ResearchBrief:
        """Use LLM to enhance research brief when automatic parsing is insufficient."""

        # Assemble context for LLM analysis
        context_docs = basic_brief.context_documents

        if context_docs:
            # Format context for LLM
            context_text = "\n\n".join([
                f"From {doc.metadata.get('title', 'Unknown')}: {doc.page_content[:500]}..."
                for doc in context_docs[:5]  # Limit to top 5 results
            ])
        else:
            context_text = "No relevant context found in knowledge base."

        # Render prompt
        prompt = render_researcher_prompt(topic, context_text, spec)

        try:
            # Get LLM analysis
            response = await self.llm_client.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            # Parse LLM response into structured brief
            enhanced_brief = self._parse_llm_research_response(response)
            enhanced_brief.context_documents = context_docs  # Preserve context docs

            return enhanced_brief

        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")
            return basic_brief

    def _parse_llm_research_response(self, response: str) -> ResearchBrief:
        """Parse LLM response into ResearchBrief model."""
        brief = ResearchBrief()

        # Simple parsing logic (could be improved)
        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            if 'KEY THEMES' in line.upper() or 'MAIN THEMES' in line.upper():
                current_section = 'themes'
            elif 'RELEVANT FACTS' in line.upper() or 'KEY FACTS' in line.upper():
                current_section = 'facts'
            elif 'RELATED TOPICS' in line.upper():
                current_section = 'topics'
            elif 'GAPS' in line.upper() or 'OPPORTUNITIES' in line.upper():
                current_section = 'gaps'
            elif 'RECOMMENDED FOCUS' in line.upper() or 'FOCUS AREAS' in line.upper():
                current_section = 'focus'

            # Parse list items
            elif current_section and (line.startswith('- ') or line.startswith('* ')):
                content = line[2:].strip()
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

        # Ensure we have at least basic content
        if not brief.key_themes:
            brief.key_themes = ["Topic research in progress"]
        if not brief.recommended_focus:
            brief.recommended_focus = ["Comprehensive topic coverage"]

        return brief

    def get_research_summary(self, brief: ResearchBrief) -> str:
        """Generate human-readable summary of research findings."""
        summary = f"""
Research Summary:
- Key Themes: {len(brief.key_themes)} identified
- Relevant Facts: {len(brief.relevant_facts)} found
- Related Content: {len(brief.related_topics)} existing posts
- Gaps Identified: {len(brief.gaps_identified)} opportunities
- Focus Areas: {len(brief.recommended_focus)} recommended

Primary Focus Recommendations:
"""
        for i, focus in enumerate(brief.recommended_focus[:3], 1):
            summary += f"{i}. {focus}\n"

        return summary.strip()
