"""
Daily summary generation service using LangChain
"""

import logging
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser
from langchain.callbacks import StreamingStdOutCallbackHandler
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.core.config import settings
from app.models.visit import Visit
from app.models.bird import Bird
from app.models.summary import Summary
from app.models.alert import Alert

logger = logging.getLogger(__name__)

class SummaryGeneratorService:
    """Service for generating daily summaries using LangChain"""
    
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.llm = OpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.7,
            max_tokens=1500,
            model_name="gpt-3.5-turbo"
        )
        
        # Initialize different LLM configurations for different summary types
        self.creative_llm = OpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.8,
            max_tokens=2000,
            model_name="gpt-3.5-turbo"
        )
        
        self.analytical_llm = OpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.3,
            max_tokens=1000,
            model_name="gpt-3.5-turbo"
        )
    
    async def generate_daily_summary(self, target_date: date, db: Session) -> Dict:
        """
        Generate a daily summary for the specified date
        
        Args:
            target_date: Date to generate summary for
            db: Database session
            
        Returns:
            Dict containing summary data
        """
        try:
            # Get visit data for the day
            visit_data = await self._get_daily_visit_data(target_date, db)
            
            # Generate summary using LangChain
            summary_content = await self._generate_summary_content(visit_data)
            
            # Extract statistics
            stats = self._extract_daily_statistics(visit_data)
            
            # Create summary record data
            summary_data = {
                "date": target_date,
                "title": f"Daily Hummingbird Activity - {target_date.strftime('%B %d, %Y')}",
                "content": summary_content,
                "total_visits": stats["total_visits"],
                "unique_birds": stats["unique_birds"],
                "peak_hour": stats["peak_hour"],
                "average_visit_duration": stats["average_duration"],
                "weather_summary": stats.get("weather_summary"),
                "temperature_range": stats.get("temperature_range"),
                "new_birds": stats.get("new_birds"),
                "unusual_activity": stats.get("unusual_activity"),
                "generation_prompt": self._get_summary_prompt(),
                "model_used": "gpt-3.5-turbo",
                "confidence_score": 0.85
            }
            
            return summary_data
            
        except Exception as e:
            # Return error summary
            return {
                "date": target_date,
                "title": f"Daily Summary - {target_date.strftime('%B %d, %Y')} (Error)",
                "content": f"Error generating summary: {str(e)}",
                "total_visits": 0,
                "unique_birds": 0,
                "generation_prompt": "Error occurred during generation",
                "model_used": "error",
                "confidence_score": 0.0
            }
    
    async def _get_daily_visit_data(self, target_date: date, db: Session) -> Dict:
        """Get visit data for the specified date"""
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # Get visits for the day
        visits = db.query(Visit).filter(
            Visit.visit_time >= start_datetime,
            Visit.visit_time <= end_datetime
        ).all()
        
        # Get bird information
        birds = db.query(Bird).all()
        bird_dict = {bird.id: bird for bird in birds}
        
        # Process visit data
        visit_data = {
            "date": target_date,
            "visits": [],
            "birds": bird_dict,
            "statistics": {}
        }
        
        for visit in visits:
            visit_info = {
                "id": visit.id,
                "bird_id": visit.bird_id,
                "bird_name": bird_dict.get(visit.bird_id, {}).name if visit.bird_id else "Unidentified",
                "feeder_id": visit.feeder_id,
                "camera_id": visit.camera_id,
                "visit_time": visit.visit_time,
                "duration_seconds": visit.duration_seconds,
                "confidence_score": visit.confidence_score,
                "temperature": visit.temperature,
                "weather_condition": visit.weather_condition
            }
            visit_data["visits"].append(visit_info)
        
        return visit_data
    
    async def _generate_summary_content(self, visit_data: Dict) -> str:
        """Generate summary content using LangChain"""
        try:
            # Create prompt template
            prompt_template = PromptTemplate(
                input_variables=["visit_data", "statistics"],
                template=self._get_summary_prompt()
            )
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            
            # Prepare data for prompt
            statistics = self._extract_daily_statistics(visit_data)
            visit_summary = self._format_visit_data_for_prompt(visit_data)
            
            # Generate summary
            result = await chain.arun(
                visit_data=visit_summary,
                statistics=statistics
            )
            
            return result
            
        except Exception as e:
            return f"Error generating AI summary: {str(e)}"
    
    def _get_summary_prompt(self) -> str:
        """Get the prompt template for summary generation"""
        return """
You are an expert ornithologist and nature writer. Generate a daily summary of hummingbird activity based on the following data:

VISIT DATA:
{visit_data}

STATISTICS:
{statistics}

Please write a engaging, informative daily summary that includes:
1. Overall activity level and notable patterns
2. Specific bird behaviors and interactions
3. Environmental factors that may have influenced activity
4. Any unusual or interesting observations
5. Recommendations for feeder maintenance or improvements

Write in a warm, accessible tone that would appeal to bird enthusiasts. Keep it concise but informative (200-300 words).
"""
    
    def _format_visit_data_for_prompt(self, visit_data: Dict) -> str:
        """Format visit data for the prompt"""
        visits = visit_data.get("visits", [])
        if not visits:
            return "No visits recorded for this date."
        
        formatted_visits = []
        for visit in visits:
            time_str = visit["visit_time"].strftime("%H:%M") if visit["visit_time"] else "Unknown"
            duration_str = f"{visit['duration_seconds']:.1f}s" if visit["duration_seconds"] else "Unknown"
            
            formatted_visits.append(
                f"- {visit['bird_name']} at {time_str} (Duration: {duration_str}, "
                f"Feeder: {visit['feeder_id']}, Confidence: {visit.get('confidence_score', 'N/A')})"
            )
        
        return "\n".join(formatted_visits)
    
    def _extract_daily_statistics(self, visit_data: Dict) -> Dict:
        """Extract statistics from visit data"""
        visits = visit_data.get("visits", [])
        
        if not visits:
            return {
                "total_visits": 0,
                "unique_birds": 0,
                "peak_hour": None,
                "average_duration": 0,
                "weather_summary": "No data",
                "temperature_range": "No data"
            }
        
        # Basic counts
        total_visits = len(visits)
        unique_birds = len(set(v["bird_id"] for v in visits if v["bird_id"]))
        
        # Peak hour
        hour_counts = {}
        for visit in visits:
            if visit["visit_time"]:
                hour = visit["visit_time"].hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
        
        # Average duration
        durations = [v["duration_seconds"] for v in visits if v["duration_seconds"]]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        # Weather summary
        weather_conditions = [v["weather_condition"] for v in visits if v["weather_condition"]]
        weather_summary = ", ".join(set(weather_conditions)) if weather_conditions else "No weather data"
        
        # Temperature range
        temperatures = [v["temperature"] for v in visits if v["temperature"]]
        if temperatures:
            temp_range = f"{min(temperatures):.1f}°F - {max(temperatures):.1f}°F"
        else:
            temp_range = "No temperature data"
        
        return {
            "total_visits": total_visits,
            "unique_birds": unique_birds,
            "peak_hour": f"{peak_hour}:00" if peak_hour else None,
            "average_duration": average_duration,
            "weather_summary": weather_summary,
            "temperature_range": temp_range
        }
    
    async def generate_weekly_summary(self, target_date: date, db: Session) -> Dict:
        """
        Generate a weekly summary for the specified week
        
        Args:
            target_date: Date within the week to summarize
            db: Database session
            
        Returns:
            Dict containing weekly summary data
        """
        try:
            # Calculate week start and end dates
            week_start = target_date - timedelta(days=target_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Get visit data for the week
            week_data = await self._get_weekly_visit_data(week_start, week_end, db)
            
            # Generate weekly summary using LangChain
            summary_content = await self._generate_weekly_summary_content(week_data)
            
            # Extract statistics
            stats = self._extract_weekly_statistics(week_data)
            
            # Create summary record data
            summary_data = {
                "date": week_start,
                "title": f"Weekly Hummingbird Activity - {week_start.strftime('%B %d')} to {week_end.strftime('%B %d, %Y')}",
                "content": summary_content,
                "total_visits": stats["total_visits"],
                "unique_birds": stats["unique_birds"],
                "peak_hour": stats["peak_hour"],
                "average_visit_duration": stats["average_duration"],
                "weather_summary": stats.get("weather_summary"),
                "temperature_range": stats.get("temperature_range"),
                "new_birds": stats.get("new_birds"),
                "unusual_activity": stats.get("unusual_activity"),
                "generation_prompt": self._get_weekly_summary_prompt(),
                "model_used": "gpt-3.5-turbo",
                "confidence_score": 0.85
            }
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {e}")
            return {
                "date": target_date,
                "title": f"Weekly Summary - {target_date.strftime('%B %d, %Y')} (Error)",
                "content": f"Error generating weekly summary: {str(e)}",
                "total_visits": 0,
                "unique_birds": 0,
                "generation_prompt": "Error occurred during generation",
                "model_used": "error",
                "confidence_score": 0.0
            }
    
    async def generate_bird_profile_summary(self, bird_id: int, days: int = 30, db: Session = None) -> Dict:
        """
        Generate a summary profile for a specific bird
        
        Args:
            bird_id: ID of the bird
            days: Number of days to analyze
            db: Database session
            
        Returns:
            Dict containing bird profile summary
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get bird data
            bird_data = await self._get_bird_profile_data(bird_id, days, db)
            
            if not bird_data:
                return {"error": f"Bird {bird_id} not found"}
            
            # Generate bird profile using LangChain
            profile_content = await self._generate_bird_profile_content(bird_data)
            
            # Extract statistics
            stats = self._extract_bird_profile_statistics(bird_data)
            
            return {
                "bird_id": bird_id,
                "bird_name": bird_data.get("bird_name", f"Bird {bird_id}"),
                "content": profile_content,
                "total_visits": stats["total_visits"],
                "average_duration": stats["average_duration"],
                "favorite_feeder": stats["favorite_feeder"],
                "peak_hour": stats["peak_hour"],
                "visit_frequency": stats["visit_frequency"],
                "behavioral_patterns": stats["behavioral_patterns"],
                "generation_prompt": self._get_bird_profile_prompt(),
                "model_used": "gpt-3.5-turbo",
                "confidence_score": 0.90
            }
            
        except Exception as e:
            logger.error(f"Error generating bird profile: {e}")
            return {
                "bird_id": bird_id,
                "content": f"Error generating bird profile: {str(e)}",
                "error": str(e)
            }
    
    async def generate_feeder_analysis_summary(self, feeder_id: str, days: int = 7, db: Session = None) -> Dict:
        """
        Generate a summary analysis for a specific feeder
        
        Args:
            feeder_id: ID of the feeder
            days: Number of days to analyze
            db: Database session
            
        Returns:
            Dict containing feeder analysis summary
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get feeder data
            feeder_data = await self._get_feeder_analysis_data(feeder_id, days, db)
            
            if not feeder_data:
                return {"error": f"Feeder {feeder_id} not found"}
            
            # Generate feeder analysis using LangChain
            analysis_content = await self._generate_feeder_analysis_content(feeder_data)
            
            # Extract statistics
            stats = self._extract_feeder_analysis_statistics(feeder_data)
            
            return {
                "feeder_id": feeder_id,
                "content": analysis_content,
                "total_visits": stats["total_visits"],
                "unique_birds": stats["unique_birds"],
                "average_daily_visits": stats["average_daily_visits"],
                "peak_hour": stats["peak_hour"],
                "nectar_estimate": stats["nectar_estimate"],
                "recommendations": stats["recommendations"],
                "generation_prompt": self._get_feeder_analysis_prompt(),
                "model_used": "gpt-3.5-turbo",
                "confidence_score": 0.88
            }
            
        except Exception as e:
            logger.error(f"Error generating feeder analysis: {e}")
            return {
                "feeder_id": feeder_id,
                "content": f"Error generating feeder analysis: {str(e)}",
                "error": str(e)
            }
    
    async def generate_alert_summary(self, alert_id: int, db: Session = None) -> Dict:
        """
        Generate a summary for a specific alert
        
        Args:
            alert_id: ID of the alert
            db: Database session
            
        Returns:
            Dict containing alert summary
        """
        try:
            if not db:
                return {"error": "Database session required"}
            
            # Get alert data
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return {"error": f"Alert {alert_id} not found"}
            
            # Get related visit data
            visit_data = await self._get_alert_related_data(alert, db)
            
            # Generate alert summary using LangChain
            summary_content = await self._generate_alert_summary_content(alert, visit_data)
            
            return {
                "alert_id": alert_id,
                "alert_type": alert.alert_type,
                "feeder_id": alert.feeder_id,
                "content": summary_content,
                "severity": alert.severity,
                "visit_count": alert.visit_count,
                "nectar_level": alert.estimated_nectar_level,
                "generation_prompt": self._get_alert_summary_prompt(),
                "model_used": "gpt-3.5-turbo",
                "confidence_score": 0.92
            }
            
        except Exception as e:
            logger.error(f"Error generating alert summary: {e}")
            return {
                "alert_id": alert_id,
                "content": f"Error generating alert summary: {str(e)}",
                "error": str(e)
            }
    
    # Helper methods for data retrieval
    async def _get_weekly_visit_data(self, week_start: date, week_end: date, db: Session) -> Dict:
        """Get visit data for a week"""
        try:
            start_datetime = datetime.combine(week_start, datetime.min.time())
            end_datetime = datetime.combine(week_end, datetime.max.time())
            
            visits = db.query(Visit).filter(
                Visit.visit_time >= start_datetime,
                Visit.visit_time <= end_datetime
            ).all()
            
            birds = db.query(Bird).all()
            bird_dict = {bird.id: bird for bird in birds}
            
            return {
                "week_start": week_start,
                "week_end": week_end,
                "visits": [
                    {
                        "id": v.id,
                        "bird_id": v.bird_id,
                        "bird_name": bird_dict.get(v.bird_id, {}).name if v.bird_id else "Unidentified",
                        "feeder_id": v.feeder_id,
                        "visit_time": v.visit_time,
                        "duration_seconds": v.duration_seconds,
                        "confidence_score": v.confidence_score,
                        "temperature": v.temperature,
                        "weather_condition": v.weather_condition
                    }
                    for v in visits
                ],
                "birds": bird_dict
            }
        except Exception as e:
            logger.error(f"Error getting weekly visit data: {e}")
            return {"visits": [], "birds": {}}
    
    async def _get_bird_profile_data(self, bird_id: int, days: int, db: Session) -> Dict:
        """Get bird profile data"""
        try:
            bird = db.query(Bird).filter(Bird.id == bird_id).first()
            if not bird:
                return None
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            visits = db.query(Visit).filter(
                Visit.bird_id == bird_id,
                Visit.visit_time >= start_date,
                Visit.visit_time <= end_date + timedelta(days=1)
            ).all()
            
            return {
                "bird": bird,
                "visits": visits,
                "date_range": {"start": start_date, "end": end_date, "days": days}
            }
        except Exception as e:
            logger.error(f"Error getting bird profile data: {e}")
            return None
    
    async def _get_feeder_analysis_data(self, feeder_id: str, days: int, db: Session) -> Dict:
        """Get feeder analysis data"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            visits = db.query(Visit).filter(
                Visit.feeder_id == feeder_id,
                Visit.visit_time >= start_date,
                Visit.visit_time <= end_date + timedelta(days=1)
            ).all()
            
            return {
                "feeder_id": feeder_id,
                "visits": visits,
                "date_range": {"start": start_date, "end": end_date, "days": days}
            }
        except Exception as e:
            logger.error(f"Error getting feeder analysis data: {e}")
            return None
    
    async def _get_alert_related_data(self, alert: Alert, db: Session) -> Dict:
        """Get data related to an alert"""
        try:
            # Get recent visits for the feeder
            recent_visits = db.query(Visit).filter(
                Visit.feeder_id == alert.feeder_id,
                Visit.visit_time >= alert.created_at - timedelta(days=1)
            ).all()
            
            return {
                "alert": alert,
                "recent_visits": recent_visits
            }
        except Exception as e:
            logger.error(f"Error getting alert related data: {e}")
            return {"alert": alert, "recent_visits": []}
    
    # Helper methods for content generation
    async def _generate_weekly_summary_content(self, week_data: Dict) -> str:
        """Generate weekly summary content using LangChain"""
        try:
            prompt_template = PromptTemplate(
                input_variables=["week_data", "statistics"],
                template=self._get_weekly_summary_prompt()
            )
            
            chain = LLMChain(llm=self.creative_llm, prompt=prompt_template)
            
            statistics = self._extract_weekly_statistics(week_data)
            week_summary = self._format_weekly_data_for_prompt(week_data)
            
            result = await chain.arun(
                week_data=week_summary,
                statistics=statistics
            )
            
            return result
        except Exception as e:
            return f"Error generating weekly summary: {str(e)}"
    
    async def _generate_bird_profile_content(self, bird_data: Dict) -> str:
        """Generate bird profile content using LangChain"""
        try:
            prompt_template = PromptTemplate(
                input_variables=["bird_data", "statistics"],
                template=self._get_bird_profile_prompt()
            )
            
            chain = LLMChain(llm=self.creative_llm, prompt=prompt_template)
            
            statistics = self._extract_bird_profile_statistics(bird_data)
            profile_summary = self._format_bird_data_for_prompt(bird_data)
            
            result = await chain.arun(
                bird_data=profile_summary,
                statistics=statistics
            )
            
            return result
        except Exception as e:
            return f"Error generating bird profile: {str(e)}"
    
    async def _generate_feeder_analysis_content(self, feeder_data: Dict) -> str:
        """Generate feeder analysis content using LangChain"""
        try:
            prompt_template = PromptTemplate(
                input_variables=["feeder_data", "statistics"],
                template=self._get_feeder_analysis_prompt()
            )
            
            chain = LLMChain(llm=self.analytical_llm, prompt=prompt_template)
            
            statistics = self._extract_feeder_analysis_statistics(feeder_data)
            analysis_summary = self._format_feeder_data_for_prompt(feeder_data)
            
            result = await chain.arun(
                feeder_data=analysis_summary,
                statistics=statistics
            )
            
            return result
        except Exception as e:
            return f"Error generating feeder analysis: {str(e)}"
    
    async def _generate_alert_summary_content(self, alert: Alert, visit_data: Dict) -> str:
        """Generate alert summary content using LangChain"""
        try:
            prompt_template = PromptTemplate(
                input_variables=["alert", "visit_data"],
                template=self._get_alert_summary_prompt()
            )
            
            chain = LLMChain(llm=self.analytical_llm, prompt=prompt_template)
            
            alert_summary = self._format_alert_data_for_prompt(alert, visit_data)
            
            result = await chain.arun(
                alert=alert_summary,
                visit_data=visit_data
            )
            
            return result
        except Exception as e:
            return f"Error generating alert summary: {str(e)}"
    
    # Helper methods for statistics extraction
    def _extract_weekly_statistics(self, week_data: Dict) -> Dict:
        """Extract weekly statistics"""
        visits = week_data.get("visits", [])
        
        if not visits:
            return {
                "total_visits": 0,
                "unique_birds": 0,
                "peak_hour": None,
                "average_duration": 0,
                "weather_summary": "No data",
                "temperature_range": "No data"
            }
        
        total_visits = len(visits)
        unique_birds = len(set(v["bird_id"] for v in visits if v["bird_id"]))
        
        # Peak hour
        hour_counts = {}
        for visit in visits:
            if visit["visit_time"]:
                hour = visit["visit_time"].hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
        
        # Average duration
        durations = [v["duration_seconds"] for v in visits if v["duration_seconds"]]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        # Weather summary
        weather_conditions = [v["weather_condition"] for v in visits if v["weather_condition"]]
        weather_summary = ", ".join(set(weather_conditions)) if weather_conditions else "No weather data"
        
        # Temperature range
        temperatures = [v["temperature"] for v in visits if v["temperature"]]
        if temperatures:
            temp_range = f"{min(temperatures):.1f}°F - {max(temperatures):.1f}°F"
        else:
            temp_range = "No temperature data"
        
        return {
            "total_visits": total_visits,
            "unique_birds": unique_birds,
            "peak_hour": f"{peak_hour}:00" if peak_hour else None,
            "average_duration": average_duration,
            "weather_summary": weather_summary,
            "temperature_range": temp_range
        }
    
    def _extract_bird_profile_statistics(self, bird_data: Dict) -> Dict:
        """Extract bird profile statistics"""
        visits = bird_data.get("visits", [])
        
        if not visits:
            return {
                "total_visits": 0,
                "average_duration": 0,
                "favorite_feeder": None,
                "peak_hour": None,
                "visit_frequency": 0,
                "behavioral_patterns": []
            }
        
        total_visits = len(visits)
        average_duration = sum(v.duration_seconds for v in visits if v.duration_seconds) / len([v for v in visits if v.duration_seconds]) if visits else 0
        
        # Feeder preferences
        feeder_counts = {}
        for visit in visits:
            feeder_counts[visit.feeder_id] = feeder_counts.get(visit.feeder_id, 0) + 1
        
        favorite_feeder = max(feeder_counts.items(), key=lambda x: x[1])[0] if feeder_counts else None
        
        # Peak hour
        hour_counts = {}
        for visit in visits:
            hour = visit.visit_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
        
        # Visit frequency (visits per day)
        date_range = bird_data.get("date_range", {})
        days = date_range.get("days", 1)
        visit_frequency = total_visits / days if days > 0 else 0
        
        return {
            "total_visits": total_visits,
            "average_duration": round(average_duration, 2),
            "favorite_feeder": favorite_feeder,
            "peak_hour": f"{peak_hour}:00" if peak_hour else None,
            "visit_frequency": round(visit_frequency, 2),
            "behavioral_patterns": []
        }
    
    def _extract_feeder_analysis_statistics(self, feeder_data: Dict) -> Dict:
        """Extract feeder analysis statistics"""
        visits = feeder_data.get("visits", [])
        
        if not visits:
            return {
                "total_visits": 0,
                "unique_birds": 0,
                "average_daily_visits": 0,
                "peak_hour": None,
                "nectar_estimate": {"remaining_percentage": 100, "needs_refill": False},
                "recommendations": []
            }
        
        total_visits = len(visits)
        unique_birds = len(set(v.bird_id for v in visits if v.bird_id))
        
        # Average daily visits
        date_range = feeder_data.get("date_range", {})
        days = date_range.get("days", 1)
        average_daily_visits = total_visits / days if days > 0 else 0
        
        # Peak hour
        hour_counts = {}
        for visit in visits:
            hour = visit.visit_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
        
        # Nectar estimate
        estimated_depletion = min(100, total_visits * 0.1 * 100)  # 10% depletion per visit
        nectar_level = max(0, 100 - estimated_depletion)
        
        return {
            "total_visits": total_visits,
            "unique_birds": unique_birds,
            "average_daily_visits": round(average_daily_visits, 2),
            "peak_hour": f"{peak_hour}:00" if peak_hour else None,
            "nectar_estimate": {
                "remaining_percentage": round(nectar_level, 1),
                "needs_refill": nectar_level < 20
            },
            "recommendations": []
        }
    
    # Helper methods for prompt templates
    def _get_weekly_summary_prompt(self) -> str:
        """Get the prompt template for weekly summary generation"""
        return """
You are an expert ornithologist and nature writer. Generate a weekly summary of hummingbird activity based on the following data:

WEEK DATA:
{week_data}

STATISTICS:
{statistics}

Please write an engaging, informative weekly summary that includes:
1. Overall activity level and trends for the week
2. Daily patterns and notable events
3. Bird behavior and interactions
4. Environmental factors that influenced activity
5. Comparison to previous weeks (if applicable)
6. Recommendations for feeder maintenance

Write in a warm, accessible tone that would appeal to bird enthusiasts. Keep it comprehensive but readable (300-400 words).
"""
    
    def _get_bird_profile_prompt(self) -> str:
        """Get the prompt template for bird profile generation"""
        return """
You are an expert ornithologist. Generate a detailed profile of a hummingbird based on the following data:

BIRD DATA:
{bird_data}

STATISTICS:
{statistics}

Please write a comprehensive bird profile that includes:
1. Behavioral patterns and preferences
2. Feeding habits and feeder preferences
3. Activity patterns and timing
4. Unique characteristics observed
5. Visit frequency and consistency
6. Environmental preferences

Write in a scientific but accessible tone. Focus on the individual bird's unique characteristics and behaviors (250-300 words).
"""
    
    def _get_feeder_analysis_prompt(self) -> str:
        """Get the prompt template for feeder analysis generation"""
        return """
You are an expert in hummingbird feeder management. Analyze a feeder's performance based on the following data:

FEEDER DATA:
{feeder_data}

STATISTICS:
{statistics}

Please write a comprehensive feeder analysis that includes:
1. Usage patterns and visit volume
2. Bird diversity and preferences
3. Peak activity times
4. Nectar consumption estimates
5. Maintenance recommendations
6. Optimization suggestions

Write in a technical but accessible tone. Focus on practical recommendations for feeder management (200-250 words).
"""
    
    def _get_alert_summary_prompt(self) -> str:
        """Get the prompt template for alert summary generation"""
        return """
You are an expert in hummingbird feeder management. Generate a summary of a feeder alert based on the following data:

ALERT:
{alert}

VISIT DATA:
{visit_data}

Please write a clear, actionable alert summary that includes:
1. Alert type and severity
2. Current feeder status
3. Visit patterns that triggered the alert
4. Immediate actions needed
5. Prevention recommendations
6. Timeline for resolution

Write in a clear, urgent tone appropriate for an alert. Focus on immediate action items (150-200 words).
"""
    
    # Helper methods for data formatting
    def _format_weekly_data_for_prompt(self, week_data: Dict) -> str:
        """Format weekly data for prompt"""
        visits = week_data.get("visits", [])
        if not visits:
            return "No visits recorded for this week."
        
        formatted_visits = []
        for visit in visits:
            time_str = visit["visit_time"].strftime("%H:%M") if visit["visit_time"] else "Unknown"
            duration_str = f"{visit['duration_seconds']:.1f}s" if visit["duration_seconds"] else "Unknown"
            
            formatted_visits.append(
                f"- {visit['bird_name']} at {time_str} (Duration: {duration_str}, "
                f"Feeder: {visit['feeder_id']}, Confidence: {visit.get('confidence_score', 'N/A')})"
            )
        
        return "\n".join(formatted_visits)
    
    def _format_bird_data_for_prompt(self, bird_data: Dict) -> str:
        """Format bird data for prompt"""
        bird = bird_data.get("bird")
        visits = bird_data.get("visits", [])
        
        if not bird or not visits:
            return "No data available for this bird."
        
        return f"Bird: {bird.name or 'Unnamed'}\nTotal visits: {len(visits)}\nRecent activity: {len(visits)} visits in the last {bird_data.get('date_range', {}).get('days', 0)} days"
    
    def _format_feeder_data_for_prompt(self, feeder_data: Dict) -> str:
        """Format feeder data for prompt"""
        visits = feeder_data.get("visits", [])
        feeder_id = feeder_data.get("feeder_id")
        
        if not visits:
            return f"No visits recorded for feeder {feeder_id}."
        
        return f"Feeder: {feeder_id}\nTotal visits: {len(visits)}\nUnique birds: {len(set(v.bird_id for v in visits if v.bird_id))}"
    
    def _format_alert_data_for_prompt(self, alert: Alert, visit_data: Dict) -> str:
        """Format alert data for prompt"""
        return f"Alert: {alert.title}\nType: {alert.alert_type}\nSeverity: {alert.severity}\nFeeder: {alert.feeder_id}\nVisit count: {alert.visit_count}\nNectar level: {alert.estimated_nectar_level}%"
