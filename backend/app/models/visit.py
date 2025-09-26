"""
Visit model for tracking hummingbird visits
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Visit(Base):
    """Visit model for tracking individual hummingbird visits"""
    
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    bird_id = Column(Integer, ForeignKey("birds.id"), nullable=True)  # Null if unidentified
    feeder_id = Column(String(50), nullable=False, index=True)
    camera_id = Column(String(50), nullable=False)
    
    # Visit details
    visit_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    duration_seconds = Column(Float, nullable=True)  # How long bird stayed
    confidence_score = Column(Float, nullable=True)  # AI confidence in identification
    
    # Image/video metadata
    image_path = Column(String(500), nullable=True)  # Path to captured image
    video_path = Column(String(500), nullable=True)  # Path to captured video
    motion_triggered = Column(String(10), default="true")  # Was this motion-triggered?
    
    # Environmental data
    temperature = Column(Float, nullable=True)  # If available from sensors
    weather_condition = Column(String(50), nullable=True)
    
    # AI processing metadata
    detection_metadata = Column(Text)  # JSON string of detection details
    embedding_vector = Column(Text)  # JSON string of embedding vector
    
    # Relationships
    bird = relationship("Bird", back_populates="visits")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
