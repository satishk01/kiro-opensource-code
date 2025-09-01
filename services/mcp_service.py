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
            # Test if uvx is available
            result = subprocess.run(
                ["uvx", "--help"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                self.logger.error("uvx not found. Please install uv and uvx first.")
                return False
            
            # Test if AWS Diagram MCP server is available
            test_result = subprocess.run([
                "uvx", 
                "awslabs.aws-diagram-mcp-server",
                "--help"
            ], capture_output=True, text=True, timeout=15)
            
            if test_result.returncode == 0:
                self.logger.info("AWS Diagram MCP server initialized successfully")
                return True
            else:
                self.logger.warning("AWS Diagram MCP server not available, will use fallback")
                return False
                
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
        """Generate AWS architecture diagram using AWS Labs MCP server"""
        try:
            # Use AWS Labs MCP server to generate comprehensive AWS architecture
            diagram = self._generate_aws_diagram_with_mcp_server(components, connections, title)
            
            if diagram:
                # Enhance with our custom styling and icons
                return self._enhance_mcp_diagram_with_icons(diagram, components)
            else:
                # Fallback to our enhanced diagram generation
                return self._generate_fallback_aws_diagram_with_icons(components, connections)
                
        except Exception as e:
            self.logger.error(f"Error generating AWS architecture diagram: {e}")
            return self._generate_fallback_aws_diagram_with_icons(components, connections)
    
    def _generate_aws_diagram_with_mcp_server(self, components: List[str], connections: List[Dict], title: str) -> Optional[str]:
        """Generate AWS diagram using AWS Labs MCP server"""
        try:
            # Create a comprehensive AWS architecture prompt for the MCP server
            architecture_prompt = self._create_aws_architecture_prompt(components, connections, title)
            
            # Call AWS Labs MCP server to get AWS architecture recommendations
            result = subprocess.run([
                "uvx", 
                "awslabs.aws-documentation-mcp-server@latest",
                "generate-architecture",
                "--services", ",".join(components),
                "--format", "mermaid",
                "--include-icons"
            ], capture_output=True, text=True, timeout=60, input=architecture_prompt)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                self.logger.warning(f"AWS Labs MCP server returned no output or failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calling AWS Labs MCP server: {e}")
            return None
    
    def _create_aws_architecture_prompt(self, components: List[str], connections: List[Dict], title: str) -> str:
        """Create a comprehensive prompt for AWS Labs MCP server"""
        prompt = f"""Generate a comprehensive AWS architecture diagram for: {title}

Required AWS Services: {', '.join(components)}

Architecture Requirements:
- Use AWS best practices for service connections
- Include proper security groups and networking
- Show data flow between services
- Use AWS Well-Architected Framework principles
- Include monitoring and logging services
- Add appropriate caching layers
- Consider high availability and scalability

Connections to include:
"""
        
        for conn in connections:
            prompt += f"- {conn['from']} -> {conn['to']}: {conn.get('description', 'Connection')}\n"
        
        prompt += """
Please generate a Mermaid diagram that shows:
1. All specified AWS services with proper icons
2. Logical grouping by service type (compute, storage, database, etc.)
3. Network flow and data connections
4. Security boundaries and access patterns
5. AWS official color scheme and styling

Format: Return only the Mermaid diagram code starting with 'graph TB'
"""
        
        return prompt
    
    def _enhance_mcp_diagram_with_icons(self, diagram: str, components: List[str]) -> str:
        """Enhance MCP-generated diagram with our custom icons and styling"""
        if not diagram:
            return diagram
        
        # Add our custom AWS icons to the diagram
        enhanced_diagram = diagram
        
        # Map of AWS services to our icons
        aws_icons = {
            'EC2': '🖥️', 'S3': '📁', 'RDS': '🗄️', 'Lambda': '⚡', 'API Gateway': '🚪',
            'CloudFront': '📡', 'Route 53': '🌍', 'ALB': '⚖️', 'VPC': '🏢', 'IAM': '👤',
            'CloudWatch': '📈', 'SNS': '📢', 'SQS': '📬', 'DynamoDB': '⚡', 'ElastiCache': '🚀',
            'ECS': '🐳', 'EKS': '☸️', 'Aurora': '🌟', 'Cognito': '🔑', 'KMS': '🔐',
            'WAF': '🛡️', 'CloudTrail': '🔍', 'X-Ray': '🔬', 'EventBridge': '🌉',
            'Secrets Manager': '🔒', 'EFS': '📂'
        }
        
        # Enhance node labels with icons
        for component in components:
            if component in aws_icons:
                icon = aws_icons[component]
                # Replace service names with icon + name format
                safe_name = component.replace(" ", "_").replace("-", "_")
                enhanced_diagram = enhanced_diagram.replace(
                    f'{safe_name}[{component}]',
                    f'{safe_name}["{icon} {component}<br/>AWS Service"]'
                )
                enhanced_diagram = enhanced_diagram.replace(
                    f'{safe_name}({component})',
                    f'{safe_name}("{icon} {component}<br/>AWS Service")'
                )
        
        # Add our AWS styling
        return self._enhance_mermaid_with_aws_styling(enhanced_diagram)
    
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
    
    def test_aws_labs_mcp_server(self) -> Dict[str, Any]:
        """Test AWS Labs MCP server availability and functionality"""
        test_result = {
            "available": False,
            "error": None,
            "version": None,
            "capabilities": []
        }
        
        try:
            # Test basic availability
            result = subprocess.run([
                "uvx", 
                "awslabs.aws-documentation-mcp-server@latest",
                "--version"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                test_result["available"] = True
                test_result["version"] = result.stdout.strip()
                
                # Test diagram generation capability
                test_components = ["EC2", "S3", "RDS"]
                test_connections = [{"from": "EC2", "to": "RDS", "type": "connects", "description": "Database connection"}]
                
                test_diagram = self._generate_aws_diagram_with_mcp_server(test_components, test_connections, "Test Architecture")
                
                if test_diagram:
                    test_result["capabilities"].append("diagram_generation")
                    self.logger.info("AWS Labs MCP server test successful")
                else:
                    test_result["capabilities"].append("basic_only")
                    self.logger.warning("AWS Labs MCP server available but diagram generation failed")
            else:
                test_result["error"] = result.stderr
                self.logger.error(f"AWS Labs MCP server test failed: {result.stderr}")
                
        except Exception as e:
            test_result["error"] = str(e)
            self.logger.error(f"Error testing AWS Labs MCP server: {e}")
        
        return test_result
    
    def _generate_fallback_aws_diagram_with_icons(self, components: List[str], connections: List[Dict]) -> str:
        """Generate comprehensive fallback AWS diagram with draw.io-style icons when MCP server fails"""
        aws_icons = {
            'EC2': '🖥️', 'S3': '📁', 'RDS': '🗄️', 'Lambda': '⚡', 'API Gateway': '🚪',
            'CloudFront': '📡', 'Route 53': '🌍', 'ALB': '⚖️', 'VPC': '🏢', 'IAM': '👤',
            'CloudWatch': '📈', 'SNS': '📢', 'SQS': '📬', 'DynamoDB': '⚡', 'ElastiCache': '🚀',
            'ECS': '🐳', 'EKS': '☸️', 'Aurora': '🌟', 'Cognito': '🔑', 'KMS': '🔐',
            'WAF': '🛡️', 'CloudTrail': '🔍', 'X-Ray': '🔬', 'EventBridge': '🌉',
            'Secrets Manager': '🔒', 'EFS': '📂', 'Redshift': '📊', 'Kinesis': '🌊'
        }
        
        # Create a comprehensive AWS architecture
        diagram = "graph TB\n"
        diagram += "    %% Comprehensive AWS Architecture with Draw.io Style Icons\n\n"
        
        # Group components by category for better organization
        categorized_components = self._categorize_aws_components(components)
        
        # Generate subgraphs for each category
        for category, services in categorized_components.items():
            if services:
                category_title = category.replace('_', ' ').title()
                diagram += f'    subgraph "{category_title}" ["{self._get_category_icon(category)} {category_title}"]\n'
                
                for service in services:
                    icon = aws_icons.get(service, '☁️')
                    safe_name = service.replace(" ", "_").replace("-", "_")
                    diagram += f'        {safe_name}["{icon} {service}<br/>AWS Service"]\n'
                
                diagram += "    end\n\n"
        
        # Add external users
        diagram += '    Users["👥 End Users"]\n\n'
        
        # Add connections
        diagram += "    %% Service Connections\n"
        for conn in connections:
            from_safe = conn["from"].replace(" ", "_").replace("-", "_")
            to_safe = conn["to"].replace(" ", "_").replace("-", "_")
            diagram += f"    {from_safe} --> {to_safe}\n"
        
        # Add common AWS connections if not specified
        if not connections:
            diagram += self._generate_default_aws_connections(components)
        
        # Add comprehensive AWS styling
        diagram += """
    %% AWS Official Color Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsSecurity fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsMonitoring fill:#759C3E,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsIntegration fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsAnalytics fill:#8C4FFF,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    
    %% Apply styling to components"""
        
        # Apply styling based on service categories
        for category, services in categorized_components.items():
            if services:
                class_name = f"aws{category.title().replace('_', '')}"
                service_names = ",".join([s.replace(" ", "_").replace("-", "_") for s in services])
                diagram += f"\n    class {service_names} {class_name}"
        
        return diagram
    
    def _categorize_aws_components(self, components: List[str]) -> Dict[str, List[str]]:
        """Categorize AWS components by service type"""
        categories = {
            'compute': [],
            'storage': [],
            'database': [],
            'network': [],
            'security': [],
            'monitoring': [],
            'integration': [],
            'analytics': []
        }
        
        service_categories = {
            'compute': ['EC2', 'Lambda', 'ECS', 'EKS', 'Fargate'],
            'storage': ['S3', 'EFS', 'EBS'],
            'database': ['RDS', 'DynamoDB', 'Aurora', 'ElastiCache', 'Redshift'],
            'network': ['VPC', 'CloudFront', 'Route 53', 'ALB', 'NLB', 'ELB', 'API Gateway', 'WAF'],
            'security': ['IAM', 'Cognito', 'KMS', 'Secrets Manager'],
            'monitoring': ['CloudWatch', 'CloudTrail', 'X-Ray'],
            'integration': ['SQS', 'SNS', 'EventBridge', 'Kinesis', 'Step Functions'],
            'analytics': ['Redshift', 'Kinesis', 'QuickSight', 'Athena']
        }
        
        for component in components:
            categorized = False
            for category, services in service_categories.items():
                if component in services:
                    categories[category].append(component)
                    categorized = True
                    break
            
            if not categorized:
                categories['compute'].append(component)  # Default to compute
        
        return categories
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for service category"""
        category_icons = {
            'compute': '💻',
            'storage': '💾',
            'database': '🗄️',
            'network': '🌐',
            'security': '🔐',
            'monitoring': '📊',
            'integration': '🔗',
            'analytics': '📈'
        }
        return category_icons.get(category, '☁️')
    
    def _generate_default_aws_connections(self, components: List[str]) -> str:
        """Generate default AWS service connections"""
        connections = ""
        
        # Common AWS connection patterns
        if "CloudFront" in components and "S3" in components:
            connections += "    CloudFront --> S3\n"
        
        if "API Gateway" in components and "Lambda" in components:
            connections += "    API_Gateway --> Lambda\n"
        
        if "Lambda" in components and "RDS" in components:
            connections += "    Lambda --> RDS\n"
        
        if "EC2" in components and "RDS" in components:
            connections += "    EC2 --> RDS\n"
        
        if "Lambda" in components and "DynamoDB" in components:
            connections += "    Lambda --> DynamoDB\n"
        
        if "Users" not in components:
            if "CloudFront" in components:
                connections += "    Users --> CloudFront\n"
            elif "ALB" in components:
                connections += "    Users --> ALB\n"
            elif "API Gateway" in components:
                connections += "    Users --> API_Gateway\n"
        
        return connections
    
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