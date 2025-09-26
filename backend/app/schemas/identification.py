"""
Pydantic schemas for bird identification
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IdentificationResponse(BaseModel):
    """Schema for bird identification response"""
    success: bool
    bird_id: Optional[int] = None
    confidence: float = 0.0
    match_type: str = "unknown"  # "existing_bird", "new_bird", "unknown"
    bird_name: Optional[str] = None
    similarity_score: float = 0.0
    message: str = ""

class BirdEmbeddingResponse(BaseModel):
    """Schema for bird embedding response"""
    bird_id: int
    embedding: List[float]
    dimension: int

class DatabaseStatsResponse(BaseModel):
    """Schema for database statistics response"""
    total_birds: int
    embedding_dimension: int
    index_type: str
    metadata_count: int
    last_updated: str

class SimilarBirdsResponse(BaseModel):
    """Schema for similar birds search response"""
    success: bool
    similar_birds: List[Dict[str, Any]]
    count: int

class BirdIdentificationRequest(BaseModel):
    """Schema for bird identification request"""
    embedding: List[float]
    bird_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BirdUpdateRequest(BaseModel):
    """Schema for updating bird embedding"""
    new_embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None

class SimilaritySearchRequest(BaseModel):
    """Schema for similarity search request"""
    embedding: List[float]
    k: int = 5
    threshold: float = 0.7
