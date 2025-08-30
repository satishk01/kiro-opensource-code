import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError
import streamlit as st

class AIService:
    """AI Service for AWS Bedrock integration with Claude and Nova models"""
    
    def __init__(self):
        self.bedrock_client = None
        self.current_model = None
        self.model_configs = {
            "Claude Sonnet 3.5 v2": {
                "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "Amazon Nova Pro": {
                "model_id": "amazon.nova-pro-v1:0",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
        self.logger = logging.getLogger(__name__)
        
    def initialize_bedrock_client(self) -> bool:
        """Initialize AWS Bedrock client using EC2 IAM role"""
        try:
            # Use default credentials (EC2 IAM role)
            session = boto3.Session()
            self.bedrock_client = session.client(
                service_name='bedrock-runtime',
                region_name='us-east-1'  # Adjust region as needed
            )
            
            # Test connection
            self._test_connection()
            return True
            
        except NoCredentialsError:
            self.logger.error("No AWS credentials found. Ensure EC2 instance has proper IAM role.")
            st.error("? AWS credentials not found. Please ensure EC2 instance has proper IAM role.")
            return False
        except ClientError as e:
            self.logger.error(f"AWS Bedrock client initialization failed: {e}")
            st.error(f"? Failed to connect to AWS Bedrock: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error initializing Bedrock client: {e}")
            st.error(f"? Unexpected error: {e}")
            return False
    
    def _test_connection(self):
        """Test Bedrock connection by listing available models"""
        try:
            # This is a simple test - in production you might want a more specific test
            response = self.bedrock_client.list_foundation_models()
            self.logger.info("Successfully connected to AWS Bedrock")
        except Exception as e:
            raise ClientError(
                error_response={'Error': {'Code': 'ConnectionTest', 'Message': str(e)}},
                operation_name='TestConnection'
            )
    
    def select_model(self, model_name: str) -> bool:
        """Select and validate AI model"""
        if model_name not in self.model_configs:
            st.error(f"? Unknown model: {model_name}")
            return False
        
        if not self.bedrock_client:
            if not self.initialize_bedrock_client():
                return False
        
        self.current_model = model_name
        st.success(f"? Selected model: {model_name}")
        return True
    
    def _prepare_claude_payload(self, prompt: str, system_prompt: str = None) -> Dict:
        """Prepare payload for Claude models"""
        config = self.model_configs[self.current_model]
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "messages": messages
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        return payload
    
    def _prepare_nova_payload(self, prompt: str, system_prompt: str = None) -> Dict:
        """Prepare payload for Nova models"""
        config = self.model_configs[self.current_model]
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
        
        payload = {
            "inputText": full_prompt,
            "textGenerationConfig": {
                "maxTokenCount": config["max_tokens"],
                "temperature": config["temperature"],
                "stopSequences": []
            }
        }
        
        return payload
    
    def _invoke_model(self, payload: Dict) -> str:
        """Invoke the selected model with payload"""
        try:
            config = self.model_configs[self.current_model]
            
            response = self.bedrock_client.invoke_model(
                modelId=config["model_id"],
                body=json.dumps(payload),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            # Parse response based on model type
            if "claude" in config["model_id"].lower():
                return response_body['content'][0]['text']
            elif "nova" in config["model_id"].lower():
                return response_body['results'][0]['outputText']
            else:
                raise ValueError(f"Unknown model type: {config['model_id']}")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ValidationException':
                raise Exception(f"Model validation error: {e}")
            elif error_code == 'ThrottlingException':
                raise Exception("Request throttled. Please try again later.")
            else:
                raise Exception(f"AWS Bedrock error: {e}")
        except Exception as e:
            raise Exception(f"Model invocation failed: {e}")
    
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text using the selected model"""
        if not self.current_model:
            raise Exception("No model selected. Please select a model first.")
        
        if not self.bedrock_client:
            if not self.initialize_bedrock_client():
                raise Exception("Failed to initialize Bedrock client")
        
        try:
            # Prepare payload based on model type
            if "claude" in self.current_model.lower():
                payload = self._prepare_claude_payload(prompt, system_prompt)
            elif "nova" in self.current_model.lower():
                payload = self._prepare_nova_payload(prompt, system_prompt)
            else:
                raise Exception(f"Unsupported model: {self.current_model}")
            
            return self._invoke_model(payload)
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            raise e
    
    def generate_requirements(self, description: str, context: Dict = None) -> str:
        """Generate EARS-format requirements from description"""
        system_prompt = """You are Kiro, an AI assistant and IDE built to assist developers. 
        Generate detailed requirements in EARS format (Easy Approach to Requirements Syntax) based on the provided description.
        
        Format the requirements as:
        1. WHEN [event] THEN [system] SHALL [response]
        2. IF [precondition] THEN [system] SHALL [response]
        
        Include user stories in the format: "As a [role], I want [feature], so that [benefit]"
        
        Be comprehensive and consider edge cases, user experience, and technical constraints."""
        
        context_str = ""
        if context:
            context_str = f"\n\nAdditional context:\n{json.dumps(context, indent=2)}"
        
        prompt = f"Generate requirements for: {description}{context_str}"
        
        return self.generate_text(prompt, system_prompt)
    
    def create_design(self, requirements: str, codebase: Dict = None) -> str:
        """Create design document from requirements"""
        system_prompt = """You are Kiro, an AI assistant and IDE built to assist developers.
        Create a comprehensive design document based on the provided requirements.
        
        Include these sections:
        - Overview
        - Architecture (with Mermaid diagrams if applicable)
        - Components and Interfaces
        - Data Models
        - Error Handling
        - Testing Strategy
        
        Be technical and specific, considering best practices and scalability."""
        
        codebase_str = ""
        if codebase:
            codebase_str = f"\n\nExisting codebase context:\n{json.dumps(codebase, indent=2)}"
        
        prompt = f"Create design document for these requirements:\n{requirements}{codebase_str}"
        
        return self.generate_text(prompt, system_prompt)
    
    def generate_tasks(self, design: str) -> List[Dict]:
        """Generate implementation tasks from design"""
        system_prompt = """You are Kiro, an AI assistant and IDE built to assist developers.
        Convert the design into actionable implementation tasks.
        
        Format as a JSON array of tasks with:
        - title: Task title
        - description: Detailed description
        - requirements_refs: Array of requirement references
        - estimated_hours: Estimated completion time
        - dependencies: Array of dependent task titles
        
        Focus only on coding tasks that can be executed by a developer."""
        
        prompt = f"Generate implementation tasks for this design:\n{design}"
        
        response = self.generate_text(prompt, system_prompt)
        
        try:
            # Try to parse as JSON, fallback to text if needed
            return json.loads(response)
        except json.JSONDecodeError:
            # Return as simple text-based tasks if JSON parsing fails
            return [{"title": "Implementation Tasks", "description": response}]
    
    def analyze_codebase(self, files: Dict) -> Dict:
        """Analyze codebase structure and patterns"""
        system_prompt = """You are Kiro, an AI assistant and IDE built to assist developers.
        Analyze the provided codebase and return insights about:
        - Architecture patterns
        - Technology stack
        - Data models and relationships
        - Potential improvements
        - Security considerations
        
        Provide actionable insights for development planning."""
        
        # Limit file content for analysis to avoid token limits
        limited_files = {}
        for path, content in files.items():
            if len(content) > 2000:  # Truncate large files
                limited_files[path] = content[:2000] + "... [truncated]"
            else:
                limited_files[path] = content
        
        prompt = f"Analyze this codebase:\n{json.dumps(limited_files, indent=2)}"
        
        response = self.generate_text(prompt, system_prompt)
        
        return {
            "analysis": response,
            "file_count": len(files),
            "total_size": sum(len(content) for content in files.values()),
            "languages": self._detect_languages(files)
        }
    
    def _detect_languages(self, files: Dict) -> List[str]:
        """Detect programming languages from file extensions"""
        extensions = set()
        for file_path in files.keys():
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                extensions.add(ext)
        
        # Map extensions to languages
        lang_map = {
            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript',
            'java': 'Java', 'cpp': 'C++', 'c': 'C', 'cs': 'C#',
            'go': 'Go', 'rs': 'Rust', 'php': 'PHP', 'rb': 'Ruby',
            'html': 'HTML', 'css': 'CSS', 'sql': 'SQL', 'json': 'JSON',
            'yaml': 'YAML', 'yml': 'YAML', 'xml': 'XML', 'md': 'Markdown'
        }
        
        return [lang_map.get(ext, ext.upper()) for ext in extensions if ext in lang_map]