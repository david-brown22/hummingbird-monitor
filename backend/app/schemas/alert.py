"""
Pydantic schemas for Alert model
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    """Base alert schema"""
    feeder_id: str
    alert_type: str
    title: str
    message: str
    severity: str = "medium"
    trigger_data: Optional[str] = None
    visit_count: Optional[int] = None
    estimated_nectar_level: Optional[float] = None

class AlertCreate(AlertBase):
    """Schema for creating an alert"""
    pass

class AlertUpdate(BaseModel):
    """Schema for updating an alert"""
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    is_acknowledged: Optional[bool] = None
    acknowledged_by: Optional[str] = None

class AlertResponse(AlertBase):
    """Schema for alert response"""
    id: int
    is_active: bool
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
