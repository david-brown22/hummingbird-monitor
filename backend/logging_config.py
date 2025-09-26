"""
Logging configuration for the Hummingbird Monitor system
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "function": "%(funcName)s", "line": %(lineno)d}'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handlers
    # Main application log
    main_handler = logging.handlers.RotatingFileHandler(
        'logs/hummingbird_monitor.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(detailed_formatter)
    
    # Error log
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    
    # Debug log
    debug_handler = logging.handlers.RotatingFileHandler(
        'logs/debug.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=2
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(detailed_formatter)
    
    # Performance log
    performance_handler = logging.handlers.RotatingFileHandler(
        'logs/performance.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(json_formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(debug_handler)
    root_logger.addHandler(performance_handler)
    root_logger.addHandler(console_handler)
    
    # Configure specific service loggers
    configure_service_loggers()
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized successfully")
    logger.info(f"Log files created in: {os.path.abspath('logs')}")

def configure_service_loggers():
    """Configure loggers for specific services"""
    
    service_configs = {
        'app.services.bird_identification': {
            'level': logging.INFO,
            'handlers': ['main', 'performance'],
            'propagate': False
        },
        'app.services.visit_tracker': {
            'level': logging.INFO,
            'handlers': ['main', 'performance'],
            'propagate': False
        },
        'app.services.summary_generator': {
            'level': logging.INFO,
            'handlers': ['main', 'performance'],
            'propagate': False
        },
        'app.services.feeder_alert_logic': {
            'level': logging.INFO,
            'handlers': ['main', 'performance'],
            'propagate': False
        },
        'app.services.capture_ingestion': {
            'level': logging.INFO,
            'handlers': ['main', 'performance'],
            'propagate': False
        },
        'app.services.blue_iris_integration': {
            'level': logging.INFO,
            'handlers': ['main', 'performance'],
            'propagate': False
        },
        'app.services.observability': {
            'level': logging.INFO,
            'handlers': ['main', 'debug'],
            'propagate': False
        },
        'app.api.routes': {
            'level': logging.INFO,
            'handlers': ['main'],
            'propagate': False
        },
        'app.core.database': {
            'level': logging.WARNING,
            'handlers': ['main', 'error'],
            'propagate': False
        }
    }
    
    for service_name, config in service_configs.items():
        service_logger = logging.getLogger(service_name)
        service_logger.setLevel(config['level'])
        service_logger.propagate = config['propagate']

def get_service_logger(service_name: str) -> logging.Logger:
    """Get a logger for a specific service"""
    return logging.getLogger(f'app.services.{service_name}')

def log_performance(operation: str, duration: float, success: bool = True, metadata: dict = None):
    """Log performance data"""
    performance_logger = logging.getLogger('app.services.observability')
    
    log_data = {
        'operation': operation,
        'duration': duration,
        'success': success,
        'metadata': metadata or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    performance_logger.info(f"Performance: {operation}", extra=log_data)

def log_metric(metric_name: str, value: float, metric_type: str = "counter", tags: dict = None):
    """Log a metric"""
    metric_logger = logging.getLogger('app.services.observability')
    
    log_data = {
        'metric_name': metric_name,
        'value': value,
        'metric_type': metric_type,
        'tags': tags or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    metric_logger.info(f"Metric: {metric_name}", extra=log_data)

def log_event(event_type: str, message: str, level: str = "INFO", service: str = "system", metadata: dict = None):
    """Log an event"""
    event_logger = logging.getLogger(f'app.services.{service}')
    
    log_data = {
        'event_type': event_type,
        'message': message,
        'level': level,
        'service': service,
        'metadata': metadata or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if level == "DEBUG":
        event_logger.debug(f"{event_type}: {message}", extra=log_data)
    elif level == "INFO":
        event_logger.info(f"{event_type}: {message}", extra=log_data)
    elif level == "WARNING":
        event_logger.warning(f"{event_type}: {message}", extra=log_data)
    elif level == "ERROR":
        event_logger.error(f"{event_type}: {message}", extra=log_data)
    elif level == "CRITICAL":
        event_logger.critical(f"{event_type}: {message}", extra=log_data)

def setup_structured_logging():
    """Setup structured logging for JSON output"""
    
    # Create structured log handler
    structured_handler = logging.handlers.RotatingFileHandler(
        'logs/structured.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    structured_handler.setLevel(logging.INFO)
    
    # JSON formatter for structured logs
    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "function": "%(funcName)s", "line": %(lineno)d, "extra": %(extra)s}'
    )
    structured_handler.setFormatter(json_formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(structured_handler)

def cleanup_old_logs(days_to_keep: int = 30):
    """Clean up old log files"""
    import glob
    import os
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    log_files = glob.glob('logs/*.log*')
    
    for log_file in log_files:
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                print(f"Removed old log file: {log_file}")
        except Exception as e:
            print(f"Error removing log file {log_file}: {e}")

if __name__ == "__main__":
    setup_logging()
    print("Logging configuration completed!")
