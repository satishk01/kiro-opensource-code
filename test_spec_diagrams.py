#!/usr/bin/env python3
"""
Test spec-based diagram generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_spec_diagram_generation():
    """Test diagram generation from spec documents"""
    print("🚀 Testing Spec-Based Diagram Generation")
    print("=" * 60)
    
    # Mock AI service for testing
    class MockAIService:
        def generate_text(self, prompt, system_prompt):
            # Return appropriate diagram based on prompt content
            if "erDiagram" in system_prompt:
                return """erDiagram
    USER {
        id int PK
        username string
        email string
        password_hash string
        created_at datetime
    }
    
    PROFILE {
        id int PK
        user_id int FK
        first_name string
        last_name string
        bio text
    }
    
    SESSION {
        id int PK
        user_id int FK
        token string
        expires_at datetime
    }
    
    USER ||--|| PROFILE : has
    USER ||--o{ SESSION : creates"""
            
            elif "sequenceDiagram" in system_prompt:
                return """sequenceDiagram
    participant User
    participant Frontend
    participant AuthAPI
    participant Database
    
    User->>+Frontend: Enter credentials
    Frontend->>+AuthAPI: POST /login
    AuthAPI->>+Database: Validate user
    Database-->>-AuthAPI: User data
    AuthAPI->>+Database: Create session
    Database-->>-AuthAPI: Session token
    AuthAPI-->>-Frontend: Login success + token
    Frontend-->>-User: Redirect to dashboard"""
            
            elif "flowchart" in system_prompt:
                return """flowchart TD
    A[User Registration] --> B[Validate Input]
    B --> C{Valid Data?}
    C -->|Yes| D[Hash Password]
    C -->|No| E[Show Errors]
    D --> F[Save to Database]
    F --> G[Send Welcome Email]
    G --> H[Create User Profile]
    H --> I[Login User]
    E --> A"""
            
            elif "classDiagram" in system_prompt:
                return """classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password_hash
        +datetime created_at
        +authenticate(password)
        +update_profile(data)
        +create_session()
    }
    
    class Profile {
        +int id
        +int user_id
        +string first_name
        +string last_name
        +string bio
        +update(data)
    }
    
    class AuthService {
        +login(credentials)
        +register(user_data)
        +logout(session)
        +validate_session(token)
    }
    
    User ||--|| Profile : has
    AuthService --> User : manages"""
            
            elif "graph" in system_prompt and "AWS" in system_prompt:
                return """graph TB
    subgraph "AWS Cloud"
        subgraph "VPC"
            subgraph "Public Subnet"
                ALB["Application Load Balancer"]
                NAT["NAT Gateway"]
            end
            
            subgraph "Private Subnet"
                EC2["EC2 Web Servers"]
                RDS["RDS PostgreSQL"]
            end
        end
        
        S3["S3 Static Assets"]
        CF["CloudFront CDN"]
        R53["Route 53 DNS"]
        Cognito["Cognito User Pool"]
    end
    
    Users["Users"] --> R53
    R53 --> CF
    CF --> ALB
    ALB --> EC2
    EC2 --> RDS
    EC2 --> S3
    EC2 --> Cognito
    
    %% AWS Styling
    classDef awsCompute fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsStorage fill:#3F48CC,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsDatabase fill:#C925D1,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef awsNetwork fill:#FF4B4B,stroke:#232F3E,stroke-width:2px,color:#fff
    
    class EC2 awsCompute
    class S3 awsStorage
    class RDS awsDatabase
    class ALB,CF,R53,NAT awsNetwork"""
            
            else:  # Architecture diagram
                return """graph TB
    subgraph "Frontend Layer"
        UI[React Web App]
        Mobile[Mobile App]
    end
    
    subgraph "API Layer"
        Gateway[API Gateway]
        Auth[Authentication Service]
        User[User Service]
    end
    
    subgraph "Data Layer"
        DB[PostgreSQL Database]
        Cache[Redis Cache]
        Files[File Storage]
    end
    
    UI --> Gateway
    Mobile --> Gateway
    Gateway --> Auth
    Gateway --> User
    Auth --> DB
    User --> DB
    User --> Cache
    User --> Files"""
    
    # Import the diagram generator
    try:
        from generators.diagram_generator import DiagramGenerator
        from services.mcp_service import MCPService
        
        # Initialize with mock AI service
        ai_service = MockAIService()
        mcp_service = MCPService()
        diagram_generator = DiagramGenerator(ai_service, mcp_service)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Sample spec content (similar to what would be generated)
    sample_spec_content = {
        "requirements.md": """# Requirements Document

## Introduction

User authentication system with registration, login, password reset, and profile management capabilities.

## Requirements

### Requirement 1: User Registration

**User Story:** As a new user, I want to register for an account, so that I can access the application.

#### Acceptance Criteria

1. WHEN a user provides valid registration data THEN the system SHALL create a new user account
2. WHEN a user provides an email that already exists THEN the system SHALL display an error message
3. WHEN a user provides invalid data THEN the system SHALL display validation errors
4. WHEN registration is successful THEN the system SHALL send a welcome email

### Requirement 2: User Authentication

**User Story:** As a registered user, I want to log in to my account, so that I can access protected features.

#### Acceptance Criteria

1. WHEN a user provides valid credentials THEN the system SHALL authenticate the user
2. WHEN a user provides invalid credentials THEN the system SHALL display an error message
3. WHEN authentication is successful THEN the system SHALL create a session token
4. WHEN a session expires THEN the system SHALL require re-authentication""",

        "design.md": """# Design Document

## Overview

The user authentication system will be built using a microservices architecture with separate services for user management and authentication.

## Architecture

### Frontend Layer
- React web application
- Mobile application (React Native)

### API Layer
- API Gateway for request routing
- Authentication Service for login/logout
- User Service for profile management

### Data Layer
- PostgreSQL database for user data
- Redis cache for session storage
- S3 for file storage (profile images)

## Components and Interfaces

### User Service
- Handles user registration and profile management
- Exposes REST API endpoints
- Integrates with email service

### Authentication Service
- Handles login/logout operations
- Manages session tokens
- Integrates with user service

## Data Models

### User Entity
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- created_at
- updated_at

### Profile Entity
- id (Primary Key)
- user_id (Foreign Key)
- first_name
- last_name
- bio
- avatar_url

### Session Entity
- id (Primary Key)
- user_id (Foreign Key)
- token (Unique)
- expires_at

## Error Handling

- Input validation on all endpoints
- Proper HTTP status codes
- Structured error responses
- Logging for debugging

## Testing Strategy

- Unit tests for all services
- Integration tests for API endpoints
- End-to-end tests for user flows""",

        "tasks.md": """# Implementation Plan

- [ ] 1. Set up project structure and core interfaces
  - Create directory structure for services and models
  - Define API interfaces and data contracts
  - _Requirements: 1.1, 2.1_

- [ ] 2. Implement User model and validation
  - Create User entity with validation
  - Implement password hashing
  - Write unit tests for User model
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3. Implement Authentication Service
  - Create login endpoint
  - Implement session management
  - Add password validation
  - Write authentication tests
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 4. Implement User Registration
  - Create registration endpoint
  - Add email validation
  - Implement duplicate checking
  - Write registration tests
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 5. Create database schema and migrations
  - Design database tables
  - Create migration scripts
  - Set up database connections
  - _Requirements: All data requirements_""",

        "feature_description.txt": "User authentication system with registration, login, password reset, and profile management for a web application"
    }
    
    # Test diagram generation for each type
    diagram_types = [
        ("ER Diagram", "er"),
        ("Data Flow Diagram", "data_flow"),
        ("Class Diagram", "class"),
        ("Sequence Diagram", "sequence"),
        ("Architecture Diagram", "architecture"),
        ("AWS Architecture Diagram", "aws_architecture")
    ]
    
    print("📊 Testing Diagram Generation from Spec Content...")
    
    successful_generations = 0
    total_types = len(diagram_types)
    
    for name, diagram_type in diagram_types:
        print(f"\n--- {name} ---")
        try:
            diagram_code = diagram_generator.generate_diagram_by_type(
                diagram_type, sample_spec_content
            )
            
            if diagram_code and len(diagram_code.strip()) > 0:
                lines = len(diagram_code.split('\n'))
                print(f"✅ {name} generated successfully ({lines} lines)")
                
                # Save to file for inspection
                filename = f"spec_{diagram_type}_diagram.mmd"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(diagram_code)
                print(f"💾 Saved to {filename}")
                
                successful_generations += 1
            else:
                print(f"❌ {name} generation failed - empty result")
                
        except Exception as e:
            print(f"❌ {name} generation error: {e}")
    
    # Test spec content detection
    print(f"\n🔍 Testing Spec Content Detection...")
    is_spec = diagram_generator._is_spec_content(sample_spec_content)
    print(f"Spec content detected: {'✅ Yes' if is_spec else '❌ No'}")
    
    # Test AWS component extraction from specs
    print(f"\n☁️ Testing AWS Component Extraction from Specs...")
    aws_components = diagram_generator._extract_aws_components_from_specs(
        sample_spec_content.get('requirements.md', ''),
        sample_spec_content.get('design.md', ''),
        sample_spec_content.get('feature_description.txt', '')
    )
    print(f"AWS components found: {aws_components}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Spec Diagram Generation Results:")
    print(f"✅ Successful generations: {successful_generations}/{total_types}")
    print(f"✅ Spec content detection: {'Working' if is_spec else 'Failed'}")
    print(f"✅ AWS component extraction: {len(aws_components)} components found")
    
    print(f"\n📁 Generated Files:")
    for _, diagram_type in diagram_types:
        print(f"  - spec_{diagram_type}_diagram.mmd")
    
    print(f"\n🔗 View diagrams at: https://mermaid.live")
    
    return successful_generations == total_types and is_spec

def main():
    """Run spec diagram generation tests"""
    print("🚀 OpenFlux Spec-Based Diagram Generation Test")
    print("=" * 60)
    
    success = test_spec_diagram_generation()
    
    if success:
        print("\n🎉 All spec diagram generation tests passed!")
        print("✅ Users can now generate diagrams directly from spec documents")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()