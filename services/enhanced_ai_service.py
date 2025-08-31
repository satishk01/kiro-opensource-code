import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError
import streamlit as st

class EnhancedAIService:
    """Enhanced AI Service for AWS Bedrock integration with coding standards support"""
    
    def __init__(self):
        self.bedrock_client = None
        self.bedrock_control_client = None
        self.current_model = None
        self.model_configs = {
            "Claude Sonnet 3.5 v2": {
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
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
            
            # Initialize both clients - bedrock for listing models, bedrock-runtime for inference
            self.bedrock_client = session.client(
                service_name='bedrock-runtime',
                region_name='us-east-1'  # Adjust region as needed
            )
            
            self.bedrock_control_client = session.client(
                service_name='bedrock',
                region_name='us-east-1'
            )
            
            # Test connection
            self._test_connection()
            return True
            
        except NoCredentialsError:
            self.logger.error("No AWS credentials found. Ensure EC2 instance has proper IAM role.")
            st.error("🚨 AWS credentials not found. Please ensure EC2 instance has proper IAM role.")
            return False
        except ClientError as e:
            self.logger.error(f"AWS Bedrock client initialization failed: {e}")
            st.error(f"🚨 Failed to connect to AWS Bedrock: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error initializing Bedrock client: {e}")
            st.error(f"🚨 Unexpected error: {e}")
            return False
    
    def _test_connection(self):
        """Test Bedrock connection"""
        try:
            # Try to list models first (requires bedrock:ListFoundationModels permission)
            try:
                response = self.bedrock_control_client.list_foundation_models()
                self.logger.info("Successfully connected to AWS Bedrock")
                
                # Verify our target models are available
                available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
                
                # Check if our configured models are available
                for model_name, config in self.model_configs.items():
                    model_id = config['model_id']
                    if model_id not in available_models:
                        self.logger.warning(f"Model {model_id} not found in available models")
                        
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDeniedException':
                    # If we can't list models, just log a warning and continue
                    self.logger.warning("Cannot list foundation models (permission denied), but clients are initialized")
                else:
                    raise e
            
        except Exception as e:
            raise ClientError(
                error_response={'Error': {'Code': 'ConnectionTest', 'Message': str(e)}},
                operation_name='TestConnection'
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.bedrock_control_client:
            if not self.initialize_bedrock_client():
                return []
        
        try:
            response = self.bedrock_control_client.list_foundation_models()
            available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
            
            # Filter to only our configured models that are available
            configured_available = []
            for model_name, config in self.model_configs.items():
                if config['model_id'] in available_models:
                    configured_available.append(model_name)
            
            return configured_available
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return list(self.model_configs.keys())  # Return all configured models as fallback
    
    def select_model(self, model_name: str) -> bool:
        """Select and validate AI model"""
        if model_name not in self.model_configs:
            st.error(f"🚨 Unknown model: {model_name}")
            return False
        
        if not self.bedrock_client:
            if not self.initialize_bedrock_client():
                return False
        
        self.current_model = model_name
        st.success(f"✅ Selected model: {model_name}")
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
        
        # Combine system prompt and user prompt for Nova
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": full_prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": config["max_tokens"],
                "temperature": config["temperature"]
            }
        }
        
        return payload
    
    def _make_bedrock_request(self, prompt: str, system_prompt: str = None) -> str:
        """Make request to Bedrock API"""
        if not self.current_model:
            raise Exception("No model selected")
        
        if not self.bedrock_client:
            raise Exception("Bedrock client not initialized")
        
        config = self.model_configs[self.current_model]
        model_id = config["model_id"]
        
        try:
            # Prepare payload based on model type
            if "claude" in model_id.lower():
                payload = self._prepare_claude_payload(prompt, system_prompt)
            elif "nova" in model_id.lower():
                payload = self._prepare_nova_payload(prompt, system_prompt)
            else:
                raise Exception(f"Unsupported model type: {model_id}")
            
            # Make the request
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content based on model type
            if "claude" in model_id.lower():
                return response_body['content'][0]['text']
            elif "nova" in model_id.lower():
                return response_body['output']['message']['content'][0]['text']
            else:
                raise Exception(f"Unknown response format for model: {model_id}")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.logger.error(f"Bedrock API error: {error_code} - {error_message}")
            raise Exception(f"AI service error: {error_message}")
        except Exception as e:
            self.logger.error(f"Unexpected error in Bedrock request: {e}")
            raise Exception(f"Unexpected AI service error: {str(e)}")
    
    def analyze_codebase_with_standards(self, files: Dict[str, str], coding_standards: Dict[str, List[str]]) -> Dict[str, str]:
        """Enhanced codebase analysis with coding standards integration"""
        
        # Prepare coding standards context
        standards_context = self._format_coding_standards(coding_standards)
        
        # Create file summary for analysis
        file_summary = self._create_file_summary(files)
        
        system_prompt = f"""You are an expert software architect and code reviewer. Analyze the provided codebase with the following coding standards in mind:

{standards_context}

Provide a comprehensive analysis that includes:
1. Overall architecture and structure assessment
2. Code quality evaluation against the provided standards
3. Technology stack identification
4. Potential improvements and recommendations
5. Compliance with coding standards
6. Security considerations
7. Performance implications

Be specific and actionable in your recommendations."""

        user_prompt = f"""Please analyze this codebase:

## Project Structure
{file_summary}

## Key Files Content (sample)
{self._get_key_files_content(files)}

Provide a detailed analysis considering the coding standards and best practices."""

        try:
            analysis_result = self._make_bedrock_request(user_prompt, system_prompt)
            
            # Generate standards compliance report
            compliance_report = self._generate_compliance_report(files, coding_standards)
            
            return {
                "analysis": analysis_result,
                "standards_compliance": compliance_report,
                "files_analyzed": len(files),
                "standards_applied": len(coding_standards)
            }
            
        except Exception as e:
            self.logger.error(f"Error in codebase analysis: {e}")
            raise Exception(f"Failed to analyze codebase: {str(e)}")
    
    def generate_requirements_with_standards(self, feature_description: str, coding_standards: Dict[str, List[str]], codebase_context: Optional[Dict[str, str]] = None) -> str:
        """Generate requirements with coding standards integration"""
        
        standards_context = self._format_coding_standards(coding_standards)
        codebase_info = ""
        
        if codebase_context:
            codebase_info = f"""
## Current Codebase Context
{self._create_file_summary(codebase_context)}
"""

        system_prompt = f"""You are an expert business analyst and software architect. Generate comprehensive requirements using EARS format (Easy Approach to Requirements Syntax) while considering the following coding standards:

{standards_context}

Create requirements that:
1. Follow EARS format (WHEN/IF...THEN...SHALL)
2. Are testable and measurable
3. Consider the existing codebase architecture
4. Align with the established coding standards
5. Include non-functional requirements (performance, security, maintainability)
6. Address integration points with existing systems"""

        user_prompt = f"""Generate detailed requirements for this feature:

## Feature Description
{feature_description}

{codebase_info}

Create a comprehensive requirements document with:
1. User stories in the format "As a [role], I want [feature], so that [benefit]"
2. Detailed acceptance criteria using EARS format
3. Non-functional requirements considering the coding standards
4. Integration requirements with existing codebase
5. Quality and compliance requirements"""

        try:
            return self._make_bedrock_request(user_prompt, system_prompt)
        except Exception as e:
            self.logger.error(f"Error generating requirements: {e}")
            raise Exception(f"Failed to generate requirements: {str(e)}")
    
    def create_design_with_standards(self, requirements: str, coding_standards: Dict[str, List[str]], codebase_context: Optional[Dict[str, str]] = None) -> str:
        """Create design document with coding standards integration"""
        
        standards_context = self._format_coding_standards(coding_standards)
        codebase_info = ""
        
        if codebase_context:
            codebase_info = f"""
## Current Codebase Architecture
{self._analyze_current_architecture(codebase_context)}
"""

        system_prompt = f"""You are an expert software architect. Create a comprehensive design document that adheres to the following coding standards:

{standards_context}

The design should:
1. Follow established architectural patterns
2. Comply with coding standards and best practices
3. Integrate seamlessly with existing codebase
4. Consider scalability, maintainability, and performance
5. Include detailed component specifications
6. Address security and error handling
7. Provide clear implementation guidance"""

        user_prompt = f"""Create a detailed design document based on these requirements:

{requirements}

{codebase_info}

Include the following sections:
1. **Overview** - High-level design summary
2. **Architecture** - System architecture and patterns
3. **Components and Interfaces** - Detailed component design
4. **Data Models** - Data structures and relationships
5. **API Design** - Interface specifications
6. **Security Considerations** - Security measures and protocols
7. **Error Handling** - Error management strategy
8. **Testing Strategy** - Testing approach and considerations
9. **Implementation Guidelines** - Coding standards compliance

Ensure the design aligns with the coding standards and integrates well with the existing codebase."""

        try:
            return self._make_bedrock_request(user_prompt, system_prompt)
        except Exception as e:
            self.logger.error(f"Error creating design: {e}")
            raise Exception(f"Failed to create design: {str(e)}")
    
    def _format_coding_standards(self, coding_standards: Dict[str, List[str]]) -> str:
        """Format coding standards for AI context"""
        if not coding_standards:
            return "No specific coding standards provided."
        
        formatted_standards = "## Coding Standards\n\n"
        
        for category, standards in coding_standards.items():
            formatted_standards += f"### {category}\n"
            if isinstance(standards, list):
                for standard in standards:
                    formatted_standards += f"- {standard}\n"
            else:
                formatted_standards += f"- {standards}\n"
            formatted_standards += "\n"
        
        return formatted_standards
    
    def _create_file_summary(self, files: Dict[str, str]) -> str:
        """Create a summary of the file structure"""
        summary = []
        
        # Group files by directory
        directories = {}
        for file_path in files.keys():
            parts = file_path.split('/')
            if len(parts) > 1:
                dir_name = parts[0]
                if dir_name not in directories:
                    directories[dir_name] = []
                directories[dir_name].append(file_path)
            else:
                if 'root' not in directories:
                    directories['root'] = []
                directories['root'].append(file_path)
        
        for dir_name, file_list in directories.items():
            summary.append(f"**{dir_name}/**: {len(file_list)} files")
            # Show first few files as examples
            for file_path in file_list[:3]:
                summary.append(f"  - {file_path}")
            if len(file_list) > 3:
                summary.append(f"  - ... and {len(file_list) - 3} more files")
        
        return "\n".join(summary)
    
    def _get_key_files_content(self, files: Dict[str, str], max_files: int = 5) -> str:
        """Get content of key files for analysis"""
        # Prioritize important files
        priority_patterns = [
            'package.json', 'requirements.txt', 'pom.xml', 'Gemfile',
            'main.py', 'app.py', 'index.js', 'App.js', 'main.java',
            'README.md', 'config', 'settings'
        ]
        
        key_files = []
        
        # First, add files matching priority patterns
        for pattern in priority_patterns:
            for file_path, content in files.items():
                if pattern.lower() in file_path.lower() and len(key_files) < max_files:
                    key_files.append((file_path, content[:1000]))  # Limit content length
        
        # Fill remaining slots with other files
        for file_path, content in files.items():
            if len(key_files) >= max_files:
                break
            if not any(file_path == kf[0] for kf in key_files):
                key_files.append((file_path, content[:1000]))
        
        result = []
        for file_path, content in key_files:
            result.append(f"### {file_path}\n```\n{content}\n```\n")
        
        return "\n".join(result)
    
    def _analyze_current_architecture(self, files: Dict[str, str]) -> str:
        """Analyze current codebase architecture"""
        analysis = []
        
        # Detect frameworks and technologies
        technologies = []
        if 'package.json' in files:
            technologies.append("Node.js/JavaScript project")
        if any('requirements.txt' in f or '.py' in f for f in files.keys()):
            technologies.append("Python project")
        if any('.java' in f for f in files.keys()):
            technologies.append("Java project")
        
        if technologies:
            analysis.append(f"**Technologies**: {', '.join(technologies)}")
        
        # Analyze directory structure
        directories = set()
        for file_path in files.keys():
            parts = file_path.split('/')
            if len(parts) > 1:
                directories.add(parts[0])
        
        if directories:
            analysis.append(f"**Main Directories**: {', '.join(sorted(directories))}")
        
        return "\n".join(analysis)
    
    def _generate_compliance_report(self, files: Dict[str, str], coding_standards: Dict[str, List[str]]) -> str:
        """Generate a compliance report against coding standards"""
        if not coding_standards:
            return "No coding standards defined for compliance checking."
        
        report = ["## Coding Standards Compliance Report\n"]
        
        for category, standards in coding_standards.items():
            report.append(f"### {category}")
            
            # Simple compliance checks based on file patterns
            if category.lower() == "linting":
                has_eslint = any('.eslintrc' in f for f in files.keys())
                has_pylint = any('pylint' in f or '.pylintrc' in f for f in files.keys())
                
                if has_eslint:
                    report.append("✅ ESLint configuration found")
                if has_pylint:
                    report.append("✅ Pylint configuration found")
                if not has_eslint and not has_pylint:
                    report.append("⚠️ No linting configuration detected")
            
            elif category.lower() == "testing":
                has_tests = any('test' in f.lower() for f in files.keys())
                if has_tests:
                    report.append("✅ Test files found")
                else:
                    report.append("⚠️ No test files detected")
            
            elif category.lower() == "documentation":
                has_readme = 'README.md' in files or 'readme.md' in files
                if has_readme:
                    report.append("✅ README documentation found")
                else:
                    report.append("⚠️ No README documentation found")
            
            report.append("")
        
        return "\n".join(report)
    
    # Legacy methods for backward compatibility
    def analyze_codebase(self, files: Dict[str, str]) -> Dict[str, str]:
        """Legacy method - analyze codebase without standards"""
        return self.analyze_codebase_with_standards(files, {})
    
    def generate_requirements(self, feature_description: str, codebase_context: Optional[Dict[str, str]] = None) -> str:
        """Legacy method - generate requirements without standards"""
        return self.generate_requirements_with_standards(feature_description, {}, codebase_context)
    
    def create_design(self, requirements: str, codebase_context: Optional[Dict[str, str]] = None) -> str:
        """Legacy method - create design without standards"""
        return self.create_design_with_standards(requirements, {}, codebase_context)