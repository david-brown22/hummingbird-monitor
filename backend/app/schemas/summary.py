"""
Pydantic schemas for Summary model
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class SummaryBase(BaseModel):
    """Base summary schema"""
    date: date
    title: str
    content: str
    total_visits: int = 0
    unique_birds: int = 0
    peak_hour: Optional[str] = None
    average_visit_duration: Optional[float] = None
    weather_summary: Optional[str] = None
    temperature_range: Optional[str] = None
    new_birds: Optional[str] = None
    unusual_activity: Optional[str] = None
    generation_prompt: Optional[str] = None
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None

class SummaryCreate(SummaryBase):
    """Schema for creating a summary"""
    pass

class SummaryUpdate(BaseModel):
    """Schema for updating a summary"""
    title: Optional[str] = None
    content: Optional[str] = None
    weather_summary: Optional[str] = None
    unusual_activity: Optional[str] = None

class SummaryResponse(SummaryBase):
    """Schema for summary response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
