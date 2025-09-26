"""
Capture ingestion service for processing motion-triggered frames from Blue Iris
"""

import asyncio
import aiohttp
import aiofiles
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from app.core.config import settings
from app.services.bird_identification import BirdIdentificationService
from app.models.visit import Visit
from app.models.bird import Bird
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class CaptureIngestionService:
    """Service for ingesting and processing motion-triggered captures"""
    
    def __init__(self):
        self.blue_iris_url = settings.blue_iris_url
        self.blue_iris_username = settings.blue_iris_username
        self.blue_iris_password = settings.blue_iris_password
        self.bird_service = BirdIdentificationService()
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def process_motion_capture(
        self, 
        image_path: str, 
        feeder_id: str, 
        camera_id: str,
        motion_data: Optional[Dict] = None,
        db: Session = None
    ) -> Dict:
        """
        Process a motion-triggered capture from Blue Iris
        
        Args:
            image_path: Path to the captured image
            feeder_id: Identifier for the feeder
            camera_id: Identifier for the camera
            motion_data: Additional motion detection data
            db: Database session
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Processing motion capture: {image_path}")
            
            # Step 1: Validate and prepare the image
            image_validation = await self._validate_image(image_path)
            if not image_validation["valid"]:
                return {
                    "success": False,
                    "error": image_validation["error"],
                    "visit_id": None
                }
            
            # Step 2: Run AI bird identification
            identification_result = await self.bird_service.identify_bird(image_path)
            
            # Step 3: Create visit record
            visit_data = await self._create_visit_record(
                image_path=image_path,
                feeder_id=feeder_id,
                camera_id=camera_id,
                identification_result=identification_result,
                motion_data=motion_data,
                db=db
            )
            
            # Step 4: Update bird statistics if identified
            if identification_result.get("bird_id") and db:
                await self._update_bird_statistics(
                    bird_id=identification_result["bird_id"],
                    db=db
                )
            
            # Step 5: Check for alert conditions
            alert_triggered = await self._check_alert_conditions(
                feeder_id=feeder_id,
                visit_data=visit_data,
                db=db
            )
            
            return {
                "success": True,
                "visit_id": visit_data.get("id"),
                "bird_id": identification_result.get("bird_id"),
                "confidence": identification_result.get("confidence", 0.0),
                "alert_triggered": alert_triggered,
                "processing_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing motion capture: {e}")
            return {
                "success": False,
                "error": str(e),
                "visit_id": None
            }
    
    async def _validate_image(self, image_path: str) -> Dict:
        """Validate the captured image"""
        try:
            image_file = Path(image_path)
            
            if not image_file.exists():
                return {"valid": False, "error": "Image file does not exist"}
            
            if image_file.stat().st_size == 0:
                return {"valid": False, "error": "Image file is empty"}
            
            # Check file size (max 10MB)
            if image_file.stat().st_size > 10 * 1024 * 1024:
                return {"valid": False, "error": "Image file too large"}
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            if image_file.suffix.lower() not in valid_extensions:
                return {"valid": False, "error": f"Invalid file type: {image_file.suffix}"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Image validation error: {str(e)}"}
    
    async def _create_visit_record(
        self,
        image_path: str,
        feeder_id: str,
        camera_id: str,
        identification_result: Dict,
        motion_data: Optional[Dict],
        db: Session
    ) -> Dict:
        """Create a visit record in the database"""
        try:
            visit = Visit(
                bird_id=identification_result.get("bird_id"),
                feeder_id=feeder_id,
                camera_id=camera_id,
                visit_time=datetime.utcnow(),
                duration_seconds=motion_data.get("duration_seconds") if motion_data else None,
                confidence_score=identification_result.get("confidence", 0.0),
                image_path=image_path,
                motion_triggered="true",
                temperature=motion_data.get("temperature") if motion_data else None,
                weather_condition=motion_data.get("weather_condition") if motion_data else None,
                detection_metadata=json.dumps(identification_result.get("metadata", {})),
                embedding_vector=json.dumps(identification_result.get("embedding", []))
            )
            
            if db:
                db.add(visit)
                db.commit()
                db.refresh(visit)
                return {"id": visit.id, "visit": visit}
            else:
                return {"id": None, "visit": visit}
                
        except Exception as e:
            logger.error(f"Error creating visit record: {e}")
            return {"id": None, "error": str(e)}
    
    async def _update_bird_statistics(self, bird_id: int, db: Session):
        """Update bird statistics after a visit"""
        try:
            bird = db.query(Bird).filter(Bird.id == bird_id).first()
            if bird:
                bird.total_visits += 1
                bird.last_seen = datetime.utcnow()
                db.commit()
                logger.info(f"Updated statistics for bird {bird_id}")
        except Exception as e:
            logger.error(f"Error updating bird statistics: {e}")
    
    async def _check_alert_conditions(
        self, 
        feeder_id: str, 
        visit_data: Dict, 
        db: Session
    ) -> bool:
        """Check if visit triggers any alert conditions"""
        try:
            if not db:
                return False
            
            # Get recent visit count for this feeder
            recent_visits = db.query(Visit).filter(
                Visit.feeder_id == feeder_id,
                Visit.visit_time >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            # Check if visit threshold is exceeded
            if recent_visits >= settings.visit_threshold_for_alert:
                await self._create_refill_alert(feeder_id, recent_visits, db)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
            return False
    
    async def _create_refill_alert(self, feeder_id: str, visit_count: int, db: Session):
        """Create a refill alert for a feeder"""
        try:
            from app.models.alert import Alert
            
            alert = Alert(
                feeder_id=feeder_id,
                alert_type="refill_needed",
                title=f"Feeder {feeder_id} Needs Refilling",
                message=f"Feeder {feeder_id} has reached {visit_count} visits today and likely needs refilling.",
                severity="medium",
                visit_count=visit_count,
                estimated_nectar_level=max(0, 100 - (visit_count * settings.nectar_depletion_rate * 100))
            )
            
            db.add(alert)
            db.commit()
            logger.info(f"Created refill alert for feeder {feeder_id}")
            
        except Exception as e:
            logger.error(f"Error creating refill alert: {e}")
    
    async def process_blue_iris_webhook(self, webhook_data: Dict) -> Dict:
        """
        Process a webhook from Blue Iris
        
        Args:
            webhook_data: Webhook payload from Blue Iris
            
        Returns:
            Dict containing processing results
        """
        try:
            # Extract data from Blue Iris webhook
            camera_name = webhook_data.get("camera", "unknown")
            trigger_type = webhook_data.get("trigger", "motion")
            timestamp = webhook_data.get("timestamp", datetime.utcnow().isoformat())
            
            # Map camera to feeder (this would be configured)
            feeder_mapping = {
                "front_camera": "feeder_001",
                "back_camera": "feeder_002",
                "side_camera": "feeder_003"
            }
            
            feeder_id = feeder_mapping.get(camera_name, "feeder_unknown")
            camera_id = camera_name
            
            # Process the capture
            result = await self.process_motion_capture(
                image_path=webhook_data.get("image_path"),
                feeder_id=feeder_id,
                camera_id=camera_id,
                motion_data={
                    "trigger_type": trigger_type,
                    "timestamp": timestamp,
                    "camera_name": camera_name
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing Blue Iris webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_capture_statistics(self, db: Session) -> Dict:
        """Get statistics about captures processed"""
        try:
            from sqlalchemy import func
            
            # Get total captures
            total_captures = db.query(Visit).count()
            
            # Get captures by feeder
            captures_by_feeder = db.query(
                Visit.feeder_id,
                func.count(Visit.id).label('count')
            ).group_by(Visit.feeder_id).all()
            
            # Get captures by day (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            captures_by_day = db.query(
                func.date(Visit.visit_time).label('date'),
                func.count(Visit.id).label('count')
            ).filter(
                Visit.visit_time >= week_ago
            ).group_by(func.date(Visit.visit_time)).all()
            
            return {
                "total_captures": total_captures,
                "captures_by_feeder": {row.feeder_id: row.count for row in captures_by_feeder},
                "captures_by_day": {str(row.date): row.count for row in captures_by_day}
            }
            
        except Exception as e:
            logger.error(f"Error getting capture statistics: {e}")
            return {"error": str(e)}
