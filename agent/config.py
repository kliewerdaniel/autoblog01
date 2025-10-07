"""
Configuration management for the Agentic Blog Post Generation System.

Uses Pydantic settings for type-safe configuration with environment variable support.
"""

import sys
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Ensure imports work in both module and direct execution contexts
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))


class AgentConfig(BaseSettings):
    """Comprehensive configuration for the blog post generation system."""

    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    blog_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "content" / "blog")
    vector_db_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / ".agent_data" / "vector_db")
    cache_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / ".agent_data" / "cache")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / ".agent_data" / "logs")

    # Ollama settings
    ollama_model: str = "qwen3-coder"
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 300  # seconds

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Vector DB settings
    collection_name: str = "blog_knowledge_base"
    top_k_retrieval: int = 5
    vector_db_provider: str = "chromadb"  # or "qdrant"

    # Generation settings
    min_word_count: int = 800
    max_word_count: int = 5000  # Increased for longer blog post generation
    temperature: float = 0.7
    max_tokens: int = 8000  # Increased for longer blog post generation

    # Qdrant settings (if using Qdrant)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    # SEO requirements
    min_headings: int = 3
    max_headings: int = 7
    require_meta_description: bool = True
    target_keyword_density: float = 0.02  # 2%

    # Logging
    log_level: str = "INFO"
    log_file: str = "agent.log"

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # CLI settings
    interactive_mode: bool = False
    verbose: bool = False
    dry_run: bool = False

    class Config:
        env_prefix = "AGENT_"
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
config = AgentConfig()
