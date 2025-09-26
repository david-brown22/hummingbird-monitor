"""
Observability API endpoints for logging, metrics, and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.observability import ObservabilityService
from app.schemas.observability import (
    SystemMetricsResponse,
    HealthStatusResponse,
    PerformanceAnalysisResponse,
    LogsResponse,
    ObservabilityConfigResponse
)

router = APIRouter()

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive system metrics
    
    Args:
        db: Database session
        
    Returns:
        SystemMetricsResponse with system metrics
    """
    try:
        observability_service = ObservabilityService()
        
        result = await observability_service.get_system_metrics(db=db)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system metrics: {str(e)}")

@router.get("/health", response_model=HealthStatusResponse)
async def get_health_status(
    db: Session = Depends(get_db)
):
    """
    Get system health status
    
    Args:
        db: Database session
        
    Returns:
        HealthStatusResponse with health status
    """
    try:
        observability_service = ObservabilityService()
        
        result = await observability_service.get_health_status(db=db)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting health status: {str(e)}")

@router.get("/performance", response_model=PerformanceAnalysisResponse)
async def get_performance_analysis():
    """
    Get performance analysis data
    
    Returns:
        PerformanceAnalysisResponse with performance analysis
    """
    try:
        observability_service = ObservabilityService()
        
        result = await observability_service.get_performance_analysis()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance analysis: {str(e)}")

@router.get("/logs", response_model=LogsResponse)
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    service: Optional[str] = Query(None, description="Filter by service"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter")
):
    """
    Get filtered logs
    
    Args:
        level: Filter by log level
        service: Filter by service
        limit: Maximum number of logs to return
        start_time: Start time filter
        end_time: End time filter
        
    Returns:
        LogsResponse with filtered logs
    """
    try:
        observability_service = ObservabilityService()
        
        result = await observability_service.get_logs(
            level=level,
            service=service,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")

@router.post("/log")
async def log_event(
    event_type: str,
    message: str,
    level: str = "INFO",
    service: str = "system",
    metadata: Optional[dict] = None
):
    """
    Log an event with structured data
    
    Args:
        event_type: Type of event
        message: Log message
        level: Log level
        service: Service name
        metadata: Additional metadata
        
    Returns:
        Dict containing log confirmation
    """
    try:
        observability_service = ObservabilityService()
        
        await observability_service.log_event(
            event_type=event_type,
            message=message,
            level=level,
            metadata=metadata,
            service=service
        )
        
        return {
            "success": True,
            "message": "Event logged successfully",
            "event_type": event_type,
            "level": level,
            "service": service
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging event: {str(e)}")

@router.post("/metric")
async def record_metric(
    metric_name: str,
    value: float,
    metric_type: str = "counter",
    tags: Optional[dict] = None
):
    """
    Record a metric value
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        metric_type: Type of metric
        tags: Additional tags
        
    Returns:
        Dict containing metric confirmation
    """
    try:
        observability_service = ObservabilityService()
        
        await observability_service.record_metric(
            metric_name=metric_name,
            value=value,
            metric_type=metric_type,
            tags=tags
        )
        
        return {
            "success": True,
            "message": "Metric recorded successfully",
            "metric_name": metric_name,
            "value": value,
            "metric_type": metric_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording metric: {str(e)}")

@router.post("/performance")
async def record_performance(
    operation: str,
    duration: float,
    success: bool = True,
    metadata: Optional[dict] = None
):
    """
    Record performance data for an operation
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        success: Whether operation was successful
        metadata: Additional metadata
        
    Returns:
        Dict containing performance confirmation
    """
    try:
        observability_service = ObservabilityService()
        
        await observability_service.record_performance(
            operation=operation,
            duration=duration,
            success=success,
            metadata=metadata
        )
        
        return {
            "success": True,
            "message": "Performance data recorded successfully",
            "operation": operation,
            "duration": duration,
            "success": success
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording performance: {str(e)}")

@router.get("/dashboard")
async def get_observability_dashboard(
    db: Session = Depends(get_db)
):
    """
    Get observability dashboard data
    
    Args:
        db: Database session
        
    Returns:
        Dict containing dashboard data
    """
    try:
        observability_service = ObservabilityService()
        
        # Get all observability data
        metrics = await observability_service.get_system_metrics(db=db)
        health = await observability_service.get_health_status(db=db)
        performance = await observability_service.get_performance_analysis()
        logs = await observability_service.get_logs(limit=50)
        
        return {
            "dashboard": {
                "metrics": metrics,
                "health": health,
                "performance": performance,
                "recent_logs": logs
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")

@router.get("/alerts/status")
async def get_alert_status(
    db: Session = Depends(get_db)
):
    """
    Get alert system status
    
    Args:
        db: Database session
        
    Returns:
        Dict containing alert status
    """
    try:
        from app.models.alert import Alert
        
        # Get alert statistics
        total_alerts = db.query(Alert).count()
        active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
        critical_alerts = db.query(Alert).filter(Alert.severity == "high").count()
        warning_alerts = db.query(Alert).filter(Alert.severity == "medium").count()
        info_alerts = db.query(Alert).filter(Alert.severity == "low").count()
        
        # Get recent alerts
        recent_alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(10).all()
        
        return {
            "alert_summary": {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "info_alerts": info_alerts,
                "resolved_alerts": total_alerts - active_alerts
            },
            "recent_alerts": [
                {
                    "id": alert.id,
                    "feeder_id": alert.feeder_id,
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                    "is_active": alert.is_active
                }
                for alert in recent_alerts
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert status: {str(e)}")

@router.get("/system/info")
async def get_system_info():
    """
    Get system information
    
    Returns:
        Dict containing system information
    """
    try:
        import platform
        import psutil
        import sys
        
        return {
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "application_info": {
                "name": "Hummingbird Monitor",
                "version": "1.0.0",
                "description": "AI-powered hummingbird monitoring and alert system"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")

@router.get("/config")
async def get_observability_config():
    """
    Get observability configuration
    
    Returns:
        Dict containing observability configuration
    """
    try:
        return {
            "config": {
                "logging": {
                    "level": "INFO",
                    "format": "structured",
                    "file_rotation": True,
                    "max_file_size": "10MB",
                    "backup_count": 5
                },
                "metrics": {
                    "collection_interval": "1 minute",
                    "retention_period": "30 days",
                    "aggregation": "hourly"
                },
                "monitoring": {
                    "health_check_interval": "30 seconds",
                    "performance_tracking": True,
                    "alert_thresholds": {
                        "response_time": 5.0,
                        "error_rate": 0.1,
                        "memory_usage": 80.0
                    }
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")

@router.get("/health/check")
async def health_check():
    """
    Simple health check endpoint
    
    Returns:
        Dict containing health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "observability"
    }
