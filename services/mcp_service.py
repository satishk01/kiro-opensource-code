"""
MCP Service for interacting with Model Context Protocol servers
"""
import json
import subprocess
import logging
from typing import Dict, List, Optional, Any
import tempfile
import os

class MCPService:
    """Service for interacting with MCP servers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.aws_diagram_server = None
        
    def initialize_aws_diagram_server(self) -> bool:
        """Initialize connection to AWS Diagram MCP server"""
        try:
            # Test if uvx and the server are available
            result = subprocess.run(
                ["uvx", "--help"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                self.logger.error("uvx not found. Please install uv and uvx first.")
                return False
                
            self.logger.info("AWS Diagram MCP server initialized successfully")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout initializing AWS Diagram MCP server")
            return False
        except FileNotFoundError:
            self.logger.error("uvx command not found. Please install uv and uvx first.")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS Diagram MCP server: {e}")
            return False
    
    def generate_aws_architecture_diagram(self, 
                                        components: List[str], 
                                        connections: List[Dict],
                                        title: str = "AWS Architecture") -> Optional[str]:
        """Generate AWS architecture diagram using MCP server with enhanced icons"""
        try:
            # Prepare the enhanced diagram specification with icon support
            diagram_spec = {
                "title": title,
                "components": self._enhance_components_with_icons(components),
                "connections": connections,
                "layout": "hierarchical",
                "style": "aws-icons",
                "format": "mermaid",
                "theme": "aws"
            }
            
            # Create temporary file for input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(diagram_spec, f, indent=2)
                input_file = f.name
            
            try:
                # Call the MCP server through uvx with enhanced options
                result = subprocess.run([
                    "uvx", 
                    "awslabs.aws-diagram-mcp-server",
                    "--input", input_file,
                    "--format", "mermaid",
                    "--style", "icons",
                    "--theme", "aws"
                ], capture_output=True, text=True, timeout=45)
                
                if result.returncode == 0:
                    diagram_output = result.stdout.strip()
                    # Post-process to ensure icons and styling
                    return self._enhance_mermaid_with_aws_styling(diagram_output)
                else:
                    self.logger.error(f"AWS diagram generation failed: {result.stderr}")
                    return self._generate_fallback_aws_diagram_with_icons(components, connections)
            finally:
                # Clean up temporary file
                os.unlink(input_file)
                
        except Exception as e:
            self.logger.error(f"Error generating AWS architecture diagram: {e}")
            return self._generate_fallback_aws_diagram_with_icons(components, connections)
    
    def generate_aws_sequence_diagram(self, 
                                    interactions: List[Dict],
                                    title: str = "AWS Sequence Diagram") -> Optional[str]:
        """Generate AWS sequence diagram"""
        try:
            # Prepare sequence diagram specification
            sequence_spec = {
                "title": title,
                "interactions": interactions,
                "type": "sequence"
            }
            
            # Create temporary file for input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(sequence_spec, f, indent=2)
                input_file = f.name
            
            try:
                # Call the MCP server
                result = subprocess.run([
                    "uvx", 
                    "awslabs.aws-diagram-mcp-server",
                    "--input", input_file,
                    "--format", "mermaid",
                    "--type", "sequence"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    self.logger.error(f"AWS sequence diagram generation failed: {result.stderr}")
                    return self._generate_fallback_sequence_diagram(interactions)
                    
            finally:
                os.unlink(input_file)
                
        except Exception as e:
            self.logger.error(f"Error generating AWS sequence diagram: {e}")
            return self._generate_fallback_sequence_diagram(interactions)
    
    def extract_aws_components_from_codebase(self, codebase: Dict) -> List[str]:
        """Extract AWS components mentioned in codebase"""
        aws_services = set()
        
        # Common AWS service patterns
        aws_patterns = {
            'ec2': ['EC2', 'Instance', 'VPC', 'Security Group'],
            's3': ['S3', 'Bucket', 'Object Storage'],
            'rds': ['RDS', 'Database', 'MySQL', 'PostgreSQL'],
            'lambda': ['Lambda', 'Function', 'Serverless'],
            'api_gateway': ['API Gateway', 'REST API', 'HTTP API'],
            'cloudfront': ['CloudFront', 'CDN', 'Distribution'],
            'route53': ['Route53', 'DNS', 'Domain'],
            'iam': ['IAM', 'Role', 'Policy', 'User'],
            'cloudwatch': ['CloudWatch', 'Logs', 'Metrics'],
            'sns': ['SNS', 'Notification', 'Topic'],
            'sqs': ['SQS', 'Queue', 'Message'],
            'dynamodb': ['DynamoDB', 'NoSQL', 'Table'],
            'elasticache': ['ElastiCache', 'Redis', 'Memcached'],
            'elb': ['Load Balancer', 'ALB', 'NLB', 'ELB'],
            'ecs': ['ECS', 'Container', 'Fargate'],
            'eks': ['EKS', 'Kubernetes', 'K8s']
        }
        
        # Search through codebase for AWS service references
        for file_path, content in codebase.items():
            content_lower = content.lower()
            
            for service, keywords in aws_patterns.items():
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        aws_services.add(keyword)
        
        return list(aws_services)
    
    def extract_connections_from_codebase(self, codebase: Dict, components: List[str]) -> List[Dict]:
        """Extract connections between AWS components from codebase"""
        connections = []
        
        # Simple heuristic: if two components are mentioned in the same file,
        # they likely have a connection
        for file_path, content in codebase.items():
            content_lower = content.lower()
            mentioned_components = []
            
            for component in components:
                if component.lower() in content_lower:
                    mentioned_components.append(component)
            
            # Create connections between components mentioned together
            for i, comp1 in enumerate(mentioned_components):
                for comp2 in mentioned_components[i+1:]:
                    connection = {
                        "from": comp1,
                        "to": comp2,
                        "type": "uses",
                        "description": f"Connection inferred from {file_path}"
                    }
                    if connection not in connections:
                        connections.append(connection)
        
        return connections
    
    def _enhance_components_with_icons(self, components: List[str]) -> List[Dict]:
        """Enhance AWS components with draw.io-style icon information"""
        aws_icons = {
            'EC2': '🖥️',
            'S3': '📁',
            'RDS': '🗄️',
            'Lambda': '⚡',
            'API Gateway': '🚪',
            'CloudFront': '📡',
            'Route 53': '🌍',
            'ELB': '⚖️',
            'ALB': '⚖️',
            'NLB': '⚖️',
            'VPC': '🏢',
            'IAM': '👤',
            'CloudWatch': '📈',
            'SNS': '📢',
            'SQS': '📬',
            'DynamoDB': '⚡',
            'ElastiCache': '🚀',
            'ECS': '🐳',
            'EKS': '☸️',
            'Aurora': '🌟',
            'Cognito': '🔑',
            'KMS': '🔐',
            'WAF': '🛡️',
            'CloudTrail': '🔍',
            'X-Ray': '🔬',
            'EventBridge': '🌉',
            'Secrets Manager': '🔒',
            'EFS': '📂',
            'Redshift': '📊',
            'Kinesis': '🌊',
            'Step Functions': '🔄',
            'CodePipeline': '🚀',
            'CodeBuild': '🔨',
            'CodeDeploy': '📦'
        }
        
        enhanced_components = []
        for component in components:
            icon = aws_icons.get(component, '☁️')
            enhanced_components.append({
                'name': component,
                'icon': icon,
                'type': 'aws-service',
                'label': f"{icon} {component}",
                'category': self._get_aws_service_category(component)
            })
        
        return enhanced_components
    
    def _get_aws_service_category(self, service: str) -> str:
        """Get AWS service category for better organization"""
        categories = {
            'compute': ['EC2', 'Lambda', 'ECS', 'EKS', 'Fargate'],
            'storage': ['S3', 'EFS', 'EBS'],
            'database': ['RDS', 'DynamoDB', 'Aurora', 'ElastiCache', 'Redshift'],
            'network': ['VPC', 'CloudFront', 'Route 53', 'ALB', 'NLB', 'ELB', 'API Gateway', 'WAF'],
            'security': ['IAM', 'Cognito', 'KMS', 'Secrets Manager'],
            'monitoring': ['CloudWatch', 'CloudTrail', 'X-Ray'],
            'integration': ['SQS', 'SNS', 'EventBridge', 'Kinesis', 'Step Functions'],
            'devops': ['CodePipeline', 'CodeBuild', 'CodeDeploy']
        }
        
        for category, services in categories.items():
            if service in services:
                return category
        return 'other'
    
    def _enhance_mermaid_with_aws_styling(self, diagram: str) -> str:
        """Enhance Mermaid diagram with AWS styling and icons"""
        if not diagram or not diagram.strip():
            return diagram
        
        # Add AWS color scheme and styling
        aws_styling = """
    %% AWS Official Color Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsSecurity fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsMonitoring fill:#759C3E,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsIntegration fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsAnalytics fill:#8C4FFF,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsDevOps fill:#FF6B6B,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold"""
        
        # Add styling to the diagram if not already present
        if "classDef aws" not in diagram:
            diagram += "\n" + aws_styling
        
        return diagram
    
    def _generate_fallback_aws_diagram(self, components: List[str], connections: List[Dict]) -> str:
        """Generate fallback AWS architecture diagram when MCP server fails"""
        return self._generate_fallback_aws_diagram_with_icons(components, connections)
    
    def _generate_fallback_aws_diagram_with_icons(self, components: List[str], connections: List[Dict]) -> str:
        """Generate fallback AWS diagram with draw.io-style icons when MCP server fails"""
        aws_icons = {
            'EC2': '🖥️', 'S3': '📁', 'RDS': '🗄️', 'Lambda': '⚡', 'API Gateway': '🚪',
            'CloudFront': '📡', 'Route 53': '🌍', 'ALB': '⚖️', 'VPC': '🏢', 'IAM': '👤',
            'CloudWatch': '📈', 'SNS': '📢', 'SQS': '📬', 'DynamoDB': '⚡', 'ElastiCache': '🚀',
            'ECS': '🐳', 'EKS': '☸️', 'Aurora': '🌟', 'Cognito': '🔑', 'KMS': '🔐',
            'WAF': '🛡️', 'CloudTrail': '🔍', 'X-Ray': '🔬', 'EventBridge': '🌉',
            'Secrets Manager': '🔒', 'EFS': '📂'
        }
        
        diagram = "graph TB\n"
        diagram += "    %% AWS Architecture with Draw.io Style Icons - Fallback\n\n"
        
        # Add components with icons
        for i, component in enumerate(components):
            icon = aws_icons.get(component, '☁️')
            safe_name = component.replace(" ", "_").replace("-", "_")
            diagram += f"    {safe_name}[\"{icon} {component}<br/>AWS Service\"]\n"
        
        diagram += "\n"
        
        # Add connections
        for conn in connections:
            from_safe = conn["from"].replace(" ", "_").replace("-", "_")
            to_safe = conn["to"].replace(" ", "_").replace("-", "_")
            diagram += f"    {from_safe} --> {to_safe}\n"
        
        # Add AWS styling
        diagram += """
    %% AWS Official Color Styling
    classDef awsService fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    class """ + ",".join([comp.replace(" ", "_").replace("-", "_") for comp in components]) + " awsService"
        
        return diagram
    
    def _generate_fallback_sequence_diagram(self, interactions: List[Dict]) -> str:
        """Generate fallback sequence diagram when MCP server fails"""
        diagram = "sequenceDiagram\n"
        
        participants = set()
        for interaction in interactions:
            participants.add(interaction.get("from", "User"))
            participants.add(interaction.get("to", "System"))
        
        # Add participants
        for participant in participants:
            diagram += f"    participant {participant}\n"
        
        # Add interactions
        for interaction in interactions:
            from_actor = interaction.get("from", "User")
            to_actor = interaction.get("to", "System")
            message = interaction.get("message", "Request")
            diagram += f"    {from_actor}->>+{to_actor}: {message}\n"
        
        return diagram