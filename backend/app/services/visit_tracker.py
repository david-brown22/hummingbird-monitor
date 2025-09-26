"""
Visit tracking service for counting and analyzing hummingbird visits
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.visit import Visit
from app.models.bird import Bird
from app.models.alert import Alert

logger = logging.getLogger(__name__)

class VisitTrackerService:
    """Service for tracking and analyzing hummingbird visits"""
    
    def __init__(self):
        self.visit_threshold_for_alert = 50  # Default threshold
        self.nectar_depletion_rate = 0.1  # Default depletion rate
    
    async def record_visit(
        self,
        bird_id: Optional[int],
        feeder_id: str,
        camera_id: str,
        visit_time: datetime = None,
        duration_seconds: Optional[float] = None,
        confidence_score: Optional[float] = None,
        temperature: Optional[float] = None,
        weather_condition: Optional[str] = None,
        db: Session = None
    ) -> Dict:
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
            Dict containing visit record and statistics
        """
        try:
            if visit_time is None:
                visit_time = datetime.utcnow()
            
            # Create visit record
            visit = Visit(
                bird_id=bird_id,
                feeder_id=feeder_id,
                camera_id=camera_id,
                visit_time=visit_time,
                duration_seconds=duration_seconds,
                confidence_score=confidence_score,
                temperature=temperature,
                weather_condition=weather_condition,
                motion_triggered="true"
            )
            
            if db:
                db.add(visit)
                db.commit()
                db.refresh(visit)
                
                # Update bird statistics if identified
                if bird_id:
                    await self._update_bird_statistics(bird_id, db)
                
                # Check for alert conditions
                alert_triggered = await self._check_alert_conditions(feeder_id, db)
                
                # Get updated statistics
                stats = await self._get_visit_statistics(visit, db)
                
                return {
                    "success": True,
                    "visit_id": visit.id,
                    "bird_id": bird_id,
                    "feeder_id": feeder_id,
                    "visit_time": visit_time.isoformat(),
                    "alert_triggered": alert_triggered,
                    "statistics": stats
                }
            else:
                return {
                    "success": True,
                    "visit_id": None,
                    "bird_id": bird_id,
                    "feeder_id": feeder_id,
                    "visit_time": visit_time.isoformat(),
                    "alert_triggered": False,
                    "statistics": {}
                }
                
        except Exception as e:
            logger.error(f"Error recording visit: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_visit_counts(
        self,
        start_date: date = None,
        end_date: date = None,
        feeder_id: str = None,
        bird_id: int = None,
        db: Session = None
    ) -> Dict:
        """
        Get visit counts with various filters
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            feeder_id: Filter by feeder
            bird_id: Filter by bird
            db: Database session
            
        Returns:
            Dict containing visit counts and statistics
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Build query
            query = db.query(Visit)
            
            # Apply filters
            if start_date:
                query = query.filter(Visit.visit_time >= start_date)
            if end_date:
                query = query.filter(Visit.visit_time <= end_date + timedelta(days=1))
            if feeder_id:
                query = query.filter(Visit.feeder_id == feeder_id)
            if bird_id:
                query = query.filter(Visit.bird_id == bird_id)
            
            # Get total counts
            total_visits = query.count()
            identified_visits = query.filter(Visit.bird_id.isnot(None)).count()
            unidentified_visits = query.filter(Visit.bird_id.is_(None)).count()
            
            # Get unique birds
            unique_birds = query.filter(Visit.bird_id.isnot(None)).distinct(Visit.bird_id).count()
            
            # Get average duration
            avg_duration = query.filter(Visit.duration_seconds.isnot(None)).with_entities(
                func.avg(Visit.duration_seconds)
            ).scalar() or 0
            
            # Get peak hour
            hour_counts = db.query(
                func.extract('hour', Visit.visit_time).label('hour'),
                func.count(Visit.id).label('count')
            ).filter(
                Visit.visit_time >= start_date if start_date else datetime.min,
                Visit.visit_time <= end_date + timedelta(days=1) if end_date else datetime.max
            )
            
            if feeder_id:
                hour_counts = hour_counts.filter(Visit.feeder_id == feeder_id)
            if bird_id:
                hour_counts = hour_counts.filter(Visit.bird_id == bird_id)
            
            hour_counts = hour_counts.group_by(func.extract('hour', Visit.visit_time)).all()
            peak_hour = max(hour_counts, key=lambda x: x.count).hour if hour_counts else None
            
            return {
                "total_visits": total_visits,
                "identified_visits": identified_visits,
                "unidentified_visits": unidentified_visits,
                "unique_birds": unique_birds,
                "average_duration": float(avg_duration),
                "peak_hour": int(peak_hour) if peak_hour else None,
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "filters": {
                    "feeder_id": feeder_id,
                    "bird_id": bird_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting visit counts: {e}")
            return {"error": str(e)}
    
    async def get_daily_visit_summary(
        self,
        target_date: date = None,
        db: Session = None
    ) -> Dict:
        """
        Get daily visit summary for a specific date
        
        Args:
            target_date: Date to summarize (defaults to today)
            db: Database session
            
        Returns:
            Dict containing daily summary
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            if not db:
                return {"error": "Database session required"}
            
            # Get visits for the day
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            visits = db.query(Visit).filter(
                Visit.visit_time >= start_datetime,
                Visit.visit_time <= end_datetime
            ).all()
            
            # Calculate statistics
            total_visits = len(visits)
            identified_visits = len([v for v in visits if v.bird_id])
            unique_birds = len(set(v.bird_id for v in visits if v.bird_id))
            
            # Hourly distribution
            hourly_counts = {}
            for visit in visits:
                hour = visit.visit_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
            
            # Duration statistics
            durations = [v.duration_seconds for v in visits if v.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Weather statistics
            weather_conditions = [v.weather_condition for v in visits if v.weather_condition]
            weather_summary = ", ".join(set(weather_conditions)) if weather_conditions else "No data"
            
            # Temperature statistics
            temperatures = [v.temperature for v in visits if v.temperature]
            temp_range = f"{min(temperatures):.1f}°F - {max(temperatures):.1f}°F" if temperatures else "No data"
            
            # Feeder breakdown
            feeder_counts = {}
            for visit in visits:
                feeder_counts[visit.feeder_id] = feeder_counts.get(visit.feeder_id, 0) + 1
            
            return {
                "date": target_date.isoformat(),
                "total_visits": total_visits,
                "identified_visits": identified_visits,
                "unidentified_visits": total_visits - identified_visits,
                "unique_birds": unique_birds,
                "peak_hour": f"{peak_hour}:00" if peak_hour else None,
                "average_duration": round(avg_duration, 2),
                "weather_summary": weather_summary,
                "temperature_range": temp_range,
                "hourly_distribution": hourly_counts,
                "feeder_breakdown": feeder_counts,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {"error": str(e)}
    
    async def get_bird_visit_history(
        self,
        bird_id: int,
        days: int = 30,
        db: Session = None
    ) -> Dict:
        """
        Get visit history for a specific bird
        
        Args:
            bird_id: ID of the bird
            days: Number of days to look back
            db: Database session
            
        Returns:
            Dict containing bird visit history
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get visits for the bird
            visits = db.query(Visit).filter(
                Visit.bird_id == bird_id,
                Visit.visit_time >= start_date,
                Visit.visit_time <= end_date + timedelta(days=1)
            ).order_by(Visit.visit_time.desc()).all()
            
            # Calculate statistics
            total_visits = len(visits)
            avg_duration = sum(v.duration_seconds for v in visits if v.duration_seconds) / len([v for v in visits if v.duration_seconds]) if visits else 0
            
            # Daily visit counts
            daily_counts = {}
            for visit in visits:
                visit_date = visit.visit_time.date()
                daily_counts[visit_date.isoformat()] = daily_counts.get(visit_date.isoformat(), 0) + 1
            
            # Feeder preferences
            feeder_counts = {}
            for visit in visits:
                feeder_counts[visit.feeder_id] = feeder_counts.get(visit.feeder_id, 0) + 1
            
            # Time preferences
            hourly_counts = {}
            for visit in visits:
                hour = visit.visit_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
            
            return {
                "bird_id": bird_id,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                },
                "total_visits": total_visits,
                "average_duration": round(avg_duration, 2),
                "daily_visits": daily_counts,
                "feeder_preferences": feeder_counts,
                "hourly_distribution": hourly_counts,
                "peak_hour": f"{peak_hour}:00" if peak_hour else None,
                "recent_visits": [
                    {
                        "visit_id": v.id,
                        "visit_time": v.visit_time.isoformat(),
                        "feeder_id": v.feeder_id,
                        "duration_seconds": v.duration_seconds,
                        "confidence_score": v.confidence_score
                    }
                    for v in visits[:10]  # Last 10 visits
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting bird visit history: {e}")
            return {"error": str(e)}
    
    async def get_feeder_statistics(
        self,
        feeder_id: str,
        days: int = 7,
        db: Session = None
    ) -> Dict:
        """
        Get statistics for a specific feeder
        
        Args:
            feeder_id: Feeder identifier
            days: Number of days to analyze
            db: Database session
            
        Returns:
            Dict containing feeder statistics
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get visits for the feeder
            visits = db.query(Visit).filter(
                Visit.feeder_id == feeder_id,
                Visit.visit_time >= start_date,
                Visit.visit_time <= end_date + timedelta(days=1)
            ).all()
            
            # Calculate statistics
            total_visits = len(visits)
            unique_birds = len(set(v.bird_id for v in visits if v.bird_id))
            
            # Daily visit counts
            daily_counts = {}
            for visit in visits:
                visit_date = visit.visit_time.date()
                daily_counts[visit_date.isoformat()] = daily_counts.get(visit_date.isoformat(), 0) + 1
            
            # Bird visit counts
            bird_counts = {}
            for visit in visits:
                if visit.bird_id:
                    bird_counts[visit.bird_id] = bird_counts.get(visit.bird_id, 0) + 1
            
            # Time analysis
            hourly_counts = {}
            for visit in visits:
                hour = visit.visit_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
            
            # Duration analysis
            durations = [v.duration_seconds for v in visits if v.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Estimate nectar depletion
            estimated_depletion = min(100, total_visits * self.nectar_depletion_rate * 100)
            nectar_level = max(0, 100 - estimated_depletion)
            
            return {
                "feeder_id": feeder_id,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                },
                "total_visits": total_visits,
                "unique_birds": unique_birds,
                "average_daily_visits": round(total_visits / days, 2),
                "peak_hour": f"{peak_hour}:00" if peak_hour else None,
                "average_duration": round(avg_duration, 2),
                "daily_visits": daily_counts,
                "bird_visits": bird_counts,
                "hourly_distribution": hourly_counts,
                "nectar_estimate": {
                    "depletion_percentage": round(estimated_depletion, 1),
                    "remaining_percentage": round(nectar_level, 1),
                    "needs_refill": nectar_level < 20
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting feeder statistics: {e}")
            return {"error": str(e)}
    
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
    
    async def _check_alert_conditions(self, feeder_id: str, db: Session) -> bool:
        """Check if visit triggers any alert conditions"""
        try:
            # Get today's visit count for this feeder
            today = date.today()
            start_datetime = datetime.combine(today, datetime.min.time())
            end_datetime = datetime.combine(today, datetime.max.time())
            
            today_visits = db.query(Visit).filter(
                Visit.feeder_id == feeder_id,
                Visit.visit_time >= start_datetime,
                Visit.visit_time <= end_datetime
            ).count()
            
            # Check if threshold is exceeded
            if today_visits >= self.visit_threshold_for_alert:
                # Check if alert already exists for today
                existing_alert = db.query(Alert).filter(
                    Alert.feeder_id == feeder_id,
                    Alert.alert_type == "refill_needed",
                    Alert.is_active == True,
                    Alert.created_at >= start_datetime
                ).first()
                
                if not existing_alert:
                    # Create new alert
                    alert = Alert(
                        feeder_id=feeder_id,
                        alert_type="refill_needed",
                        title=f"Feeder {feeder_id} Needs Refilling",
                        message=f"Feeder {feeder_id} has reached {today_visits} visits today and likely needs refilling.",
                        severity="medium",
                        visit_count=today_visits,
                        estimated_nectar_level=max(0, 100 - (today_visits * self.nectar_depletion_rate * 100))
                    )
                    
                    db.add(alert)
                    db.commit()
                    logger.info(f"Created refill alert for feeder {feeder_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
            return False
    
    async def _get_visit_statistics(self, visit: Visit, db: Session) -> Dict:
        """Get statistics for a specific visit"""
        try:
            # Get today's statistics for the feeder
            today = date.today()
            start_datetime = datetime.combine(today, datetime.min.time())
            end_datetime = datetime.combine(today, datetime.max.time())
            
            today_visits = db.query(Visit).filter(
                Visit.feeder_id == visit.feeder_id,
                Visit.visit_time >= start_datetime,
                Visit.visit_time <= end_datetime
            ).count()
            
            return {
                "feeder_daily_visits": today_visits,
                "feeder_id": visit.feeder_id,
                "bird_id": visit.bird_id,
                "visit_time": visit.visit_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting visit statistics: {e}")
            return {}
