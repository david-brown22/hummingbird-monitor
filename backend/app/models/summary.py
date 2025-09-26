"""
Summary model for daily activity summaries
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from app.core.database import Base

class Summary(Base):
    """Summary model for daily activity summaries"""
    
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)  # Date of summary
    
    # Summary content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Generated summary text
    
    # Statistics
    total_visits = Column(Integer, default=0)
    unique_birds = Column(Integer, default=0)
    peak_hour = Column(String(10), nullable=True)  # Hour with most activity
    average_visit_duration = Column(Float, nullable=True)  # Average duration in seconds
    
    # Weather and environmental
    weather_summary = Column(String(200), nullable=True)
    temperature_range = Column(String(50), nullable=True)  # e.g., "65-75°F"
    
    # Notable events
    new_birds = Column(Text, nullable=True)  # JSON string of new bird IDs
    unusual_activity = Column(Text, nullable=True)  # Description of unusual patterns
    
    # AI generation metadata
    generation_prompt = Column(Text, nullable=True)  # Prompt used for generation
    model_used = Column(String(100), nullable=True)  # AI model used
    confidence_score = Column(Float, nullable=True)  # Confidence in summary accuracy
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
