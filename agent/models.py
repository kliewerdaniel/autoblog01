"""
Data models using Pydantic for the blog post generation system.

Includes models for blog posts, documents, generation specs, and API responses.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class BlogPost(BaseModel):
    """Represents a parsed blog post with frontmatter and content."""

    file_path: Path
    title: str
    date: datetime
    categories: List[str]
    tags: List[str]
    excerpt: Optional[str] = None
    slug: Optional[str] = None
    content: str
    word_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class DocumentChunk(BaseModel):
    """A chunk of content from a blog post for vector storage."""

    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_index: int = 0
    source_file: Path
    embedding: Optional[List[float]] = None


class Document(BaseModel):
    """Represents a document with metadata for retrieval."""

    page_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class GenerationSpec(BaseModel):
    """Specification for blog post generation."""

    topic: str
    style: str = "technical"  # technical, casual, professional
    length: str = "medium"    # short, medium, long
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    tone: str = "informative"  # informative, persuasive, educational
    target_audience: Optional[str] = None
    special_requirements: Optional[str] = None
    min_words: int = Field(default=1000)
    max_words: int = Field(default=1500)


class ResearchBrief(BaseModel):
    """Research findings and context gathered from knowledge base."""

    key_themes: List[str] = Field(default_factory=list)
    relevant_facts: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    gaps_identified: List[str] = Field(default_factory=list)
    recommended_focus: List[str] = Field(default_factory=list)
    context_documents: List[Document] = Field(default_factory=list)


class ContentOutline(BaseModel):
    """Structured outline for the blog post."""

    title: str
    headline: str
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    seo_recommendations: Dict[str, Any] = Field(default_factory=dict)
    word_count_targets: Dict[str, int] = Field(default_factory=dict)


class GeneratedContent(BaseModel):
    """Final generated blog post content."""

    title: str
    content: str
    frontmatter: Dict[str, Any] = Field(default_factory=dict)
    word_count: int = 0
    headings: List[str] = Field(default_factory=list)
    seo_metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMMesssage(BaseModel):
    """Message format for LLM interactions."""

    role: str  # system, user, assistant
    content: str


class LLMResponse(BaseModel):
    """Response from LLM API."""

    content: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class ValidationResult(BaseModel):
    """Result of content validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
