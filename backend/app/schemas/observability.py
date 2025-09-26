"""
Pydantic schemas for observability
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SystemMetricsResponse(BaseModel):
    """Schema for system metrics response"""
    metrics: Dict[str, Any]
    performance: Dict[str, Any]
    logs: List[Dict[str, Any]]
    health_score: float
    generated_at: str

class HealthStatusResponse(BaseModel):
    """Schema for health status response"""
    overall_status: str
    health_checks: Dict[str, Any]
    timestamp: str

class PerformanceAnalysisResponse(BaseModel):
    """Schema for performance analysis response"""
    performance_analysis: Dict[str, Any]
    generated_at: str

class LogsResponse(BaseModel):
    """Schema for logs response"""
    logs: List[Dict[str, Any]]
    total_count: int
    filters: Dict[str, Any]
    generated_at: str

class ObservabilityConfigResponse(BaseModel):
    """Schema for observability configuration response"""
    config: Dict[str, Any]
    generated_at: str

class LogEventRequest(BaseModel):
    """Schema for log event request"""
    event_type: str
    message: str
    level: str = "INFO"
    service: str = "system"
    metadata: Optional[Dict[str, Any]] = None

class LogEventResponse(BaseModel):
    """Schema for log event response"""
    success: bool
    message: str
    event_type: str
    level: str
    service: str

class MetricRequest(BaseModel):
    """Schema for metric request"""
    metric_name: str
    value: float
    metric_type: str = "counter"
    tags: Optional[Dict[str, Any]] = None

class MetricResponse(BaseModel):
    """Schema for metric response"""
    success: bool
    message: str
    metric_name: str
    value: float
    metric_type: str

class PerformanceRequest(BaseModel):
    """Schema for performance request"""
    operation: str
    duration: float
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None

class PerformanceResponse(BaseModel):
    """Schema for performance response"""
    success: bool
    message: str
    operation: str
    duration: float
    success: bool

class DashboardResponse(BaseModel):
    """Schema for dashboard response"""
    dashboard: Dict[str, Any]
    generated_at: str

class AlertStatusResponse(BaseModel):
    """Schema for alert status response"""
    alert_summary: Dict[str, Any]
    recent_alerts: List[Dict[str, Any]]
    generated_at: str

class SystemInfoResponse(BaseModel):
    """Schema for system info response"""
    system_info: Dict[str, Any]
    application_info: Dict[str, Any]
    generated_at: str

class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: str
    service: str

class ObservabilityDashboardData(BaseModel):
    """Schema for observability dashboard data"""
    system_metrics: Dict[str, Any]
    health_status: Dict[str, Any]
    performance_data: Dict[str, Any]
    recent_logs: List[Dict[str, Any]]
    alert_status: Dict[str, Any]
    system_info: Dict[str, Any]
    generated_at: str

class LogFilterRequest(BaseModel):
    """Schema for log filter request"""
    level: Optional[str] = None
    service: Optional[str] = None
    limit: int = 100
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class MetricFilterRequest(BaseModel):
    """Schema for metric filter request"""
    metric_name: Optional[str] = None
    metric_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 1000

class PerformanceFilterRequest(BaseModel):
    """Schema for performance filter request"""
    operation: Optional[str] = None
    success: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 500

class ObservabilityStatsResponse(BaseModel):
    """Schema for observability stats response"""
    total_logs: int
    total_metrics: int
    total_performance_records: int
    system_uptime: float
    health_score: float
    error_rate: float
    average_response_time: float
    generated_at: str

class ObservabilityHealthResponse(BaseModel):
    """Schema for observability health response"""
    service_status: str
    database_status: str
    logging_status: str
    metrics_status: str
    performance_status: str
    overall_health: str
    health_score: float
    timestamp: str

class ObservabilityConfigUpdateRequest(BaseModel):
    """Schema for observability config update request"""
    logging_level: Optional[str] = None
    metrics_retention: Optional[int] = None
    health_check_interval: Optional[int] = None
    performance_tracking: Optional[bool] = None
    alert_thresholds: Optional[Dict[str, float]] = None

class ObservabilityConfigUpdateResponse(BaseModel):
    """Schema for observability config update response"""
    success: bool
    message: str
    updated_config: Dict[str, Any]
    timestamp: str
