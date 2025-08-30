"""
Monitoring and logging utilities for the Kiro Streamlit app
"""
import logging
import time
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import streamlit as st
from functools import wraps
import boto3
from botocore.exceptions import ClientError

class KiroLogger:
    """Enhanced logging for the Kiro application"""
    
    def __init__(self, name: str = "kiro_app"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration"""
        if not self.logger.handlers:
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Set logging level
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            self.logger.setLevel(getattr(logging, log_level))
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            simple_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            
            # File handler for detailed logs
            file_handler = logging.FileHandler("logs/app.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            
            # Console handler for simple logs
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            
            # Error file handler
            error_handler = logging.FileHandler("logs/error.log")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.addHandler(error_handler)
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user actions with context"""
        log_data = {
            "action": action,
            "session_id": st.session_state.get("session_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.logger.info(f"USER_ACTION: {json.dumps(log_data)}")
    
    def log_ai_interaction(self, model: str, prompt_length: int, response_length: int, duration: float):
        """Log AI model interactions"""
        log_data = {
            "model": model,
            "prompt_length": prompt_length,
            "response_length": response_length,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"AI_INTERACTION: {json.dumps(log_data)}")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with context"""
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self.logger.error(f"ERROR: {json.dumps(log_data)}", exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        log_data = {
            "operation": operation,
            "duration_seconds": duration,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"PERFORMANCE: {json.dumps(log_data)}")

class MetricsCollector:
    """Collect and send metrics to CloudWatch"""
    
    def __init__(self):
        self.cloudwatch = None
        self.namespace = "KiroApp"
        self.setup_cloudwatch()
    
    def setup_cloudwatch(self):
        """Set up CloudWatch client"""
        try:
            session = boto3.Session()
            self.cloudwatch = session.client('cloudwatch')
        except Exception as e:
            logger.error(f"Failed to setup CloudWatch: {e}")
    
    def put_metric(self, metric_name: str, value: float, unit: str = 'Count', dimensions: Dict[str, str] = None):
        """Send metric to CloudWatch"""
        if not self.cloudwatch:
            return
        
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
            
            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': v} for k, v in dimensions.items()
                ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
        except ClientError as e:
            logger.error(f"Failed to send metric to CloudWatch: {e}")
    
    def record_user_action(self, action: str):
        """Record user action metric"""
        self.put_metric(
            metric_name='UserActions',
            value=1,
            dimensions={'Action': action}
        )
    
    def record_ai_request(self, model: str, success: bool, duration: float):
        """Record AI request metrics"""
        self.put_metric(
            metric_name='AIRequests',
            value=1,
            dimensions={'Model': model, 'Success': str(success)}
        )
        
        self.put_metric(
            metric_name='AIRequestDuration',
            value=duration,
            unit='Seconds',
            dimensions={'Model': model}
        )
    
    def record_error(self, error_type: str):
        """Record error metric"""
        self.put_metric(
            metric_name='Errors',
            value=1,
            dimensions={'ErrorType': error_type}
        )
    
    def record_file_upload(self, file_count: int, total_size: int):
        """Record file upload metrics"""
        self.put_metric(
            metric_name='FileUploads',
            value=file_count
        )
        
        self.put_metric(
            metric_name='UploadSize',
            value=total_size,
            unit='Bytes'
        )

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.start_times = {}
        self.metrics = MetricsCollector()
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.start_times[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str, operation: str = None) -> float:
        """End timing and record duration"""
        if timer_id not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[timer_id]
        del self.start_times[timer_id]
        
        if operation:
            logger.log_performance(operation, duration)
            self.metrics.put_metric(
                metric_name='OperationDuration',
                value=duration,
                unit='Seconds',
                dimensions={'Operation': operation}
            )
        
        return duration
    
    def monitor_memory_usage(self):
        """Monitor memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            self.metrics.put_metric(
                metric_name='MemoryUsage',
                value=memory_info.rss,
                unit='Bytes'
            )
            
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return None
    
    def monitor_cpu_usage(self):
        """Monitor CPU usage"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            
            self.metrics.put_metric(
                metric_name='CPUUsage',
                value=cpu_percent,
                unit='Percent'
            )
            
            return cpu_percent
        except ImportError:
            logger.warning("psutil not available for CPU monitoring")
            return None

def performance_monitor(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            timer_id = monitor.start_timer(operation_name)
            
            try:
                result = func(*args, **kwargs)
                duration = monitor.end_timer(timer_id, operation_name)
                logger.log_performance(operation_name, duration, {"success": True})
                return result
            except Exception as e:
                duration = monitor.end_timer(timer_id, operation_name)
                logger.log_performance(operation_name, duration, {"success": False, "error": str(e)})
                raise
        
        return wrapper
    return decorator

class HealthChecker:
    """Application health monitoring"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
    
    def check_aws_connectivity(self) -> Dict[str, Any]:
        """Check AWS services connectivity"""
        try:
            session = boto3.Session()
            bedrock = session.client('bedrock-runtime')
            bedrock.list_foundation_models()
            
            self.metrics.put_metric('AWSConnectivity', 1, dimensions={'Service': 'Bedrock'})
            return {"status": "healthy", "service": "bedrock"}
        except Exception as e:
            self.metrics.put_metric('AWSConnectivity', 0, dimensions={'Service': 'Bedrock'})
            return {"status": "unhealthy", "service": "bedrock", "error": str(e)}
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            free_percent = (free / total) * 100
            self.metrics.put_metric('DiskSpaceFree', free_percent, unit='Percent')
            
            status = "healthy" if free_percent > 10 else "warning" if free_percent > 5 else "critical"
            
            return {
                "status": status,
                "free_percent": free_percent,
                "free_gb": free / (1024**3),
                "total_gb": total / (1024**3)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        checks = {
            "aws": self.check_aws_connectivity(),
            "disk": self.check_disk_space(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine overall health
        overall_status = "healthy"
        for check in checks.values():
            if isinstance(check, dict) and check.get("status") in ["unhealthy", "critical", "error"]:
                overall_status = "unhealthy"
                break
            elif isinstance(check, dict) and check.get("status") == "warning":
                overall_status = "warning"
        
        checks["overall"] = overall_status
        
        # Send overall health metric
        health_value = 1 if overall_status == "healthy" else 0
        self.metrics.put_metric('ApplicationHealth', health_value)
        
        return checks

# Global instances
logger = KiroLogger()
metrics = MetricsCollector()
performance_monitor_instance = PerformanceMonitor()
health_checker = HealthChecker()

def setup_monitoring():
    """Initialize monitoring for the application"""
    logger.logger.info("Monitoring system initialized")
    
    # Log application startup
    logger.log_user_action("application_startup", {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })
    
    # Send startup metric
    metrics.put_metric('ApplicationStartup', 1)
    
    return {
        "logger": logger,
        "metrics": metrics,
        "performance": performance_monitor_instance,
        "health": health_checker
    }