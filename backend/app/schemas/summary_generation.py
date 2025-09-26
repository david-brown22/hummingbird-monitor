"""
Pydantic schemas for summary generation
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import date, datetime

class DailySummaryResponse(BaseModel):
    """Schema for daily summary response"""
    date: str
    title: str
    content: str
    total_visits: int
    unique_birds: int
    peak_hour: Optional[str] = None
    average_duration: float
    weather_summary: str
    temperature_range: str
    generation_prompt: str
    model_used: str
    confidence_score: float

class WeeklySummaryResponse(BaseModel):
    """Schema for weekly summary response"""
    date: str
    title: str
    content: str
    total_visits: int
    unique_birds: int
    peak_hour: Optional[str] = None
    average_visit_duration: float
    weather_summary: Optional[str] = None
    temperature_range: Optional[str] = None
    new_birds: Optional[int] = None
    unusual_activity: Optional[str] = None
    generation_prompt: str
    model_used: str
    confidence_score: float

class BirdProfileResponse(BaseModel):
    """Schema for bird profile response"""
    bird_id: int
    bird_name: str
    content: str
    total_visits: int
    average_duration: float
    favorite_feeder: Optional[str] = None
    peak_hour: Optional[str] = None
    visit_frequency: float
    behavioral_patterns: List[str]
    generation_prompt: str
    model_used: str
    confidence_score: float

class FeederAnalysisResponse(BaseModel):
    """Schema for feeder analysis response"""
    feeder_id: str
    content: str
    total_visits: int
    unique_birds: int
    average_daily_visits: float
    peak_hour: Optional[str] = None
    nectar_estimate: Dict[str, Any]
    recommendations: List[str]
    generation_prompt: str
    model_used: str
    confidence_score: float

class AlertSummaryResponse(BaseModel):
    """Schema for alert summary response"""
    alert_id: int
    alert_type: str
    feeder_id: str
    content: str
    severity: str
    visit_count: int
    nectar_level: float
    generation_prompt: str
    model_used: str
    confidence_score: float

class SummaryPromptResponse(BaseModel):
    """Schema for summary prompt response"""
    prompts: Dict[str, str]
    description: str

class SummaryModelResponse(BaseModel):
    """Schema for summary model response"""
    models: Dict[str, Dict[str, Any]]
    description: str

class SummaryGenerationRequest(BaseModel):
    """Schema for summary generation request"""
    target_date: Optional[date] = None
    days: Optional[int] = None
    model_type: Optional[str] = "default"
    custom_prompt: Optional[str] = None

class BirdProfileRequest(BaseModel):
    """Schema for bird profile request"""
    bird_id: int
    days: int = 30
    model_type: Optional[str] = "creative"
    include_behavioral_analysis: bool = True

class FeederAnalysisRequest(BaseModel):
    """Schema for feeder analysis request"""
    feeder_id: str
    days: int = 7
    model_type: Optional[str] = "analytical"
    include_recommendations: bool = True

class AlertSummaryRequest(BaseModel):
    """Schema for alert summary request"""
    alert_id: int
    model_type: Optional[str] = "analytical"
    include_action_items: bool = True

class SummaryGenerationConfig(BaseModel):
    """Schema for summary generation configuration"""
    default_model: str = "gpt-3.5-turbo"
    default_temperature: float = 0.7
    default_max_tokens: int = 1500
    creative_temperature: float = 0.8
    analytical_temperature: float = 0.3
    enable_streaming: bool = False
    cache_generated_summaries: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30

class SummaryQualityMetrics(BaseModel):
    """Schema for summary quality metrics"""
    readability_score: float
    completeness_score: float
    accuracy_score: float
    relevance_score: float
    overall_quality: float
    word_count: int
    sentence_count: int
    average_sentence_length: float
    generated_at: datetime

class SummaryGenerationStats(BaseModel):
    """Schema for summary generation statistics"""
    total_summaries_generated: int
    daily_summaries: int
    weekly_summaries: int
    bird_profiles: int
    feeder_analyses: int
    alert_summaries: int
    average_generation_time: float
    success_rate: float
    error_rate: float
    most_used_model: str
    last_generated: Optional[datetime] = None
