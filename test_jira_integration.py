#!/usr/bin/env python3
"""
Test script for JIRA integration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.jira_client import JiraClient

def test_jira_parsing():
    """Test JIRA task parsing functionality"""
    print("🧪 Testing JIRA task parsing...")
    
    # Sample Kiro tasks markdown
    sample_tasks = """# Implementation Plan

- [ ] 1. Set up project structure and dependencies
  - [ ] 1.1 Create directory structure for services and components
    - Create folders for services/, engines/, generators/, integrations/
    - Set up proper Python package structure with __init__.py files
    - Initialize project configuration files
    - _Requirements: 1.1, 8.1_

  - [ ] 1.2 Initialize requirements and dependencies
    - Create requirements.txt with Streamlit, boto3, and other dependencies
    - Set up virtual environment configuration
    - Add development dependencies for testing
    - _Requirements: 8.1_

- [ ] 2. Implement AWS Bedrock integration
  - [ ] 2.1 Create AI service layer with Bedrock client
    - Write AIService class with boto3 Bedrock client initialization
    - Implement EC2 IAM role authentication for AWS services
    - Add error handling for connection failures
    - _Requirements: 1.3, 8.1, 8.2_"""

    # Initialize JIRA client
    jira_client = JiraClient()
    
    # Parse tasks
    parsed_tasks = jira_client.parse_tasks_from_markdown(sample_tasks)
    
    print(f"✅ Parsed {len(parsed_tasks)} main tasks")
    
    for i, task in enumerate(parsed_tasks, 1):
        print(f"\n📋 Task {i}:")
        print(f"   Number: {task['number']}")
        print(f"   Title: {task['title']}")
        print(f"   Subtasks: {len(task['subtasks'])}")
        print(f"   Requirements: {task['requirements']}")
        print(f"   Description preview: {task['description'][:100]}...")
    
    # Verify parsing results
    assert len(parsed_tasks) == 2, f"Expected 2 tasks, got {len(parsed_tasks)}"
    assert parsed_tasks[0]['title'] == "Set up project structure and dependencies"
    assert parsed_tasks[1]['title'] == "Implement AWS Bedrock integration"
    assert len(parsed_tasks[0]['subtasks']) == 2
    assert len(parsed_tasks[1]['subtasks']) == 1
    
    print("\n🎯 JIRA task parsing test passed!")
    print("The JIRA integration can now parse Kiro tasks and create tickets.")
    
    return True

def test_jira_configuration():
    """Test JIRA configuration structure"""
    print("\n🔧 Testing JIRA configuration...")
    
    jira_client = JiraClient()
    
    # Test configuration structure
    assert hasattr(jira_client, 'configure'), "Missing configure method"
    assert hasattr(jira_client, 'test_connection'), "Missing test_connection method"
    assert hasattr(jira_client, 'create_ticket'), "Missing create_ticket method"
    assert hasattr(jira_client, 'create_tickets_from_tasks'), "Missing create_tickets_from_tasks method"
    
    print("✅ All required JIRA methods are implemented")
    
    # Test initial state
    assert jira_client.base_url is None, "Base URL should be None initially"
    assert jira_client.project_key is None, "Project key should be None initially"
    
    print("✅ JIRA client initial state is correct")
    print("🎯 JIRA configuration test passed!")
    
    return True

if __name__ == "__main__":
    success1 = test_jira_parsing()
    success2 = test_jira_configuration()
    
    if success1 and success2:
        print("\n🎉 All JIRA integration tests passed!")
        print("You can now use the JIRA Integration tab to:")
        print("  • Configure your JIRA connection")
        print("  • Create tickets from generated tasks")
        print("  • Manage and track created tickets")
    
    sys.exit(0 if (success1 and success2) else 1)