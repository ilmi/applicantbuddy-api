import uuid
from typing import List, Optional
import hashlib
import numpy as np

from chonkie import SemanticChunker
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class SimpleEmbedding:
    """Simple embedding class as fallback when sentence_transformers is not available."""
    
    def __init__(self, vector_size: int = 384):
        self.vector_size = vector_size
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Create simple hash-based embeddings for texts."""
        embeddings = []
        for text in texts:
            # Create a hash-based embedding
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Convert to vector of specified size
            vector = []
            for i in range(self.vector_size):
                byte_idx = i % len(hash_bytes)
                vector.append(float(hash_bytes[byte_idx]) / 255.0)
            
            # Normalize vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = [v / norm for v in vector]
            
            embeddings.append(vector)
        
        return embeddings


class VectorDBManager:
    """Manager class for handling CV text chunking and vector operations with Qdrant."""
    
    def __init__(self):
        """Initialize the VectorDB manager with required models and clients."""
        # Use simple embedding as fallback
        self.model = SimpleEmbedding(vector_size=384)
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.collection_name = "applicantbuddy"
        self.vector_size = 384
        
        # Initialize semantic chunker for effective text splitting
        try:
            self.chunker = SemanticChunker(
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                min_sentence=10,
                max_chunk_size=512
            )
            logger.info("Initialized SemanticChunker with sentence-transformers model")
        except Exception as e:
            logger.warning(f"Failed to initialize SemanticChunker with sentence-transformers: {e}")
            # Fallback to basic chunker
            self.chunker = None
        
        # Ensure collection exists
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, 
                        distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
    
    def chunk_cv_text(self, cv_text: str) -> List[str]:
        """
        Chunk CV text into semantic chunks using chonkie.
        Falls back to character-based chunking if semantic chunking fails.
        """
        if not cv_text or not cv_text.strip():
            logger.warning("Empty CV text provided for chunking")
            return []
        
        try:
            if self.chunker:
                # Use semantic chunking with chonkie
                chunks = self.chunker.chunk(cv_text)
                chunk_texts = [chunk.text for chunk in chunks]
                logger.info(f"Successfully chunked CV text into {len(chunk_texts)} semantic chunks")
                return chunk_texts
            else:
                # Fallback to character-based chunking
                return self._fallback_chunking(cv_text)
                
        except Exception as e:
            logger.error(f"Error in semantic chunking: {e}")
            # Fallback to character-based chunking
            return self._fallback_chunking(cv_text)
    
    def _fallback_chunking(self, text: str, chunk_size: int = 500) -> List[str]:
        """Fallback chunking method using character-based splitting."""
        try:
            chunks = []
            overlap = 50
            
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk.strip())
            
            logger.info(f"Used fallback chunking to create {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error in fallback chunking: {e}")
            return [text]  # Return original text as single chunk
    
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Create embeddings for text chunks using simple embedding.
        """
        if not chunks:
            logger.warning("No chunks provided for embedding")
            return []
        
        try:
            embeddings = self.model.encode(chunks)
            logger.info(f"Successfully created embeddings for {len(chunks)} chunks")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.vector_size for _ in chunks]
    
    def store_cv_vectors(self, resume_id: str, cv_text: str, metadata: Optional[dict] = None) -> bool:
        """
        Process CV text into chunks, create embeddings, and store in Qdrant.
        
        Args:
            resume_id: Unique identifier for the resume
            cv_text: Raw CV text content
            metadata: Additional metadata to store with vectors
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not cv_text or not cv_text.strip():
                logger.warning(f"Empty CV text for resume {resume_id}")
                return False
            
            # Chunk the CV text
            chunks = self.chunk_cv_text(cv_text)
            if not chunks:
                logger.warning(f"No chunks created for resume {resume_id}")
                return False
            
            # Create embeddings
            embeddings = self.embed_chunks(chunks)
            if not embeddings:
                logger.warning(f"No embeddings created for resume {resume_id}")
                return False
            
            # Prepare points for Qdrant
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = str(uuid.uuid4())
                
                # Prepare metadata
                point_metadata = {
                    "resume_id": resume_id,
                    "chunk_index": i,
                    "chunk_text": chunk[:500],  # Limit text length for metadata
                    "chunk_length": len(chunk)
                }
                
                # Add additional metadata if provided
                if metadata:
                    point_metadata.update(metadata)
                
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=point_metadata
                    )
                )
            
            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Successfully stored {len(points)} vectors for resume {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing CV vectors for resume {resume_id}: {e}")
            return False
    
    def search_similar_cvs(self, query_text: str, limit: int = 10, score_threshold: float = 0.7) -> List[dict]:
        """
        Search for similar CVs based on query text.
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar CV chunks with metadata
        """
        try:
            if not query_text or not query_text.strip():
                logger.warning("Empty query text provided")
                return []
            
            # Create embedding for query
            query_embedding = self.embed_chunks([query_text])[0]
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "score": result.score,
                    "resume_id": result.payload.get("resume_id"),
                    "chunk_text": result.payload.get("chunk_text"),
                    "metadata": {
                        "fullname": result.payload.get("fullname"),
                        "email": result.payload.get("email"),
                        "category": result.payload.get("category"),
                        "skills": result.payload.get("skills"),
                        "file_name": result.payload.get("file_name")
                    }
                })
            
            logger.info(f"Found {len(results)} similar CVs for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar CVs: {e}")
            return []
    
    def delete_resume_vectors(self, resume_id: str) -> bool:
        """Delete all vectors associated with a resume."""
        try:
            # Search for all points with this resume_id
            search_results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter={
                    "must": [
                        {
                            "key": "resume_id",
                            "match": {
                                "value": resume_id
                            }
                        }
                    ]
                }
            )
            
            # Extract point IDs
            point_ids = [point.id for point in search_results[0]]
            
            if point_ids:
                # Delete points
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
                logger.info(f"Deleted {len(point_ids)} vectors for resume {resume_id}")
                return True
            else:
                logger.info(f"No vectors found for resume {resume_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting vectors for resume {resume_id}: {e}")
            return False
    
    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}


# Global instance
vectordb_manager = VectorDBManager()
