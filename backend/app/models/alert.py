"""
Alert model for feeder refill notifications
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Alert(Base):
    """Alert model for feeder refill notifications"""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    feeder_id = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # "refill_needed", "low_activity", etc.
    
    # Alert details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Alert status
    is_active = Column(Boolean, default=True, index=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    
    # Trigger data
    trigger_data = Column(Text)  # JSON string of data that triggered the alert
    visit_count = Column(Integer, nullable=True)  # Visit count that triggered alert
    estimated_nectar_level = Column(Float, nullable=True)  # Estimated remaining nectar %
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
