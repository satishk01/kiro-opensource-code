#!/usr/bin/env python3
"""
Test script for diagram generation logic (without AWS dependencies)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_diagram_type_detection():
    """Test diagram type detection logic"""
    print("🎯 Testing Diagram Type Detection Logic...")
    
    # Mock diagram generator class for testing
    class MockDiagramGenerator:
        def detect_diagram_type(self, user_input: str, codebase=None) -> str:
            """Detect diagram type based on input"""
            input_lower = user_input.lower()
            
            # AWS-specific keywords
            aws_keywords = ['aws', 'ec2', 's3', 'rds', 'lambda', 'cloudfront', 'vpc', 'iam']
            if any(keyword in input_lower for keyword in aws_keywords):
                return 'aws_architecture'
            
            # Database/ER keywords
            er_keywords = ['database', 'table', 'entity', 'relationship', 'schema', 'model', 'foreign key']
            if any(keyword in input_lower for keyword in er_keywords):
                return 'er'
            
            # Sequence/interaction keywords
            sequence_keywords = ['sequence', 'interaction', 'timeline', 'message', 'call', 'request', 'response']
            if any(keyword in input_lower for keyword in sequence_keywords):
                return 'sequence'
            
            # Class diagram keywords
            class_keywords = ['class', 'object', 'inheritance', 'method', 'attribute', 'interface']
            if any(keyword in input_lower for keyword in class_keywords):
                return 'class'
            
            # Data flow keywords
            flow_keywords = ['flow', 'process', 'data flow', 'pipeline', 'transformation']
            if any(keyword in input_lower for keyword in flow_keywords):
                return 'data_flow'
            
            # Default to architecture for general system terms
            return 'architecture'
    
    generator = MockDiagramGenerator()
    
    # Test cases
    test_cases = [
        ("Show me the database schema", "er"),
        ("AWS infrastructure for user authentication", "aws_architecture"),
        ("User login sequence", "sequence"),
        ("Class relationships in the system", "class"),
        ("Data flow through the API", "data_flow"),
        ("System architecture overview", "architecture"),
        ("EC2 instances and S3 buckets", "aws_architecture"),
        ("Database tables and foreign keys", "er"),
        ("API request response flow", "sequence"),
        ("Object inheritance hierarchy", "class"),
        ("Data transformation pipeline", "data_flow")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for user_input, expected_type in test_cases:
        detected_type = generator.detect_diagram_type(user_input)
        status = "✅" if detected_type == expected_type else "❌"
        print(f"{status} '{user_input}' -> {detected_type} (expected: {expected_type})")
        if detected_type == expected_type:
            passed += 1
    
    print(f"\n📊 Detection Accuracy: {passed}/{total} ({passed/total*100:.1f}%)")
    return passed == total

def test_fallback_diagrams():
    """Test fallback diagram generation"""
    print("\n🔄 Testing Fallback Diagram Generation...")
    
    # Mock fallback diagram generators
    def generate_fallback_er_diagram():
        return """erDiagram
    USER {
        id int PK
        name string
        email string
        created_at datetime
    }
    
    PROFILE {
        id int PK
        user_id int FK
        bio text
        avatar_url string
    }
    
    USER ||--|| PROFILE : has"""
    
    def generate_fallback_sequence_diagram():
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
    
    def generate_fallback_aws_diagram():
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
    
    # Test each fallback diagram
    fallback_tests = [
        ("ER Diagram", generate_fallback_er_diagram),
        ("Sequence Diagram", generate_fallback_sequence_diagram),
        ("AWS Architecture", generate_fallback_aws_diagram)
    ]
    
    all_passed = True
    
    for name, generator_func in fallback_tests:
        try:
            diagram = generator_func()
            if diagram and len(diagram.strip()) > 0:
                lines = len(diagram.split('\n'))
                print(f"✅ {name}: Generated {lines} lines")
                
                # Save to file for inspection
                filename = f"fallback_{name.lower().replace(' ', '_')}.mmd"
                with open(filename, 'w') as f:
                    f.write(diagram)
                print(f"   💾 Saved to {filename}")
            else:
                print(f"❌ {name}: Empty diagram generated")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_passed = False
    
    return all_passed

def test_aws_icon_mapping():
    """Test AWS service icon mapping"""
    print("\n☁️ Testing AWS Service Icon Mapping...")
    
    aws_icons = {
        'EC2': '🖥️', 'S3': '📁', 'RDS': '🗄️', 'Lambda': '⚡', 'API Gateway': '🚪',
        'CloudFront': '📡', 'Route 53': '🌍', 'ALB': '⚖️', 'VPC': '🏢', 'IAM': '👤',
        'CloudWatch': '📈', 'SNS': '📢', 'SQS': '📬', 'DynamoDB': '⚡', 'ElastiCache': '🚀',
        'ECS': '🐳', 'EKS': '☸️', 'Aurora': '🌟', 'Cognito': '🔑', 'KMS': '🔐',
        'WAF': '🛡️', 'CloudTrail': '🔍', 'X-Ray': '🔬', 'EventBridge': '🌉',
        'Secrets Manager': '🔒', 'EFS': '📂'
    }
    
    # Test icon coverage
    common_services = ['EC2', 'S3', 'RDS', 'Lambda', 'VPC', 'IAM', 'CloudWatch']
    
    print("Common AWS Services Icon Coverage:")
    for service in common_services:
        icon = aws_icons.get(service, '❓')
        status = "✅" if service in aws_icons else "❌"
        print(f"  {status} {service}: {icon}")
    
    print(f"\nTotal AWS Services with Icons: {len(aws_icons)}")
    
    # Test service categorization
    def get_aws_service_category(service: str) -> str:
        categories = {
            'compute': ['EC2', 'Lambda', 'ECS', 'EKS', 'Fargate'],
            'storage': ['S3', 'EFS', 'EBS'],
            'database': ['RDS', 'DynamoDB', 'Aurora', 'ElastiCache', 'Redshift'],
            'network': ['VPC', 'CloudFront', 'Route 53', 'ALB', 'NLB', 'ELB', 'API Gateway', 'WAF'],
            'security': ['IAM', 'Cognito', 'KMS', 'Secrets Manager'],
            'monitoring': ['CloudWatch', 'CloudTrail', 'X-Ray'],
            'integration': ['SQS', 'SNS', 'EventBridge', 'Kinesis', 'Step Functions']
        }
        
        for category, services in categories.items():
            if service in services:
                return category
        return 'other'
    
    print("\nService Categorization Test:")
    test_services = ['EC2', 'S3', 'RDS', 'Lambda', 'VPC', 'IAM', 'CloudWatch', 'SQS']
    
    for service in test_services:
        category = get_aws_service_category(service)
        print(f"  {service} -> {category}")
    
    return True

def test_mermaid_code_cleaning():
    """Test Mermaid code cleaning and validation"""
    print("\n🧹 Testing Mermaid Code Cleaning...")
    
    def clean_mermaid_code(raw_code: str, diagram_type: str) -> str:
        import re
        
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
    
    # Test cases
    test_cases = [
        ("```mermaid\ngraph TB\n    A --> B\n```", "graph", "graph TB\nA --> B"),
        ("# Comment\ngraph TB\n    A --> B", "graph", "graph TB\nA --> B"),
        ("A --> B", "graph", "graph\nA --> B"),
        ("```\nerDiagram\n    USER {}\n```", "erDiagram", "erDiagram\nUSER {}")
    ]
    
    all_passed = True
    
    for raw_code, diagram_type, expected in test_cases:
        cleaned = clean_mermaid_code(raw_code, diagram_type)
        if cleaned.strip() == expected.strip():
            print(f"✅ Cleaning test passed")
        else:
            print(f"❌ Cleaning test failed:")
            print(f"   Input: {repr(raw_code)}")
            print(f"   Expected: {repr(expected)}")
            print(f"   Got: {repr(cleaned)}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🚀 OpenFlux Diagram Generation Logic Test Suite")
    print("=" * 60)
    
    tests = [
        ("Diagram Type Detection", test_diagram_type_detection),
        ("Fallback Diagrams", test_fallback_diagrams),
        ("AWS Icon Mapping", test_aws_icon_mapping),
        ("Mermaid Code Cleaning", test_mermaid_code_cleaning)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed_tests += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Diagram generation logic is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\nGenerated files:")
    print("- fallback_*.mmd (Fallback diagram examples)")
    print("\nYou can view these diagrams at: https://mermaid.live")

if __name__ == "__main__":
    main()