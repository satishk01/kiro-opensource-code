#!/usr/bin/env python3
"""
Test script for AWS Labs MCP server integration
"""

import sys
import subprocess
from services.mcp_service import MCPService

def test_aws_labs_mcp_server():
    """Test AWS Labs MCP server functionality"""
    print("🔍 Testing AWS Labs MCP Server Integration...")
    print("=" * 50)
    
    # Initialize MCP service
    mcp_service = MCPService()
    
    # Test server availability
    print("1. Testing server availability...")
    test_result = mcp_service.test_aws_labs_mcp_server()
    
    if test_result["available"]:
        print("✅ AWS Labs MCP Server is available")
        if test_result["version"]:
            print(f"📦 Version: {test_result['version']}")
        
        print(f"🎯 Capabilities: {', '.join(test_result['capabilities'])}")
    else:
        print("❌ AWS Labs MCP Server is not available")
        if test_result["error"]:
            print(f"Error: {test_result['error']}")
        print("\n💡 To install:")
        print("pip install uv")
        print("uvx awslabs.aws-documentation-mcp-server@latest --help")
    
    print("\n" + "=" * 50)
    
    # Test diagram generation
    print("2. Testing diagram generation...")
    
    test_components = ["EC2", "RDS", "S3", "API Gateway", "Lambda", "CloudFront"]
    test_connections = [
        {"from": "CloudFront", "to": "S3", "type": "serves", "description": "Serves static content"},
        {"from": "API Gateway", "to": "Lambda", "type": "triggers", "description": "Triggers functions"},
        {"from": "Lambda", "to": "RDS", "type": "queries", "description": "Database queries"},
        {"from": "EC2", "to": "RDS", "type": "connects", "description": "Database connections"}
    ]
    
    diagram = mcp_service.generate_aws_architecture_diagram(
        components=test_components,
        connections=test_connections,
        title="Test AWS Architecture"
    )
    
    if diagram and len(diagram.strip()) > 100:
        print("✅ Diagram generation successful")
        print(f"📊 Generated diagram length: {len(diagram)} characters")
        print("\n📋 Sample diagram preview:")
        print("-" * 30)
        print(diagram[:300] + "..." if len(diagram) > 300 else diagram)
        print("-" * 30)
    else:
        print("❌ Diagram generation failed or returned minimal content")
        if diagram:
            print(f"Received: {diagram[:100]}...")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_aws_labs_mcp_server()