#!/usr/bin/env python3
"""
Test script for enhanced diagram generation with AWS MCP server integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService
from services.mcp_service import MCPService
from generators.diagram_generator import DiagramGenerator

def test_mcp_server_connection():
    """Test AWS Labs MCP server connection"""
    print("🔗 Testing AWS Labs MCP Server Connection...")
    
    mcp_service = MCPService()
    test_result = mcp_service.test_aws_labs_mcp_server()
    
    print(f"Available: {test_result['available']}")
    if test_result['error']:
        print(f"Error: {test_result['error']}")
    if test_result['version']:
        print(f"Version: {test_result['version']}")
    if test_result['capabilities']:
        print(f"Capabilities: {', '.join(test_result['capabilities'])}")
    
    return test_result['available']

def test_diagram_generation():
    """Test all diagram types"""
    print("\n📊 Testing Diagram Generation...")
    
    # Initialize services
    ai_service = AIService()
    mcp_service = MCPService()
    diagram_generator = DiagramGenerator(ai_service, mcp_service)
    
    # Sample codebase for testing
    sample_codebase = {
        "models/user.py": """
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
    
    def save(self):
        pass
    
    def delete(self):
        pass

class Profile:
    def __init__(self, user_id, bio):
        self.user_id = user_id
        self.bio = bio
""",
        "api/auth.py": """
from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Authenticate user
    user = authenticate_user(username, password)
    if user:
        return jsonify({'token': generate_token(user)})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    user_data = request.json
    
    # Store user in RDS
    user = create_user(user_data)
    
    # Store profile image in S3
    if 'profile_image' in user_data:
        s3_client.put_object(
            Bucket='user-profiles',
            Key=f"profiles/{user.id}.jpg",
            Body=user_data['profile_image']
        )
    
    return jsonify({'user_id': user.id})
""",
        "services/user_service.py": """
import boto3
from models.user import User

class UserService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('users')
    
    def create_user(self, user_data):
        user = User(**user_data)
        self.table.put_item(Item=user.__dict__)
        return user
    
    def get_user(self, user_id):
        response = self.table.get_item(Key={'id': user_id})
        return response.get('Item')
    
    def update_user(self, user_id, updates):
        self.table.update_item(
            Key={'id': user_id},
            UpdateExpression='SET #name = :name, #email = :email',
            ExpressionAttributeNames={'#name': 'name', '#email': 'email'},
            ExpressionAttributeValues={':name': updates['name'], ':email': updates['email']}
        )
"""
    }
    
    # Test diagram type detection
    print("\n🎯 Testing Diagram Type Detection...")
    test_inputs = [
        ("Show me the database schema", "er"),
        ("AWS infrastructure for user authentication", "aws_architecture"),
        ("User login sequence", "sequence"),
        ("Class relationships in the system", "class"),
        ("Data flow through the API", "data_flow"),
        ("System architecture overview", "architecture")
    ]
    
    for user_input, expected_type in test_inputs:
        detected_type = diagram_generator.detect_diagram_type(user_input, sample_codebase)
        print(f"Input: '{user_input}' -> Detected: {detected_type} (Expected: {expected_type})")
    
    # Test each diagram type
    diagram_types = [
        ("ER Diagram", "er"),
        ("Data Flow Diagram", "data_flow"),
        ("Class Diagram", "class"),
        ("Sequence Diagram", "sequence"),
        ("Architecture Diagram", "architecture"),
        ("AWS Architecture Diagram", "aws_architecture")
    ]
    
    print("\n🔧 Testing Diagram Generation...")
    
    for name, diagram_type in diagram_types:
        print(f"\n--- {name} ---")
        try:
            diagram_code = diagram_generator.generate_diagram_by_type(
                diagram_type, sample_codebase
            )
            
            if diagram_code:
                print(f"✅ {name} generated successfully")
                print(f"Lines: {len(diagram_code.split(chr(10)))}")
                print(f"Preview: {diagram_code[:100]}...")
                
                # Save to file for inspection
                filename = f"test_output_{diagram_type}_diagram.mmd"
                with open(filename, 'w') as f:
                    f.write(diagram_code)
                print(f"💾 Saved to {filename}")
            else:
                print(f"❌ {name} generation failed")
                
        except Exception as e:
            print(f"❌ {name} generation error: {e}")

def test_aws_component_extraction():
    """Test AWS component extraction from codebase"""
    print("\n☁️ Testing AWS Component Extraction...")
    
    mcp_service = MCPService()
    
    aws_codebase = {
        "infrastructure/main.tf": """
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
}

resource "aws_s3_bucket" "data" {
  bucket = "my-app-data"
}

resource "aws_rds_instance" "database" {
  engine         = "mysql"
  instance_class = "db.t2.micro"
}

resource "aws_lambda_function" "processor" {
  function_name = "data-processor"
  runtime       = "python3.9"
}
""",
        "config/aws.py": """
import boto3

# Initialize AWS services
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')
rds = boto3.client('rds')
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
sqs = boto3.client('sqs')
""",
        "services/storage.py": """
import boto3

class StorageService:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
    
    def upload_file(self, file_data, bucket, key):
        return self.s3.put_object(Bucket=bucket, Key=key, Body=file_data)
    
    def store_metadata(self, table_name, item):
        table = self.dynamodb.Table(table_name)
        return table.put_item(Item=item)
"""
    }
    
    # Extract AWS components
    components = mcp_service.extract_aws_components_from_codebase(aws_codebase)
    print(f"Extracted AWS Components: {components}")
    
    # Extract connections
    connections = mcp_service.extract_connections_from_codebase(aws_codebase, components)
    print(f"Extracted Connections: {len(connections)} connections found")
    
    for conn in connections[:5]:  # Show first 5 connections
        print(f"  {conn['from']} -> {conn['to']}: {conn['description']}")
    
    # Test AWS diagram generation
    print("\n🏗️ Testing AWS Architecture Diagram Generation...")
    try:
        aws_diagram = mcp_service.generate_aws_architecture_diagram(
            components, connections, "Test AWS Architecture"
        )
        
        if aws_diagram:
            print("✅ AWS Architecture diagram generated successfully")
            print(f"Lines: {len(aws_diagram.split(chr(10)))}")
            
            # Save to file
            with open("test_output_aws_architecture.mmd", 'w') as f:
                f.write(aws_diagram)
            print("💾 Saved to test_output_aws_architecture.mmd")
        else:
            print("❌ AWS Architecture diagram generation failed")
            
    except Exception as e:
        print(f"❌ AWS diagram generation error: {e}")

def main():
    """Run all tests"""
    print("🚀 OpenFlux Enhanced Diagram Generation Test Suite")
    print("=" * 60)
    
    # Test MCP server connection
    mcp_available = test_mcp_server_connection()
    
    if not mcp_available:
        print("\n⚠️ AWS Labs MCP Server not available - testing fallback mode")
    
    # Test diagram generation
    test_diagram_generation()
    
    # Test AWS-specific functionality
    test_aws_component_extraction()
    
    print("\n✅ Test suite completed!")
    print("\nGenerated files:")
    print("- test_output_*_diagram.mmd (Mermaid diagram files)")
    print("\nYou can view these diagrams at: https://mermaid.live")

if __name__ == "__main__":
    main()