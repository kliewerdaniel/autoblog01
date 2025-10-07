"""Ingestor Agent: Saves finalized content and updates knowledge base."""

import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import GeneratedContent, BlogPost
from llm_client import llm_client
from utils.file_utils import write_blog_post, generate_filename, generate_frontmatter

logger = logging.getLogger(__name__)


class IngestorAgent:
    """Agent responsible for saving finalized blog posts and updating the knowledge base."""

    def __init__(self, llm_client_instance=None):
        self.llm_client = llm_client_instance or llm_client

    async def ingest_final_content(self, final_draft: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the approved blog post and update the knowledge base.

        Args:
            final_draft: Final approved content
            spec: Generation specifications

        Returns:
            Ingestion result with file paths and confirmation
        """
        logger.info(f"Ingestor agent saving final content: {final_draft.get('topic', 'Unknown topic')}")

        try:
            content = final_draft['content']
            topic = final_draft.get('topic', 'Generated Post')

            # Create GeneratedContent object with corrected date format
            spec_dict = spec if isinstance(spec, dict) else spec.dict()
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            gen_content = GeneratedContent(
                title=self._extract_title(content) or topic,
                content=content,
                frontmatter={
                    'title': self._extract_title(content) or topic,
                    'date': date_str,
                    'categories': spec_dict.get('categories', []),
                    'tags': spec_dict.get('tags', []),
                    'description': self._extract_description(content)
                },
                word_count=final_draft.get('word_count', 0)
            )

            # Generate filename and save
            filename = generate_filename(gen_content)
            # Ensure .md extension
            if not filename.endswith('.md'):
                filename += '.md'

            # Use draft spec to create GenerationSpec for frontmatter
            from models import GenerationSpec
            draft_spec = final_draft.get('spec', {})
            gen_spec = GenerationSpec(**draft_spec)
            frontmatter = generate_frontmatter(gen_spec, gen_content)

            # Write the file using the utility function
            file_path = write_blog_post(filename, frontmatter, content.lstrip())

            logger.info(f"Blog post saved to: {file_path}")

            return {
                "success": True,
                "file_path": str(file_path),
                "file_url": f"/blog/{filename.replace('.md', '')}",
                "word_count": gen_content.word_count,
                "title": gen_content.title
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": final_draft.get('topic', 'Unknown')
            }

    def _extract_title(self, content: str) -> str:
        """Extract title from H1 header."""
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return None

    def _extract_description(self, content: str) -> str:
        """Extract or generate description from content."""
        # Look for frontmatter description first
        if 'description:' in content[:500]:
            lines = content[:500].split('\n')
            for line in lines:
                if line.startswith('description:'):
                    desc = line.split(':', 1)[1].strip()
                    if desc.startswith('"') and desc.endswith('"'):
                        desc = desc[1:-1]
                    return desc

        # Fallback: use first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            first_para = paragraphs[0]
            # Remove markdown headers and take first 150 chars
            desc = re.sub(r'^#\s*', '', first_para)
            return desc[:150] + '...' if len(desc) > 150 else desc

        return "Generated blog post content"
