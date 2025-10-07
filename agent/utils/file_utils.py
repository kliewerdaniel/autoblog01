"""
File I/O utilities for reading, writing, and managing blog posts.
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from slugify import slugify

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from config import config
from models import BlogPost, GeneratedContent, GenerationSpec


def scan_blog_posts(blog_dir: Path) -> List[Path]:
    """
    Scan the blog directory for markdown files.

    Args:
        blog_dir: Path to the blog directory

    Returns:
        List of markdown file paths
    """
    if not blog_dir.exists():
        raise FileNotFoundError(f"Blog directory not found: {blog_dir}")

    md_files = []
    for file_path in blog_dir.rglob("*.md"):
        if file_path.is_file():
            md_files.append(file_path)

    return sorted(md_files)


def generate_filename(content: GeneratedContent) -> str:
    """
    Generate filename for a new blog post.

    Args:
        content: Generated content object

    Returns:
        Filename in YYYY-MM-DD-slug.md format
    """
    if not content.frontmatter.get('date'):
        # Generate current date if not provided
        now = datetime.now(timezone(timedelta(hours=-5)))  # CDT timezone
        date_str = now.strftime("%Y-%m-%d")
    else:
        # Use provided date
        date_obj = content.frontmatter['date']
        if isinstance(date_obj, datetime):
            date_str = date_obj.strftime("%Y-%m-%d")
        else:
            date_str = str(date_obj).split()[0]

    # Generate slug from title
    slug = content.frontmatter.get('slug')
    if not slug:
        slug = slugify(content.title)

    # Check for existing files and add suffix if needed
    base_filename = f"{date_str}-{slug}.md"
    filename = base_filename
    counter = 1

    while (config.blog_dir / filename).exists():
        filename = f"{date_str}-{slug}-{counter}.md"
        counter += 1

    return filename


def generate_frontmatter(spec: GenerationSpec, content: GeneratedContent, seo_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate complete frontmatter for a blog post.

    Args:
        spec: Generation specification
        content: Generated content
        seo_metadata: Additional SEO metadata

    Returns:
        Frontmatter dictionary
    """
    # Generate timestamp with microseconds, no timezone since example doesn't show it
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")

    # Generate slug
    slug = slugify(content.title)

    # Build frontmatter
    frontmatter = {
        "title": content.title,
        "date": date_str,
        "categories": spec.categories or ["Uncategorized"],
        "tags": spec.tags or [],
        "description": generate_excerpt(content.content, spec.topic),
        "slug": slug
    }

    # Add SEO metadata if available
    if seo_metadata:
        if 'meta_description' in seo_metadata:
            frontmatter['description'] = seo_metadata['meta_description']
        if 'optimized_title' in seo_metadata:
            frontmatter['title'] = seo_metadata['optimized_title']

    return frontmatter


def generate_excerpt(content: str, topic: str, max_length: int = 160) -> str:
    """
    Generate a compelling excerpt from content.

    Args:
        content: Full content string
        topic: Topic for context
        max_length: Maximum excerpt length

    Returns:
        Generated excerpt
    """
    # Extract first meaningful paragraph
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    for paragraph in paragraphs:
        # Skip if it's just a heading or too short
        if paragraph.startswith('#') or len(paragraph) < 50:
            continue

        # Clean up markdown formatting
        clean_para = paragraph.replace('*', '').replace('_', '').replace('`', '').strip()

        # Truncate to max length
        if len(clean_para) > max_length:
            clean_para = clean_para[:max_length-3] + "..."

        # Ensure it ends with a complete sentence if possible
        if not clean_para.endswith(('.', '!', '?')):
            last_sentence_end = max(
                clean_para.rfind('.'),
                clean_para.rfind('!'),
                clean_para.rfind('?')
            )
            if last_sentence_end > max_length * 0.5:  # At least half the excerpt
                clean_para = clean_para[:last_sentence_end+1]

        return clean_para

    # Fallback: generate from topic
    return f"Learn about {topic.lower()}. Discover insights, best practices, and practical guidance."


def write_blog_post(filename: str, frontmatter: Dict[str, Any], content: str) -> Path:
    """
    Write a complete blog post to file.

    Args:
        filename: Target filename
        frontmatter: Frontmatter dictionary
        content: Content string

    Returns:
        Path to the written file

    Raises:
        Exception: If writing fails
    """
    file_path = config.blog_dir / filename

    # Ensure blog directory exists
    config.blog_dir.mkdir(parents=True, exist_ok=True)

    # Create backup if file exists
    if file_path.exists():
        backup_path = file_path.with_suffix('.backup.md')
        shutil.copy2(file_path, backup_path)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("---\n")

            # Write frontmatter in exact format matching the desired output
            f.write(f"title: \"{frontmatter['title']}\"\n")
            f.write(f"date: {frontmatter['date']}\n")

            # Format categories and tags as quoted items in list format
            categories_formatted = ', '.join(f'"{c}"' for c in frontmatter['categories'])
            tags_formatted = ', '.join(f'"{t}"' for t in frontmatter['tags'])
            f.write(f"categories: [{categories_formatted}]\n")
            f.write(f"tags: [{tags_formatted}]\n")
            f.write(f"description: \"{frontmatter['description']}\"\n")

            f.write("---\n\n")
            f.write(content)

        return file_path

    except Exception as e:
        # Restore backup if it exists
        if file_path.with_suffix('.backup.md').exists():
            shutil.move(file_path.with_suffix('.backup.md'), file_path)
        raise Exception(f"Failed to write blog post: {e}")


def create_index_manifest(posts: List[BlogPost], manifest_path: Path = None) -> Dict[str, Any]:
    """
    Create an index manifest tracking ingested posts and their metadata.

    Args:
        posts: List of parsed blog posts
        manifest_path: Path to save manifest (optional)

    Returns:
        Manifest dictionary
    """
    manifest = {
        "version": "1.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_posts": len(posts),
        "posts": {}
    }

    for post in posts:
        manifest["posts"][str(post.file_path)] = {
            "title": post.title,
            "date": post.date.isoformat() if post.date else None,
            "word_count": post.word_count,
            "categories": post.categories,
            "tags": post.tags,
            "slug": post.slug,
            "file_modified": post.file_path.stat().st_mtime if post.file_path.exists() else None
        }

    if manifest_path:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


def read_index_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Read existing index manifest.

    Args:
        manifest_path: Path to manifest file

    Returns:
        Manifest dictionary or empty dict if file doesn't exist
    """
    if not manifest_path.exists():
        return {}

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def get_new_or_modified_posts(existing_manifest: Dict[str, Any], all_posts: List[BlogPost]) -> List[BlogPost]:
    """
    Identify posts that are new or have been modified since last ingestion.

    Args:
        existing_manifest: Previously saved manifest
        all_posts: All current blog posts

    Returns:
        List of posts that need processing
    """
    changed_posts = []

    for post in all_posts:
        post_key = str(post.file_path)
        existing_data = existing_manifest.get("posts", {}).get(post_key)

        if not existing_data:
            # New post
            changed_posts.append(post)
        else:
            # Check if modified
            current_mtime = post.file_path.stat().st_mtime
            existing_mtime = existing_data.get("file_modified")

            if existing_mtime is None or current_mtime > existing_mtime:
                changed_posts.append(post)

    return changed_posts


def safe_filename(filename: str) -> str:
    """
    Generate a safe filename from an arbitrary string.

    Args:
        filename: Input filename

    Returns:
        Safe filename
    """
    # Remove or replace unsafe characters
    safe = re.sub(r'[^\w\-_\.]', '_', filename)

    # Ensure it doesn't start or end with problematic characters
    safe = safe.strip('._-')

    # Ensure it's not empty
    if not safe:
        safe = "unnamed_file"

    # Limit length
    if len(safe) > 255:
        name, ext = os.path.splitext(safe)
        safe = name[:255-len(ext)] + ext

    return safe
