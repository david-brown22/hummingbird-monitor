"""
Pydantic schemas for feeder alert logic
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class NectarDepletionResponse(BaseModel):
    """Schema for nectar depletion analysis response"""
    feeder_id: str
    total_visits: int
    weighted_visits: float
    estimated_depletion: float
    remaining_nectar: float
    depletion_percentage: float
    depletion_rate: float
    alert_level: str
    days_until_empty: float
    seasonal_factor: float
    recommendations: List[str]
    analysis_date: str

class AlertStatusResponse(BaseModel):
    """Schema for alert status response"""
    alert_created: bool
    alert_id: Optional[int] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    existing_alerts: int
    depletion_status: Dict[str, Any]
    message: str

class AlertHistoryResponse(BaseModel):
    """Schema for alert history response"""
    feeder_id: str
    date_range: Dict[str, str]
    total_alerts: int
    active_alerts: int
    severity_breakdown: Dict[str, int]
    alert_frequency: float
    recent_depletion: Dict[str, Any]
    alerts: List[Dict[str, Any]]

class FeederPredictionResponse(BaseModel):
    """Schema for feeder prediction response"""
    feeder_id: str
    prediction_period: Dict[str, Any]
    current_status: Dict[str, Any]
    predicted_depletion: float
    predicted_remaining: float
    predicted_alerts: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float
    generated_at: str

class SystemAlertOverviewResponse(BaseModel):
    """Schema for system alert overview response"""
    system_health: Dict[str, Any]
    alert_summary: Dict[str, int]
    feeder_count: int
    feeder_statuses: List[Dict[str, Any]]
    active_alerts: List[Dict[str, Any]]
    generated_at: str

class FeederRefillRequest(BaseModel):
    """Schema for feeder refill request"""
    feeder_id: str
    refill_amount: Optional[float] = None
    refill_notes: Optional[str] = None
    refill_timestamp: Optional[datetime] = None

class FeederRefillResponse(BaseModel):
    """Schema for feeder refill response"""
    success: bool
    feeder_id: str
    alerts_resolved: int
    refill_amount: Optional[float] = None
    message: str

class AlertConfigurationRequest(BaseModel):
    """Schema for alert configuration request"""
    feeder_id: Optional[str] = None
    nectar_capacity: Optional[float] = None
    depletion_rate: Optional[float] = None
    alert_thresholds: Optional[Dict[str, float]] = None
    seasonal_adjustments: Optional[Dict[str, float]] = None
    visit_weight_factors: Optional[Dict[str, float]] = None

class AlertConfigurationResponse(BaseModel):
    """Schema for alert configuration response"""
    feeder_id: str
    configuration: Dict[str, Any]
    updated_at: str
    message: str

class FeederMaintenanceRequest(BaseModel):
    """Schema for feeder maintenance request"""
    feeder_id: str
    maintenance_type: str
    maintenance_notes: Optional[str] = None
    maintenance_date: Optional[datetime] = None
    next_maintenance_due: Optional[datetime] = None

class FeederMaintenanceResponse(BaseModel):
    """Schema for feeder maintenance response"""
    success: bool
    feeder_id: str
    maintenance_type: str
    maintenance_id: Optional[int] = None
    message: str

class AlertStatisticsResponse(BaseModel):
    """Schema for alert statistics response"""
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    average_resolution_time: float
    most_common_alert_type: str
    feeder_with_most_alerts: str
    alert_trends: Dict[str, Any]
    generated_at: str

class FeederHealthScoreResponse(BaseModel):
    """Schema for feeder health score response"""
    feeder_id: str
    health_score: float
    health_status: str
    factors: Dict[str, Any]
    recommendations: List[str]
    last_updated: str

class SystemHealthMetricsResponse(BaseModel):
    """Schema for system health metrics response"""
    overall_health: float
    system_status: str
    feeder_health_scores: List[Dict[str, Any]]
    alert_health_score: float
    visit_health_score: float
    maintenance_health_score: float
    recommendations: List[str]
    generated_at: str

class AlertNotificationRequest(BaseModel):
    """Schema for alert notification request"""
    alert_id: int
    notification_type: str
    recipient: str
    message: str
    priority: str = "medium"

class AlertNotificationResponse(BaseModel):
    """Schema for alert notification response"""
    success: bool
    notification_id: Optional[int] = None
    alert_id: int
    notification_type: str
    recipient: str
    sent_at: str
    message: str

class FeederCapacityAnalysisResponse(BaseModel):
    """Schema for feeder capacity analysis response"""
    feeder_id: str
    current_capacity: float
    recommended_capacity: float
    utilization_rate: float
    peak_usage_periods: List[Dict[str, Any]]
    capacity_recommendations: List[str]
    analysis_date: str

class SeasonalAdjustmentResponse(BaseModel):
    """Schema for seasonal adjustment response"""
    current_season: str
    seasonal_factor: float
    adjusted_depletion_rate: float
    seasonal_recommendations: List[str]
    next_season: str
    next_season_factor: float
    generated_at: str
