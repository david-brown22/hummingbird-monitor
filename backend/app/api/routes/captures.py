"""
Capture ingestion API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime
import json

from app.core.database import get_db
from app.services.capture_ingestion import CaptureIngestionService
from app.schemas.capture import CaptureResponse, CaptureStatsResponse

router = APIRouter()

@router.post("/process", response_model=CaptureResponse)
async def process_capture(
    file: UploadFile = File(...),
    feeder_id: str = Form(...),
    camera_id: str = Form(...),
    motion_data: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Process a motion-triggered capture
    
    Args:
        file: Uploaded image file
        feeder_id: Feeder identifier
        camera_id: Camera identifier
        motion_data: Optional motion detection data (JSON string)
        db: Database session
        
    Returns:
        CaptureResponse with processing results
    """
    try:
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = f"uploads/{filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse motion data if provided
        motion_data_dict = None
        if motion_data:
            try:
                motion_data_dict = json.loads(motion_data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid motion_data JSON")
        
        # Process the capture
        capture_service = CaptureIngestionService()
        result = await capture_service.process_motion_capture(
            image_path=file_path,
            feeder_id=feeder_id,
            camera_id=camera_id,
            motion_data=motion_data_dict,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        return {
            "success": True,
            "visit_id": result["visit_id"],
            "bird_id": result.get("bird_id"),
            "confidence": result.get("confidence", 0.0),
            "alert_triggered": result.get("alert_triggered", False),
            "processing_time": result.get("processing_time"),
            "message": "Capture processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing capture: {str(e)}")

@router.post("/webhook/blue-iris")
async def blue_iris_webhook(
    webhook_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Handle webhook from Blue Iris
    
    Args:
        webhook_data: Webhook payload from Blue Iris
        db: Database session
        
    Returns:
        Processing results
    """
    try:
        capture_service = CaptureIngestionService()
        result = await capture_service.process_blue_iris_webhook(webhook_data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Webhook processing failed"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@router.get("/stats", response_model=CaptureStatsResponse)
async def get_capture_statistics(db: Session = Depends(get_db)):
    """
    Get capture processing statistics
    
    Returns:
        CaptureStatsResponse with statistics
    """
    try:
        capture_service = CaptureIngestionService()
        stats = await capture_service.get_capture_statistics(db)
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return {
            "total_captures": stats["total_captures"],
            "captures_by_feeder": stats["captures_by_feeder"],
            "captures_by_day": stats["captures_by_day"],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.get("/health")
async def capture_health_check():
    """
    Health check for capture ingestion service
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "capture_ingestion",
        "timestamp": datetime.utcnow().isoformat()
    }
