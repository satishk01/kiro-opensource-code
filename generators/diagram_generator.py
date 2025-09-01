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
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.mcp_service = MCPService()
    
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
    
    def generate_aws_architecture_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate AWS architecture diagram using MCP server"""
        try:
            # Initialize MCP service if not already done
            if not self.mcp_service.initialize_aws_diagram_server():
                return self._generate_fallback_aws_architecture(codebase)
            
            # Extract AWS components from codebase
            components = self.mcp_service.extract_aws_components_from_codebase(codebase)
            connections = self.mcp_service.extract_connections_from_codebase(codebase, components)
            
            if not components:
                # Use AI to identify potential AWS components
                components = self._ai_extract_aws_components(codebase)
                connections = self._ai_extract_aws_connections(codebase, components)
            
            # Generate diagram using MCP server
            diagram = self.mcp_service.generate_aws_architecture_diagram(
                components=components,
                connections=connections,
                title="AWS Architecture"
            )
            
            return diagram if diagram else self._generate_fallback_aws_architecture(codebase)
            
        except Exception as e:
            return self._generate_fallback_aws_architecture(codebase)
    
    def generate_sequence_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate sequence diagram showing interactions"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
        
        Analyze the provided codebase and generate a Mermaid sequence diagram that shows:
        - User interactions with the system
        - API call flows
        - Service-to-service communications
        - Database interactions
        
        Return ONLY the Mermaid diagram code, starting with 'sequenceDiagram' and properly formatted."""
        
        # Extract API and service interactions
        interactions = self._extract_interactions_from_codebase(codebase)
        
        prompt = f"""Generate a sequence diagram for this codebase:

{json.dumps(codebase, indent=2)[:3000]}...

Focus on:
1. User-system interactions
2. API request/response flows
3. Service communications
4. Database operations
5. External API calls"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "sequenceDiagram")
        except Exception as e:
            return self._generate_fallback_sequence_diagram(interactions)
    
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
        
        # Ensure diagram starts with correct type
        if not cleaned.strip().startswith(diagram_type):
            cleaned = f"{diagram_type}\n{cleaned}"
        
        # Basic validation and cleanup
        lines = cleaned.split('\n')
        valid_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Remove comments
                valid_lines.append(line)
        
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
    
    def _ai_extract_aws_components(self, codebase: Dict) -> List[str]:
        """Use AI to extract AWS components from codebase"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in AWS architecture analysis.
        
        Analyze the provided codebase and identify AWS services and components that are used or referenced.
        Return a JSON list of AWS service names found in the code.
        
        Look for:
        - AWS SDK calls
        - Infrastructure as Code (CloudFormation, Terraform)
        - Configuration files mentioning AWS services
        - Import statements for AWS libraries
        - Environment variables with AWS service names
        
        Return ONLY a JSON array of service names, like: ["EC2", "S3", "RDS", "Lambda"]"""
        
        prompt = f"""Identify AWS services in this codebase:

{json.dumps(codebase, indent=2)[:4000]}...

Return only the JSON array of AWS service names."""
        
        try:
            response = self.ai_service.generate_text(prompt, system_prompt)
            # Try to parse JSON response
            import json
            components = json.loads(response.strip())
            return components if isinstance(components, list) else []
        except:
            # Fallback to common AWS services
            return ["EC2", "S3", "RDS", "Lambda", "API Gateway"]
    
    def _ai_extract_aws_connections(self, codebase: Dict, components: List[str]) -> List[Dict]:
        """Use AI to extract connections between AWS components"""
        if not components:
            return []
        
        system_prompt = """You are OpenFlux, an AI assistant specialized in AWS architecture analysis.
        
        Given a list of AWS components and codebase, identify likely connections between these components.
        Return a JSON array of connection objects with 'from', 'to', 'type', and 'description' fields.
        
        Example format:
        [
            {"from": "API Gateway", "to": "Lambda", "type": "triggers", "description": "API calls trigger Lambda functions"},
            {"from": "Lambda", "to": "RDS", "type": "queries", "description": "Lambda functions query database"}
        ]"""
        
        prompt = f"""Identify connections between these AWS components: {components}

Based on this codebase:
{json.dumps(codebase, indent=2)[:3000]}...

Return only the JSON array of connection objects."""
        
        try:
            response = self.ai_service.generate_text(prompt, system_prompt)
            connections = json.loads(response.strip())
            return connections if isinstance(connections, list) else []
        except:
            # Generate basic connections
            connections = []
            for i, comp1 in enumerate(components):
                for comp2 in components[i+1:]:
                    connections.append({
                        "from": comp1,
                        "to": comp2,
                        "type": "connects",
                        "description": f"{comp1} connects to {comp2}"
                    })
            return connections[:5]  # Limit to 5 connections
    
    def _extract_interactions_from_codebase(self, codebase: Dict) -> List[Dict]:
        """Extract interaction patterns from codebase for sequence diagrams"""
        interactions = []
        
        # Look for API endpoints and their handlers
        for file_path, content in codebase.items():
            # Find API route definitions
            api_patterns = [
                r'@app\.route\([\'"]([^\'"]+)[\'"]',
                r'@api\.route\([\'"]([^\'"]+)[\'"]',
                r'app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]',
                r'router\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        method = match[0] if len(match) > 1 else "request"
                        endpoint = match[1] if len(match) > 1 else match[0]
                    else:
                        method = "request"
                        endpoint = match
                    
                    interactions.append({
                        "from": "Client",
                        "to": "API",
                        "message": f"{method.upper()} {endpoint}",
                        "file": file_path
                    })
        
        return interactions
    
    def _generate_fallback_aws_architecture(self, codebase: Dict) -> str:
        """Generate fallback AWS architecture diagram"""
        return """graph TB
    subgraph "AWS Cloud"
        subgraph "Compute"
            EC2[EC2 Instances]
            Lambda[Lambda Functions]
        end
        
        subgraph "Storage"
            S3[S3 Buckets]
            RDS[RDS Database]
        end
        
        subgraph "Networking"
            ALB[Application Load Balancer]
            API[API Gateway]
        end
    end
    
    User[Users] --> ALB
    ALB --> EC2
    API --> Lambda
    Lambda --> RDS
    EC2 --> S3
    Lambda --> S3"""
    
    def _generate_fallback_sequence_diagram(self, interactions: List[Dict]) -> str:
        """Generate fallback sequence diagram"""
        return """sequenceDiagram
    participant User
    participant API
    participant Service
    participant Database
    
    User->>+API: HTTP Request
    API->>+Service: Process Request
    Service->>+Database: Query Data
    Database-->>-Service: Return Data
    Service-->>-API: Process Response
    API-->>-User: HTTP Response"""