"""
JIRA Integration Client for creating and managing tickets
"""
import requests
import json
import base64
from typing import Dict, List, Optional, Any
import streamlit as st
from datetime import datetime

class JiraClient:
    """JIRA API client for ticket management"""
    
    def __init__(self):
        self.base_url = None
        self.auth_token = None
        self.username = None
        self.project_key = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def configure(self, base_url: str, username: str, api_token: str, project_key: str) -> bool:
        """Configure JIRA connection settings"""
        try:
            self.base_url = base_url.rstrip('/')
            self.username = username
            self.project_key = project_key
            
            # Create basic auth token
            auth_string = f"{username}:{api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_token = base64.b64encode(auth_bytes).decode('ascii')
            
            self.session.headers.update({
                'Authorization': f'Basic {auth_token}'
            })
            
            # Test connection
            return self.test_connection()
            
        except Exception as e:
            st.error(f"JIRA configuration failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test JIRA connection"""
        try:
            if not self.base_url:
                return False
                
            response = self.session.get(f"{self.base_url}/rest/api/2/myself")
            
            if response.status_code == 200:
                user_info = response.json()
                st.success(f"✅ Connected to JIRA as {user_info.get('displayName', self.username)}")
                return True
            else:
                st.error(f"❌ JIRA connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            st.error(f"❌ JIRA connection test failed: {e}")
            return False
    
    def get_projects(self) -> List[Dict]:
        """Get available JIRA projects"""
        try:
            if not self.base_url:
                return []
                
            response = self.session.get(f"{self.base_url}/rest/api/2/project")
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to get projects: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error getting projects: {e}")
            return []
    
    def get_issue_types(self, project_key: str = None) -> List[Dict]:
        """Get available issue types for a project"""
        try:
            if not self.base_url:
                return []
            
            project = project_key or self.project_key
            if not project:
                return []
                
            response = self.session.get(f"{self.base_url}/rest/api/2/project/{project}")
            
            if response.status_code == 200:
                project_data = response.json()
                return project_data.get('issueTypes', [])
            else:
                st.error(f"Failed to get issue types: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error getting issue types: {e}")
            return []
    
    def create_ticket(self, summary: str, description: str, issue_type: str = "Task", 
                     priority: str = "Medium", labels: List[str] = None) -> Optional[Dict]:
        """Create a JIRA ticket"""
        try:
            if not all([self.base_url, self.project_key]):
                st.error("JIRA not properly configured")
                return None
            
            # Prepare ticket data
            ticket_data = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type}
                }
            }
            
            # Add priority if specified
            if priority:
                ticket_data["fields"]["priority"] = {"name": priority}
            
            # Add labels if specified
            if labels:
                ticket_data["fields"]["labels"] = labels
            
            response = self.session.post(
                f"{self.base_url}/rest/api/2/issue",
                data=json.dumps(ticket_data)
            )
            
            if response.status_code == 201:
                ticket = response.json()
                return {
                    "key": ticket["key"],
                    "id": ticket["id"],
                    "url": f"{self.base_url}/browse/{ticket['key']}"
                }
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        error_msg = "; ".join([f"{k}: {v}" for k, v in error_data["errors"].items()])
                except:
                    pass
                st.error(f"Failed to create ticket: {response.status_code} - {error_msg}")
                return None
                
        except Exception as e:
            st.error(f"Error creating ticket: {e}")
            return None
    
    def create_tickets_from_tasks(self, tasks_markdown: str, issue_type: str = "Task") -> List[Dict]:
        """Create JIRA tickets from OpenFlux tasks markdown"""
        try:
            tickets_created = []
            
            # Parse tasks from markdown
            tasks = self.parse_tasks_from_markdown(tasks_markdown)
            
            for task in tasks:
                # Create ticket for each main task
                ticket = self.create_ticket(
                    summary=task["title"],
                    description=task["description"],
                    issue_type=issue_type,
                    priority=task.get("priority", "Medium"),
                    labels=["openflux-generated", "implementation"]
                )
                
                if ticket:
                    tickets_created.append({
                        "task": task["title"],
                        "ticket": ticket
                    })
            
            return tickets_created
            
        except Exception as e:
            st.error(f"Error creating tickets from tasks: {e}")
            return []
    
    def parse_tasks_from_markdown(self, markdown: str) -> List[Dict]:
        """Parse tasks from OpenFlux markdown format"""
        tasks = []
        current_task = None
        
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Main task (- [ ] 1. Task title)
            if line.startswith('- [ ]') and '. ' in line:
                if current_task:
                    tasks.append(current_task)
                
                # Extract task number and title
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    task_num = parts[0].replace('- [ ]', '').strip()
                    title = parts[1].strip()
                    
                    current_task = {
                        "number": task_num,
                        "title": title,
                        "description": "",
                        "subtasks": [],
                        "requirements": [],
                        "priority": "Medium"
                    }
            
            # Sub-task (  - [ ] 1.1 Sub-task title)
            elif line.startswith('  - [ ]') and current_task:
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    subtask_num = parts[0].replace('- [ ]', '').strip()
                    subtask_title = parts[1].strip()
                    current_task["subtasks"].append({
                        "number": subtask_num,
                        "title": subtask_title
                    })
            
            # Description lines (start with - but not checkbox)
            elif line.startswith('    -') and current_task:
                desc_line = line.replace('    -', '').strip()
                if desc_line.startswith('_Requirements:'):
                    # Extract requirements
                    req_text = desc_line.replace('_Requirements:', '').replace('_', '').strip()
                    current_task["requirements"] = [r.strip() for r in req_text.split(',')]
                else:
                    # Add to description
                    if current_task["description"]:
                        current_task["description"] += "\n"
                    current_task["description"] += f"• {desc_line}"
        
        # Add the last task
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def get_ticket_status(self, ticket_key: str) -> Optional[Dict]:
        """Get status of a JIRA ticket"""
        try:
            if not self.base_url:
                return None
                
            response = self.session.get(f"{self.base_url}/rest/api/2/issue/{ticket_key}")
            
            if response.status_code == 200:
                issue = response.json()
                return {
                    "key": issue["key"],
                    "status": issue["fields"]["status"]["name"],
                    "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned",
                    "summary": issue["fields"]["summary"],
                    "url": f"{self.base_url}/browse/{issue['key']}"
                }
            else:
                return None
                
        except Exception as e:
            st.error(f"Error getting ticket status: {e}")
            return None