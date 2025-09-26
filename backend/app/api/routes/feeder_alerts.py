"""
Feeder alert logic API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.services.feeder_alert_logic import FeederAlertLogicService
from app.schemas.feeder_alerts import (
    NectarDepletionResponse,
    AlertStatusResponse,
    AlertHistoryResponse,
    FeederPredictionResponse,
    SystemAlertOverviewResponse
)

router = APIRouter()

@router.get("/feeder/{feeder_id}/depletion", response_model=NectarDepletionResponse)
async def calculate_nectar_depletion(
    feeder_id: str,
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Calculate nectar depletion for a specific feeder
    
    Args:
        feeder_id: Feeder identifier
        days: Number of days to analyze
        db: Database session
        
    Returns:
        NectarDepletionResponse with depletion analysis
    """
    try:
        alert_service = FeederAlertLogicService()
        
        result = await alert_service.calculate_nectar_depletion(
            feeder_id=feeder_id,
            days=days,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating nectar depletion: {str(e)}")

@router.post("/feeder/{feeder_id}/check-alerts", response_model=AlertStatusResponse)
async def check_alert_conditions(
    feeder_id: str,
    db: Session = Depends(get_db)
):
    """
    Check if alert conditions are met for a feeder
    
    Args:
        feeder_id: Feeder identifier
        db: Database session
        
    Returns:
        AlertStatusResponse with alert status
    """
    try:
        alert_service = FeederAlertLogicService()
        
        result = await alert_service.check_alert_conditions(
            feeder_id=feeder_id,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking alert conditions: {str(e)}")

@router.get("/feeder/{feeder_id}/history", response_model=AlertHistoryResponse)
async def get_feeder_alert_history(
    feeder_id: str,
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get alert history for a specific feeder
    
    Args:
        feeder_id: Feeder identifier
        days: Number of days to look back
        db: Database session
        
    Returns:
        AlertHistoryResponse with alert history
    """
    try:
        alert_service = FeederAlertLogicService()
        
        result = await alert_service.get_feeder_alert_history(
            feeder_id=feeder_id,
            days=days,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert history: {str(e)}")

@router.get("/feeder/{feeder_id}/predict", response_model=FeederPredictionResponse)
async def predict_feeder_needs(
    feeder_id: str,
    days_ahead: int = Query(7, description="Number of days to predict"),
    db: Session = Depends(get_db)
):
    """
    Predict feeder needs for the next few days
    
    Args:
        feeder_id: Feeder identifier
        days_ahead: Number of days to predict
        db: Database session
        
    Returns:
        FeederPredictionResponse with predictions
    """
    try:
        alert_service = FeederAlertLogicService()
        
        result = await alert_service.predict_feeder_needs(
            feeder_id=feeder_id,
            days_ahead=days_ahead,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting feeder needs: {str(e)}")

@router.get("/system/overview", response_model=SystemAlertOverviewResponse)
async def get_system_alert_overview(
    db: Session = Depends(get_db)
):
    """
    Get system-wide alert overview
    
    Args:
        db: Database session
        
    Returns:
        SystemAlertOverviewResponse with system overview
    """
    try:
        alert_service = FeederAlertLogicService()
        
        result = await alert_service.get_system_alert_overview(db=db)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system overview: {str(e)}")

@router.post("/feeder/{feeder_id}/refill")
async def mark_feeder_refilled(
    feeder_id: str,
    refill_amount: Optional[float] = Query(None, description="Amount refilled in ml"),
    db: Session = Depends(get_db)
):
    """
    Mark a feeder as refilled and resolve related alerts
    
    Args:
        feeder_id: Feeder identifier
        refill_amount: Amount refilled in ml
        db: Database session
        
    Returns:
        Dict containing refill confirmation
    """
    try:
        from app.models.alert import Alert
        
        # Resolve active alerts for this feeder
        active_alerts = db.query(Alert).filter(
            Alert.feeder_id == feeder_id,
            Alert.alert_type == "refill_needed",
            Alert.is_active == True
        ).all()
        
        resolved_count = 0
        for alert in active_alerts:
            alert.is_active = False
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = f"Feeder refilled with {refill_amount}ml" if refill_amount else "Feeder refilled"
            resolved_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "feeder_id": feeder_id,
            "alerts_resolved": resolved_count,
            "refill_amount": refill_amount,
            "message": f"Feeder {feeder_id} marked as refilled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking feeder as refilled: {str(e)}")

@router.get("/alerts/active")
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (high, medium, low)"),
    feeder_id: Optional[str] = Query(None, description="Filter by feeder ID"),
    db: Session = Depends(get_db)
):
    """
    Get all active alerts with optional filtering
    
    Args:
        severity: Filter by severity
        feeder_id: Filter by feeder ID
        db: Database session
        
    Returns:
        Dict containing active alerts
    """
    try:
        from app.models.alert import Alert
        
        query = db.query(Alert).filter(Alert.is_active == True)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        if feeder_id:
            query = query.filter(Alert.feeder_id == feeder_id)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        
        return {
            "total_alerts": len(alerts),
            "filters": {
                "severity": severity,
                "feeder_id": feeder_id
            },
            "alerts": [
                {
                    "id": alert.id,
                    "feeder_id": alert.feeder_id,
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                    "visit_count": alert.visit_count,
                    "nectar_level": alert.estimated_nectar_level
                }
                for alert in alerts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active alerts: {str(e)}")

@router.get("/health")
async def feeder_alerts_health():
    """
    Health check for feeder alert logic service
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "feeder_alerts",
        "timestamp": datetime.utcnow().isoformat()
    }
