"""
Bird identification service using AI and embeddings
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.bird import Bird
from app.models.visit import Visit

logger = logging.getLogger(__name__)

class BirdIdentificationService:
    """Service for identifying hummingbirds using AI and embeddings"""
    
    def __init__(self):
        self.codeproject_ai_url = settings.codeproject_ai_url
        self.pinecone_api_key = settings.pinecone_api_key
        self.pinecone_index_name = settings.pinecone_index_name
        
        # Initialize vector database
        from app.services.vector_database import VectorDatabaseService
        self.vector_db = VectorDatabaseService()
    
    async def identify_bird(self, image_path: str) -> Dict:
        """
        Identify a bird from an image using CodeProject.AI and embeddings
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing identification results
        """
        try:
            # Step 1: Object detection with CodeProject.AI
            detection_result = await self._detect_objects(image_path)
            
            if not detection_result.get("objects"):
                return {
                    "bird_id": None,
                    "confidence": 0.0,
                    "metadata": {"error": "No birds detected in image"},
                    "embedding": []
                }
            
            # Step 2: Extract bird region and generate embedding
            bird_embedding = await self._generate_bird_embedding(image_path, detection_result)
            
            if not bird_embedding:
                return {
                    "bird_id": None,
                    "confidence": 0.0,
                    "metadata": detection_result,
                    "embedding": []
                }
            
            # Step 3: Match against known birds using Pinecone/FAISS
            match_result = await self._match_bird_embedding(bird_embedding)
            
            return {
                "bird_id": match_result.get("bird_id"),
                "confidence": match_result.get("confidence", 0.0),
                "metadata": {
                    "detection": detection_result,
                    "match": match_result
                },
                "embedding": bird_embedding
            }
            
        except Exception as e:
            return {
                "bird_id": None,
                "confidence": 0.0,
                "metadata": {"error": str(e)},
                "embedding": []
            }
    
    async def _detect_objects(self, image_path: str) -> Dict:
        """Detect objects in image using CodeProject.AI"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.codeproject_ai_url}/v1/vision/detection",
                    files=files,
                    timeout=30
                )
                
            if response.status_code == 200:
                result = response.json()
                return {
                    "objects": result.get("predictions", []),
                    "success": True
                }
            else:
                return {
                    "objects": [],
                    "success": False,
                    "error": f"CodeProject.AI error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "objects": [],
                "success": False,
                "error": str(e)
            }
    
    async def _generate_bird_embedding(self, image_path: str, detection_result: Dict) -> List[float]:
        """Generate embedding for the detected bird"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Extract bird region from detection
            objects = detection_result.get("objects", [])
            bird_objects = [obj for obj in objects if obj.get("label", "").lower() in ["bird", "hummingbird"]]
            
            if not bird_objects:
                return []
            
            # Use the largest bird detection
            largest_bird = max(bird_objects, key=lambda x: x.get("confidence", 0))
            
            # Extract region of interest
            x1, y1, x2, y2 = largest_bird.get("bbox", [0, 0, 0, 0])
            bird_region = image[int(y1):int(y2), int(x1):int(x2)]
            
            # Generate embedding using a simple feature extraction
            # In production, this would use a pre-trained model like ResNet or CLIP
            embedding = self._extract_simple_features(bird_region)
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def _extract_simple_features(self, image: np.ndarray) -> List[float]:
        """Extract simple features from bird image for embedding"""
        try:
            # Resize to standard size
            image = cv2.resize(image, (224, 224))
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract color histogram features
            hist_r = cv2.calcHist([image_rgb], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([image_rgb], [1], None, [32], [0, 256])
            hist_b = cv2.calcHist([image_rgb], [2], None, [32], [0, 256])
            
            # Extract texture features using LBP
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lbp = self._local_binary_pattern(gray)
            hist_lbp = cv2.calcHist([lbp], [0], None, [32], [0, 256])
            
            # Combine features
            features = np.concatenate([
                hist_r.flatten(),
                hist_g.flatten(),
                hist_b.flatten(),
                hist_lbp.flatten()
            ])
            
            # Normalize
            features = features / (np.linalg.norm(features) + 1e-8)
            
            return features.tolist()
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return []
    
    def _local_binary_pattern(self, image: np.ndarray, radius: int = 1, n_points: int = 8) -> np.ndarray:
        """Compute Local Binary Pattern"""
        # Simple LBP implementation
        rows, cols = image.shape
        lbp = np.zeros_like(image)
        
        for i in range(radius, rows - radius):
            for j in range(radius, cols - radius):
                center = image[i, j]
                binary_string = ""
                for k in range(n_points):
                    angle = 2 * np.pi * k / n_points
                    x = int(i + radius * np.cos(angle))
                    y = int(j + radius * np.sin(angle))
                    if x < rows and y < cols:
                        binary_string += "1" if image[x, y] >= center else "0"
                    else:
                        binary_string += "0"
                
                lbp[i, j] = int(binary_string, 2)
        
        return lbp
    
    async def _match_bird_embedding(self, embedding: List[float]) -> Dict:
        """Match bird embedding against known birds using vector database"""
        try:
            if not embedding:
                return {"bird_id": None, "confidence": 0.0}
            
            # Search for similar birds in vector database
            similar_birds = await self.vector_db.search_similar_birds(
                query_embedding=embedding,
                k=5,
                threshold=0.7  # 70% similarity threshold
            )
            
            if similar_birds:
                # Return the most similar bird
                best_match = similar_birds[0]
                return {
                    "bird_id": best_match["bird_id"],
                    "confidence": best_match["similarity"],
                    "match_type": "existing_bird",
                    "bird_name": best_match.get("bird_name"),
                    "similarity_score": best_match["similarity"]
                }
            else:
                # No similar birds found - this is a new bird
                return {
                    "bird_id": None,
                    "confidence": 0.0,
                    "match_type": "new_bird"
                }
            
        except Exception as e:
            logger.error(f"Error matching bird embedding: {e}")
            return {
                "bird_id": None,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def add_bird_to_database(
        self, 
        embedding: List[float], 
        bird_id: int, 
        bird_name: str = None,
        metadata: Dict = None,
        db: Session = None
    ) -> bool:
        """
        Add a new bird to the vector database
        
        Args:
            embedding: Bird embedding vector
            bird_id: Database ID of the bird
            bird_name: Optional name for the bird
            metadata: Additional metadata
            db: Database session
            
        Returns:
            bool: Success status
        """
        try:
            # Add to vector database
            success = await self.vector_db.add_bird_embedding(
                embedding=embedding,
                bird_id=bird_id,
                bird_name=bird_name,
                metadata=metadata
            )
            
            if success and db:
                # Update bird record in database
                bird = db.query(Bird).filter(Bird.id == bird_id).first()
                if bird:
                    bird.embedding_id = f"vector_{bird_id}"
                    db.commit()
                    logger.info(f"Added bird {bird_id} to vector database")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding bird to database: {e}")
            return False
    
    async def update_bird_embedding(
        self, 
        bird_id: int, 
        new_embedding: List[float],
        metadata: Dict = None
    ) -> bool:
        """Update embedding for an existing bird"""
        try:
            success = await self.vector_db.update_bird_embedding(
                bird_id=bird_id,
                new_embedding=new_embedding,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Updated embedding for bird {bird_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating bird embedding: {e}")
            return False
    
    async def remove_bird_from_database(self, bird_id: int) -> bool:
        """Remove a bird from the vector database"""
        try:
            success = await self.vector_db.remove_bird_embedding(bird_id)
            
            if success:
                logger.info(f"Removed bird {bird_id} from vector database")
            
            return success
            
        except Exception as e:
            logger.error(f"Error removing bird from database: {e}")
            return False
    
    async def get_bird_embedding(self, bird_id: int) -> Optional[List[float]]:
        """Get embedding for a specific bird"""
        try:
            return await self.vector_db.get_bird_embedding(bird_id)
        except Exception as e:
            logger.error(f"Error getting bird embedding: {e}")
            return None
    
    async def get_database_statistics(self) -> Dict:
        """Get statistics about the bird identification database"""
        try:
            stats = await self.vector_db.get_database_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return {"error": str(e)}
    
    async def rebuild_identification_database(self) -> bool:
        """Rebuild the entire identification database"""
        try:
            success = await self.vector_db.rebuild_index()
            if success:
                logger.info("Successfully rebuilt identification database")
            return success
        except Exception as e:
            logger.error(f"Error rebuilding database: {e}")
            return False
