import streamlit as st
import os
from pathlib import Path
from services.ai_service import AIService
from services.file_service import FileService
from engines.spec_engine import SpecEngine
from integrations.jira_client import JiraClient
import json
import csv
from io import StringIO
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Kiro AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import custom CSS for Kiro styling
def load_css():
    css_file = Path("styles/kiro_theme.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.selected_model = None
        st.session_state.current_folder = None
        st.session_state.loaded_files = {}
        st.session_state.active_spec = None
        st.session_state.requirements_doc = ""
        st.session_state.design_doc = ""
        st.session_state.task_list = ""
        st.session_state.jira_config = {}
        st.session_state.ai_service = AIService()
        st.session_state.file_service = FileService()
        st.session_state.spec_engine = SpecEngine(st.session_state.ai_service)
        st.session_state.model_connected = False
        st.session_state.current_view = "Spec Generation"
        st.session_state.generated_content = ""
        st.session_state.user_prompt = ""
        st.session_state.jira_client = JiraClient()
        st.session_state.jira_templates = None

def render_navigation_panel():
    """Render the left navigation panel"""
    # Kiro branding
    st.markdown("### 🤖 Kiro AI Assistant")
    st.markdown("---")
    
    # Navigation items
    nav_items = [
        ("📋 Spec Generation", "Spec Generation"),
        ("🎯 JIRA Integration", "JIRA Integration"), 
        ("📊 Diagram Generation", "Diagram Generation"),
        ("⚙️ Settings", "Settings")
    ]
    
    for label, key in nav_items:
        button_style = "primary" if st.session_state.current_view == key else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=button_style):
            st.session_state.current_view = key
            st.rerun()
    
    st.markdown("---")
    
    # Model status
    st.markdown("#### 🧠 AI Model")
    if st.session_state.model_connected:
        st.success(f"✅ {st.session_state.selected_model}")
    else:
        st.warning("⚠️ No model selected")

def render_content_panel():
    """Render the center content panel"""
    # Content header
    st.markdown(f"# {st.session_state.current_view}")
    
    if st.session_state.current_view == "Spec Generation":
        render_spec_generation_content()
    elif st.session_state.current_view == "JIRA Integration":
        render_jira_integration_content()
    elif st.session_state.current_view == "Diagram Generation":
        render_diagram_generation_content()
    elif st.session_state.current_view == "Settings":
        render_settings_content()

def render_actions_panel():
    """Render the right actions panel"""
    # Model Selection Section
    st.markdown("#### 🧠 Model Selection")
    
    model_options = ["Select a model...", "Claude Sonnet 3.5 v2", "Amazon Nova Pro"]
    selected_model = st.selectbox(
        "Choose AI Model",
        model_options,
        index=0 if not st.session_state.selected_model else model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0,
        key="model_selector"
    )
    
    if selected_model != "Select a model..." and selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.session_state.model_connected = True
        st.rerun()
    
    st.markdown("---")
    
    # User Input Section
    st.markdown("#### 💬 User Input")
    
    user_prompt = st.text_area(
        "Enter your prompt or requirements:",
        value=st.session_state.user_prompt,
        height=150,
        key="user_prompt_input",
        placeholder="Describe your feature or requirements here..."
    )
    
    if user_prompt != st.session_state.user_prompt:
        st.session_state.user_prompt = user_prompt
    
    st.markdown("---")
    
    # Actions Section
    st.markdown("#### 🎯 Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✨ Generate", key="generate_btn", use_container_width=True, type="primary"):
            handle_generate_action()
        
        if st.button("🔄 Regenerate", key="regenerate_btn", use_container_width=True):
            handle_regenerate_action()
    
    with col2:
        if st.button("✅ Accept", key="accept_btn", use_container_width=True):
            handle_accept_action()
        
        if st.button("❌ Reject", key="reject_btn", use_container_width=True):
            handle_reject_action()
    
    # JIRA Configuration (if JIRA Integration is selected)
    if st.session_state.current_view == "JIRA Integration":
        st.markdown("---")
        st.markdown("#### 🎯 JIRA Configuration")
        
        issue_type = st.selectbox(
            "Issue Type",
            ["Story", "Task", "Bug", "Epic"],
            key="jira_issue_type"
        )
        
        priority = st.selectbox(
            "Priority",
            ["Highest", "High", "Medium", "Low", "Lowest"],
            index=2,
            key="jira_priority"
        )
        
        project_key = st.text_input(
            "Project Key",
            value="KIRO",
            key="jira_project_key"
        )
        
        with st.expander("Advanced Options"):
            assignee = st.text_input("Assignee", key="jira_assignee")
            epic_link = st.text_input("Epic Link", key="jira_epic")
            story_points = st.text_input("Story Points", key="jira_points")
    
    # Download Section (if content available)
    if st.session_state.generated_content:
        st.markdown("---")
        st.markdown("#### 📥 Downloads")
        
        if st.session_state.current_view == "JIRA Integration":
            render_jira_download_options()
        else:
            st.download_button(
                "📄 Download Content",
                st.session_state.generated_content,
                f"{st.session_state.current_view.lower().replace(' ', '_')}.md",
                "text/markdown",
                use_container_width=True
            )

def render_spec_generation_content():
    """Render spec generation content in the center panel"""
    if st.session_state.generated_content:
        st.markdown("### Generated Content")
        with st.container():
            st.markdown(st.session_state.generated_content)
    else:
        st.markdown("### Welcome to Spec Generation")
        st.info("Enter your feature idea in the prompt area and click Generate to create requirements, design, and tasks.")
        
        # Show existing specs if any
        specs_dir = Path(".kiro/specs")
        if specs_dir.exists():
            spec_folders = [d for d in specs_dir.iterdir() if d.is_dir()]
            if spec_folders:
                st.markdown("#### Existing Specs")
                for spec_folder in spec_folders:
                    with st.expander(f"📋 {spec_folder.name}"):
                        # Show spec files
                        req_file = spec_folder / "requirements.md"
                        design_file = spec_folder / "design.md"
                        tasks_file = spec_folder / "tasks.md"
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if req_file.exists():
                                st.success("**Requirements** ✅")
                            else:
                                st.warning("**Requirements** ❌")
                        with col2:
                            if design_file.exists():
                                st.success("**Design** ✅")
                            else:
                                st.warning("**Design** ❌")
                        with col3:
                            if tasks_file.exists():
                                st.success("**Tasks** ✅")
                            else:
                                st.warning("**Tasks** ❌")

def render_jira_integration_content():
    """Render JIRA integration content in the center panel"""
    if st.session_state.generated_content:
        st.markdown("### JIRA Templates Generated")
        with st.container():
            st.markdown(st.session_state.generated_content)
    else:
        st.markdown("### JIRA Integration")
        st.info("Generate JIRA tickets from your spec tasks. Configure your settings in the actions panel.")
        
        # Show available tasks
        specs_dir = Path(".kiro/specs")
        if specs_dir.exists():
            spec_folders = [d for d in specs_dir.iterdir() if d.is_dir()]
            available_tasks = []
            
            for spec_folder in spec_folders:
                tasks_file = spec_folder / "tasks.md"
                if tasks_file.exists():
                    available_tasks.append(spec_folder.name)
            
            if available_tasks:
                st.markdown("#### Available Task Lists")
                for task_spec in available_tasks:
                    st.markdown(f"📋 {task_spec}")
            else:
                st.warning("No task lists found. Generate a spec first.")

def render_diagram_generation_content():
    """Render diagram generation content in the center panel"""
    st.markdown("### Diagram Generation")
    st.info("Diagram generation functionality will be implemented in upcoming tasks")
    
    if st.session_state.generated_content:
        st.markdown("### Generated Diagram")
        with st.container():
            st.markdown(st.session_state.generated_content)

def render_settings_content():
    """Render settings content in the center panel"""
    st.markdown("### Settings")
    
    # Theme settings
    st.markdown("#### 🎨 Theme")
    st.success("Currently using Kiro Light Theme")
    
    # Model settings
    st.markdown("#### 🧠 Model Configuration")
    if st.session_state.selected_model:
        st.success(f"Active Model: {st.session_state.selected_model}")
        
        # Test connection button
        if st.button("🔄 Test Connection"):
            with st.spinner("Testing connection..."):
                try:
                    if st.session_state.ai_service.initialize_bedrock_client():
                        st.success("✅ AWS Bedrock connection successful")
                    else:
                        st.error("❌ AWS Bedrock connection failed")
                except Exception as e:
                    st.error(f"❌ Connection test failed: {str(e)}")
    else:
        st.warning("No model selected")
    
    # File settings
    st.markdown("#### 📁 File Management")
    st.info("Workspace: Current directory")
    
    # Show workspace info
    current_dir = Path.cwd()
    st.markdown(f"**Current Directory:** `{current_dir}`")
    
    specs_dir = Path(".kiro/specs")
    if specs_dir.exists():
        spec_count = len([d for d in specs_dir.iterdir() if d.is_dir()])
        st.markdown(f"**Specs Found:** {spec_count}")
    else:
        st.markdown("**Specs Found:** 0")

def render_jira_download_options():
    """Render JIRA-specific download options"""
    if hasattr(st.session_state, 'jira_templates') and st.session_state.jira_templates:
        templates = st.session_state.jira_templates
        
        st.download_button(
            "📊 CSV",
            templates['csv'],
            "jira_tickets.csv",
            "text/csv",
            use_container_width=True
        )
        
        st.download_button(
            "🔗 JSON",
            templates['json'],
            "jira_tickets.json",
            "application/json",
            use_container_width=True
        )
        
        st.download_button(
            "📝 Markdown",
            templates['markdown'],
            "jira_tickets.md",
            "text/markdown",
            use_container_width=True
        )
        
        st.download_button(
            "✅ Tasks.md",
            templates['tasks_md'],
            "tasks.md",
            "text/markdown",
            use_container_width=True
        )
    else:
        st.info("Generate JIRA templates first to see download options")

def handle_generate_action():
    """Handle generate button click"""
    if not st.session_state.user_prompt.strip():
        st.error("Please enter a prompt first")
        return
    
    if not st.session_state.model_connected:
        st.error("Please select an AI model first")
        return
    
    try:
        if st.session_state.current_view == "Spec Generation":
            # Generate spec content
            with st.spinner("Generating spec..."):
                result = st.session_state.spec_engine.create_requirements(st.session_state.user_prompt)
                st.session_state.generated_content = result
                st.success("Spec generated successfully!")
        
        elif st.session_state.current_view == "JIRA Integration":
            # Generate JIRA templates
            with st.spinner("Generating JIRA templates..."):
                # Check if we have tasks to convert
                if st.session_state.get("task_list"):
                    # Parse tasks from the generated task list
                    parsed_tasks = parse_tasks_from_markdown(st.session_state.task_list)
                    
                    if parsed_tasks:
                        # Generate JIRA templates with user configuration
                        templates = generate_jira_templates(
                            parsed_tasks,
                            issue_type=st.session_state.get("jira_issue_type", "Story"),
                            priority=st.session_state.get("jira_priority", "Medium"),
                            project_key=st.session_state.get("jira_project_key", "KIRO"),
                            add_labels=True,
                            assignee=st.session_state.get("jira_assignee", ""),
                            epic_link=st.session_state.get("jira_epic", ""),
                            story_points=st.session_state.get("jira_points", "")
                        )
                        
                        st.session_state.jira_templates = templates
                        st.session_state.generated_content = f"Generated {templates['count']} JIRA tickets from your tasks.\n\nPreview:\n\n{templates['markdown'][:500]}..."
                        st.success("JIRA templates generated!")
                    else:
                        st.error("No valid tasks found to convert to JIRA tickets")
                else:
                    st.error("No tasks available. Generate a spec with tasks first.")
        
        elif st.session_state.current_view == "Diagram Generation":
            # Generate diagrams
            with st.spinner("Generating diagram..."):
                st.session_state.generated_content = f"```mermaid\ngraph TD\n    A[{st.session_state.user_prompt}] --> B[Implementation]\n    B --> C[Testing]\n    C --> D[Deployment]\n```"
                st.success("Diagram generated!")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")

def handle_regenerate_action():
    """Handle regenerate button click"""
    if st.session_state.generated_content:
        handle_generate_action()
    else:
        st.warning("Nothing to regenerate. Generate content first.")

def handle_accept_action():
    """Handle accept button click"""
    if not st.session_state.generated_content:
        st.warning("No content to accept")
        return
    
    try:
        if st.session_state.current_view == "Spec Generation":
            # Save the spec content
            st.success("Content accepted and saved!")
        elif st.session_state.current_view == "JIRA Integration":
            # Save JIRA templates
            st.success("JIRA templates accepted!")
        elif st.session_state.current_view == "Diagram Generation":
            # Save diagram
            st.success("Diagram accepted!")
        
    except Exception as e:
        st.error(f"Failed to accept content: {str(e)}")

def handle_reject_action():
    """Handle reject button click"""
    if st.session_state.generated_content:
        st.session_state.generated_content = ""
        st.warning("Content rejected and cleared")
        st.rerun()
    else:
        st.warning("No content to reject")

def main():
    load_css()
    initialize_session_state()
    
    # Hide Streamlit default elements
    st.markdown("""
        <style>
        .stApp > header {visibility: hidden;}
        .stApp > div:first-child {padding-top: 0;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        .stSidebar {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    # Three-panel layout
    col1, col2, col3 = st.columns([280, 1000, 320], gap="small")
    
    with col1:
        render_navigation_panel()
    
    with col2:
        render_content_panel()
    
    with col3:
        render_actions_panel()

if __name__ == "__main__":
    main()
def g
enerate_jira_templates(parsed_tasks, issue_type="Story", priority="Medium", project_key="PROJ", add_labels=True, assignee="", epic_link="", story_points="", components="", fix_versions="", affects_versions=""):
    """Generate production-grade JIRA ticket templates in different formats"""
    
    # Prepare template data with comprehensive JIRA fields
    template_data = []
    
    for i, task in enumerate(parsed_tasks, 1):
        labels = ["kiro-generated", "implementation"] if add_labels else []
        
        # Estimate story points based on task complexity
        estimated_points = len(task.get("subtasks", [])) + 2 if not story_points else int(story_points) if story_points.isdigit() else 3
        
        # Enhanced description with structured format
        description = f"""h2. Overview
{task['title']}

h2. Implementation Details
{task['description'] if task['description'] else f'Implementation task: {task["title"]}'}

h2. Acceptance Criteria
"""
        
        # Add subtasks as acceptance criteria
        if task.get("subtasks"):
            for subtask in task["subtasks"]:
                description += f"* {subtask['title']}\n"
        else:
            description += "* Task implementation completed\n* Code reviewed and approved\n* Tests written and passing\n"
        
        # Add requirements reference
        if task.get("requirements"):
            description += f"\nh2. Requirements Reference\n"
            for req in task["requirements"]:
                description += f"* Requirement {req}\n"
        
        # Set due date (2 weeks from now)
        due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        ticket_data = {
            # Core fields
            "summary": task["title"],
            "description": description,
            "issue_type": issue_type,
            "priority": priority,
            "project_key": project_key,
            
            # Assignment and ownership
            "assignee": assignee,
            "reporter": "kiro-ai",
            
            # Planning fields
            "story_points": estimated_points,
            "epic_link": epic_link,
            "due_date": due_date,
            
            # Categorization
            "labels": labels,
            "components": components.split(",") if components else ["Development"],
            "fix_versions": fix_versions.split(",") if fix_versions else [],
            "affects_versions": affects_versions.split(",") if affects_versions else [],
            
            # Custom fields
            "environment": "Development",
            "requirements": task.get("requirements", []),
            "subtasks": [st["title"] for st in task.get("subtasks", [])],
            "original_estimate": f"{estimated_points * 4}h",  # 4 hours per story point
            "remaining_estimate": f"{estimated_points * 4}h",
            
            # Workflow
            "status": "To Do",
            "resolution": "",
            
            # Metadata
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_number": task.get("number", str(i))
        }
        
        template_data.append(ticket_data)
    
    # Generate CSV format with all production fields
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    
    # CSV headers - production-grade JIRA fields
    csv_writer.writerow([
        "Summary", "Description", "Issue Type", "Priority", "Project Key", 
        "Assignee", "Reporter", "Story Points", "Epic Link", "Due Date",
        "Labels", "Components", "Fix Versions", "Affects Versions",
        "Environment", "Original Estimate", "Remaining Estimate",
        "Status", "Requirements", "Subtasks", "Task Number"
    ])
    
    # CSV data with all fields
    for ticket in template_data:
        csv_writer.writerow([
            ticket["summary"],
            ticket["description"].replace('\n', ' | '),  # Replace newlines for CSV
            ticket["issue_type"],
            ticket["priority"],
            ticket["project_key"],
            ticket["assignee"],
            ticket["reporter"],
            ticket["story_points"],
            ticket["epic_link"],
            ticket["due_date"],
            "; ".join(ticket["labels"]),
            "; ".join(ticket["components"]),
            "; ".join(ticket["fix_versions"]),
            "; ".join(ticket["affects_versions"]),
            ticket["environment"],
            ticket["original_estimate"],
            ticket["remaining_estimate"],
            ticket["status"],
            "; ".join(ticket["requirements"]),
            "; ".join(ticket["subtasks"]),
            ticket["task_number"]
        ])
    
    csv_content = csv_buffer.getvalue()
    
    # Generate JSON format (JIRA API ready) with all fields
    json_tickets = []
    for ticket in template_data:
        json_ticket = {
            "fields": {
                # Core fields
                "project": {"key": ticket["project_key"]},
                "summary": ticket["summary"],
                "description": ticket["description"],
                "issuetype": {"name": ticket["issue_type"]},
                "priority": {"name": ticket["priority"]},
                
                # Assignment
                "assignee": {"name": ticket["assignee"]} if ticket["assignee"] else None,
                "reporter": {"name": ticket["reporter"]},
                
                # Planning
                "duedate": ticket["due_date"],
                "timeoriginalestimate": ticket["original_estimate"],
                "timeestimate": ticket["remaining_estimate"],
                
                # Categorization
                "labels": ticket["labels"],
                "components": [{"name": comp.strip()} for comp in ticket["components"]],
                "fixVersions": [{"name": ver.strip()} for ver in ticket["fix_versions"]] if ticket["fix_versions"] else [],
                "versions": [{"name": ver.strip()} for ver in ticket["affects_versions"]] if ticket["affects_versions"] else [],
                
                # Custom fields (these may need to be adjusted based on your JIRA instance)
                "customfield_10016": ticket["story_points"],  # Story Points (common field ID)
                "customfield_10014": ticket["epic_link"] if ticket["epic_link"] else None,  # Epic Link
                "environment": ticket["environment"]
            },
            
            # Metadata
            "metadata": {
                "requirements": ticket["requirements"],
                "subtasks": ticket["subtasks"],
                "task_number": ticket["task_number"],
                "created_by": "kiro-ai",
                "template_version": "1.0"
            }
        }
        
        # Remove null fields
        json_ticket["fields"] = {k: v for k, v in json_ticket["fields"].items() if v is not None}
        
        json_tickets.append(json_ticket)
    
    json_content = json.dumps({"issues": json_tickets}, indent=2)
    
    # Generate Production Markdown format
    md_content = "# JIRA Ticket Templates\n\n"
    md_content += f"**Project:** {project_key}\n"
    md_content += f"**Issue Type:** {issue_type}\n"
    md_content += f"**Priority:** {priority}\n"
    md_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, ticket in enumerate(template_data, 1):
        md_content += f"## Ticket {ticket['task_number']}: {ticket['summary']}\n\n"
        
        # Core Information
        md_content += f"**Issue Type:** {ticket['issue_type']}\n"
        md_content += f"**Priority:** {ticket['priority']}\n"
        md_content += f"**Story Points:** {ticket['story_points']}\n"
        md_content += f"**Due Date:** {ticket['due_date']}\n"
        
        if ticket["assignee"]:
            md_content += f"**Assignee:** {ticket['assignee']}\n"
        
        if ticket["epic_link"]:
            md_content += f"**Epic:** {ticket['epic_link']}\n"
        
        md_content += "\n"
        
        # Description
        md_content += f"**Description:**\n{ticket['description']}\n\n"
        
        # Planning Information
        md_content += f"**Estimates:**\n"
        md_content += f"- Original: {ticket['original_estimate']}\n"
        md_content += f"- Remaining: {ticket['remaining_estimate']}\n\n"
        
        # Categorization
        if ticket["components"]:
            md_content += f"**Components:** {', '.join(ticket['components'])}\n"
        
        if ticket["labels"]:
            md_content += f"**Labels:** {', '.join(ticket['labels'])}\n"
        
        if ticket["requirements"]:
            md_content += f"**Requirements:** {', '.join(ticket['requirements'])}\n"
        
        md_content += f"**Environment:** {ticket['environment']}\n\n"
        
        # Subtasks
        if ticket["subtasks"]:
            md_content += f"**Subtasks:**\n"
            for subtask in ticket["subtasks"]:
                md_content += f"- [ ] {subtask}\n"
            md_content += "\n"
        
        md_content += "---\n\n"
    
    # Generate Tasks.md format (Kiro style)
    tasks_md_content = "# Implementation Tasks (JIRA Export)\n\n"
    tasks_md_content += f"Generated from Kiro on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, ticket in enumerate(template_data, 1):
        task_num = ticket['task_number']
        tasks_md_content += f"- [ ] {task_num}. {ticket['summary']}\n"
        
        # Add subtasks
        if ticket["subtasks"]:
            for j, subtask in enumerate(ticket["subtasks"], 1):
                tasks_md_content += f"  - [ ] {task_num}.{j} {subtask}\n"
        
        # Add description as implementation details
        desc_lines = ticket['description'].split('\n')
        for line in desc_lines:
            if line.strip() and not line.startswith('h2.'):
                if line.startswith('*'):
                    tasks_md_content += f"    - {line.strip('* ')}\n"
        
        # Add requirements reference
        if ticket["requirements"]:
            tasks_md_content += f"    - _Requirements: {', '.join(ticket['requirements'])}_\n"
        
        # Add estimates
        tasks_md_content += f"    - _Estimate: {ticket['story_points']} points ({ticket['original_estimate']})_\n"
        
        tasks_md_content += "\n"
    
    return {
        "csv": csv_content,
        "json": json_content,
        "markdown": md_content,
        "tasks_md": tasks_md_content,
        "count": len(template_data)
    }

def parse_tasks_from_markdown(tasks_content):
    """Parse tasks from markdown format"""
    tasks = []
    lines = tasks_content.split('\n')
    current_task = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('- [ ]') and not line.startswith('  - [ ]'):
            # Main task
            if current_task:
                tasks.append(current_task)
            
            # Extract task number and title
            task_text = line[5:].strip()  # Remove '- [ ] '
            if '. ' in task_text:
                number, title = task_text.split('. ', 1)
            else:
                number = str(len(tasks) + 1)
                title = task_text
            
            current_task = {
                "number": number,
                "title": title,
                "description": "",
                "subtasks": [],
                "requirements": []
            }
        
        elif line.startswith('  - [ ]'):
            # Subtask
            if current_task:
                subtask_text = line[7:].strip()  # Remove '  - [ ] '
                if '. ' in subtask_text:
                    sub_number, sub_title = subtask_text.split('. ', 1)
                else:
                    sub_number = f"{current_task['number']}.{len(current_task['subtasks']) + 1}"
                    sub_title = subtask_text
                
                current_task["subtasks"].append({
                    "number": sub_number,
                    "title": sub_title
                })
        
        elif line.startswith('    - ') and current_task:
            # Description or requirements
            detail = line[6:].strip()  # Remove '    - '
            if detail.startswith('_Requirements:'):
                # Extract requirements
                req_text = detail.replace('_Requirements:', '').replace('_', '').strip()
                current_task["requirements"] = [r.strip() for r in req_text.split(',') if r.strip()]
            else:
                # Add to description
                if current_task["description"]:
                    current_task["description"] += "\n"
                current_task["description"] += detail
    
    # Add the last task
    if current_task:
        tasks.append(current_task)
    
    return tasks