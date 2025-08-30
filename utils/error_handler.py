"""
Comprehensive error handling for the Kiro Streamlit app
"""
import streamlit as st
import logging
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KiroError(Exception):
    """Base exception class for Kiro application errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class AWSBedrockError(KiroError):
    """Errors related to AWS Bedrock service"""
    pass

class FileSystemError(KiroError):
    """Errors related to file system operations"""
    pass

class JIRAIntegrationError(KiroError):
    """Errors related to JIRA integration"""
    pass

class ValidationError(KiroError):
    """Errors related to input validation"""
    pass

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def handle_aws_bedrock_error(error: Exception) -> str:
        """Handle AWS Bedrock specific errors"""
        if isinstance(error, NoCredentialsError):
            logger.error("AWS credentials not found")
            return "AWS credentials not configured. Please ensure your EC2 instance has the proper IAM role."
        
        elif isinstance(error, ClientError):
            error_code = error.response['Error']['Code']
            error_message = error.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                logger.error(f"AWS access denied: {error_message}")
                return "Access denied to AWS Bedrock. Please check your IAM permissions."
            
            elif error_code == 'ThrottlingException':
                logger.error(f"AWS throttling: {error_message}")
                return "AWS Bedrock is currently throttling requests. Please try again in a moment."
            
            elif error_code == 'ValidationException':
                logger.error(f"AWS validation error: {error_message}")
                return f"Invalid request to AWS Bedrock: {error_message}"
            
            else:
                logger.error(f"AWS Bedrock error {error_code}: {error_message}")
                return f"AWS Bedrock error: {error_message}"
        
        elif isinstance(error, BotoCoreError):
            logger.error(f"AWS connection error: {str(error)}")
            return "Unable to connect to AWS Bedrock. Please check your network connection."
        
        else:
            logger.error(f"Unexpected AWS error: {str(error)}")
            return "An unexpected error occurred with AWS Bedrock. Please try again."
    
    @staticmethod
    def handle_file_system_error(error: Exception, file_path: str = None) -> str:
        """Handle file system related errors"""
        if isinstance(error, PermissionError):
            logger.error(f"Permission denied accessing file: {file_path}")
            return f"Permission denied accessing {'the file' if not file_path else file_path}. Please check file permissions."
        
        elif isinstance(error, FileNotFoundError):
            logger.error(f"File not found: {file_path}")
            return f"File not found: {'Unknown file' if not file_path else file_path}"
        
        elif isinstance(error, IsADirectoryError):
            logger.error(f"Expected file but got directory: {file_path}")
            return f"Expected a file but found a directory: {file_path}"
        
        elif isinstance(error, OSError) and "File name too long" in str(error):
            logger.error(f"File name too long: {file_path}")
            return "File name is too long. Please use shorter file names."
        
        elif isinstance(error, UnicodeDecodeError):
            logger.error(f"Unable to decode file: {file_path}")
            return f"Unable to read file (encoding issue): {'Unknown file' if not file_path else file_path}"
        
        else:
            logger.error(f"File system error: {str(error)}")
            return f"File system error: {str(error)}"
    
    @staticmethod
    def handle_jira_error(error: Exception) -> str:
        """Handle JIRA integration errors"""
        error_str = str(error).lower()
        
        if "authentication" in error_str or "unauthorized" in error_str:
            logger.error("JIRA authentication failed")
            return "JIRA authentication failed. Please check your credentials and permissions."
        
        elif "connection" in error_str or "network" in error_str:
            logger.error("JIRA connection failed")
            return "Unable to connect to JIRA. Please check your network connection and JIRA URL."
        
        elif "project" in error_str and "not found" in error_str:
            logger.error("JIRA project not found")
            return "JIRA project not found. Please verify the project key is correct."
        
        elif "rate limit" in error_str or "too many requests" in error_str:
            logger.error("JIRA rate limit exceeded")
            return "JIRA rate limit exceeded. Please wait a moment before trying again."
        
        else:
            logger.error(f"JIRA integration error: {str(error)}")
            return f"JIRA integration error: {str(error)}"
    
    @staticmethod
    def validate_input(value: Any, validation_type: str, **kwargs) -> bool:
        """Validate user inputs"""
        try:
            if validation_type == "file_size":
                max_size = kwargs.get("max_size", 10 * 1024 * 1024)  # 10MB default
                if hasattr(value, 'size') and value.size > max_size:
                    raise ValidationError(f"File size exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB")
            
            elif validation_type == "file_type":
                allowed_types = kwargs.get("allowed_types", [".txt", ".py", ".js", ".md", ".json"])
                if hasattr(value, 'name'):
                    file_ext = "." + value.name.split(".")[-1].lower()
                    if file_ext not in allowed_types:
                        raise ValidationError(f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_types)}")
            
            elif validation_type == "folder_path":
                import os
                if not os.path.exists(value):
                    raise ValidationError(f"Folder path does not exist: {value}")
                if not os.path.isdir(value):
                    raise ValidationError(f"Path is not a directory: {value}")
            
            elif validation_type == "text_length":
                max_length = kwargs.get("max_length", 10000)
                if len(str(value)) > max_length:
                    raise ValidationError(f"Text exceeds maximum length of {max_length} characters")
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validation error: {str(e)}")

def error_boundary(error_message: str = "An error occurred"):
    """Decorator for handling errors in Streamlit functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KiroError as e:
                st.error(f"🚨 {e.message}")
                if e.details:
                    with st.expander("Error Details"):
                        st.json(e.details)
                logger.error(f"KiroError in {func.__name__}: {e.message}")
            except Exception as e:
                st.error(f"🚨 {error_message}: {str(e)}")
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
        return wrapper
    return decorator

def display_error_with_retry(error_message: str, retry_callback: Callable = None):
    """Display error with optional retry button"""
    st.error(f"🚨 {error_message}")
    
    if retry_callback:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col2:
            if st.button("🔄 Retry", key=f"retry_{hash(error_message)}"):
                retry_callback()

def log_user_action(action: str, details: Dict[str, Any] = None):
    """Log user actions for monitoring and debugging"""
    log_data = {
        "action": action,
        "timestamp": st.session_state.get("current_time"),
        "session_id": st.session_state.get("session_id"),
        "details": details or {}
    }
    logger.info(f"User action: {log_data}")

class HealthChecker:
    """Check system health and dependencies"""
    
    @staticmethod
    def check_aws_connection() -> Dict[str, Any]:
        """Check AWS Bedrock connectivity"""
        try:
            session = boto3.Session()
            bedrock = session.client('bedrock-runtime')
            # Simple check - list available models
            response = bedrock.list_foundation_models()
            return {"status": "healthy", "details": "AWS Bedrock accessible"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    def check_file_system() -> Dict[str, Any]:
        """Check file system access"""
        try:
            import tempfile
            import os
            
            # Test write access
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"test")
                tmp.flush()
                os.fsync(tmp.fileno())
            
            return {"status": "healthy", "details": "File system accessible"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    def run_health_check() -> Dict[str, Any]:
        """Run comprehensive health check"""
        results = {
            "aws": HealthChecker.check_aws_connection(),
            "filesystem": HealthChecker.check_file_system(),
            "overall": "healthy"
        }
        
        # Determine overall health
        if any(check["status"] == "unhealthy" for check in results.values() if isinstance(check, dict)):
            results["overall"] = "unhealthy"
        
        return results