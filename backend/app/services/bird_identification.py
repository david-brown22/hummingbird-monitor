"""
Bird identification service using AI and embeddings
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import requests
from app.core.config import settings

class BirdIdentificationService:
    """Service for identifying hummingbirds using AI and embeddings"""
    
    def __init__(self):
        self.codeproject_ai_url = settings.codeproject_ai_url
        self.pinecone_api_key = settings.pinecone_api_key
        self.pinecone_index_name = settings.pinecone_index_name
    
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
        """Match bird embedding against known birds using Pinecone/FAISS"""
        try:
            if not embedding:
                return {"bird_id": None, "confidence": 0.0}
            
            # For now, return a placeholder match
            # In production, this would query Pinecone or FAISS
            return {
                "bird_id": None,  # Would be actual bird ID from vector DB
                "confidence": 0.0,  # Would be similarity score
                "match_type": "new_bird"  # Indicates this is a new bird
            }
            
        except Exception as e:
            return {
                "bird_id": None,
                "confidence": 0.0,
                "error": str(e)
            }
