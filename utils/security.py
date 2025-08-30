"""
Security utilities for the Kiro Streamlit app
"""
import os
import re
import hashlib
import secrets
from typing import List, Dict, Any, Optional
import streamlit as st
from pathlib import Path
import mimetypes

class SecurityValidator:
    """Security validation and protection utilities"""
    
    # Allowed file extensions for upload
    ALLOWED_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
        '.xml', '.html', '.css', '.scss', '.sass', '.sql', '.sh', '.bat', '.ps1',
        '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs',
        '.swift', '.kt', '.scala', '.clj', '.hs', '.ml', '.r', '.m', '.pl', '.lua'
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Maximum total upload size (100MB)
    MAX_TOTAL_SIZE = 100 * 1024 * 1024
    
    # Dangerous file patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'vbscript:',                 # VBScript URLs
        r'on\w+\s*=',                 # Event handlers
        r'eval\s*\(',                 # eval() calls
        r'exec\s*\(',                 # exec() calls
        r'import\s+os',               # OS imports (Python)
        r'subprocess\.',              # Subprocess calls
        r'system\s*\(',               # System calls
        r'shell_exec\s*\(',           # Shell execution (PHP)
        r'passthru\s*\(',             # Passthru (PHP)
    ]
    
    @classmethod
    def validate_file_upload(cls, uploaded_file) -> Dict[str, Any]:
        """Validate uploaded file for security"""
        if not uploaded_file:
            return {"valid": False, "error": "No file provided"}
        
        # Check file size
        if hasattr(uploaded_file, 'size') and uploaded_file.size > cls.MAX_FILE_SIZE:
            return {
                "valid": False, 
                "error": f"File size ({uploaded_file.size / (1024*1024):.1f}MB) exceeds maximum allowed size ({cls.MAX_FILE_SIZE / (1024*1024):.1f}MB)"
            }
        
        # Check file extension
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"File type '{file_ext}' not allowed. Allowed types: {', '.join(sorted(cls.ALLOWED_EXTENSIONS))}"
            }
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if mime_type and not mime_type.startswith(('text/', 'application/json', 'application/xml')):
            return {
                "valid": False,
                "error": f"MIME type '{mime_type}' not allowed. Only text files are permitted."
            }
        
        return {"valid": True, "error": None}
    
    @classmethod
    def validate_folder_path(cls, folder_path: str) -> Dict[str, Any]:
        """Validate folder path for security"""
        if not folder_path:
            return {"valid": False, "error": "No folder path provided"}
        
        # Normalize path to prevent directory traversal
        try:
            normalized_path = os.path.normpath(folder_path)
            resolved_path = os.path.realpath(normalized_path)
        except Exception as e:
            return {"valid": False, "error": f"Invalid path: {str(e)}"}
        
        # Check for directory traversal attempts
        if '..' in normalized_path or normalized_path.startswith('/'):
            return {"valid": False, "error": "Directory traversal not allowed"}
        
        # Check if path exists and is a directory
        if not os.path.exists(resolved_path):
            return {"valid": False, "error": f"Path does not exist: {folder_path}"}
        
        if not os.path.isdir(resolved_path):
            return {"valid": False, "error": f"Path is not a directory: {folder_path}"}
        
        # Check read permissions
        if not os.access(resolved_path, os.R_OK):
            return {"valid": False, "error": f"No read permission for directory: {folder_path}"}
        
        return {"valid": True, "error": None, "resolved_path": resolved_path}
    
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(user_input, str):
            return str(user_input)
        
        # Remove null bytes
        sanitized = user_input.replace('\x00', '')
        
        # Limit length
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        
        # Remove potentially dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '[REMOVED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def validate_file_content(cls, content: str, filename: str = "") -> Dict[str, Any]:
        """Validate file content for security issues"""
        if not content:
            return {"valid": True, "warnings": []}
        
        warnings = []
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Potentially dangerous pattern detected: {pattern}")
        
        # Check for suspicious imports/includes
        suspicious_imports = [
            'import subprocess', 'import os', 'import sys', 'from os import',
            '#include <windows.h>', '#include <unistd.h>', 'require("child_process")',
            'eval(', 'exec(', 'system(', 'shell_exec(', 'passthru('
        ]
        
        for imp in suspicious_imports:
            if imp.lower() in content.lower():
                warnings.append(f"Suspicious import/call detected: {imp}")
        
        # Check file size
        if len(content.encode('utf-8')) > cls.MAX_FILE_SIZE:
            return {
                "valid": False,
                "error": f"File content too large ({len(content.encode('utf-8')) / (1024*1024):.1f}MB)"
            }
        
        return {"valid": True, "warnings": warnings}
    
    @classmethod
    def generate_session_id(cls) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def hash_sensitive_data(cls, data: str) -> str:
        """Hash sensitive data for logging"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class SessionManager:
    """Manage secure sessions"""
    
    @staticmethod
    def initialize_session():
        """Initialize secure session state"""
        if "session_id" not in st.session_state:
            st.session_state.session_id = SecurityValidator.generate_session_id()
        
        if "security_context" not in st.session_state:
            st.session_state.security_context = {
                "upload_count": 0,
                "total_upload_size": 0,
                "last_upload_time": None,
                "rate_limit_violations": 0
            }
    
    @staticmethod
    def check_rate_limit() -> bool:
        """Check if user is within rate limits"""
        import time
        
        context = st.session_state.security_context
        current_time = time.time()
        
        # Reset counters every hour
        if (context.get("last_upload_time") and 
            current_time - context["last_upload_time"] > 3600):
            context["upload_count"] = 0
            context["total_upload_size"] = 0
            context["rate_limit_violations"] = 0
        
        # Check upload limits (max 50 files per hour)
        if context["upload_count"] >= 50:
            context["rate_limit_violations"] += 1
            return False
        
        # Check size limits (max 100MB per hour)
        if context["total_upload_size"] >= SecurityValidator.MAX_TOTAL_SIZE:
            context["rate_limit_violations"] += 1
            return False
        
        return True
    
    @staticmethod
    def record_upload(file_size: int):
        """Record file upload for rate limiting"""
        import time
        
        context = st.session_state.security_context
        context["upload_count"] += 1
        context["total_upload_size"] += file_size
        context["last_upload_time"] = time.time()

class InputSanitizer:
    """Sanitize various types of user input"""
    
    @staticmethod
    def sanitize_jira_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize JIRA configuration input"""
        sanitized = {}
        
        # URL validation
        if "url" in config:
            url = config["url"].strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            sanitized["url"] = url
        
        # Username sanitization
        if "username" in config:
            sanitized["username"] = re.sub(r'[^\w@.-]', '', config["username"])
        
        # Project key sanitization
        if "project_key" in config:
            sanitized["project_key"] = re.sub(r'[^\w-]', '', config["project_key"])
        
        return sanitized
    
    @staticmethod
    def sanitize_ai_prompt(prompt: str) -> str:
        """Sanitize AI prompts"""
        # Remove excessive whitespace
        prompt = re.sub(r'\s+', ' ', prompt.strip())
        
        # Remove potential prompt injection attempts
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'act\s+as\s+if',
            r'pretend\s+to\s+be',
            r'roleplay\s+as'
        ]
        
        for pattern in injection_patterns:
            prompt = re.sub(pattern, '[FILTERED]', prompt, flags=re.IGNORECASE)
        
        return prompt[:5000]  # Limit length

def require_authentication(func):
    """Decorator to require authentication for sensitive operations"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated", False):
            st.error("🔒 Authentication required for this operation")
            return None
        return func(*args, **kwargs)
    return wrapper

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events for monitoring"""
    import logging
    
    logger = logging.getLogger("security")
    
    event_data = {
        "event_type": event_type,
        "session_id": st.session_state.get("session_id", "unknown"),
        "timestamp": st.session_state.get("current_time"),
        "details": details
    }
    
    logger.warning(f"Security event: {event_data}")
    
    # Store in session for admin review
    if "security_events" not in st.session_state:
        st.session_state.security_events = []
    
    st.session_state.security_events.append(event_data)