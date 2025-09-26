"""
Visit-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.visit import Visit
from app.schemas.visit import VisitCreate, VisitResponse, VisitUpdate
from app.services.bird_identification import BirdIdentificationService

router = APIRouter()

@router.get("/", response_model=List[VisitResponse])
async def get_visits(
    skip: int = 0,
    limit: int = 100,
    feeder_id: Optional[str] = None,
    bird_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get visits with optional filtering"""
    query = db.query(Visit)
    
    if feeder_id:
        query = query.filter(Visit.feeder_id == feeder_id)
    if bird_id:
        query = query.filter(Visit.bird_id == bird_id)
    if date_from:
        query = query.filter(Visit.visit_time >= date_from)
    if date_to:
        query = query.filter(Visit.visit_time <= date_to)
    
    visits = query.offset(skip).limit(limit).all()
    return visits

@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get a specific visit by ID"""
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.post("/", response_model=VisitResponse)
async def create_visit(visit_data: VisitCreate, db: Session = Depends(get_db)):
    """Create a new visit record"""
    visit = Visit(**visit_data.dict())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit

@router.post("/process-image")
async def process_motion_image(
    file: UploadFile = File(...),
    feeder_id: str = None,
    camera_id: str = None,
    db: Session = Depends(get_db)
):
    """Process a motion-triggered image from Blue Iris"""
    if not feeder_id or not camera_id:
        raise HTTPException(status_code=400, detail="feeder_id and camera_id are required")
    
    # Save uploaded file
    file_path = f"uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process with AI identification
    bird_service = BirdIdentificationService()
    identification_result = await bird_service.identify_bird(file_path)
    
    # Create visit record
    visit_data = VisitCreate(
        feeder_id=feeder_id,
        camera_id=camera_id,
        image_path=file_path,
        motion_triggered="true",
        confidence_score=identification_result.get("confidence", 0.0),
        detection_metadata=str(identification_result.get("metadata", {})),
        embedding_vector=str(identification_result.get("embedding", []))
    )
    
    if identification_result.get("bird_id"):
        visit_data.bird_id = identification_result["bird_id"]
    
    visit = Visit(**visit_data.dict())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    
    return {
        "visit": visit,
        "identification": identification_result
    }

@router.get("/stats/daily")
async def get_daily_stats(
    date: Optional[date] = None,
    feeder_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get daily visit statistics"""
    target_date = date or datetime.now().date()
    
    query = db.query(Visit).filter(
        Visit.visit_time >= target_date,
        Visit.visit_time < target_date.replace(day=target_date.day + 1)
    )
    
    if feeder_id:
        query = query.filter(Visit.feeder_id == feeder_id)
    
    visits = query.all()
    
    stats = {
        "date": target_date,
        "total_visits": len(visits),
        "unique_birds": len(set(v.bird_id for v in visits if v.bird_id)),
        "unidentified_visits": len([v for v in visits if not v.bird_id]),
        "feeder_id": feeder_id,
        "peak_hour": max(set(v.visit_time.hour for v in visits), default=None),
        "average_duration": sum(v.duration_seconds for v in visits if v.duration_seconds) / len([v for v in visits if v.duration_seconds]) if visits else 0
    }
    
    return stats
