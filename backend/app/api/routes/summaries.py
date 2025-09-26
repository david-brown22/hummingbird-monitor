"""
Summary-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.summary import Summary
from app.schemas.summary import SummaryCreate, SummaryResponse, SummaryUpdate
from app.services.summary_generator import SummaryGeneratorService

router = APIRouter()

@router.get("/", response_model=List[SummaryResponse])
async def get_summaries(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get summaries with optional date filtering"""
    query = db.query(Summary)
    
    if date_from:
        query = query.filter(Summary.date >= date_from)
    if date_to:
        query = query.filter(Summary.date <= date_to)
    
    summaries = query.order_by(Summary.date.desc()).offset(skip).limit(limit).all()
    return summaries

@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """Get a specific summary by ID"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.post("/", response_model=SummaryResponse)
async def create_summary(summary_data: SummaryCreate, db: Session = Depends(get_db)):
    """Create a new summary"""
    summary = Summary(**summary_data.dict())
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary

@router.post("/generate/{target_date}")
async def generate_daily_summary(
    target_date: date,
    db: Session = Depends(get_db)
):
    """Generate a daily summary for a specific date"""
    # Check if summary already exists
    existing_summary = db.query(Summary).filter(Summary.date == target_date).first()
    if existing_summary:
        raise HTTPException(status_code=400, detail="Summary already exists for this date")
    
    # Generate summary using AI service
    summary_service = SummaryGeneratorService()
    summary_data = await summary_service.generate_daily_summary(target_date, db)
    
    # Create summary record
    summary = Summary(**summary_data)
    db.add(summary)
    db.commit()
    db.refresh(summary)
    
    return summary

@router.get("/latest", response_model=SummaryResponse)
async def get_latest_summary(db: Session = Depends(get_db)):
    """Get the most recent summary"""
    summary = db.query(Summary).order_by(Summary.date.desc()).first()
    if not summary:
        raise HTTPException(status_code=404, detail="No summaries found")
    return summary

@router.get("/stats/monthly")
async def get_monthly_summary_stats(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get monthly summary statistics"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    summaries = db.query(Summary).filter(
        Summary.date >= start_date,
        Summary.date < end_date
    ).all()
    
    if not summaries:
        return {"message": "No summaries found for this month"}
    
    stats = {
        "month": f"{year}-{month:02d}",
        "total_summaries": len(summaries),
        "total_visits": sum(s.total_visits for s in summaries),
        "total_unique_birds": sum(s.unique_birds for s in summaries),
        "average_visits_per_day": sum(s.total_visits for s in summaries) / len(summaries),
        "most_active_day": max(summaries, key=lambda s: s.total_visits).date if summaries else None,
        "weather_summary": [s.weather_summary for s in summaries if s.weather_summary]
    }
    
    return stats
