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
        """Generate Entity-Relationship diagram from codebase or specification"""
        is_spec_content = analysis and analysis.get('source') == 'specification'
        
        if is_spec_content:
            system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
            
            Analyze the provided specification content (requirements, design, tasks) and generate a Mermaid ER diagram that shows:
            - Database entities/models mentioned in the spec
            - Relationships between entities
            - Key attributes for each entity based on requirements
            - Cardinality of relationships
            
            Return ONLY the Mermaid diagram code, starting with 'erDiagram' and properly formatted."""
        else:
            system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
            
            Analyze the provided codebase and generate a Mermaid ER diagram that shows:
            - Database entities/models
            - Relationships between entities
            - Key attributes for each entity
            - Cardinality of relationships
            
            Return ONLY the Mermaid diagram code, starting with 'erDiagram' and properly formatted."""
        
        # Extract model-related files
        model_files = self._extract_model_files(codebase)
        
        if is_spec_content:
            prompt = f"""Generate an ER diagram from this specification:

Specification content:
{json.dumps(codebase, indent=2)}

Focus on identifying from the spec:
1. Data entities mentioned in requirements and design
2. Relationships described in the specification
3. Attributes and properties defined in requirements
4. Database schema implied by the design"""
        else:
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
        is_spec_content = analysis and analysis.get('source') == 'specification'
        
        if is_spec_content:
            system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
            
            Analyze the provided specification content and generate a Mermaid graph that shows:
            - System architecture components described in the design
            - Component relationships from requirements
            - Layer separation mentioned in the specification
            - External dependencies and integrations
            
            Return ONLY the Mermaid diagram code, starting with 'graph TB' and properly formatted."""
            
            prompt = f"""Generate an architecture diagram from this specification:

Specification content:
{json.dumps(codebase, indent=2)}

Focus on:
1. System components described in the design document
2. Architecture patterns mentioned in requirements
3. Component interactions from the specification
4. External systems and integrations described"""
        else:
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
        """Generate AWS architecture diagram with optional MCP server enhancement"""
        try:
            is_spec_content = analysis and analysis.get('source') == 'specification'
            use_mcp_server = analysis and analysis.get('use_mcp_server', False)
            
            # For basic AWS Architecture, use AI-based generation
            if not use_mcp_server:
                return self._generate_basic_aws_architecture(codebase, is_spec_content)
            
            # For AWS Architecture with AWS Components, use MCP server
            # Initialize MCP service if not already done
            if not self.mcp_service.initialize_aws_diagram_server():
                return self._generate_enhanced_fallback_aws_architecture(codebase, is_spec_content)
            
            # Extract AWS components from codebase or spec
            if is_spec_content:
                # For spec content, use AI to extract AWS components from requirements and design
                components = self._ai_extract_aws_components_from_spec(codebase)
                connections = self._ai_extract_aws_connections(codebase, components)
            else:
                components = self.mcp_service.extract_aws_components_from_codebase(codebase)
                connections = self.mcp_service.extract_connections_from_codebase(codebase, components)
                
                if not components:
                    # Use AI to identify potential AWS components
                    components = self._ai_extract_aws_components(codebase)
                    connections = self._ai_extract_aws_connections(codebase, components)
            
            # Generate diagram using MCP server
            title = "Enhanced AWS Architecture from Specification" if is_spec_content else "Enhanced AWS Architecture"
            diagram = self.mcp_service.generate_aws_architecture_diagram(
                components=components,
                connections=connections,
                title=title
            )
            
            return diagram if diagram else self._generate_enhanced_fallback_aws_architecture(codebase, is_spec_content)
            
        except Exception as e:
            return self._generate_enhanced_fallback_aws_architecture(codebase, is_spec_content)
    
    def generate_sequence_diagram(self, codebase: Dict, analysis: Dict = None) -> str:
        """Generate sequence diagram showing interactions"""
        is_spec_content = analysis and analysis.get('source') == 'specification'
        
        if is_spec_content:
            system_prompt = """You are OpenFlux, an AI assistant specialized in creating technical diagrams.
            
            Analyze the provided specification content and generate a Mermaid sequence diagram that shows:
            - User interactions described in requirements
            - System workflows from the design
            - Component interactions mentioned in the spec
            - Process flows described in tasks
            
            Return ONLY the Mermaid diagram code, starting with 'sequenceDiagram' and properly formatted."""
            
            prompt = f"""Generate a sequence diagram from this specification:

Specification content:
{json.dumps(codebase, indent=2)}

Focus on:
1. User workflows described in requirements
2. System interactions from the design
3. Process flows mentioned in tasks
4. Component communications described in the spec"""
        else:
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
        """Clean and validate Mermaid diagram code for consistency"""
        if not raw_code or not raw_code.strip():
            return f"{diagram_type}\n    %% No content generated"
        
        # Remove any markdown code blocks
        cleaned = re.sub(r'```mermaid\n?', '', raw_code)
        cleaned = re.sub(r'```\n?', '', cleaned)
        
        # Split into lines for processing
        lines = cleaned.strip().split('\n')
        cleaned_lines = []
        
        # Ensure it starts with the correct diagram type
        if not lines[0].strip().startswith(diagram_type):
            cleaned_lines.append(diagram_type)
        
        # Process each line
        for line in lines:
            line = line.strip()
            if line:
                # Fix common Mermaid syntax issues
                line = self._fix_mermaid_syntax(line)
                cleaned_lines.append(line)
        
        # Validate the final diagram
        result = '\n'.join(cleaned_lines)
        return self._validate_mermaid_diagram(result, diagram_type)
    
    def _fix_mermaid_syntax(self, line: str) -> str:
        """Fix common Mermaid syntax issues"""
        # Fix node ID issues - ensure IDs are valid
        line = re.sub(r'[^\w\-\[\](){}":;,\s<>|&%/\\.]', '', line)
        
        # Fix arrow syntax
        line = re.sub(r'-->', '-->', line)  # Ensure consistent arrow syntax
        line = re.sub(r'->', '-->', line)   # Convert single arrows to double
        
        # Fix subgraph syntax
        if line.strip().startswith('subgraph'):
            # Ensure subgraph has proper quotes if needed
            if '"' not in line and '[' not in line and len(line.split()) > 1:
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    line = f'{parts[0]} "{parts[1]}"'
        
        # Fix node definitions with special characters
        if '[' in line and ']' in line:
            # Ensure node labels are properly formatted
            line = re.sub(r'\[([^]]*)\]', lambda m: f'[{m.group(1)}]', line)
        
        return line
    
    def _validate_mermaid_diagram(self, diagram: str, diagram_type: str) -> str:
        """Validate and fix Mermaid diagram structure"""
        lines = diagram.split('\n')
        validated_lines = []
        
        # Track if we have the diagram type declaration
        has_diagram_type = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for diagram type
            if line.startswith(diagram_type):
                has_diagram_type = True
                validated_lines.append(line)
                continue
            
            # Skip invalid lines that might break rendering
            if self._is_valid_mermaid_line(line):
                validated_lines.append(line)
        
        # Ensure we have diagram type
        if not has_diagram_type:
            validated_lines.insert(0, diagram_type)
        
        # Add fallback content if diagram is too minimal
        if len(validated_lines) < 3:
            return self._generate_minimal_fallback(diagram_type)
        
        return '\n'.join(validated_lines)
    
    def _is_valid_mermaid_line(self, line: str) -> bool:
        """Check if a line is valid Mermaid syntax"""
        if not line.strip():
            return False
        
        # Allow comments
        if line.strip().startswith('%%'):
            return True
        
        # Allow subgraphs
        if line.strip().startswith('subgraph'):
            return True
        
        # Allow end statements
        if line.strip() == 'end':
            return True
        
        # Allow classDef statements
        if line.strip().startswith('classDef'):
            return True
        
        # Allow class assignments
        if line.strip().startswith('class '):
            return True
        
        # Allow node definitions and connections
        valid_patterns = [
            r'^\s*\w+\[.*\]',  # Node definitions
            r'^\s*\w+\s*-->\s*\w+',  # Connections
            r'^\s*\w+\s*->>.*\w+',  # Sequence diagram arrows
            r'^\s*participant\s+\w+',  # Sequence participants
            r'^\s*class\s+\w+',  # Class definitions
            r'^\s*\w+\s*:\s*.*',  # ER diagram attributes
        ]
        
        return any(re.match(pattern, line) for pattern in valid_patterns)
    
    def _generate_minimal_fallback(self, diagram_type: str) -> str:
        """Generate minimal fallback diagram"""
        fallbacks = {
            'graph': """graph TB
    A[Start] --> B[Process]
    B --> C[End]""",
            'sequenceDiagram': """sequenceDiagram
    participant User
    participant System
    User->>System: Request
    System-->>User: Response""",
            'erDiagram': """erDiagram
    USER {
        int id
        string name
    }""",
            'classDiagram': """classDiagram
    class User {
        +String name
        +getId()
    }"""
        }
        return fallbacks.get(diagram_type, f"{diagram_type}\n    A --> B")
    
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
    
    def _ai_extract_aws_components_from_spec(self, spec_content: Dict) -> List[str]:
        """Use AI to extract AWS components from specification content"""
        system_prompt = """You are OpenFlux, an AI assistant specialized in AWS architecture analysis.
        
        Analyze the provided specification content (requirements, design, tasks) and identify AWS services and components that should be used based on the requirements and design.
        Return a JSON list of AWS service names that would be appropriate for this system.
        
        Look for:
        - Infrastructure requirements mentioned in the spec
        - Scalability and performance requirements
        - Storage and database needs
        - API and web service requirements
        - Security and compliance needs
        - Integration requirements
        
        Return ONLY a JSON array of service names, like: ["EC2", "S3", "RDS", "Lambda", "API Gateway"]"""
        
        prompt = f"""Identify appropriate AWS services for this specification:

Specification content:
{json.dumps(spec_content, indent=2)}

Based on the requirements and design, suggest AWS services that would be needed.
Return only the JSON array of AWS service names."""
        
        try:
            response = self.ai_service.generate_text(prompt, system_prompt)
            # Try to parse JSON response
            import json
            components = json.loads(response.strip())
            return components if isinstance(components, list) else []
        except:
            # Fallback based on common web application patterns
            return ["EC2", "RDS", "S3", "API Gateway", "Lambda", "CloudFront"]
    
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
    
    def _generate_basic_aws_architecture(self, codebase: Dict, is_spec_content: bool = False) -> str:
        """Generate basic AWS architecture diagram using AI"""
        if is_spec_content:
            system_prompt = """You are OpenFlux, an AI assistant specialized in AWS architecture diagrams.
            
            Analyze the provided specification content and generate a clean, basic AWS architecture diagram using Mermaid.
            Focus on high-level AWS services and their relationships based on the requirements and design.
            
            Return ONLY the Mermaid diagram code, starting with 'graph TB' and properly formatted."""
            
            prompt = f"""Generate a basic AWS architecture diagram from this specification:

Specification content:
{json.dumps(codebase, indent=2)}

Create a simple, clean AWS architecture showing:
1. Main AWS services needed based on requirements
2. Basic service relationships
3. User interaction points
4. Data flow between services"""
        else:
            system_prompt = """You are OpenFlux, an AI assistant specialized in AWS architecture diagrams.
            
            Analyze the provided codebase and generate a clean, basic AWS architecture diagram using Mermaid.
            Focus on identifying AWS services used and their relationships.
            
            Return ONLY the Mermaid diagram code, starting with 'graph TB' and properly formatted."""
            
            prompt = f"""Generate a basic AWS architecture diagram for this codebase:

{json.dumps(codebase, indent=2)[:3000]}...

Create a simple, clean AWS architecture showing:
1. AWS services identified in the code
2. Basic service relationships
3. User interaction points
4. Data flow between services"""
        
        try:
            diagram_code = self.ai_service.generate_text(prompt, system_prompt)
            return self._clean_mermaid_code(diagram_code, "graph")
        except Exception as e:
            return self._generate_fallback_aws_architecture(codebase, is_spec_content)
    
    def _generate_fallback_aws_architecture(self, codebase: Dict, is_spec_content: bool = False) -> str:
        """Generate fallback AWS architecture diagram"""
        if is_spec_content:
            return """graph TB
    subgraph "AWS Cloud Architecture"
        subgraph "Frontend Layer"
            CF[CloudFront CDN]
            S3Web[S3 Static Website]
        end
        
        subgraph "API Layer"
            ALB[Application Load Balancer]
            API[API Gateway]
            Lambda[Lambda Functions]
        end
        
        subgraph "Application Layer"
            EC2[EC2 Instances]
            ECS[ECS Containers]
        end
        
        subgraph "Data Layer"
            RDS[RDS Database]
            S3[S3 Storage]
            Cache[ElastiCache]
        end
        
        subgraph "Security & Monitoring"
            IAM[IAM Roles]
            CW[CloudWatch]
        end
    end
    
    Users[End Users] --> CF
    CF --> S3Web
    Users --> ALB
    ALB --> EC2
    Users --> API
    API --> Lambda
    Lambda --> RDS
    EC2 --> RDS
    Lambda --> S3
    EC2 --> S3
    EC2 --> Cache"""
        else:
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
    
    def _generate_enhanced_fallback_aws_architecture(self, codebase: Dict, is_spec_content: bool = False) -> str:
        """Generate enhanced fallback AWS architecture diagram with draw.io-style AWS icons"""
        return self._generate_aws_diagram_with_drawio_icons(is_spec_content)
    
    def _generate_aws_diagram_with_drawio_icons(self, is_spec_content: bool = False) -> str:
        """Generate AWS architecture diagram with draw.io-style icons and proper styling"""
        if is_spec_content:
            return """graph TB
    %% AWS Architecture with Draw.io Style Icons - From Specification
    subgraph "aws-cloud" ["☁️ AWS Cloud Infrastructure"]
        subgraph "edge-layer" ["🌐 Edge & Content Delivery"]
            R53["🌍 Route 53<br/>DNS Management"]
            CF["📡 CloudFront<br/>Global CDN"]
            WAF["🛡️ AWS WAF<br/>Web Application Firewall"]
        end
        
        subgraph "frontend-layer" ["🖥️ Frontend & Static Assets"]
            S3Web["📁 S3 Bucket<br/>Static Website Hosting"]
            S3Assets["📦 S3 Bucket<br/>Static Assets"]
        end
        
        subgraph "api-layer" ["🔌 API & Load Balancing"]
            ALB["⚖️ Application<br/>Load Balancer"]
            APIGW["🚪 API Gateway<br/>REST/HTTP API"]
            APIGW2["🔗 API Gateway<br/>WebSocket API"]
        end
        
        subgraph "compute-layer" ["💻 Compute Services"]
            EC2["🖥️ EC2<br/>Auto Scaling Group"]
            Lambda["⚡ Lambda<br/>Serverless Functions"]
            ECS["🐳 ECS Fargate<br/>Containerized Apps"]
            EKS["☸️ EKS<br/>Kubernetes Cluster"]
        end
        
        subgraph "data-layer" ["💾 Data & Storage"]
            RDS["🗄️ RDS<br/>Relational Database"]
            Aurora["🌟 Aurora<br/>Serverless Database"]
            DynamoDB["⚡ DynamoDB<br/>NoSQL Database"]
            S3Data["🏗️ S3 Bucket<br/>Data Lake Storage"]
            EFS["📂 EFS<br/>Elastic File System"]
        end
        
        subgraph "cache-layer" ["🚀 Caching & Performance"]
            ElastiCache["🚀 ElastiCache<br/>Redis/Memcached"]
            DAX["⚡ DynamoDB<br/>Accelerator (DAX)"]
        end
        
        subgraph "security-layer" ["🔐 Security & Identity"]
            IAM["👤 IAM<br/>Identity & Access Management"]
            Cognito["🔑 Cognito<br/>User Authentication"]
            SecretsManager["🔒 Secrets Manager<br/>Credential Storage"]
            KMS["🔐 AWS KMS<br/>Key Management Service"]
        end
        
        subgraph "monitoring-layer" ["📊 Monitoring & Observability"]
            CloudWatch["📈 CloudWatch<br/>Metrics & Logs"]
            CloudTrail["🔍 CloudTrail<br/>API Audit Logging"]
            XRay["🔬 X-Ray<br/>Distributed Tracing"]
        end
        
        subgraph "integration-layer" ["🔗 Integration & Messaging"]
            SQS["📬 SQS<br/>Message Queues"]
            SNS["📢 SNS<br/>Push Notifications"]
            EventBridge["🌉 EventBridge<br/>Event-Driven Architecture"]
        end
    end
    
    %% External Users and Connections
    Users["👥 End Users"]
    
    %% Primary User Flow
    Users --> R53
    R53 --> CF
    CF --> WAF
    WAF --> S3Web
    CF --> ALB
    
    %% API and Compute Flows
    ALB --> EC2
    ALB --> ECS
    APIGW --> Lambda
    APIGW2 --> Lambda
    
    %% Data Access Patterns
    Lambda --> RDS
    Lambda --> Aurora
    Lambda --> DynamoDB
    EC2 --> RDS
    ECS --> Aurora
    
    %% Caching Patterns
    Lambda --> ElastiCache
    EC2 --> ElastiCache
    DynamoDB --> DAX
    
    %% Storage Patterns
    Lambda --> S3Data
    EC2 --> S3Assets
    ECS --> EFS
    
    %% Messaging Patterns
    Lambda --> SQS
    SQS --> SNS
    Lambda --> EventBridge
    
    %% AWS Official Color Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsSecurity fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsMonitoring fill:#759C3E,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsIntegration fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsAnalytics fill:#8C4FFF,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    
    %% Apply Styling to Services
    class EC2,Lambda,ECS,EKS awsCompute
    class S3Web,S3Assets,S3Data,EFS awsStorage
    class RDS,Aurora,DynamoDB,ElastiCache,DAX awsDatabase
    class R53,CF,ALB,APIGW,APIGW2,WAF awsNetwork
    class IAM,Cognito,SecretsManager,KMS awsSecurity
    class CloudWatch,CloudTrail,XRay awsMonitoring
    class SQS,SNS,EventBridge awsIntegration"""
        else:
            return """graph TB
    %% AWS Architecture with Draw.io Style Icons - From Codebase
    subgraph "aws-cloud" ["☁️ AWS Cloud Infrastructure"]
        subgraph "frontend-tier" ["🌐 Frontend & CDN"]
            R53["🌍 Route 53<br/>DNS Service"]
            CF["📡 CloudFront<br/>Content Delivery Network"]
            S3Web["📁 S3 Bucket<br/>Static Website"]
        end
        
        subgraph "application-tier" ["🔌 Application Layer"]
            ALB["⚖️ Application<br/>Load Balancer"]
            EC2ASG["🖥️ EC2<br/>Auto Scaling Group"]
            Lambda["⚡ Lambda<br/>Serverless Functions"]
            APIGW["🚪 API Gateway<br/>REST API"]
        end
        
        subgraph "data-tier" ["💾 Data & Storage"]
            RDS["🗄️ RDS<br/>Relational Database"]
            DynamoDB["⚡ DynamoDB<br/>NoSQL Database"]
            S3["📦 S3 Bucket<br/>Object Storage"]
            ElastiCache["🚀 ElastiCache<br/>In-Memory Cache"]
        end
        
        subgraph "security-tier" ["🔐 Security & Monitoring"]
            IAM["👤 IAM<br/>Identity & Access Management"]
            CloudWatch["📈 CloudWatch<br/>Monitoring & Logging"]
            VPC["🏢 VPC<br/>Virtual Private Cloud"]
        end
        
        subgraph "integration-tier" ["🔗 Integration Services"]
            SQS["📬 SQS<br/>Message Queues"]
            SNS["📢 SNS<br/>Notification Service"]
        end
    end
    
    %% External Users
    Users["👥 Users"]
    
    %% Connection Flows
    Users --> R53
    R53 --> CF
    CF --> S3Web
    Users --> ALB
    ALB --> EC2ASG
    APIGW --> Lambda
    Lambda --> RDS
    Lambda --> DynamoDB
    EC2ASG --> RDS
    Lambda --> S3
    EC2ASG --> ElastiCache
    Lambda --> SQS
    SQS --> SNS
    
    %% AWS Official Color Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsSecurity fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    classDef awsIntegration fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff,font-weight:bold
    
    %% Apply Styling
    class EC2ASG,Lambda awsCompute
    class S3Web,S3 awsStorage
    class RDS,DynamoDB,ElastiCache awsDatabase
    class R53,CF,ALB,APIGW awsNetwork
    class IAM,CloudWatch,VPC awsSecurity
    class SQS,SNS awsIntegration"""
        end
        
        subgraph "Frontend Hosting"
            S3Web[S3 Static Website]
            S3Assets[S3 Assets Bucket]
        end
        
        subgraph "Load Balancing & API"
            ALB[Application Load Balancer]
            NLB[Network Load Balancer]
            APIGW[API Gateway]
            APIGW2[API Gateway v2]
        end
        
        subgraph "Compute Services"
            EC2[EC2 Auto Scaling Group]
            Lambda[Lambda Functions]
            ECS[ECS Fargate]
            EKS[EKS Cluster]
        end
        
        subgraph "Database & Storage"
            RDS[RDS Multi-AZ]
            Aurora[Aurora Serverless]
            DynamoDB[DynamoDB Tables]
            S3Data[S3 Data Lake]
            EFS[EFS File System]
        end
        
        subgraph "Caching & Performance"
            ElastiCache[ElastiCache Redis]
            DAX[DynamoDB Accelerator]
        end
        
        subgraph "Security & Identity"
            IAM[IAM Roles & Policies]
            Cognito[Cognito User Pools]
            SecretsManager[Secrets Manager]
            KMS[AWS KMS]
        end
        
        subgraph "Monitoring & Logging"
            CloudWatch[CloudWatch Metrics]
            CloudTrail[CloudTrail Logs]
            XRay[X-Ray Tracing]
        end
        
        subgraph "Integration & Messaging"
            SQS[SQS Queues]
            SNS[SNS Topics]
            EventBridge[EventBridge]
        end
    end
    
    Users[End Users] --> R53
    R53 --> CF
    CF --> WAF
    WAF --> S3Web
    CF --> ALB
    ALB --> EC2
    ALB --> ECS
    APIGW --> Lambda
    Lambda --> RDS
    Lambda --> DynamoDB
    EC2 --> ElastiCache
    Lambda --> S3Data
    EC2 --> Aurora
    Lambda --> SQS
    SQS --> SNS"""
        else:
            return """graph TB
    subgraph "AWS Cloud - Enhanced Architecture"
        subgraph "Frontend & CDN"
            CF[CloudFront]
            S3Web[S3 Website]
            R53[Route 53]
        end
        
        subgraph "Application Tier"
            ALB[Application Load Balancer]
            EC2ASG[EC2 Auto Scaling]
            Lambda[Lambda Functions]
            APIGW[API Gateway]
        end
        
        subgraph "Data & Storage"
            RDS[RDS Database]
            DynamoDB[DynamoDB]
            S3[S3 Buckets]
            ElastiCache[ElastiCache]
        end
        
        subgraph "Security & Monitoring"
            IAM[IAM]
            CloudWatch[CloudWatch]
            VPC[VPC & Subnets]
        end
        
        subgraph "Integration"
            SQS[SQS]
            SNS[SNS]
        end
    end
    
    Users --> R53
    R53 --> CF
    CF --> S3Web
    Users --> ALB
    ALB --> EC2ASG
    APIGW --> Lambda
    Lambda --> RDS
    Lambda --> DynamoDB
    EC2ASG --> RDS
    Lambda --> S3
    EC2ASG --> ElastiCache
    Lambda --> SQS
    SQS --> SNS"""
    
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