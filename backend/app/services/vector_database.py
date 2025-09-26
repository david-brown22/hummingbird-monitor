"""
Vector database service for bird embeddings using Pinecone and FAISS
"""

import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import faiss
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorDatabaseService:
    """Service for managing bird embeddings in vector database"""
    
    def __init__(self):
        self.embedding_dim = 128  # Dimension of our embeddings
        self.index_path = Path("data/faiss_index")
        self.metadata_path = Path("data/bird_metadata.pkl")
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self.index = None
        self.bird_metadata = {}
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            index_file = self.index_path / "bird_index.faiss"
            metadata_file = self.metadata_path
            
            if index_file.exists() and metadata_file.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.bird_metadata = pickle.load(f)
                
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.bird_metadata = {}
                logger.info("Created new FAISS index")
                
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.bird_metadata = {}
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            index_file = self.index_path / "bird_index.faiss"
            metadata_file = self.metadata_path
            
            # Save FAISS index
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.bird_metadata, f)
            
            logger.info("Saved FAISS index and metadata")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    async def add_bird_embedding(
        self, 
        embedding: List[float], 
        bird_id: int, 
        bird_name: str = None,
        metadata: Dict = None
    ) -> bool:
        """
        Add a bird embedding to the vector database
        
        Args:
            embedding: Bird embedding vector
            bird_id: Database ID of the bird
            bird_name: Optional name for the bird
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        try:
            if len(embedding) != self.embedding_dim:
                logger.error(f"Embedding dimension mismatch: {len(embedding)} != {self.embedding_dim}")
                return False
            
            # Convert to numpy array
            embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
            
            # Add to FAISS index
            self.index.add(embedding_array)
            
            # Store metadata
            vector_id = self.index.ntotal - 1
            self.bird_metadata[vector_id] = {
                "bird_id": bird_id,
                "bird_name": bird_name,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "vector_id": vector_id
            }
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Added embedding for bird {bird_id} (vector_id: {vector_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding bird embedding: {e}")
            return False
    
    async def search_similar_birds(
        self, 
        query_embedding: List[float], 
        k: int = 5,
        threshold: float = 0.8
    ) -> List[Dict]:
        """
        Search for similar birds using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar birds with scores
        """
        try:
            if len(query_embedding) != self.embedding_dim:
                logger.error(f"Query embedding dimension mismatch: {len(query_embedding)} != {self.embedding_dim}")
                return []
            
            if self.index.ntotal == 0:
                logger.info("No birds in database")
                return []
            
            # Convert to numpy array
            query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
            
            # Search for similar vectors
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                
                # Convert distance to similarity score (0-1)
                similarity = 1.0 / (1.0 + distance)
                
                if similarity >= threshold:
                    metadata = self.bird_metadata.get(idx, {})
                    results.append({
                        "bird_id": metadata.get("bird_id"),
                        "bird_name": metadata.get("bird_name"),
                        "similarity": similarity,
                        "distance": distance,
                        "vector_id": idx,
                        "metadata": metadata.get("metadata", {})
                    })
            
            # Sort by similarity (highest first)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(f"Found {len(results)} similar birds for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar birds: {e}")
            return []
    
    async def get_bird_embedding(self, bird_id: int) -> Optional[List[float]]:
        """Get embedding for a specific bird"""
        try:
            for vector_id, metadata in self.bird_metadata.items():
                if metadata.get("bird_id") == bird_id:
                    return metadata.get("embedding")
            return None
            
        except Exception as e:
            logger.error(f"Error getting bird embedding: {e}")
            return None
    
    async def update_bird_embedding(
        self, 
        bird_id: int, 
        new_embedding: List[float],
        metadata: Dict = None
    ) -> bool:
        """Update embedding for an existing bird"""
        try:
            # Find the vector ID for this bird
            vector_id = None
            for vid, meta in self.bird_metadata.items():
                if meta.get("bird_id") == bird_id:
                    vector_id = vid
                    break
            
            if vector_id is None:
                logger.warning(f"Bird {bird_id} not found in vector database")
                return False
            
            # Update the embedding in the index
            if len(new_embedding) != self.embedding_dim:
                logger.error(f"Embedding dimension mismatch: {len(new_embedding)} != {self.embedding_dim}")
                return False
            
            embedding_array = np.array(new_embedding, dtype=np.float32).reshape(1, -1)
            self.index.remove_ids(np.array([vector_id]))
            self.index.add(embedding_array)
            
            # Update metadata
            self.bird_metadata[vector_id]["embedding"] = new_embedding
            if metadata:
                self.bird_metadata[vector_id]["metadata"].update(metadata)
            self.bird_metadata[vector_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Updated embedding for bird {bird_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating bird embedding: {e}")
            return False
    
    async def remove_bird_embedding(self, bird_id: int) -> bool:
        """Remove embedding for a specific bird"""
        try:
            # Find the vector ID for this bird
            vector_id = None
            for vid, meta in self.bird_metadata.items():
                if meta.get("bird_id") == bird_id:
                    vector_id = vid
                    break
            
            if vector_id is None:
                logger.warning(f"Bird {bird_id} not found in vector database")
                return False
            
            # Remove from FAISS index
            self.index.remove_ids(np.array([vector_id]))
            
            # Remove from metadata
            del self.bird_metadata[vector_id]
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Removed embedding for bird {bird_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing bird embedding: {e}")
            return False
    
    async def get_database_stats(self) -> Dict:
        """Get statistics about the vector database"""
        try:
            return {
                "total_birds": self.index.ntotal,
                "embedding_dimension": self.embedding_dim,
                "index_type": "FAISS_FlatL2",
                "metadata_count": len(self.bird_metadata),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
    
    async def rebuild_index(self) -> bool:
        """Rebuild the entire index from metadata"""
        try:
            logger.info("Rebuilding FAISS index...")
            
            # Create new index
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            
            # Rebuild from metadata
            embeddings = []
            new_metadata = {}
            vector_id = 0
            
            for old_vector_id, metadata in self.bird_metadata.items():
                embedding = metadata.get("embedding")
                if embedding and len(embedding) == self.embedding_dim:
                    embeddings.append(embedding)
                    new_metadata[vector_id] = metadata.copy()
                    new_metadata[vector_id]["vector_id"] = vector_id
                    vector_id += 1
            
            if embeddings:
                # Add all embeddings at once
                embedding_array = np.array(embeddings, dtype=np.float32)
                self.index.add(embedding_array)
                
                # Update metadata
                self.bird_metadata = new_metadata
                
                # Save to disk
                self._save_index()
                
                logger.info(f"Rebuilt index with {len(embeddings)} embeddings")
                return True
            else:
                logger.warning("No valid embeddings found for rebuild")
                return False
                
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False
