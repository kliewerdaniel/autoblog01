"""
Vector store operations for semantic search using ChromaDB.

Supports document storage, retrieval, and similarity search.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from .config import config
    from .models import Document
except ImportError:
    from config import config
    from models import Document

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    """Base exception for vector store operations."""
    pass


class VectorStore:
    """Abstracts vector database operations supporting ChromaDB and Qdrant."""

    def __init__(self, collection_name: str = None, persist_directory: str = None):
        if not CHROMA_AVAILABLE:
            raise VectorStoreError("ChromaDB not available. Install with: pip install chromadb")

        self.collection_name = collection_name or config.collection_name
        self.persist_directory = persist_directory or str(config.vector_db_dir)

        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except (ValueError, Exception):
            try:
                self.collection = self.client.create_collection(name=self.collection_name)
            except Exception as e:
                logger.warning(f"Could not create collection {self.collection_name}: {e}")
                # Create a dummy collection to prevent crashes
                self.collection = None

    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents with embeddings to the vector store.

        Args:
            texts: List of document texts
            embeddings: Numpy array of embeddings (n_samples, n_features)
            metadata: List of metadata dictionaries
            ids: Optional list of document IDs
        """
        if ids is None:
            # Generate IDs based on content hash
            import hashlib
            ids = [hashlib.md5(text.encode()).hexdigest() for text in texts]

        if len(texts) != len(embeddings) or len(texts) != len(metadata):
            raise ValueError("texts, embeddings, and metadata must have the same length")

        # Convert embeddings to list if numpy array
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadata,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents: {e}")

    def similarity_search(
        self,
        query: str,
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search on the vector store.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of Document objects with similarity scores
        """
        if top_k is None:
            top_k = config.top_k_retrieval

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filters,
                include=["documents", "metadatas", "distances"]
            )

            documents = []
            for i, (doc_text, metadata) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0]
            )):
                # Calculate relevance score (lower distance = higher relevance)
                distance = results["distances"][0][i] if "distances" in results else 0.0
                relevance_score = 1.0 / (1.0 + distance)  # Convert distance to similarity

                document = Document(
                    page_content=doc_text,
                    metadata={
                        **metadata,
                        "relevance_score": relevance_score,
                        "distance": distance
                    }
                )
                documents.append(document)

            return documents

        except Exception as e:
            raise VectorStoreError(f"Similarity search failed: {e}")

    def hybrid_search(
        self,
        query: str,
        keywords: List[str],
        top_k: int = None
    ) -> List[Document]:
        """
        Perform hybrid search combining semantic and keyword matching.

        Args:
            query: Main search query
            keywords: Additional keywords to boost
            top_k: Number of results to return

        Returns:
            List of documents sorted by hybrid score
        """
        # First perform semantic search
        semantic_results = self.similarity_search(query, top_k=top_k * 2)

        # Boost results that contain keywords
        for doc in semantic_results:
            keyword_matches = sum(1 for keyword in keywords
                                if keyword.lower() in doc.page_content.lower())
            # Add keyword boost to relevance score
            doc.metadata["keyword_boost"] = min(keyword_matches * 0.1, 0.5)
            doc.metadata["hybrid_score"] = (
                doc.metadata["relevance_score"] + doc.metadata["keyword_boost"]
            )

        # Sort by hybrid score and return top_k
        semantic_results.sort(key=lambda x: x.metadata["hybrid_score"], reverse=True)

        return semantic_results[:top_k or config.top_k_retrieval]

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store.

        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from vector store")
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents: {e}")

    def update_document(
        self,
        document_id: str,
        text: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update an existing document in the vector store.

        Args:
            document_id: ID of the document to update
            text: New document text
            embedding: New embedding vector
            metadata: New metadata
        """
        try:
            # Delete old document first
            self.collection.delete(ids=[document_id])

            # Add updated document
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()

            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[document_id]
            )
            logger.info(f"Updated document {document_id}")
        except Exception as e:
            raise VectorStoreError(f"Failed to update document: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "provider": "chromadb"
            }
        except Exception as e:
            raise VectorStoreError(f"Failed to get collection stats: {e}")

    def list_collections(self) -> List[str]:
        """List all available collections."""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            raise VectorStoreError(f"Failed to list collections: {e}")

    def reset_collection(self) -> None:
        """Reset (delete and recreate) the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"Reset collection: {self.collection_name}")
        except Exception as e:
            raise VectorStoreError(f"Failed to reset collection: {e}")


# Global vector store instance
vector_store = VectorStore()
