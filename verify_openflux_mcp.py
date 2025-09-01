#!/usr/bin/env python3
"""
Verify OpenFlux MCP Configuration Setup
"""

import os
import json
from pathlib import Path

def verify_openflux_mcp_config():
    """Verify OpenFlux MCP configuration is properly set up"""
    print("🔍 Verifying OpenFlux MCP Configuration")
    print("=" * 50)
    
    # Expected configuration path
    config_path = ".openflux/settings/mcp.json"
    
    print(f"📁 Expected config path: {config_path}")
    
    # Check if directory exists
    config_dir = Path(config_path).parent
    if config_dir.exists():
        print(f"✅ Configuration directory exists: {config_dir}")
    else:
        print(f"❌ Configuration directory missing: {config_dir}")
        print(f"💡 Please create the directory: {config_dir}")
        return False
    
    # Check if config file exists
    if os.path.exists(config_path):
        print(f"✅ Configuration file exists: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                if not content:
                    print("❌ Configuration file is empty")
                    return False
                config = json.loads(content)
            
            print("📋 Configuration content:")
            print(json.dumps(config, indent=2))
            
            # Verify AWS Labs MCP server configuration
            if "mcpServers" in config:
                servers = config["mcpServers"]
                
                if "awslabs.aws-diagram-mcp-server" in servers:
                    aws_server = servers["awslabs.aws-diagram-mcp-server"]
                    print("\n✅ AWS Labs MCP server configured:")
                    print(f"   Command: {aws_server.get('command', 'Not set')}")
                    print(f"   Args: {aws_server.get('args', 'Not set')}")
                    print(f"   Disabled: {aws_server.get('disabled', 'Not set')}")
                    
                    # Check required fields
                    required_fields = ['command', 'args']
                    missing_fields = [field for field in required_fields if field not in aws_server]
                    
                    if missing_fields:
                        print(f"❌ Missing required fields: {missing_fields}")
                        return False
                    else:
                        print("✅ All required fields present")
                        return True
                else:
                    print("❌ AWS Labs MCP server not configured")
                    return False
            else:
                print("❌ No MCP servers configured")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return False
    else:
        print(f"❌ Configuration file missing: {config_path}")
        print("\n💡 Expected configuration:")
        expected_config = {
            "mcpServers": {
                "awslabs.aws-diagram-mcp-server": {
                    "command": "uvx",
                    "args": ["awslabs.aws-diagram-mcp-server"],
                    "env": {
                        "FASTMCP_LOG_LEVEL": "ERROR"
                    },
                    "autoApprove": [],
                    "disabled": False
                }
            }
        }
        print(json.dumps(expected_config, indent=2))
        return False

def test_uvx_availability():
    """Test if uvx command is available"""
    print("\n🔧 Testing uvx availability...")
    
    try:
        import subprocess
        result = subprocess.run(["uvx", "--help"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ uvx command is available")
            return True
        else:
            print("❌ uvx command failed")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ uvx command not found")
        print("💡 Please install uv and uvx first:")
        print("   - Visit: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    except subprocess.TimeoutExpired:
        print("❌ uvx command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing uvx: {e}")
        return False

def test_aws_mcp_server():
    """Test AWS Labs MCP server availability"""
    print("\n☁️ Testing AWS Labs MCP server...")
    
    try:
        import subprocess
        result = subprocess.run([
            "uvx", 
            "awslabs.aws-diagram-mcp-server",
            "--help"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ AWS Labs MCP server is available")
            return True
        else:
            print("❌ AWS Labs MCP server failed")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ uvx command not found")
        return False
    except subprocess.TimeoutExpired:
        print("❌ AWS Labs MCP server test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing AWS Labs MCP server: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 OpenFlux MCP Configuration Verification")
    print("=" * 60)
    
    tests = [
        ("MCP Configuration", verify_openflux_mcp_config),
        ("uvx Availability", test_uvx_availability),
        ("AWS Labs MCP Server", test_aws_mcp_server)
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
    print(f"📊 Verification Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 OpenFlux MCP configuration is ready!")
        print("✅ You can now use enhanced diagram generation with AWS MCP server")
    else:
        print("⚠️ Some tests failed. Please check the output above for details.")
        
        if passed_tests == 0:
            print("\n📋 Setup Instructions:")
            print("1. Create directory: .openflux/settings/")
            print("2. Create file: .openflux/settings/mcp.json with the AWS Labs MCP server configuration")
            print("3. Install uv and uvx: https://docs.astral.sh/uv/getting-started/installation/")
            print("4. Run this script again to verify")

if __name__ == "__main__":
    main()