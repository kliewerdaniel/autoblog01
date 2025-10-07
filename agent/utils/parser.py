"""
Utility functions for parsing Markdown files and frontmatter.

Handles blog post parsing, frontmatter extraction, and content processing.
"""

import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import frontmatter
import yaml

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from models import BlogPost, Document, DocumentChunk


def parse_blog_post(file_path: Path) -> BlogPost:
    """
    Parse a blog post from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Parsed BlogPost object

    Raises:
        ValueError: If the file cannot be parsed
    """
    try:
        post = frontmatter.load(str(file_path))

        # Extract frontmatter
        metadata = dict(post.metadata)

        # Parse date - handle different formats
        date_str = metadata.get('date')
        if isinstance(date_str, str):
            # Try common date formats
            date_formats = [
                '%Y-%m-%d %H:%M:%S %z',  # e.g., "2025-10-07 10:30:00 -0500"
                '%Y-%m-%d %H:%M:%S%z',   # e.g., "2025-10-07 10:30:00-0500"
                '%Y-%m-%d',               # e.g., "2025-10-07"
            ]
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue

            if parsed_date is None:
                # Try with space between time and timezone
                try:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
                except ValueError:
                    raise ValueError(f"Could not parse date: {date_str}")

            # Ensure timestamp is aware
            if parsed_date.tzinfo is None:
                # Assume it's in the local timezone, convert to offset-aware
                parsed_date = parsed_date.replace(tzinfo=timezone(timedelta(hours=-5)))  # Default to CDT

            date = parsed_date
        else:
            date = datetime.now(timezone.utc)

        # Extract other fields
        title = metadata.get('title', 'Untitled')
        categories = metadata.get('categories', [])
        if isinstance(categories, str):
            categories = [categories]
        tags = metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        excerpt = metadata.get('excerpt')
        slug = metadata.get('slug')

        # Word count
        word_count = len(str(post.content).split())

        return BlogPost(
            file_path=file_path,
            title=title,
            date=date,
            categories=categories,
            tags=tags,
            excerpt=excerpt,
            slug=slug,
            content=str(post.content),
            word_count=word_count,
            metadata=metadata
        )

    except Exception as e:
        raise ValueError(f"Failed to parse blog post {file_path}: {e}")


def extract_headings(content: str) -> List[Tuple[int, str]]:
    """
    Extract headings from markdown content.

    Args:
        content: Markdown content string

    Returns:
        List of (level, text) tuples for headings
    """
    headings = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            # Count the number of # to determine level
            level = 0
            i = 0
            while i < len(line) and line[i] == '#':
                level += 1
                i += 1

            # Skip the space after #
            if i < len(line) and line[i] == ' ':
                i += 1

            # Extract heading text
            heading_text = line[i:].strip()
            if heading_text:
                headings.append((level, heading_text))

    return headings


def chunk_content(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split content into semantically meaningful chunks.

    Args:
        content: Text content to chunk
        chunk_size: Target chunk size in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of content chunks
    """
    if not content:
        return []

    chunks = []

    # Split by paragraphs first (assuming double newlines separate paragraphs)
    paragraphs = re.split(r'\n\s*\n', content)

    current_chunk = ""
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # If adding this paragraph would exceed chunk_size, save current chunk
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with some overlap from previous
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + " " + paragraph
        else:
            current_chunk += (" " + paragraph) if current_chunk else paragraph

        # If current chunk is large enough, save it
        if len(current_chunk) >= chunk_size:
            chunks.append(current_chunk[:chunk_size].strip())
            current_chunk = current_chunk[chunk_size - overlap:].strip()

    # Add remaining content
    if current_chunk:
        chunks.append(current_chunk.strip())

    # Filter out very small chunks (less than 100 characters)
    chunks = [chunk for chunk in chunks if len(chunk) >= 100]

    return chunks


def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from content using simple heuristics.

    Args:
        content: Text content
        max_keywords: Maximum number of keywords to extract

    Returns:
        List of potential keywords
    """
    # Simple keyword extraction (in production, use NLP libraries)
    words = re.findall(r'\b\w+\b', content.lower())

    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
    }

    keywords = [word for word in words if len(word) > 3 and word not in stop_words]

    # Count frequency and get top keywords
    from collections import Counter
    keyword_freq = Counter(keywords)
    top_keywords = [word for word, _ in keyword_freq.most_common(max_keywords)]

    return top_keywords


def get_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time in minutes.

    Args:
        content: Text content
        words_per_minute: Average reading speed

    Returns:
        Estimated reading time in minutes
    """
    words = len(content.split())
    return max(1, round(words / words_per_minute))


def clean_markdown(content: str) -> str:
    """
    Clean markdown content for processing.

    Args:
        content: Raw markdown content

    Returns:
        Cleaned content
    """
    # Remove code blocks temporarily (they can interfere with processing)
    code_blocks = []
    def replace_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    content = re.sub(r'```.*?```', replace_code_block, content, flags=re.DOTALL)
    content = re.sub(r'`.*?`', replace_code_block, content)

    # Remove markdown links: [text](url) -> text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

    # Remove markdown formatting
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # bold
    content = re.sub(r'\*([^*]+)\*', r'\1', content)      # italic
    content = re.sub(r'_([^_]+)_', r'\1', content)        # italic underscore

    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        content = content.replace(f"__CODE_BLOCK_{i}__", code_block)

    return content
