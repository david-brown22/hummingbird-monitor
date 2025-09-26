"""
Bird model for storing individual bird information
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from app.core.database import Base

class Bird(Base):
    """Bird model for individual hummingbird identification"""
    
    __tablename__ = "birds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)  # Optional human-readable name
    embedding_id = Column(String(255), unique=True, index=True)  # Pinecone/FAISS ID
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    total_visits = Column(Integer, default=0)
    
    # Physical characteristics (for AI identification)
    dominant_colors = Column(Text)  # JSON string of dominant colors
    size_estimate = Column(Float)  # Estimated size in cm
    distinctive_features = Column(Text)  # AI-generated description
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
