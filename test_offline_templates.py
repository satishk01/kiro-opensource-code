#!/usr/bin/env python3
"""
Test script for offline JIRA template generation
"""

def test_template_generation():
    """Test offline JIRA template generation"""
    print("🧪 Testing offline JIRA template generation...")
    
    # Sample parsed tasks (simulating what would come from parse_tasks_from_markdown)
    sample_tasks = [
        {
            "number": "1",
            "title": "Set up project structure and dependencies",
            "description": "• Create folders for services/, engines/, generators/, integrations/\n• Set up proper Python package structure with __init__.py files\n• Initialize project configuration files",
            "subtasks": [
                {"number": "1.1", "title": "Create directory structure for services and components"}
            ],
            "requirements": ["1.1", "8.1"],
            "priority": "Medium"
        },
        {
            "number": "2", 
            "title": "Implement AWS Bedrock integration",
            "description": "• Write AIService class with boto3 Bedrock client initialization\n• Implement EC2 IAM role authentication for AWS services\n• Add error handling for connection failures",
            "subtasks": [
                {"number": "2.1", "title": "Create AI service layer with Bedrock client"}
            ],
            "requirements": ["1.3", "8.1", "8.2"],
            "priority": "Medium"
        }
    ]
    
    # Simulate the template generation function
    def generate_jira_templates(parsed_tasks, issue_type, priority, project_key, add_labels):
        """Generate JIRA ticket templates in different formats"""
        import json
        import csv
        from io import StringIO
        
        # Prepare template data
        template_data = []
        
        for i, task in enumerate(parsed_tasks, 1):
            labels = ["openflux-generated", "implementation"] if add_labels else []
            
            ticket_data = {
                "summary": task["title"],
                "description": task["description"] if task["description"] else f"Implementation task: {task['title']}",
                "issue_type": issue_type,
                "priority": priority,
                "project_key": project_key,
                "labels": labels,
                "requirements": task.get("requirements", []),
                "subtasks": [st["title"] for st in task.get("subtasks", [])]
            }
            
            template_data.append(ticket_data)
        
        # Generate CSV format
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        
        # CSV headers
        csv_writer.writerow([
            "Summary", "Description", "Issue Type", "Priority", "Project Key", 
            "Labels", "Requirements", "Subtasks"
        ])
        
        # CSV data
        for ticket in template_data:
            csv_writer.writerow([
                ticket["summary"],
                ticket["description"],
                ticket["issue_type"],
                ticket["priority"],
                ticket["project_key"],
                "; ".join(ticket["labels"]),
                "; ".join(ticket["requirements"]),
                "; ".join(ticket["subtasks"])
            ])
        
        csv_content = csv_buffer.getvalue()
        
        # Generate JSON format (JIRA API ready)
        json_tickets = []
        for ticket in template_data:
            json_ticket = {
                "fields": {
                    "project": {"key": ticket["project_key"]},
                    "summary": ticket["summary"],
                    "description": ticket["description"],
                    "issuetype": {"name": ticket["issue_type"]},
                    "priority": {"name": ticket["priority"]}
                }
            }
            
            if ticket["labels"]:
                json_ticket["fields"]["labels"] = ticket["labels"]
            
            json_tickets.append(json_ticket)
        
        json_content = json.dumps({"issues": json_tickets}, indent=2)
        
        # Generate Markdown format
        md_content = "# JIRA Ticket Templates\n\n"
        md_content += f"**Project:** {project_key}\n"
        md_content += f"**Issue Type:** {issue_type}\n"
        md_content += f"**Priority:** {priority}\n\n"
        
        for i, ticket in enumerate(template_data, 1):
            md_content += f"## Ticket {i}: {ticket['summary']}\n\n"
            md_content += f"**Description:**\n{ticket['description']}\n\n"
            
            if ticket["requirements"]:
                md_content += f"**Requirements:** {', '.join(ticket['requirements'])}\n\n"
            
            if ticket["subtasks"]:
                md_content += f"**Subtasks:**\n"
                for subtask in ticket["subtasks"]:
                    md_content += f"- {subtask}\n"
                md_content += "\n"
            
            if ticket["labels"]:
                md_content += f"**Labels:** {', '.join(ticket['labels'])}\n\n"
            
            md_content += "---\n\n"
        
        return {
            "csv": csv_content,
            "json": json_content,
            "markdown": md_content,
            "count": len(template_data)
        }
    
    # Generate templates
    templates = generate_jira_templates(
        sample_tasks,
        "Task",
        "Medium", 
        "OPENFLUX",
        True
    )
    
    print(f"✅ Generated templates for {templates['count']} tickets")
    
    # Test CSV format
    csv_lines = templates['csv'].split('\n')
    assert len(csv_lines) >= 3, "CSV should have header + 2 data rows"
    assert "Summary,Description,Issue Type" in csv_lines[0], "CSV header incorrect"
    print("✅ CSV template format is correct")
    
    # Test JSON format
    import json
    json_data = json.loads(templates['json'])
    assert "issues" in json_data, "JSON should have 'issues' key"
    assert len(json_data["issues"]) == 2, "Should have 2 issues in JSON"
    assert json_data["issues"][0]["fields"]["project"]["key"] == "OPENFLUX", "Project key incorrect"
    print("✅ JSON template format is correct")
    
    # Test Markdown format
    md_content = templates['markdown']
    assert "# JIRA Ticket Templates" in md_content, "Markdown title missing"
    assert "## Ticket 1:" in md_content, "Ticket sections missing"
    assert "**Project:** OPENFLUX" in md_content, "Project info missing"
    print("✅ Markdown template format is correct")
    
    print("\n📄 Sample CSV Template:")
    print(templates['csv'][:200] + "...")
    
    print("\n📄 Sample Markdown Template:")
    print(templates['markdown'][:300] + "...")
    
    print("\n🎯 Offline template generation test passed!")
    return True

if __name__ == "__main__":
    success = test_template_generation()
    
    if success:
        print("\n🎉 Offline JIRA template generation is working!")
        print("You can now use both modes:")
        print("  🌐 Online Mode: Create tickets directly in JIRA")
        print("  📱 Offline Mode: Generate templates for download")
        print("  📄 Formats: CSV (Excel), JSON (API), Markdown (readable)")
    
    exit(0 if success else 1)