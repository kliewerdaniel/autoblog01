"""
Content validation utilities for blog posts.

Validates frontmatter, content structure, and SEO requirements.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any
import sys
from pathlib import Path
from slugify import slugify

# Ensure imports work in both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from config import config
from models import ValidationResult, BlogPost, GeneratedContent
from utils.parser import extract_headings


def validate_blog_post(file_path: Path = None, content: str = None) -> ValidationResult:
    """
    Comprehensive validation of a blog post.

    Args:
        file_path: Path to the blog post file (alternative to content)
        content: Raw blog post content string (alternative to file_path)

    Returns:
        ValidationResult with errors, warnings, and suggestions
    """
    errors = []
    warnings = []
    suggestions = []

    try:
        if file_path and content is None:
            from .parser import parse_blog_post
            post = parse_blog_post(file_path)
            full_content = f"---\n{open(file_path).read()}"
        elif content:
            # Parse frontmatter from content
            import frontmatter
            post_data = frontmatter.loads(content)
            post = _create_blog_post_from_frontmatter(post_data, Path("temp.md"))
            full_content = content
        else:
            raise ValueError("Either file_path or content must be provided")

        # Validate frontmatter
        fm_errors, fm_warnings = _validate_frontmatter(post)
        errors.extend(fm_errors)
        warnings.extend(fm_warnings)

        # Validate content structure
        content_errors, content_warnings, content_suggestions = _validate_content_structure(post.content, post.title)
        errors.extend(content_errors)
        warnings.extend(content_warnings)
        suggestions.extend(content_suggestions)

        # Validate SEO elements
        seo_errors, seo_warnings, seo_suggestions = _validate_seo_elements(post, full_content)
        errors.extend(seo_errors)
        warnings.extend(seo_warnings)
        suggestions.extend(seo_suggestions)

    except Exception as e:
        errors.append(f"Failed to parse blog post: {str(e)}")

    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions
    )


def _create_blog_post_from_frontmatter(post_data, file_path: Path) -> BlogPost:
    """Helper to create BlogPost from frontmatter data."""
    return BlogPost(
        file_path=file_path,
        title=post_data.metadata.get('title', 'Untitled'),
        date=datetime.now(),
        categories=post_data.metadata.get('categories', []),
        tags=post_data.metadata.get('tags', []),
        excerpt=post_data.metadata.get('excerpt'),
        slug=post_data.metadata.get('slug'),
        content=post_data.content,
        word_count=len(post_data.content.split())
    )


def _validate_frontmatter(post: BlogPost) -> Tuple[List[str], List[str]]:
    """Validate frontmatter fields."""
    errors = []
    warnings = []

    # Required fields
    required_fields = ['layout', 'title', 'date', 'categories', 'tags']
    for field in required_fields:
        if not hasattr(post, field) or getattr(post, field) is None:
            errors.append(f"Missing required frontmatter field: {field}")
        elif field == 'title' and not getattr(post, field).strip():
            errors.append("Title cannot be empty")

    # Validate layout
    if hasattr(post, 'metadata') and post.metadata.get('layout') != 'post':
        errors.append("Layout must be 'post'")

    # Validate categories and tags are lists
    if hasattr(post, 'categories') and not isinstance(post.categories, list):
        errors.append("Categories must be a list")
    if hasattr(post, 'tags') and not isinstance(post.tags, list):
        errors.append("Tags must be a list")

    # Validate slug
    if hasattr(post, 'slug') and post.slug:
        expected_slug = slugify(post.title.lower())
        if post.slug != expected_slug and not post.slug.startswith(expected_slug):
            warnings.append(f"Slug '{post.slug}' doesn't match expected '{expected_slug}'")

    return errors, warnings


def _validate_content_structure(content: str, title: str) -> Tuple[List[str], List[str], List[str]]:
    """Validate content structure and readability."""
    errors = []
    warnings = []
    suggestions = []

    # Check word count
    word_count = len(content.split())
    if word_count < config.min_word_count:
        errors.append(f"Content too short: {word_count} words (minimum: {config.min_word_count})")
    elif word_count > config.max_word_count:
        warnings.append(f"Content very long: {word_count} words (target: {config.max_word_count})")

    # Check headings
    headings = extract_headings(content)
    h1_count = sum(1 for level, _ in headings if level == 1)
    h2_count = sum(1 for level, _ in headings if level == 2)
    h3_count = sum(1 for level, _ in headings if level == 3)

    if h1_count != 1:
        errors.append(f"Must have exactly one H1 heading, found {h1_count}")
    if h2_count < 1:
        warnings.append("Consider adding H2 sections for better structure")
    if h2_count > config.max_headings:
        warnings.append(f"Many H2 sections ({h2_count}), consider consolidating")

    # Check for heading hierarchy issues
    heading_levels = [level for level, _ in headings]
    prev_level = 0
    for level in heading_levels:
        if level - prev_level > 1 and prev_level > 0:
            warnings.append(f"Skipped heading level: H{prev_level} followed by H{level}")
        prev_level = level

    # Check for long paragraphs (> 300 words)
    paragraphs = re.split(r'\n\s*\n', content)
    long_paragraphs = [p for p in paragraphs if len(p.split()) > 300]
    if long_paragraphs:
        suggestions.append(f"Consider breaking up {len(long_paragraphs)} long paragraphs")

    # Check for code blocks and lists
    if '```' in content:
        suggestions.append("Ensure code blocks have proper syntax highlighting")
    if re.search(r'^[\s]*[-\*\+]\s+', content, re.MULTILINE):
        # Has lists, check if they're properly formatted
        pass

    # Check for internal links
    internal_links = re.findall(r'\[([^\]]+)\]\((?!http)([^\)]+)\)', content)
    if not internal_links:
        suggestions.append("Consider adding internal links to other blog posts")

    return errors, warnings, suggestions


def _validate_seo_elements(post: BlogPost, full_content: str) -> Tuple[List[str], List[str], List[str]]:
    """Validate SEO elements and optimization."""
    errors = []
    warnings = []
    suggestions = []

    # Check title length (30-60 characters)
    title_length = len(post.title) if post.title else 0
    if title_length < 30:
        warnings.append(f"Title too short: {title_length} characters (aim for 30-60)")
    elif title_length > 60:
        warnings.append(f"Title too long: {title_length} characters (aim for 30-60)")

    # Check excerpt (meta description)
    excerpt = getattr(post, 'excerpt', '') or ''
    excerpt_length = len(excerpt)
    if not excerpt:
        if config.require_meta_description:
            errors.append("Missing excerpt/meta description (required for SEO)")
    elif excerpt_length < 120:
        warnings.append(f"Meta description too short: {excerpt_length} characters (aim for 150-160)")
    elif excerpt_length > 160:
        warnings.append(f"Meta description too long: {excerpt_length} characters (aim for 150-160)")
    else:
        # Check if excerpt contains primary keyword
        if post.title and len(post.title.split()) > 2:
            primary_keyword = post.title.split()[0].lower()
            if primary_keyword not in excerpt.lower():
                suggestions.append(f"Consider including primary keyword '{primary_keyword}' in meta description")

    # Check keyword density (target: ~2%)
    if post.title:
        content_words = re.findall(r'\b\w+\b', full_content.lower())
        title_keywords = post.title.lower().split()[:3]  # First 3 words of title

        keyword_density = {}
        for keyword in title_keywords:
            count = content_words.count(keyword)
            if len(content_words) > 0:
                density = (count / len(content_words)) * 100
                keyword_density[keyword] = density

                if density < config.target_keyword_density * 70:  # 70% of target
                    suggestions.append(f"'{keyword}' keyword density low: {density:.2f}%")
                elif density > config.target_keyword_density * 300:  # 300% of target
                    warnings.append(f"'{keyword}' keyword stuffing detected: {density:.2f}%")

    # Check for image alt text
    if '![' in full_content:
        alt_texts = re.findall(r'!\[([^\]]*)\]\([^)]+\)', full_content)
        empty_alts = [alt for alt in alt_texts if not alt.strip()]
        if empty_alts:
            warnings.append(f"Found {len(empty_alts)} images without alt text")

    # Check URL structure in slug
    if hasattr(post, 'slug') and post.slug:
        if not re.match(r'^[a-z0-9-]+$', post.slug):
            errors.append("Slug contains invalid characters (only lowercase letters, numbers, and hyphens allowed)")

    # Check for broken internal links
    internal_links = re.findall(r'\[([^\]]+)\]\((?!http)([^\)]+)\)', full_content)
    for link_text, link_url in internal_links:
        if not link_url.endswith('.md'):
            warnings.append(f"Internal link '{link_url}' should point to .md file")

    return errors, warnings, suggestions


def validate_generation_spec(spec: Dict[str, Any]) -> ValidationResult:
    """Validate generation specification."""
    errors = []
    warnings = []
    suggestions = []

    # Required fields
    if not spec.get('topic'):
        errors.append("Topic is required")
    elif len(spec['topic']) < 10:
        warnings.append("Topic is very short, consider being more specific")

    # Validate categories
    categories = spec.get('categories', [])
    if not categories:
        warnings.append("Consider adding categories for better organization")

    # Validate keywords
    keywords = spec.get('keywords', [])
    if not keywords and spec.get('topic'):
        suggestions.append("Consider adding 2-3 primary keywords for better SEO")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions
    )


def validate_generated_content(content: GeneratedContent) -> ValidationResult:
    """Validate generated content before output."""
    errors = []
    warnings = []
    suggestions = []

    # Basic validation
    if not content.content.strip():
        errors.append("Generated content is empty")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions)

    # Validate word count
    if content.word_count < config.min_word_count:
        errors.append(f"Content too short: {content.word_count} words (minimum: {config.min_word_count})")

    # Validate frontmatter
    required_fm = ['layout', 'title', 'date', 'categories', 'tags']
    for field in required_fm:
        if field not in content.frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Validate headings
    if len(content.headings) < config.min_headings:
        warnings.append(f"Few headings found: {len(content.headings)} (recommended: {config.min_headings})")

    # Check for broken markdown
    if '**' in content.content:
        open_bold = content.content.count('**') % 2
        if open_bold:
            warnings.append("Unclosed bold formatting detected")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions
    )
