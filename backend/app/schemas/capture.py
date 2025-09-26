"""
Pydantic schemas for capture ingestion
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class CaptureResponse(BaseModel):
    """Schema for capture processing response"""
    success: bool
    visit_id: Optional[int] = None
    bird_id: Optional[int] = None
    confidence: float = 0.0
    alert_triggered: bool = False
    processing_time: Optional[str] = None
    message: str = ""

class CaptureStatsResponse(BaseModel):
    """Schema for capture statistics response"""
    total_captures: int
    captures_by_feeder: Dict[str, int]
    captures_by_day: Dict[str, int]
    generated_at: str

class MotionData(BaseModel):
    """Schema for motion detection data"""
    trigger_type: str = "motion"
    timestamp: str
    camera_name: str
    duration_seconds: Optional[float] = None
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    confidence: Optional[float] = None

class BlueIrisWebhook(BaseModel):
    """Schema for Blue Iris webhook payload"""
    camera: str
    trigger: str = "motion"
    timestamp: str
    image_path: str
    motion_data: Optional[MotionData] = None
    additional_data: Optional[Dict[str, Any]] = None
