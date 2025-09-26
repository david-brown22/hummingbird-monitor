"""
Pydantic schemas for visit tracking
"""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import date, datetime

class VisitRecordResponse(BaseModel):
    """Schema for visit record response"""
    success: bool
    visit_id: Optional[int] = None
    bird_id: Optional[int] = None
    feeder_id: str
    visit_time: str
    alert_triggered: bool = False
    statistics: Dict[str, Any] = {}
    message: str = ""

class VisitCountsResponse(BaseModel):
    """Schema for visit counts response"""
    total_visits: int
    identified_visits: int
    unidentified_visits: int
    unique_birds: int
    average_duration: float
    peak_hour: Optional[int] = None
    date_range: Dict[str, Optional[str]]
    filters: Dict[str, Optional[str]]

class DailySummaryResponse(BaseModel):
    """Schema for daily summary response"""
    date: str
    total_visits: int
    identified_visits: int
    unidentified_visits: int
    unique_birds: int
    peak_hour: Optional[str] = None
    average_duration: float
    weather_summary: str
    temperature_range: str
    hourly_distribution: Dict[int, int]
    feeder_breakdown: Dict[str, int]
    generated_at: str

class BirdHistoryResponse(BaseModel):
    """Schema for bird visit history response"""
    bird_id: int
    date_range: Dict[str, str]
    total_visits: int
    average_duration: float
    daily_visits: Dict[str, int]
    feeder_preferences: Dict[str, int]
    hourly_distribution: Dict[int, int]
    peak_hour: Optional[str] = None
    recent_visits: List[Dict[str, Any]]

class FeederStatsResponse(BaseModel):
    """Schema for feeder statistics response"""
    feeder_id: str
    date_range: Dict[str, str]
    total_visits: int
    unique_birds: int
    average_daily_visits: float
    peak_hour: Optional[str] = None
    average_duration: float
    daily_visits: Dict[str, int]
    bird_visits: Dict[int, int]
    hourly_distribution: Dict[int, int]
    nectar_estimate: Dict[str, Any]

class VisitTrendsResponse(BaseModel):
    """Schema for visit trends response"""
    date_range: Dict[str, str]
    trends: List[Dict[str, Any]]
    feeder_id: Optional[str] = None

class VisitAnalyticsResponse(BaseModel):
    """Schema for visit analytics response"""
    date_range: Dict[str, str]
    overall_stats: Dict[str, Any]
    top_birds: List[Dict[str, Any]]
    feeder_stats: List[Dict[str, Any]]
    hourly_distribution: List[Dict[str, Any]]

class VisitRecordRequest(BaseModel):
    """Schema for visit record request"""
    bird_id: Optional[int] = None
    feeder_id: str
    camera_id: str
    visit_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    confidence_score: Optional[float] = None
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None

class VisitCountsRequest(BaseModel):
    """Schema for visit counts request"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    feeder_id: Optional[str] = None
    bird_id: Optional[int] = None

class BirdHistoryRequest(BaseModel):
    """Schema for bird history request"""
    bird_id: int
    days: int = 30

class FeederStatsRequest(BaseModel):
    """Schema for feeder stats request"""
    feeder_id: str
    days: int = 7
