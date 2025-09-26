"""
Pydantic schemas for Visit model
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VisitBase(BaseModel):
    """Base visit schema"""
    feeder_id: str
    camera_id: str
    visit_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    confidence_score: Optional[float] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    motion_triggered: str = "true"
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    detection_metadata: Optional[str] = None
    embedding_vector: Optional[str] = None

class VisitCreate(VisitBase):
    """Schema for creating a visit"""
    bird_id: Optional[int] = None

class VisitUpdate(BaseModel):
    """Schema for updating a visit"""
    bird_id: Optional[int] = None
    duration_seconds: Optional[float] = None
    confidence_score: Optional[float] = None
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None

class VisitResponse(VisitBase):
    """Schema for visit response"""
    id: int
    bird_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
