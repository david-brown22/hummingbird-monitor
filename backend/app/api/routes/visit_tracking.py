"""
Visit tracking API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.services.visit_tracker import VisitTrackerService
from app.schemas.visit_tracking import (
    VisitRecordResponse,
    VisitCountsResponse,
    DailySummaryResponse,
    BirdHistoryResponse,
    FeederStatsResponse
)

router = APIRouter()

@router.post("/record", response_model=VisitRecordResponse)
async def record_visit(
    bird_id: Optional[int] = None,
    feeder_id: str = Query(..., description="Feeder identifier"),
    camera_id: str = Query(..., description="Camera identifier"),
    visit_time: Optional[datetime] = None,
    duration_seconds: Optional[float] = None,
    confidence_score: Optional[float] = None,
    temperature: Optional[float] = None,
    weather_condition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Record a new visit in the system
    
    Args:
        bird_id: ID of the bird (None if unidentified)
        feeder_id: Feeder identifier
        camera_id: Camera identifier
        visit_time: Time of visit (defaults to now)
        duration_seconds: Duration of visit
        confidence_score: AI confidence in identification
        temperature: Environmental temperature
        weather_condition: Weather condition
        db: Database session
        
    Returns:
        VisitRecordResponse with visit record and statistics
    """
    try:
        visit_tracker = VisitTrackerService()
        
        result = await visit_tracker.record_visit(
            bird_id=bird_id,
            feeder_id=feeder_id,
            camera_id=camera_id,
            visit_time=visit_time,
            duration_seconds=duration_seconds,
            confidence_score=confidence_score,
            temperature=temperature,
            weather_condition=weather_condition,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to record visit"))
        
        return {
            "success": True,
            "visit_id": result["visit_id"],
            "bird_id": result["bird_id"],
            "feeder_id": result["feeder_id"],
            "visit_time": result["visit_time"],
            "alert_triggered": result["alert_triggered"],
            "statistics": result["statistics"],
            "message": "Visit recorded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording visit: {str(e)}")

@router.get("/counts", response_model=VisitCountsResponse)
async def get_visit_counts(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    feeder_id: Optional[str] = Query(None, description="Filter by feeder"),
    bird_id: Optional[int] = Query(None, description="Filter by bird"),
    db: Session = Depends(get_db)
):
    """
    Get visit counts with various filters
    
    Args:
        start_date: Start date for filtering
        end_date: End date for filtering
        feeder_id: Filter by feeder
        bird_id: Filter by bird
        db: Database session
        
    Returns:
        VisitCountsResponse with visit counts and statistics
    """
    try:
        visit_tracker = VisitTrackerService()
        
        result = await visit_tracker.get_visit_counts(
            start_date=start_date,
            end_date=end_date,
            feeder_id=feeder_id,
            bird_id=bird_id,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting visit counts: {str(e)}")

@router.get("/daily-summary", response_model=DailySummaryResponse)
async def get_daily_summary(
    target_date: Optional[date] = Query(None, description="Date to summarize (defaults to today)"),
    db: Session = Depends(get_db)
):
    """
    Get daily visit summary for a specific date
    
    Args:
        target_date: Date to summarize (defaults to today)
        db: Database session
        
    Returns:
        DailySummaryResponse with daily summary
    """
    try:
        visit_tracker = VisitTrackerService()
        
        result = await visit_tracker.get_daily_visit_summary(
            target_date=target_date,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting daily summary: {str(e)}")

@router.get("/bird/{bird_id}/history", response_model=BirdHistoryResponse)
async def get_bird_visit_history(
    bird_id: int,
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get visit history for a specific bird
    
    Args:
        bird_id: ID of the bird
        days: Number of days to look back
        db: Database session
        
    Returns:
        BirdHistoryResponse with bird visit history
    """
    try:
        visit_tracker = VisitTrackerService()
        
        result = await visit_tracker.get_bird_visit_history(
            bird_id=bird_id,
            days=days,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bird history: {str(e)}")

@router.get("/feeder/{feeder_id}/stats", response_model=FeederStatsResponse)
async def get_feeder_statistics(
    feeder_id: str,
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific feeder
    
    Args:
        feeder_id: Feeder identifier
        days: Number of days to analyze
        db: Database session
        
    Returns:
        FeederStatsResponse with feeder statistics
    """
    try:
        visit_tracker = VisitTrackerService()
        
        result = await visit_tracker.get_feeder_statistics(
            feeder_id=feeder_id,
            days=days,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feeder statistics: {str(e)}")

@router.get("/trends")
async def get_visit_trends(
    days: int = Query(7, description="Number of days to analyze"),
    feeder_id: Optional[str] = Query(None, description="Filter by feeder"),
    db: Session = Depends(get_db)
):
    """
    Get visit trends over time
    
    Args:
        days: Number of days to analyze
        feeder_id: Filter by feeder
        db: Database session
        
    Returns:
        Dict containing visit trends
    """
    try:
        from app.models.visit import Visit
        from sqlalchemy import func
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = db.query(
            func.date(Visit.visit_time).label('date'),
            func.count(Visit.id).label('visits'),
            func.count(Visit.bird_id).label('identified_visits')
        ).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1)
        )
        
        if feeder_id:
            query = query.filter(Visit.feeder_id == feeder_id)
        
        trends = query.group_by(func.date(Visit.visit_time)).order_by('date').all()
        
        return {
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "trends": [
                {
                    "date": str(trend.date),
                    "total_visits": trend.visits,
                    "identified_visits": trend.identified_visits,
                    "unidentified_visits": trend.visits - trend.identified_visits
                }
                for trend in trends
            ],
            "feeder_id": feeder_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting visit trends: {str(e)}")

@router.get("/analytics")
async def get_visit_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive visit analytics
    
    Args:
        days: Number of days to analyze
        db: Database session
        
    Returns:
        Dict containing comprehensive analytics
    """
    try:
        from app.models.visit import Visit
        from app.models.bird import Bird
        from sqlalchemy import func
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Overall statistics
        total_visits = db.query(Visit).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1)
        ).count()
        
        identified_visits = db.query(Visit).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1),
            Visit.bird_id.isnot(None)
        ).count()
        
        unique_birds = db.query(Visit.bird_id).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1),
            Visit.bird_id.isnot(None)
        ).distinct().count()
        
        # Top birds by visit count
        top_birds = db.query(
            Visit.bird_id,
            func.count(Visit.id).label('visit_count')
        ).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1),
            Visit.bird_id.isnot(None)
        ).group_by(Visit.bird_id).order_by(func.count(Visit.id).desc()).limit(10).all()
        
        # Feeder statistics
        feeder_stats = db.query(
            Visit.feeder_id,
            func.count(Visit.id).label('visit_count')
        ).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1)
        ).group_by(Visit.feeder_id).all()
        
        # Hourly distribution
        hourly_dist = db.query(
            func.extract('hour', Visit.visit_time).label('hour'),
            func.count(Visit.id).label('count')
        ).filter(
            Visit.visit_time >= start_date,
            Visit.visit_time <= end_date + timedelta(days=1)
        ).group_by(func.extract('hour', Visit.visit_time)).all()
        
        return {
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "overall_stats": {
                "total_visits": total_visits,
                "identified_visits": identified_visits,
                "unidentified_visits": total_visits - identified_visits,
                "unique_birds": unique_birds,
                "identification_rate": round(identified_visits / total_visits * 100, 2) if total_visits > 0 else 0
            },
            "top_birds": [
                {
                    "bird_id": bird.bird_id,
                    "visit_count": bird.visit_count
                }
                for bird in top_birds
            ],
            "feeder_stats": [
                {
                    "feeder_id": feeder.feeder_id,
                    "visit_count": feeder.visit_count
                }
                for feeder in feeder_stats
            ],
            "hourly_distribution": [
                {
                    "hour": int(hour.hour),
                    "count": hour.count
                }
                for hour in hourly_dist
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@router.get("/health")
async def visit_tracking_health():
    """
    Health check for visit tracking service
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "visit_tracking",
        "timestamp": datetime.utcnow().isoformat()
    }
