"""
Observability service for logging, metrics, and monitoring
"""

import logging
import time
import json
import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.visit import Visit
from app.models.alert import Alert
from app.models.bird import Bird
from app.models.summary import Summary
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class ObservabilityService:
    """Service for system observability, logging, metrics, and monitoring"""
    
    def __init__(self):
        self.metrics = {}
        self.logs = []
        self.performance_data = {}
        self.health_checks = {}
        self.start_time = datetime.utcnow()
        
        # Configure logging
        self._setup_logging()
        
        # Initialize metrics
        self._initialize_metrics()
    
    def _setup_logging(self):
        """Setup structured logging configuration"""
        try:
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            json_formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "function": "%(funcName)s", "line": %(lineno)d}'
            )
            
            # Setup file handlers
            file_handler = logging.FileHandler('logs/hummingbird_monitor.log')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(detailed_formatter)
            
            error_handler = logging.FileHandler('logs/errors.log')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(json_formatter)
            
            # Setup console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(detailed_formatter)
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(file_handler)
            root_logger.addHandler(error_handler)
            root_logger.addHandler(console_handler)
            
            # Configure specific loggers
            self._configure_service_loggers()
            
            logger.info("Logging system initialized successfully")
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
    
    def _configure_service_loggers(self):
        """Configure loggers for specific services"""
        service_loggers = [
            'app.services.bird_identification',
            'app.services.visit_tracker',
            'app.services.summary_generator',
            'app.services.feeder_alert_logic',
            'app.services.capture_ingestion',
            'app.services.blue_iris_integration'
        ]
        
        for service_name in service_loggers:
            service_logger = logging.getLogger(service_name)
            service_logger.setLevel(logging.INFO)
    
    def _initialize_metrics(self):
        """Initialize system metrics"""
        self.metrics = {
            "system": {
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": 0,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0
            },
            "visits": {
                "total_visits": 0,
                "identified_visits": 0,
                "unidentified_visits": 0,
                "unique_birds": 0,
                "average_duration": 0.0,
                "peak_hour": None
            },
            "alerts": {
                "total_alerts": 0,
                "active_alerts": 0,
                "critical_alerts": 0,
                "warning_alerts": 0,
                "info_alerts": 0,
                "resolved_alerts": 0
            },
            "feeders": {
                "total_feeders": 0,
                "healthy_feeders": 0,
                "warning_feeders": 0,
                "critical_feeders": 0,
                "average_nectar_level": 0.0
            },
            "ai_services": {
                "bird_identifications": 0,
                "summary_generations": 0,
                "alert_calculations": 0,
                "average_confidence": 0.0,
                "api_calls": 0,
                "api_errors": 0
            }
        }
    
    async def log_event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        metadata: Dict = None,
        service: str = "system"
    ) -> None:
        """
        Log an event with structured data
        
        Args:
            event_type: Type of event (visit, alert, error, etc.)
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            metadata: Additional metadata
            service: Service name
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "level": level,
                "message": message,
                "service": service,
                "metadata": metadata or {}
            }
            
            # Add to in-memory logs (for API access)
            self.logs.append(log_entry)
            
            # Keep only last 1000 logs in memory
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]
            
            # Log to appropriate logger
            service_logger = logging.getLogger(f"app.services.{service}")
            
            if level == "DEBUG":
                service_logger.debug(f"{event_type}: {message}", extra={"metadata": metadata})
            elif level == "INFO":
                service_logger.info(f"{event_type}: {message}", extra={"metadata": metadata})
            elif level == "WARNING":
                service_logger.warning(f"{event_type}: {message}", extra={"metadata": metadata})
            elif level == "ERROR":
                service_logger.error(f"{event_type}: {message}", extra={"metadata": metadata})
            elif level == "CRITICAL":
                service_logger.critical(f"{event_type}: {message}", extra={"metadata": metadata})
            
        except Exception as e:
            print(f"Error logging event: {e}")
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "counter",
        tags: Dict = None
    ) -> None:
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of metric (counter, gauge, histogram)
            tags: Additional tags
        """
        try:
            metric_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "metric_name": metric_name,
                "value": value,
                "metric_type": metric_type,
                "tags": tags or {}
            }
            
            # Update metrics dictionary
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []
            
            self.metrics[metric_name].append(metric_entry)
            
            # Keep only last 1000 entries per metric
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]
            
            # Update system metrics
            self._update_system_metrics(metric_name, value, tags)
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    async def record_performance(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        metadata: Dict = None
    ) -> None:
        """
        Record performance data for an operation
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            success: Whether operation was successful
            metadata: Additional metadata
        """
        try:
            performance_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "duration": duration,
                "success": success,
                "metadata": metadata or {}
            }
            
            if operation not in self.performance_data:
                self.performance_data[operation] = []
            
            self.performance_data[operation].append(performance_entry)
            
            # Keep only last 500 entries per operation
            if len(self.performance_data[operation]) > 500:
                self.performance_data[operation] = self.performance_data[operation][-500:]
            
            # Update system metrics
            self.metrics["system"]["total_requests"] += 1
            if success:
                self.metrics["system"]["successful_requests"] += 1
            else:
                self.metrics["system"]["failed_requests"] += 1
            
            # Update average response time
            total_requests = self.metrics["system"]["total_requests"]
            current_avg = self.metrics["system"]["average_response_time"]
            self.metrics["system"]["average_response_time"] = (
                (current_avg * (total_requests - 1) + duration) / total_requests
            )
            
        except Exception as e:
            logger.error(f"Error recording performance: {e}")
    
    async def get_system_metrics(self, db: Session = None) -> Dict:
        """
        Get comprehensive system metrics
        
        Args:
            db: Database session
            
        Returns:
            Dict containing system metrics
        """
        try:
            if db:
                # Get database metrics
                db_metrics = await self._get_database_metrics(db)
                self.metrics.update(db_metrics)
            
            # Update uptime
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            self.metrics["system"]["uptime_seconds"] = uptime
            
            # Calculate health score
            health_score = self._calculate_health_score()
            self.metrics["system"]["health_score"] = health_score
            
            return {
                "metrics": self.metrics,
                "performance": self.performance_data,
                "logs": self.logs[-100:],  # Last 100 logs
                "health_score": health_score,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    async def get_health_status(self, db: Session = None) -> Dict:
        """
        Get system health status
        
        Args:
            db: Database session
            
        Returns:
            Dict containing health status
        """
        try:
            health_checks = {}
            
            # Database health
            if db:
                try:
                    db.query(Visit).limit(1).all()
                    health_checks["database"] = {"status": "healthy", "response_time": 0.001}
                except Exception as e:
                    health_checks["database"] = {"status": "unhealthy", "error": str(e)}
            
            # System health
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            health_checks["system"] = {
                "status": "healthy" if uptime > 0 else "starting",
                "uptime_seconds": uptime
            }
            
            # Memory health
            import psutil
            memory = psutil.virtual_memory()
            health_checks["memory"] = {
                "status": "healthy" if memory.percent < 80 else "warning",
                "usage_percent": memory.percent,
                "available_mb": memory.available / (1024 * 1024)
            }
            
            # CPU health
            cpu_percent = psutil.cpu_percent(interval=1)
            health_checks["cpu"] = {
                "status": "healthy" if cpu_percent < 80 else "warning",
                "usage_percent": cpu_percent
            }
            
            # Overall health
            overall_status = "healthy"
            if any(check.get("status") == "unhealthy" for check in health_checks.values()):
                overall_status = "unhealthy"
            elif any(check.get("status") == "warning" for check in health_checks.values()):
                overall_status = "warning"
            
            return {
                "overall_status": overall_status,
                "health_checks": health_checks,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {"error": str(e)}
    
    async def get_performance_analysis(self) -> Dict:
        """
        Get performance analysis data
        
        Returns:
            Dict containing performance analysis
        """
        try:
            analysis = {}
            
            for operation, data in self.performance_data.items():
                if not data:
                    continue
                
                durations = [entry["duration"] for entry in data]
                successes = [entry["success"] for entry in data]
                
                analysis[operation] = {
                    "total_operations": len(data),
                    "success_rate": sum(successes) / len(successes) if successes else 0,
                    "average_duration": sum(durations) / len(durations) if durations else 0,
                    "min_duration": min(durations) if durations else 0,
                    "max_duration": max(durations) if durations else 0,
                    "recent_operations": data[-10:]  # Last 10 operations
                }
            
            return {
                "performance_analysis": analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analysis: {e}")
            return {"error": str(e)}
    
    async def get_logs(
        self,
        level: str = None,
        service: str = None,
        limit: int = 100,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict:
        """
        Get filtered logs
        
        Args:
            level: Filter by log level
            service: Filter by service
            limit: Maximum number of logs to return
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            Dict containing filtered logs
        """
        try:
            filtered_logs = self.logs.copy()
            
            # Apply filters
            if level:
                filtered_logs = [log for log in filtered_logs if log["level"] == level]
            
            if service:
                filtered_logs = [log for log in filtered_logs if log["service"] == service]
            
            if start_time:
                filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log["timestamp"]) >= start_time]
            
            if end_time:
                filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log["timestamp"]) <= end_time]
            
            # Apply limit
            filtered_logs = filtered_logs[-limit:] if limit else filtered_logs
            
            return {
                "logs": filtered_logs,
                "total_count": len(filtered_logs),
                "filters": {
                    "level": level,
                    "service": service,
                    "limit": limit,
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return {"error": str(e)}
    
    async def _get_database_metrics(self, db: Session) -> Dict:
        """Get metrics from database"""
        try:
            # Visit metrics
            total_visits = db.query(Visit).count()
            identified_visits = db.query(Visit).filter(Visit.bird_id.isnot(None)).count()
            unique_birds = db.query(Visit.bird_id).filter(Visit.bird_id.isnot(None)).distinct().count()
            
            # Alert metrics
            total_alerts = db.query(Alert).count()
            active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
            critical_alerts = db.query(Alert).filter(Alert.severity == "high").count()
            warning_alerts = db.query(Alert).filter(Alert.severity == "medium").count()
            info_alerts = db.query(Alert).filter(Alert.severity == "low").count()
            
            # Feeder metrics
            feeders = db.query(Visit.feeder_id).distinct().all()
            total_feeders = len(feeders)
            
            # Average duration
            avg_duration = db.query(func.avg(Visit.duration_seconds)).filter(
                Visit.duration_seconds.isnot(None)
            ).scalar() or 0
            
            # Peak hour
            hour_counts = db.query(
                func.extract('hour', Visit.visit_time).label('hour'),
                func.count(Visit.id).label('count')
            ).group_by(func.extract('hour', Visit.visit_time)).all()
            
            peak_hour = max(hour_counts, key=lambda x: x.count).hour if hour_counts else None
            
            return {
                "visits": {
                    "total_visits": total_visits,
                    "identified_visits": identified_visits,
                    "unidentified_visits": total_visits - identified_visits,
                    "unique_birds": unique_birds,
                    "average_duration": float(avg_duration),
                    "peak_hour": int(peak_hour) if peak_hour else None
                },
                "alerts": {
                    "total_alerts": total_alerts,
                    "active_alerts": active_alerts,
                    "critical_alerts": critical_alerts,
                    "warning_alerts": warning_alerts,
                    "info_alerts": info_alerts,
                    "resolved_alerts": total_alerts - active_alerts
                },
                "feeders": {
                    "total_feeders": total_feeders,
                    "healthy_feeders": total_feeders,  # Placeholder
                    "warning_feeders": 0,  # Placeholder
                    "critical_feeders": 0,  # Placeholder
                    "average_nectar_level": 75.0  # Placeholder
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {}
    
    def _update_system_metrics(self, metric_name: str, value: float, tags: Dict):
        """Update system metrics based on recorded metric"""
        try:
            # Update specific metrics based on name
            if "visit" in metric_name.lower():
                self.metrics["visits"]["total_visits"] += 1
            elif "alert" in metric_name.lower():
                self.metrics["alerts"]["total_alerts"] += 1
            elif "feeder" in metric_name.lower():
                self.metrics["feeders"]["total_feeders"] = max(
                    self.metrics["feeders"]["total_feeders"], 
                    int(value) if value.is_integer() else self.metrics["feeders"]["total_feeders"]
                )
            elif "ai" in metric_name.lower() or "identification" in metric_name.lower():
                self.metrics["ai_services"]["bird_identifications"] += 1
            elif "summary" in metric_name.lower():
                self.metrics["ai_services"]["summary_generations"] += 1
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def _calculate_health_score(self) -> float:
        """Calculate overall system health score"""
        try:
            score = 100.0
            
            # Deduct points for failed requests
            total_requests = self.metrics["system"]["total_requests"]
            if total_requests > 0:
                failure_rate = self.metrics["system"]["failed_requests"] / total_requests
                score -= failure_rate * 50  # Up to 50 points for failures
            
            # Deduct points for high response times
            avg_response_time = self.metrics["system"]["average_response_time"]
            if avg_response_time > 5.0:  # 5 seconds
                score -= min(30, (avg_response_time - 5.0) * 10)  # Up to 30 points for slow responses
            
            # Deduct points for critical alerts
            critical_alerts = self.metrics["alerts"]["critical_alerts"]
            score -= min(20, critical_alerts * 5)  # Up to 20 points for critical alerts
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50.0  # Default score
