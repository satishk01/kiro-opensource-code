"""
Diagram Generator for creating Mermaid diagrams from code analysis
"""
import re
import json
from typing import Dict, List, Optional, Any
from services.ai_service import AIService
from services.mcp_service import MCPService

class DiagramGenerator:
    """Generate various types of diagrams from codebase analysis"""
    
    def __init__(self, ai_service: AIService, mcp_service: Optional[MCPService] = None):
        self.ai_service = ai_service
        self.mcp_service = mcp_service or MCPService()
        
        # Initialize AWS MCP server connection
        self.aws_mcp_available = self.mcp_service.initialize_aws_diagram_server()
    
    def generate_er_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate Entity-Relationship diagram from codebase"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
        
        Analyze the provided codebase and generate a Mermaid ER diagram that shows:
        - Database entities/models
        - Relationships between entities
        - Key attributes for each entity
        - Cardinality of relationships
        
        Return ONLY the Mermaid diagram code, starting with 'erDiagram' and properly formatted."""
        
        # Extract model-related files
        model_files = self._extract_model_files(codebase)
        
        prompt = f"""Generate an ER diagram for this codebase:

Model files:
{json.dumps(model_files, indent=2)}

Full codebase context:
{json.dumps(codebase, indent=2)[:3000]}...

Focus on identifying:
1. Data models/entities
2. Relationships between models
3. Key attributes and foreign keys
4. Database schema structure"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "erDiagram")
        except Exception as e:
            return self._generate_fallback_er_diagram(model_files)
    
    def generate_data_flow_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate data flow diagram from codebase structure"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
        
        Analyze the provided codebase and generate a Mermaid flowchart that shows:
        - Data flow between components
        - API endpoints and their interactions
        - Service layer communications
        - External system integrations
        
        Return ONLY the Mermaid diagram code, starting with 'flowchart TD' and properly formatted."""
        
        # Extract API and service files
        api_files = self._extract_api_files(codebase)
        service_files = self._extract_service_files(codebase)
        
        prompt = f"""Generate a data flow diagram for this codebase:

API files:
{json.dumps(api_files, indent=2)}

Service files:
{json.dumps(service_files, indent=2)}

Full codebase context:
{json.dumps(codebase, indent=2)[:3000]}...

Focus on:
1. Request/response flows
2. Service interactions
3. Data transformations
4. External API calls"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "flowchart")
        except Exception as e:
            return self._generate_fallback_flow_diagram(api_files, service_files)
    
    def generate_architecture_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate system architecture diagram"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
        
        Analyze the provided codebase and generate a Mermaid graph that shows:
        - System architecture components
        - Module dependencies
        - Layer separation (presentation, business, data)
        - External dependencies
        
        Return ONLY the Mermaid diagram code, starting with 'graph TB' and properly formatted."""
        
        prompt = f"""Generate an architecture diagram for this codebase:

{json.dumps(codebase, indent=2)[:4000]}...

Analysis context:
{json.dumps(analysis, indent=2) if analysis else 'No analysis provided'}

Focus on:
1. High-level system components
2. Module relationships
3. Architectural layers
4. External integrations"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "graph")
        except Exception as e:
            return self._generate_fallback_architecture_diagram(codebase)
    
    def generate_class_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate class diagram from object-oriented code"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
        
        Analyze the provided codebase and generate a Mermaid class diagram that shows:
        - Classes and their methods/attributes
        - Inheritance relationships
        - Composition and aggregation
        - Interface implementations
        
        Return ONLY the Mermaid diagram code, starting with 'classDiagram' and properly formatted."""
        
        # Extract class-based files
        class_files = self._extract_class_files(codebase)
        
        prompt = f"""Generate a class diagram for this codebase:

Class files:
{json.dumps(class_files, indent=2)}

Focus on:
1. Class definitions and structures
2. Method signatures
3. Inheritance hierarchies
4. Interface implementations"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "classDiagram")
        except Exception as e:
            return self._generate_fallback_class_diagram(class_files)
    
    def generate_sequence_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate sequence diagram showing interactions over time"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
        
        Analyze the provided codebase and generate a Mermaid sequence diagram that shows:
        - Interactions between objects/components over time
        - Method calls and message passing
        - Synchronous and asynchronous operations
        - Return values and responses
        
        Return ONLY the Mermaid diagram code, starting with 'sequenceDiagram' and properly formatted."""
        
        # Extract interaction patterns from API and service files
        api_files = self._extract_api_files(codebase)
        service_files = self._extract_service_files(codebase)
        
        prompt = f"""Generate a sequence diagram for this codebase:

API files:
{json.dumps(api_files, indent=2)}

Service files:
{json.dumps(service_files, indent=2)}

Focus on:
1. Request/response flows
2. Service method calls
3. Database interactions
4. External API calls
5. Error handling flows"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "sequenceDiagram")
        except Exception as e:
            return self._generate_fallback_sequence_diagram(api_files, service_files)
    
    def generate_aws_architecture_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate AWS architecture diagram with proper AWS components"""
        if self.aws_mcp_available and self.mcp_service:
            # Use AWS MCP server for enhanced diagram generation
            components = self.mcp_service.extract_aws_components_from_codebase(codebase)
            connections = self.mcp_service.extract_connections_from_codebase(codebase, components)
            
            # Generate diagram using MCP server
            mcp_diagram = self.mcp_service.generate_aws_architecture_diagram(
                components, connections, "AWS Architecture"
            )
            
            if mcp_diagram:
                return mcp_diagram
        
        # Fallback to AI-generated AWS diagram
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating AWS architecture diagrams.
        
        Analyze the provided codebase and generate a Mermaid graph diagram that shows:
        - AWS services and components with proper icons
        - VPC boundaries and networking
        - Security groups and access patterns
        - Data flow between services
        - AWS best practices and Well-Architected principles
        
        Use AWS official colors and draw.io-style icons. Return ONLY the Mermaid diagram code."""
        
        # Extract AWS-related content
        aws_content = self._extract_aws_content(codebase)
        
        prompt = f"""Generate an AWS architecture diagram for this codebase:

AWS-related content:
{json.dumps(aws_content, indent=2)}

Full codebase context:
{json.dumps(codebase, indent=2)[:3000]}...

Focus on:
1. AWS services used (EC2, S3, RDS, Lambda, etc.)
2. Network architecture (VPC, subnets, security groups)
3. Data flow and connections
4. Security boundaries
5. Monitoring and logging services

Use proper AWS service icons and official AWS colors."""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._enhance_aws_diagram_with_icons(diagram_code)
        except Exception as e:
            return self._generate_fallback_aws_architecture_diagram(codebase)
    
    def _extract_model_files(self, codebase: Dict) -> Dict:
        """Extract files that likely contain data models"""
        model_files = {}
        model_patterns = [
            r'model', r'entity', r'schema', r'dto', r'domain',
            r'migration', r'table', r'database'
        ]
        
        for file_path, content in codebase.items():
            file_lower = file_path.lower()
            if any(pattern in file_lower for pattern in model_patterns):
                model_files[file_path] = content
            elif self._contains_model_keywords(content):
                model_files[file_path] = content
        
        return model_files
    
    def _extract_api_files(self, codebase: Dict) -> Dict:
        """Extract files that contain API definitions"""
        api_files = {}
        api_patterns = [
            r'api', r'controller', r'route', r'endpoint', r'handler',
            r'rest', r'graphql', r'service'
        ]
        
        for file_path, content in codebase.items():
            file_lower = file_path.lower()
            if any(pattern in file_lower for pattern in api_patterns):
                api_files[file_path] = content
            elif self._contains_api_keywords(content):
                api_files[file_path] = content
        
        return api_files
    
    def _extract_service_files(self, codebase: Dict) -> Dict:
        """Extract service layer files"""
        service_files = {}
        service_patterns = [
            r'service', r'business', r'logic', r'manager', r'processor'
        ]
        
        for file_path, content in codebase.items():
            file_lower = file_path.lower()
            if any(pattern in file_lower for pattern in service_patterns):
                service_files[file_path] = content
        
        return service_files
    
    def _extract_class_files(self, codebase: Dict) -> Dict:
        """Extract files containing class definitions"""
        class_files = {}
        
        for file_path, content in codebase.items():
            if self._contains_class_definitions(content):
                class_files[file_path] = content
        
        return class_files
    
    def _contains_model_keywords(self, content: str) -> bool:
        """Check if content contains model-related keywords"""
        keywords = [
            'class.*Model', 'Entity', 'Table', 'Column', 'ForeignKey',
            'relationship', 'schema', 'migration', 'CREATE TABLE'
        ]
        return any(re.search(keyword, content, re.IGNORECASE) for keyword in keywords)
    
    def _contains_api_keywords(self, content: str) -> bool:
        """Check if content contains API-related keywords"""
        keywords = [
            '@app.route', '@api.route', 'def get_', 'def post_', 'def put_', 'def delete_',
            'FastAPI', 'Flask', 'Express', 'router', 'endpoint'
        ]
        return any(re.search(keyword, content, re.IGNORECASE) for keyword in keywords)
    
    def _contains_class_definitions(self, content: str) -> bool:
        """Check if content contains class definitions"""
        patterns = [
            r'class\s+\w+', r'interface\s+\w+', r'public class', r'private class'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def _clean_mermaid_code(self, raw_code: str, diagram_type: str) -> str:
        """Clean and validate Mermaid diagram code"""
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```mermaid\n?', '', raw_code)
        cleaned = re.sub(r'```\n?', '', cleaned)
        
        # Basic validation and cleanup
        lines = cleaned.split('\n')
        valid_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Remove comments
                valid_lines.append(line)
        
        # Ensure diagram starts with correct type
        if valid_lines and not valid_lines[0].strip().startswith(diagram_type):
            valid_lines.insert(0, diagram_type)
        elif not valid_lines:
            valid_lines = [diagram_type]
        
        return '\n'.join(valid_lines)
    
    def _generate_fallback_er_diagram(self, model_files: Dict) -> str:
        """Generate a basic ER diagram when AI generation fails"""
        if not model_files:
            return """erDiagram
    ENTITY {
        id int PK
        name string
        created_at datetime
    }"""
        
        entities = []
        for file_path in model_files.keys():
            # Extract potential entity names from file paths
            entity_name = file_path.split('/')[-1].split('.')[0].upper()
            entities.append(f"""    {entity_name} {{
        id int PK
        name string
        created_at datetime
    }}""")
        
        return f"erDiagram\n" + '\n'.join(entities)
    
    def _generate_fallback_flow_diagram(self, api_files: Dict, service_files: Dict) -> str:
        """Generate a basic flow diagram when AI generation fails"""
        return """flowchart TD
    A[Client Request] --> B[API Layer]
    B --> C[Service Layer]
    C --> D[Data Layer]
    D --> E[Database]
    C --> F[External APIs]
    B --> G[Response]"""
    
    def _generate_fallback_architecture_diagram(self, codebase: Dict) -> str:
        """Generate a basic architecture diagram when AI generation fails"""
        return """graph TB
    subgraph "Presentation Layer"
        UI[User Interface]
        API[API Endpoints]
    end
    
    subgraph "Business Layer"
        SVC[Services]
        BL[Business Logic]
    end
    
    subgraph "Data Layer"
        DB[Database]
        EXT[External APIs]
    end
    
    UI --> API
    API --> SVC
    SVC --> BL
    BL --> DB
    BL --> EXT"""
    
    def _generate_fallback_class_diagram(self, class_files: Dict) -> str:
        """Generate a basic class diagram when AI generation fails"""
        return """classDiagram
    class BaseClass {
        +id: int
        +created_at: datetime
        +save()
        +delete()
    }
    
    class DerivedClass {
        +name: string
        +process()
    }
    
    BaseClass <|-- DerivedClass"""
    
    def _generate_fallback_sequence_diagram(self, api_files: Dict, service_files: Dict) -> str:
        """Generate a basic sequence diagram when AI generation fails"""
        return """sequenceDiagram
    participant User
    participant API as API Layer
    participant Service as Service Layer
    participant DB as Database
    
    User->>+API: HTTP Request
    API->>+Service: Process Request
    Service->>+DB: Query Data
    DB-->>-Service: Return Data
    Service-->>-API: Processed Response
    API-->>-User: HTTP Response"""
    
    def _extract_aws_content(self, codebase: Dict) -> Dict:
        """Extract AWS-related content from codebase"""
        aws_content = {}
        aws_keywords = [
            'aws', 'ec2', 's3', 'rds', 'lambda', 'api gateway', 'cloudfront',
            'route53', 'iam', 'vpc', 'cloudwatch', 'sns', 'sqs', 'dynamodb',
            'elasticache', 'elb', 'alb', 'nlb', 'ecs', 'eks', 'fargate'
        ]
        
        for file_path, content in codebase.items():
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in aws_keywords):
                aws_content[file_path] = content
        
        return aws_content
    
    def _enhance_aws_diagram_with_icons(self, diagram: str) -> str:
        """Enhance AWS diagram with draw.io-style icons and AWS colors"""
        if not diagram:
            return diagram
        
        # AWS service icon mappings
        aws_icons = {
            'EC2': '🖥️', 'S3': '📁', 'RDS': '🗄️', 'Lambda': '⚡', 'API Gateway': '🚪',
            'CloudFront': '📡', 'Route 53': '🌍', 'ALB': '⚖️', 'VPC': '🏢', 'IAM': '👤',
            'CloudWatch': '📈', 'SNS': '📢', 'SQS': '📬', 'DynamoDB': '⚡', 'ElastiCache': '🚀',
            'ECS': '🐳', 'EKS': '☸️', 'Aurora': '🌟', 'Cognito': '🔑', 'KMS': '🔐'
        }
        
        enhanced_diagram = diagram
        
        # Add icons to service names
        for service, icon in aws_icons.items():
            service_pattern = rf'\b{re.escape(service)}\b'
            enhanced_diagram = re.sub(
                service_pattern,
                f'{icon} {service}',
                enhanced_diagram,
                flags=re.IGNORECASE
            )
        
        # Add AWS styling if not present
        if "classDef aws" not in enhanced_diagram:
            aws_styling = """
    %% AWS Official Color Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsSecurity fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff"""
            enhanced_diagram += aws_styling
        
        return enhanced_diagram
    
    def _generate_fallback_aws_architecture_diagram(self, codebase: Dict) -> str:
        """Generate fallback AWS architecture diagram when all else fails"""
        return """graph TB
    subgraph "AWS Cloud"
        subgraph "VPC"
            subgraph "Public Subnet"
                ALB["⚖️ Application Load Balancer"]
                NAT["🌐 NAT Gateway"]
            end
            
            subgraph "Private Subnet"
                EC2["🖥️ EC2 Instances"]
                RDS["🗄️ RDS Database"]
            end
        end
        
        S3["📁 S3 Bucket"]
        CF["📡 CloudFront"]
        R53["🌍 Route 53"]
    end
    
    Users["👥 Users"] --> R53
    R53 --> CF
    CF --> ALB
    ALB --> EC2
    EC2 --> RDS
    EC2 --> S3
    
    %% AWS Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff
    
    class EC2 awsCompute
    class S3 awsStorage
    class RDS awsDatabase
    class ALB,CF,R53,NAT awsNetwork"""
    
    def detect_diagram_type(self, user_input: str, codebase: Dict = None) -> str:
        """Automatically detect the most appropriate diagram type based on input"""
        input_lower = user_input.lower()
        
        # AWS-specific keywords (highest priority)
        aws_keywords = ['aws', 'ec2', 's3', 'rds', 'lambda', 'cloudfront', 'vpc', 'iam', 'bucket', 'instance']
        if any(keyword in input_lower for keyword in aws_keywords):
            return 'aws_architecture'
        
        # Sequence/interaction keywords (high priority for specific terms)
        sequence_keywords = ['sequence', 'interaction', 'timeline', 'message', 'call', 'request', 'response', 'login', 'authentication flow']
        if any(keyword in input_lower for keyword in sequence_keywords):
            return 'sequence'
        
        # Class diagram keywords (check for OOP terms)
        class_keywords = ['class', 'object', 'inheritance', 'method', 'attribute', 'interface', 'oop', 'polymorphism']
        if any(keyword in input_lower for keyword in class_keywords):
            return 'class'
        
        # Database/ER keywords (check for data modeling terms)
        er_keywords = ['database', 'table', 'entity', 'relationship', 'schema', 'model', 'foreign key', 'primary key', 'er diagram']
        if any(keyword in input_lower for keyword in er_keywords):
            return 'er'
        
        # Data flow keywords (check for process terms)
        flow_keywords = ['flow', 'process', 'data flow', 'pipeline', 'transformation', 'workflow']
        if any(keyword in input_lower for keyword in flow_keywords):
            return 'data_flow'
        
        # Default to architecture for general system terms
        return 'architecture'
    
    def generate_diagram_by_type(self, diagram_type: str, codebase: Dict, analysis: Dict = None) -> str:
        """Generate diagram based on specified type"""
        generators = {
            'er': self.generate_er_diagram,
            'data_flow': self.generate_data_flow_diagram,
            'class': self.generate_class_diagram,
            'sequence': self.generate_sequence_diagram,
            'architecture': self.generate_architecture_diagram,
            'aws_architecture': self.generate_aws_architecture_diagram
        }
        
        generator = generators.get(diagram_type, self.generate_architecture_diagram)
        return generator(codebase, analysis)