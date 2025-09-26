"""
Feeder alert logic service for estimating nectar depletion and triggering refill alerts
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.visit import Visit
from app.models.alert import Alert
from app.models.bird import Bird
from app.models.summary import Summary

logger = logging.getLogger(__name__)

class FeederAlertLogicService:
    """Service for managing feeder alerts and nectar depletion estimation"""
    
    def __init__(self):
        # Default configuration values
        self.default_nectar_capacity = 100.0  # ml
        self.default_depletion_rate = 0.5  # ml per visit
        self.alert_thresholds = {
            "critical": 10.0,  # 10% remaining
            "warning": 25.0,   # 25% remaining
            "info": 50.0       # 50% remaining
        }
        self.visit_weight_factors = {
            "duration": 0.3,      # Duration impact on depletion
            "confidence": 0.2,    # Confidence impact on depletion
            "temperature": 0.1,   # Temperature impact on depletion
            "weather": 0.1        # Weather impact on depletion
        }
        self.seasonal_adjustments = {
            "spring": 1.2,       # 20% more visits in spring
            "summer": 1.5,       # 50% more visits in summer
            "fall": 1.0,         # Normal visits in fall
            "winter": 0.3        # 70% fewer visits in winter
        }
    
    async def calculate_nectar_depletion(
        self,
        feeder_id: str,
        days: int = 7,
        db: Session = None
    ) -> Dict:
        """
        Calculate nectar depletion for a specific feeder
        
        Args:
            feeder_id: Feeder identifier
            days: Number of days to analyze
            db: Database session
            
        Returns:
            Dict containing depletion analysis
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get visit data for the feeder
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            visits = db.query(Visit).filter(
                Visit.feeder_id == feeder_id,
                Visit.visit_time >= start_date,
                Visit.visit_time <= end_date + timedelta(days=1)
            ).all()
            
            if not visits:
                return {
                    "feeder_id": feeder_id,
                    "total_visits": 0,
                    "estimated_depletion": 0.0,
                    "remaining_nectar": 100.0,
                    "depletion_rate": 0.0,
                    "alert_level": "none",
                    "days_until_empty": float('inf'),
                    "recommendations": ["No recent activity - feeder may need attention"]
                }
            
            # Calculate weighted depletion
            total_depletion = 0.0
            weighted_visits = 0
            
            for visit in visits:
                visit_weight = self._calculate_visit_weight(visit)
                depletion = self.default_depletion_rate * visit_weight
                total_depletion += depletion
                weighted_visits += visit_weight
            
            # Apply seasonal adjustment
            seasonal_factor = self._get_seasonal_factor()
            adjusted_depletion = total_depletion * seasonal_factor
            
            # Calculate remaining nectar
            remaining_nectar = max(0.0, self.default_nectar_capacity - adjusted_depletion)
            depletion_percentage = (adjusted_depletion / self.default_nectar_capacity) * 100
            
            # Determine alert level
            alert_level = self._determine_alert_level(remaining_nectar)
            
            # Calculate days until empty
            daily_depletion = adjusted_depletion / days if days > 0 else 0
            days_until_empty = remaining_nectar / daily_depletion if daily_depletion > 0 else float('inf')
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                remaining_nectar, 
                depletion_percentage, 
                alert_level,
                visits
            )
            
            return {
                "feeder_id": feeder_id,
                "total_visits": len(visits),
                "weighted_visits": weighted_visits,
                "estimated_depletion": round(adjusted_depletion, 2),
                "remaining_nectar": round(remaining_nectar, 2),
                "depletion_percentage": round(depletion_percentage, 2),
                "depletion_rate": round(daily_depletion, 2),
                "alert_level": alert_level,
                "days_until_empty": round(days_until_empty, 1),
                "seasonal_factor": seasonal_factor,
                "recommendations": recommendations,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating nectar depletion: {e}")
            return {"error": str(e)}
    
    async def check_alert_conditions(
        self,
        feeder_id: str,
        db: Session = None
    ) -> Dict:
        """
        Check if alert conditions are met for a feeder
        
        Args:
            feeder_id: Feeder identifier
            db: Database session
            
        Returns:
            Dict containing alert status and recommendations
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get current depletion status
            depletion_status = await self.calculate_nectar_depletion(feeder_id, 7, db)
            
            if "error" in depletion_status:
                return depletion_status
            
            # Check for existing alerts
            existing_alerts = db.query(Alert).filter(
                Alert.feeder_id == feeder_id,
                Alert.alert_type == "refill_needed",
                Alert.is_active == True
            ).all()
            
            # Determine if new alert is needed
            alert_needed = False
            alert_severity = "info"
            alert_message = ""
            
            if depletion_status["alert_level"] == "critical":
                alert_needed = True
                alert_severity = "high"
                alert_message = f"CRITICAL: Feeder {feeder_id} is nearly empty ({depletion_status['remaining_nectar']:.1f}ml remaining)"
            elif depletion_status["alert_level"] == "warning":
                alert_needed = True
                alert_severity = "medium"
                alert_message = f"WARNING: Feeder {feeder_id} is running low ({depletion_status['remaining_nectar']:.1f}ml remaining)"
            elif depletion_status["alert_level"] == "info":
                alert_needed = True
                alert_severity = "low"
                alert_message = f"INFO: Feeder {feeder_id} is at {depletion_status['remaining_nectar']:.1f}ml"
            
            # Check if alert already exists
            if existing_alerts:
                # Update existing alert if severity changed
                latest_alert = max(existing_alerts, key=lambda x: x.created_at)
                if latest_alert.severity != alert_severity:
                    latest_alert.severity = alert_severity
                    latest_alert.message = alert_message
                    latest_alert.updated_at = datetime.utcnow()
                    db.commit()
                    alert_needed = False  # Alert updated, no new alert needed
            
            # Create new alert if needed
            if alert_needed and not existing_alerts:
                new_alert = Alert(
                    feeder_id=feeder_id,
                    alert_type="refill_needed",
                    title=f"Feeder {feeder_id} Needs Attention",
                    message=alert_message,
                    severity=alert_severity,
                    visit_count=depletion_status["total_visits"],
                    estimated_nectar_level=depletion_status["remaining_nectar"],
                    is_active=True
                )
                
                db.add(new_alert)
                db.commit()
                db.refresh(new_alert)
                
                return {
                    "alert_created": True,
                    "alert_id": new_alert.id,
                    "severity": alert_severity,
                    "message": alert_message,
                    "depletion_status": depletion_status
                }
            
            return {
                "alert_created": False,
                "existing_alerts": len(existing_alerts),
                "depletion_status": depletion_status,
                "message": "No new alert needed"
            }
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
            return {"error": str(e)}
    
    async def get_feeder_alert_history(
        self,
        feeder_id: str,
        days: int = 30,
        db: Session = None
    ) -> Dict:
        """
        Get alert history for a specific feeder
        
        Args:
            feeder_id: Feeder identifier
            days: Number of days to look back
            db: Database session
            
        Returns:
            Dict containing alert history
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get alerts for the feeder
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            alerts = db.query(Alert).filter(
                Alert.feeder_id == feeder_id,
                Alert.created_at >= start_date,
                Alert.created_at <= end_date + timedelta(days=1)
            ).order_by(Alert.created_at.desc()).all()
            
            # Calculate alert statistics
            total_alerts = len(alerts)
            active_alerts = len([a for a in alerts if a.is_active])
            severity_counts = {
                "high": len([a for a in alerts if a.severity == "high"]),
                "medium": len([a for a in alerts if a.severity == "medium"]),
                "low": len([a for a in alerts if a.severity == "low"])
            }
            
            # Calculate alert frequency
            alert_frequency = total_alerts / days if days > 0 else 0
            
            # Get recent depletion trends
            recent_depletion = await self.calculate_nectar_depletion(feeder_id, 7, db)
            
            return {
                "feeder_id": feeder_id,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                },
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "severity_breakdown": severity_counts,
                "alert_frequency": round(alert_frequency, 2),
                "recent_depletion": recent_depletion,
                "alerts": [
                    {
                        "id": alert.id,
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "created_at": alert.created_at.isoformat(),
                        "is_active": alert.is_active,
                        "visit_count": alert.visit_count,
                        "nectar_level": alert.estimated_nectar_level
                    }
                    for alert in alerts
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return {"error": str(e)}
    
    async def predict_feeder_needs(
        self,
        feeder_id: str,
        days_ahead: int = 7,
        db: Session = None
    ) -> Dict:
        """
        Predict feeder needs for the next few days
        
        Args:
            feeder_id: Feeder identifier
            days_ahead: Number of days to predict
            db: Database session
            
        Returns:
            Dict containing predictions
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get historical data
            historical_data = await self.calculate_nectar_depletion(feeder_id, 14, db)
            
            if "error" in historical_data:
                return historical_data
            
            # Calculate trend
            current_depletion = historical_data["depletion_rate"]
            seasonal_factor = historical_data["seasonal_factor"]
            
            # Predict future depletion
            predicted_depletion = current_depletion * days_ahead * seasonal_factor
            predicted_remaining = max(0.0, historical_data["remaining_nectar"] - predicted_depletion)
            
            # Predict alert levels
            predicted_alerts = []
            for day in range(1, days_ahead + 1):
                day_depletion = current_depletion * day * seasonal_factor
                day_remaining = max(0.0, historical_data["remaining_nectar"] - day_depletion)
                day_alert_level = self._determine_alert_level(day_remaining)
                
                if day_alert_level != "none":
                    predicted_alerts.append({
                        "day": day,
                        "remaining_nectar": round(day_remaining, 2),
                        "alert_level": day_alert_level,
                        "date": (date.today() + timedelta(days=day)).isoformat()
                    })
            
            # Generate recommendations
            recommendations = self._generate_predictive_recommendations(
                predicted_remaining,
                predicted_alerts,
                days_ahead
            )
            
            return {
                "feeder_id": feeder_id,
                "prediction_period": {
                    "days_ahead": days_ahead,
                    "start_date": date.today().isoformat(),
                    "end_date": (date.today() + timedelta(days=days_ahead)).isoformat()
                },
                "current_status": historical_data,
                "predicted_depletion": round(predicted_depletion, 2),
                "predicted_remaining": round(predicted_remaining, 2),
                "predicted_alerts": predicted_alerts,
                "recommendations": recommendations,
                "confidence_score": self._calculate_prediction_confidence(historical_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting feeder needs: {e}")
            return {"error": str(e)}
    
    async def get_system_alert_overview(
        self,
        db: Session = None
    ) -> Dict:
        """
        Get system-wide alert overview
        
        Args:
            db: Database session
            
        Returns:
            Dict containing system alert overview
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get all active alerts
            active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
            
            # Get all feeders
            feeders = db.query(Visit.feeder_id).distinct().all()
            feeder_ids = [f[0] for f in feeders]
            
            # Calculate system statistics
            total_alerts = len(active_alerts)
            critical_alerts = len([a for a in active_alerts if a.severity == "high"])
            warning_alerts = len([a for a in active_alerts if a.severity == "medium"])
            info_alerts = len([a for a in active_alerts if a.severity == "low"])
            
            # Get feeder statuses
            feeder_statuses = []
            for feeder_id in feeder_ids:
                depletion_status = await self.calculate_nectar_depletion(feeder_id, 7, db)
                if "error" not in depletion_status:
                    feeder_statuses.append({
                        "feeder_id": feeder_id,
                        "alert_level": depletion_status["alert_level"],
                        "remaining_nectar": depletion_status["remaining_nectar"],
                        "days_until_empty": depletion_status["days_until_empty"]
                    })
            
            # Calculate system health score
            health_score = self._calculate_system_health_score(feeder_statuses)
            
            return {
                "system_health": {
                    "score": health_score,
                    "status": "healthy" if health_score > 80 else "warning" if health_score > 60 else "critical"
                },
                "alert_summary": {
                    "total": total_alerts,
                    "critical": critical_alerts,
                    "warning": warning_alerts,
                    "info": info_alerts
                },
                "feeder_count": len(feeder_ids),
                "feeder_statuses": feeder_statuses,
                "active_alerts": [
                    {
                        "id": alert.id,
                        "feeder_id": alert.feeder_id,
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in active_alerts
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system alert overview: {e}")
            return {"error": str(e)}
    
    # Helper methods
    def _calculate_visit_weight(self, visit: Visit) -> float:
        """Calculate weight factor for a visit based on various factors"""
        try:
            weight = 1.0  # Base weight
            
            # Duration factor
            if visit.duration_seconds:
                duration_factor = min(2.0, visit.duration_seconds / 30.0)  # Max 2x for 60+ seconds
                weight *= (1.0 + (duration_factor - 1.0) * self.visit_weight_factors["duration"])
            
            # Confidence factor
            if visit.confidence_score:
                confidence_factor = visit.confidence_score
                weight *= (1.0 + (confidence_factor - 0.5) * self.visit_weight_factors["confidence"])
            
            # Temperature factor
            if visit.temperature:
                temp_factor = 1.0 + (visit.temperature - 70.0) / 100.0  # Higher temp = more visits
                weight *= (1.0 + (temp_factor - 1.0) * self.visit_weight_factors["temperature"])
            
            # Weather factor
            if visit.weather_condition:
                weather_factor = self._get_weather_factor(visit.weather_condition)
                weight *= (1.0 + (weather_factor - 1.0) * self.visit_weight_factors["weather"])
            
            return max(0.1, min(3.0, weight))  # Clamp between 0.1 and 3.0
            
        except Exception as e:
            logger.error(f"Error calculating visit weight: {e}")
            return 1.0
    
    def _get_weather_factor(self, weather_condition: str) -> float:
        """Get weather impact factor"""
        weather_factors = {
            "sunny": 1.2,
            "cloudy": 1.0,
            "rainy": 0.8,
            "stormy": 0.6,
            "foggy": 0.9,
            "windy": 1.1
        }
        return weather_factors.get(weather_condition.lower(), 1.0)
    
    def _get_seasonal_factor(self) -> float:
        """Get seasonal adjustment factor"""
        month = datetime.now().month
        if month in [3, 4, 5]:  # Spring
            return self.seasonal_adjustments["spring"]
        elif month in [6, 7, 8]:  # Summer
            return self.seasonal_adjustments["summer"]
        elif month in [9, 10, 11]:  # Fall
            return self.seasonal_adjustments["fall"]
        else:  # Winter
            return self.seasonal_adjustments["winter"]
    
    def _determine_alert_level(self, remaining_nectar: float) -> str:
        """Determine alert level based on remaining nectar"""
        if remaining_nectar <= self.alert_thresholds["critical"]:
            return "critical"
        elif remaining_nectar <= self.alert_thresholds["warning"]:
            return "warning"
        elif remaining_nectar <= self.alert_thresholds["info"]:
            return "info"
        else:
            return "none"
    
    def _generate_recommendations(
        self,
        remaining_nectar: float,
        depletion_percentage: float,
        alert_level: str,
        visits: List[Visit]
    ) -> List[str]:
        """Generate recommendations based on current status"""
        recommendations = []
        
        if alert_level == "critical":
            recommendations.extend([
                "URGENT: Refill feeder immediately",
                "Check for leaks or damage",
                "Consider adding backup feeder"
            ])
        elif alert_level == "warning":
            recommendations.extend([
                "Plan to refill within 24 hours",
                "Monitor visit frequency closely",
                "Consider increasing feeder capacity"
            ])
        elif alert_level == "info":
            recommendations.extend([
                "Refill within 2-3 days",
                "Monitor depletion rate",
                "Consider seasonal adjustments"
            ])
        else:
            recommendations.extend([
                "Feeder is in good condition",
                "Continue regular monitoring",
                "Consider maintenance schedule"
            ])
        
        # Add specific recommendations based on visit patterns
        if visits:
            avg_duration = sum(v.duration_seconds for v in visits if v.duration_seconds) / len([v for v in visits if v.duration_seconds]) if visits else 0
            if avg_duration > 30:
                recommendations.append("Long visit durations suggest high nectar demand")
            
            if len(visits) > 50:
                recommendations.append("High visit frequency - consider larger feeder")
        
        return recommendations
    
    def _generate_predictive_recommendations(
        self,
        predicted_remaining: float,
        predicted_alerts: List[Dict],
        days_ahead: int
    ) -> List[str]:
        """Generate predictive recommendations"""
        recommendations = []
        
        if predicted_remaining <= 0:
            recommendations.append("CRITICAL: Feeder will be empty within prediction period")
        elif predicted_remaining <= 20:
            recommendations.append("WARNING: Feeder will be very low within prediction period")
        elif predicted_remaining <= 50:
            recommendations.append("INFO: Feeder will be moderately low within prediction period")
        
        if predicted_alerts:
            critical_days = [a["day"] for a in predicted_alerts if a["alert_level"] == "critical"]
            if critical_days:
                recommendations.append(f"Plan refill before day {min(critical_days)}")
        
        recommendations.extend([
            f"Monitor depletion rate over next {days_ahead} days",
            "Adjust seasonal factors if needed",
            "Consider preventive maintenance"
        ])
        
        return recommendations
    
    def _calculate_prediction_confidence(self, historical_data: Dict) -> float:
        """Calculate confidence score for predictions"""
        try:
            # Base confidence on data quality and consistency
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on visit count
            visit_count = historical_data.get("total_visits", 0)
            if visit_count > 20:
                confidence += 0.2
            elif visit_count > 10:
                confidence += 0.1
            
            # Increase confidence based on data consistency
            depletion_rate = historical_data.get("depletion_rate", 0)
            if depletion_rate > 0:
                confidence += 0.2
            
            # Seasonal factor confidence
            seasonal_factor = historical_data.get("seasonal_factor", 1.0)
            if 0.5 <= seasonal_factor <= 2.0:
                confidence += 0.1
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating prediction confidence: {e}")
            return 0.5
    
    def _calculate_system_health_score(self, feeder_statuses: List[Dict]) -> float:
        """Calculate overall system health score"""
        try:
            if not feeder_statuses:
                return 0.0
            
            total_score = 0.0
            for status in feeder_statuses:
                remaining = status.get("remaining_nectar", 0)
                if remaining >= 80:
                    total_score += 100
                elif remaining >= 60:
                    total_score += 80
                elif remaining >= 40:
                    total_score += 60
                elif remaining >= 20:
                    total_score += 40
                else:
                    total_score += 20
            
            return total_score / len(feeder_statuses)
            
        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return 0.0
