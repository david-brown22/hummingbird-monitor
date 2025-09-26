"""
Pydantic schemas for Bird model
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BirdBase(BaseModel):
    """Base bird schema"""
    name: Optional[str] = None
    embedding_id: str
    dominant_colors: Optional[str] = None
    size_estimate: Optional[float] = None
    distinctive_features: Optional[str] = None

class BirdCreate(BirdBase):
    """Schema for creating a bird"""
    pass

class BirdUpdate(BaseModel):
    """Schema for updating a bird"""
    name: Optional[str] = None
    dominant_colors: Optional[str] = None
    size_estimate: Optional[float] = None
    distinctive_features: Optional[str] = None

class BirdResponse(BirdBase):
    """Schema for bird response"""
    id: int
    first_seen: datetime
    last_seen: datetime
    total_visits: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
