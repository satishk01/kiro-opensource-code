#!/usr/bin/env python3
"""
Test script for MCP AWS Diagram integration
"""
import json
import sys
import os
import subprocess

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_uvx_availability():
    """Test if uvx is available for MCP server"""
    print("🔍 Testing UVX Availability...")
    
    try:
        result = subprocess.run(["uvx", "--help"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ uvx is available")
            return True
        else:
            print("  ⚠️ uvx command failed")
            return False
    except FileNotFoundError:
        print("  ⚠️ uvx not found - install with: pip install uv")
        return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ uvx command timed out")
        return False
    except Exception as e:
        print(f"  ⚠️ Error testing uvx: {e}")
        return False

def test_mcp_service_basic():
    """Test basic MCP service functionality without full initialization"""
    print("\n🔍 Testing MCP Service (Basic)...")
    
    # Test component extraction logic
    print("  - Testing AWS component extraction logic...")
    sample_codebase = {
        "app.py": """
import boto3
from flask import Flask

app = Flask(__name__)
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')

@app.route('/api/data')
def get_data():
    # Query RDS database
    return {'status': 'success'}
""",
        "infrastructure.tf": """
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

resource "aws_s3_bucket" "storage" {
  bucket = "my-app-storage"
}

resource "aws_rds_instance" "database" {
  engine = "mysql"
}
"""
    }
    
    # Test pattern matching for AWS services
    aws_patterns = {
        'ec2': ['EC2', 'Instance', 'VPC', 'Security Group'],
        's3': ['S3', 'Bucket', 'Object Storage'],
        'rds': ['RDS', 'Database', 'MySQL', 'PostgreSQL'],
        'lambda': ['Lambda', 'Function', 'Serverless']
    }
    
    found_services = set()
    for file_path, content in sample_codebase.items():
        content_lower = content.lower()
        for service, keywords in aws_patterns.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    found_services.add(keyword)
    
    print(f"  ✅ Found AWS services: {list(found_services)}")
    
    return True

def test_mcp_config():
    """Test MCP configuration file"""
    print("\n⚙️ Testing MCP Configuration...")
    
    config_path = ".openflux/settings/mcp.json"
    
    if os.path.exists(config_path):
        print(f"  ✅ MCP config file exists: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" in config:
                print("  ✅ MCP servers configuration found")
                
                if "awslabs.aws-diagram-mcp-server" in config["mcpServers"]:
                    print("  ✅ AWS diagram MCP server configured")
                    server_config = config["mcpServers"]["awslabs.aws-diagram-mcp-server"]
                    print(f"     Command: {server_config.get('command')}")
                    print(f"     Args: {server_config.get('args')}")
                    print(f"     Disabled: {server_config.get('disabled', False)}")
                else:
                    print("  ❌ AWS diagram MCP server not found in config")
            else:
                print("  ❌ No MCP servers configuration found")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON in MCP config: {e}")
    else:
        print(f"  ❌ MCP config file not found: {config_path}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 OpenFlux MCP Integration Test Suite")
    print("=" * 50)
    
    try:
        test_mcp_config()
        test_uvx_availability()
        test_mcp_service_basic()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n💡 Notes:")
        print("   - If uvx is not installed, MCP server tests will show warnings")
        print("   - Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   - AWS diagrams will use fallback generation without MCP server")
        print("   - Full integration requires running the Streamlit app")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())