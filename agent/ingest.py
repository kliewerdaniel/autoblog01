"""
Knowledge base ingestion pipeline.

Handles scanning, parsing, chunking, embedding generation, and vector database storage.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from sentence_transformers import SentenceTransformer

# Import with fallback for direct execution
try:
    from .config import config
    from .models import BlogPost, DocumentChunk
    from .utils.parser import parse_blog_post, chunk_content, clean_markdown
    from .utils.file_utils import (
        scan_blog_posts,
        create_index_manifest,
        read_index_manifest,
        get_new_or_modified_posts
    )
    from .vector_store import vector_store
except ImportError:
    from config import config
    from models import BlogPost, DocumentChunk
    from utils.parser import parse_blog_post, chunk_content, clean_markdown
    from utils.file_utils import (
        scan_blog_posts,
        create_index_manifest,
        read_index_manifest,
        get_new_or_modified_posts
    )
    from vector_store import vector_store

logger = logging.getLogger(__name__)


def ingest_knowledge_base(force: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Ingest blog posts into the vector database knowledge base.

    Args:
        force: Force re-ingestion of all posts
        verbose: Enable verbose logging

    Returns:
        Ingestion statistics and results
    """
    logger.info("Starting knowledge base ingestion...")

    # Initialize embedding model
    try:
        logger.info(f"Loading embedding model: {config.embedding_model}")
        embed_model = SentenceTransformer(config.embedding_model)
    except Exception as e:
        raise Exception(f"Failed to load embedding model: {e}")

    # Scan for blog posts
    logger.info(f"Scanning blog directory: {config.blog_dir}")
    try:
        md_files = scan_blog_posts(config.blog_dir)
        logger.info(f"Found {len(md_files)} markdown files")
    except Exception as e:
        raise Exception(f"Failed to scan blog directory: {e}")

    if not md_files:
        logger.warning("No markdown files found in blog directory")
        return {"error": "No markdown files found"}

    # Parse blog posts
    logger.info("Parsing blog posts...")
    posts = []
    for i, file_path in enumerate(md_files):
        if verbose:
            logger.info(f"Processing: {file_path.name} ({i+1}/{len(md_files)})")

        try:
            post = parse_blog_post(file_path)
            posts.append(post)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            continue

    logger.info(f"Successfully parsed {len(posts)} blog posts")

    # Check manifest for incremental updates
    manifest_path = config.vector_db_dir / "index_manifest.json"
    existing_manifest = read_index_manifest(manifest_path)

    posts_to_process = posts
    if not force and existing_manifest:
        posts_to_process = get_new_or_modified_posts(existing_manifest, posts)
        logger.info(f"Incremental update: processing {len(posts_to_process)} changed/new posts")

    if not posts_to_process:
        logger.info("No posts to process - knowledge base is up to date")
        return {
            "message": "Knowledge base is up to date",
            "total_posts": len(posts),
            "processed": 0
        }

    # Process posts: chunk, embed, and store
    total_chunks = 0
    processed_texts = []
    processed_metadata = []
    processed_ids = []

    for post in posts_to_process:
        if verbose:
            logger.info(f"Chunking and embedding: {post.title}")

        try:
            # Clean content for better embeddings
            clean_content = clean_markdown(post.content)

            # Chunk the content
            chunks = chunk_content(
                clean_content,
                chunk_size=config.chunk_size,
                overlap=config.chunk_overlap
            )

            if not chunks:
                logger.warning(f"No chunks generated for: {post.title}")
                continue

            # Generate embeddings for chunks within this post to ensure matching
            embeddings = embed_model.encode(chunks, show_progress_bar=False)

            # Only process chunks that have corresponding embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Enhanced metadata for retrieval (ChromaDB requires simple types)
                metadata = {
                    "source_file": str(post.file_path),
                    "title": post.title,
                    "date": post.date.isoformat() if post.date else None,
                    "categories": ", ".join(post.categories) if post.categories else "",
                    "tags": ", ".join(post.tags) if post.tags else "",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "word_count": post.word_count,
                    "excerpt": post.excerpt or "",
                    "full_content_hash": hash(post.content) % 10**8,  # Simple content hash
                }

                processed_texts.append(chunk)
                processed_metadata.append(metadata)
                processed_ids.append(f"{post.file_path.stem}_chunk_{i}")

            total_chunks += len(chunks)

        except Exception as e:
            logger.error(f"Failed to process {post.title}: {e}")
            continue

    # Store in vector database using batched inserts
    if processed_texts:
        logger.info(f"Storing {len(processed_texts)} chunks in vector database...")

        try:
            # Use ChromaDB's recommended batch size limit
            batch_size = 5000  # Well under ChromaDB's 5461 limit

            for i in range(0, len(processed_texts), batch_size):
                end_idx = min(i + batch_size, len(processed_texts))
                batch_texts = processed_texts[i:end_idx]
                batch_metadata = processed_metadata[i:end_idx]
                batch_ids = processed_ids[i:end_idx]

                logger.info(f"Processing batch {i//batch_size + 1} of {(len(processed_texts) + batch_size - 1)//batch_size}: chunks {i}-{end_idx-1}")

                # Generate embeddings for this batch
                batch_embeddings = embed_model.encode(batch_texts, show_progress_bar=False)

                # Add batch to vector store
                vector_store.add_documents(
                    texts=batch_texts,
                    embeddings=batch_embeddings,
                    metadata=batch_metadata,
                    ids=batch_ids
                )

            logger.info("Successfully stored all chunks in vector database")
        except Exception as e:
            raise Exception(f"Failed to store documents in vector database: {e}")

    # Update manifest
    try:
        create_index_manifest(posts, manifest_path)
        logger.info("Updated index manifest")
    except Exception as e:
        logger.warning(f"Failed to update index manifest: {e}")

    # Return statistics
    result = {
        "total_posts": len(posts),
        "processed_posts": len(posts_to_process),
        "total_chunks": total_chunks,
        "vector_store_stats": vector_store.get_collection_stats(),
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"Ingestion completed successfully. Stats: {result}")

    return result


def get_knowledge_base_stats() -> Dict[str, Any]:
    """Get statistics about the knowledge base."""
    try:
        vector_stats = vector_store.get_collection_stats()

        manifest_path = config.vector_db_dir / "index_manifest.json"
        manifest = read_index_manifest(manifest_path)

        return {
            "vector_database": vector_stats,
            "manifest": manifest,
            "total_content": manifest.get("total_posts", 0)
        }
    except Exception as e:
        logger.error(f"Failed to get knowledge base stats: {e}")
        return {"error": str(e)}


def reset_knowledge_base() -> None:
    """Reset the entire knowledge base."""
    try:
        vector_store.reset_collection()

        manifest_path = config.vector_db_dir / "index_manifest.json"
        if manifest_path.exists():
            manifest_path.unlink()

        logger.info("Knowledge base reset successfully")
    except Exception as e:
        raise Exception(f"Failed to reset knowledge base: {e}")


def search_knowledge_base(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search the knowledge base for relevant content.

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        List of search results with metadata
    """
    try:
        results = vector_store.similarity_search(query, top_k=top_k)

        # Convert to dictionary format for easier consumption
        search_results = []
        for doc in results:
            result = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": doc.metadata.get("relevance_score", 0),
                "source_file": doc.metadata.get("source_file"),
                "title": doc.metadata.get("title")
            }
            search_results.append(result)

        return search_results

    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        return []
