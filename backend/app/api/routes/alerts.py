"""
Alert-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    feeder_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    query = db.query(Alert)
    
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    if feeder_id:
        query = query.filter(Alert.feeder_id == feeder_id)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/", response_model=AlertResponse)
async def create_alert(alert_data: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    alert = Alert(**alert_data.dict())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    for field, value in alert_data.dict(exclude_unset=True).items():
        setattr(alert, field, value)
    
    alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert

@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = acknowledged_by
    alert.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Alert acknowledged successfully"}

@router.put("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: int, db: Session = Depends(get_db)):
    """Dismiss an alert (mark as inactive)"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    alert.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Alert dismissed successfully"}

@router.get("/stats/active")
async def get_active_alert_stats(db: Session = Depends(get_db)):
    """Get statistics for active alerts"""
    active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
    
    stats = {
        "total_active": len(active_alerts),
        "by_type": {},
        "by_severity": {},
        "by_feeder": {}
    }
    
    for alert in active_alerts:
        # Count by type
        stats["by_type"][alert.alert_type] = stats["by_type"].get(alert.alert_type, 0) + 1
        
        # Count by severity
        stats["by_severity"][alert.severity] = stats["by_severity"].get(alert.severity, 0) + 1
        
        # Count by feeder
        stats["by_feeder"][alert.feeder_id] = stats["by_feeder"].get(alert.feeder_id, 0) + 1
    
    return stats
