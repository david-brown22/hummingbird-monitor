"""
Summary generation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.services.summary_generator import SummaryGeneratorService
from app.schemas.summary_generation import (
    DailySummaryResponse,
    WeeklySummaryResponse,
    BirdProfileResponse,
    FeederAnalysisResponse,
    AlertSummaryResponse
)

router = APIRouter()

@router.post("/daily", response_model=DailySummaryResponse)
async def generate_daily_summary(
    target_date: Optional[date] = Query(None, description="Date to summarize (defaults to today)"),
    db: Session = Depends(get_db)
):
    """
    Generate a daily summary for the specified date
    
    Args:
        target_date: Date to summarize (defaults to today)
        db: Database session
        
    Returns:
        DailySummaryResponse with daily summary
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        summary_service = SummaryGeneratorService()
        
        result = await summary_service.generate_daily_summary(
            target_date=target_date,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating daily summary: {str(e)}")

@router.post("/weekly", response_model=WeeklySummaryResponse)
async def generate_weekly_summary(
    target_date: Optional[date] = Query(None, description="Date within the week to summarize (defaults to today)"),
    db: Session = Depends(get_db)
):
    """
    Generate a weekly summary for the specified week
    
    Args:
        target_date: Date within the week to summarize (defaults to today)
        db: Database session
        
    Returns:
        WeeklySummaryResponse with weekly summary
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        summary_service = SummaryGeneratorService()
        
        result = await summary_service.generate_weekly_summary(
            target_date=target_date,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly summary: {str(e)}")

@router.post("/bird/{bird_id}/profile", response_model=BirdProfileResponse)
async def generate_bird_profile(
    bird_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Generate a summary profile for a specific bird
    
    Args:
        bird_id: ID of the bird
        days: Number of days to analyze
        db: Database session
        
    Returns:
        BirdProfileResponse with bird profile summary
    """
    try:
        summary_service = SummaryGeneratorService()
        
        result = await summary_service.generate_bird_profile_summary(
            bird_id=bird_id,
            days=days,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating bird profile: {str(e)}")

@router.post("/feeder/{feeder_id}/analysis", response_model=FeederAnalysisResponse)
async def generate_feeder_analysis(
    feeder_id: str,
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Generate a summary analysis for a specific feeder
    
    Args:
        feeder_id: ID of the feeder
        days: Number of days to analyze
        db: Database session
        
    Returns:
        FeederAnalysisResponse with feeder analysis summary
    """
    try:
        summary_service = SummaryGeneratorService()
        
        result = await summary_service.generate_feeder_analysis_summary(
            feeder_id=feeder_id,
            days=days,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating feeder analysis: {str(e)}")

@router.post("/alert/{alert_id}/summary", response_model=AlertSummaryResponse)
async def generate_alert_summary(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate a summary for a specific alert
    
    Args:
        alert_id: ID of the alert
        db: Database session
        
    Returns:
        AlertSummaryResponse with alert summary
    """
    try:
        summary_service = SummaryGeneratorService()
        
        result = await summary_service.generate_alert_summary(
            alert_id=alert_id,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating alert summary: {str(e)}")

@router.get("/prompts")
async def get_summary_prompts():
    """
    Get available summary generation prompts
    
    Returns:
        Dict containing available prompts
    """
    try:
        summary_service = SummaryGeneratorService()
        
        prompts = {
            "daily_summary": summary_service._get_daily_summary_prompt(),
            "weekly_summary": summary_service._get_weekly_summary_prompt(),
            "bird_profile": summary_service._get_bird_profile_prompt(),
            "feeder_analysis": summary_service._get_feeder_analysis_prompt(),
            "alert_summary": summary_service._get_alert_summary_prompt()
        }
        
        return {
            "prompts": prompts,
            "description": "Available summary generation prompts for different types of summaries"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting prompts: {str(e)}")

@router.get("/models")
async def get_available_models():
    """
    Get available LLM models for summary generation
    
    Returns:
        Dict containing available models
    """
    try:
        models = {
            "default": {
                "name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1500,
                "description": "Standard model for general summaries"
            },
            "creative": {
                "name": "gpt-3.5-turbo",
                "temperature": 0.8,
                "max_tokens": 2000,
                "description": "Creative model for engaging summaries"
            },
            "analytical": {
                "name": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 1000,
                "description": "Analytical model for technical summaries"
            }
        }
        
        return {
            "models": models,
            "description": "Available LLM models for different summary types"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@router.get("/health")
async def summary_generation_health():
    """
    Health check for summary generation service
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "summary_generation",
        "timestamp": date.today().isoformat()
    }
