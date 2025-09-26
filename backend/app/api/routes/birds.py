"""
Bird-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.bird import Bird
from app.schemas.bird import BirdCreate, BirdResponse, BirdUpdate

router = APIRouter()

@router.get("/", response_model=List[BirdResponse])
async def get_birds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all birds with pagination"""
    birds = db.query(Bird).offset(skip).limit(limit).all()
    return birds

@router.get("/{bird_id}", response_model=BirdResponse)
async def get_bird(bird_id: int, db: Session = Depends(get_db)):
    """Get a specific bird by ID"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    return bird

@router.post("/", response_model=BirdResponse)
async def create_bird(bird_data: BirdCreate, db: Session = Depends(get_db)):
    """Create a new bird record"""
    bird = Bird(**bird_data.dict())
    db.add(bird)
    db.commit()
    db.refresh(bird)
    return bird

@router.put("/{bird_id}", response_model=BirdResponse)
async def update_bird(
    bird_id: int,
    bird_data: BirdUpdate,
    db: Session = Depends(get_db)
):
    """Update a bird record"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    
    for field, value in bird_data.dict(exclude_unset=True).items():
        setattr(bird, field, value)
    
    bird.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bird)
    return bird

@router.delete("/{bird_id}")
async def delete_bird(bird_id: int, db: Session = Depends(get_db)):
    """Delete a bird record"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    
    db.delete(bird)
    db.commit()
    return {"message": "Bird deleted successfully"}

@router.get("/{bird_id}/visits", response_model=List[dict])
async def get_bird_visits(
    bird_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get visits for a specific bird"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    if not bird:
        raise HTTPException(status_code=404, detail="Bird not found")
    
    visits = db.query(Visit).filter(Visit.bird_id == bird_id).offset(skip).limit(limit).all()
    return visits
