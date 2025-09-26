"""
Daily summary generation service using LangChain
"""

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.visit import Visit
from app.models.bird import Bird
from app.models.summary import Summary

class SummaryGeneratorService:
    """Service for generating daily summaries using LangChain"""
    
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.llm = OpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.7,
            max_tokens=1000
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
