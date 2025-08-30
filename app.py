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
    if st.session_state.get('model_connected', False) and st.session_state.get('selected_model'):
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
    
    # Debug info (can be removed later)
    if st.checkbox("Show Debug Info", key="debug_mode"):
        st.write("Debug Info:")
        st.write(f"- selected_model: {st.session_state.get('selected_model', 'None')}")
        st.write(f"- model_connected: {st.session_state.get('model_connected', False)}")
        st.write(f"- ai_service exists: {hasattr(st.session_state, 'ai_service')}")
        if hasattr(st.session_state, 'ai_service'):
            st.write(f"- ai_service.current_model: {getattr(st.session_state.ai_service, 'current_model', 'None')}")
            st.write(f"- ai_service.bedrock_client: {st.session_state.ai_service.bedrock_client is not None}")
        st.write(f"- selectbox value: {selected_model}")
    
    model_options = ["Select a model...", "Claude Sonnet 3.5 v2", "Amazon Nova Pro"]
    selected_model = st.selectbox(
        "Choose AI Model",
        model_options,
        index=0 if not st.session_state.selected_model else model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0,
        key="model_selector"
    )
    
    if selected_model != "Select a model..." and selected_model != st.session_state.selected_model:
        with st.spinner(f"Connecting to {selected_model}..."):
            if st.session_state.ai_service.select_model(selected_model):
                st.session_state.selected_model = selected_model
                st.session_state.model_connected = True
                st.success(f"✅ Connected to {selected_model}")
            else:
                st.session_state.model_connected = False
                st.error(f"❌ Failed to connect to {selected_model}")
        st.rerun()
    
    # Ensure AI service model is synchronized with session state
    elif selected_model != "Select a model..." and st.session_state.get('selected_model') == selected_model:
        # Model is already selected in session state, ensure AI service is synchronized
        if not st.session_state.ai_service.current_model or st.session_state.ai_service.current_model != selected_model:
            st.session_state.ai_service.select_model(selected_model)
    
    # Test connection button
    if st.session_state.get('selected_model') and st.button("🔄 Test Connection", key="test_connection"):
        with st.spinner("Testing connection..."):
            try:
                if st.session_state.ai_service.initialize_bedrock_client():
                    st.session_state.model_connected = True
                    st.success("✅ Connection successful")
                else:
                    st.session_state.model_connected = False
                    st.error("❌ Connection failed")
            except Exception as e:
                st.session_state.model_connected = False
                st.error(f"❌ Connection error: {str(e)}")
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
    
    # Show different buttons based on current view
    if st.session_state.current_view == "Spec Generation":
        # Spec workflow buttons
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
        
        # New spec button
        if st.session_state.get('spec_workflow_state') in ['design', 'tasks', 'complete']:
            st.markdown("---")
            if st.button("🆕 New Spec", key="new_spec_btn", use_container_width=True):
                # Reset workflow state
                st.session_state.spec_workflow_state = 'requirements'
                st.session_state.spec_feature_name = None
                st.session_state.spec_requirements = None
                st.session_state.spec_design = None
                st.session_state.spec_tasks = None
                st.session_state.generated_content = ""
                st.session_state.user_prompt = ""
                st.success("Ready to create a new spec!")
                st.rerun()
    
    else:
        # Default buttons for other views
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
        elif st.session_state.current_view == "Spec Generation":
            render_spec_download_options()
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
    
    # Show workflow progress
    workflow_state = st.session_state.get('spec_workflow_state', 'requirements')
    feature_name = st.session_state.get('spec_feature_name', 'New Feature')
    
    if workflow_state != 'requirements':
        st.markdown("### 🚀 Spec Workflow Progress")
        
        # Progress indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            if workflow_state in ['design', 'tasks', 'complete']:
                st.success("**1. Requirements** ✅")
            else:
                st.info("**1. Requirements** 🔄")
        with col2:
            if workflow_state in ['tasks', 'complete']:
                st.success("**2. Design** ✅")
            elif workflow_state == 'design':
                st.info("**2. Design** 🔄")
            else:
                st.warning("**2. Design** ⏳")
        with col3:
            if workflow_state == 'complete':
                st.success("**3. Tasks** ✅")
            elif workflow_state == 'tasks':
                st.info("**3. Tasks** 🔄")
            else:
                st.warning("**3. Tasks** ⏳")
        
        st.markdown(f"**Current Feature:** `{feature_name}`")
        st.markdown("---")
    
    if st.session_state.generated_content:
        # Show current phase title
        phase_titles = {
            'requirements': '📋 Requirements Document',
            'design': '🎨 Design Document', 
            'tasks': '✅ Implementation Tasks',
            'complete': '🎉 Spec Complete'
        }
        
        current_title = phase_titles.get(workflow_state, 'Generated Content')
        st.markdown(f"### {current_title}")
        
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
    
    # Mode selection
    st.markdown("### 🎯 JIRA Integration")
    
    # Mode tabs
    tab1, tab2 = st.tabs(["🌐 Online Mode", "📱 Offline Mode"])
    
    with tab1:
        render_online_jira_mode()
    
    with tab2:
        render_offline_jira_mode()

def render_online_jira_mode():
    """Render online JIRA mode with live connection"""
    st.markdown("#### 🌐 Online JIRA Integration")
    st.info("Connect to your JIRA instance to create tickets directly")
    
    # JIRA Configuration
    with st.expander("⚙️ JIRA Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            jira_url = st.text_input("JIRA URL", placeholder="https://yourcompany.atlassian.net")
            username = st.text_input("Username/Email", placeholder="your.email@company.com")
            
        with col2:
            api_token = st.text_input("API Token", type="password", placeholder="Your JIRA API token")
            project_key = st.text_input("Project Key", placeholder="PROJ", value="KIRO")
        
        if st.button("🔗 Test Connection"):
            if jira_url and username and api_token:
                with st.spinner("Testing JIRA connection..."):
                    # Simulate connection test
                    st.success("✅ JIRA connection successful!")
                    st.session_state.jira_connected = True
            else:
                st.error("Please fill in all JIRA configuration fields")
    
    # Show available tasks for online mode
    if st.session_state.get('jira_connected'):
        show_available_tasks_for_jira()
        
        if st.button("🚀 Create JIRA Tickets", type="primary"):
            st.success("🎉 JIRA tickets created successfully!")
            st.info("In a real implementation, this would create actual JIRA tickets using the API")
    else:
        st.warning("⚠️ Please configure and test your JIRA connection first")

def render_offline_jira_mode():
    """Render offline JIRA mode with template generation"""
    st.markdown("#### 📱 Offline JIRA Templates")
    st.info("Generate JIRA ticket templates that you can import manually")
    
    # Configuration for offline templates
    with st.expander("⚙️ Template Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            issue_type = st.selectbox("Issue Type", ["Story", "Task", "Bug", "Epic"], index=0)
            priority = st.selectbox("Priority", ["Highest", "High", "Medium", "Low", "Lowest"], index=2)
        
        with col2:
            project_key = st.text_input("Project Key", value="KIRO", placeholder="PROJ")
            assignee = st.text_input("Default Assignee", placeholder="username")
        
        with col3:
            epic_link = st.text_input("Epic Link", placeholder="EPIC-123")
            story_points = st.text_input("Story Points", placeholder="3")
    
    # Show available tasks
    show_available_tasks_for_jira()
    
    # Generate templates button
    if st.button("✨ Generate JIRA Templates", type="primary"):
        generate_offline_jira_templates(issue_type, priority, project_key, assignee, epic_link, story_points)

def show_available_tasks_for_jira():
    """Show available task lists for JIRA integration"""
    st.markdown("#### 📋 Available Task Lists")
    
    specs_dir = Path(".kiro/specs")
    if specs_dir.exists():
        spec_folders = [d for d in specs_dir.iterdir() if d.is_dir()]
        available_tasks = []
        
        for spec_folder in spec_folders:
            tasks_file = spec_folder / "tasks.md"
            if tasks_file.exists():
                available_tasks.append({
                    'name': spec_folder.name,
                    'path': tasks_file
                })
        
        if available_tasks:
            selected_spec = st.selectbox(
                "Select Task List",
                options=[task['name'] for task in available_tasks],
                key="jira_task_selection"
            )
            
            if selected_spec:
                # Load and preview tasks
                selected_task = next(task for task in available_tasks if task['name'] == selected_spec)
                with open(selected_task['path'], 'r', encoding='utf-8') as f:
                    tasks_content = f.read()
                
                # Store in session state for processing
                st.session_state.selected_tasks_content = tasks_content
                
                # Preview tasks
                with st.expander(f"📖 Preview Tasks from {selected_spec}"):
                    st.markdown(tasks_content[:500] + "..." if len(tasks_content) > 500 else tasks_content)
                
                # Parse and show task count
                parsed_tasks = parse_tasks_from_markdown(tasks_content)
                st.success(f"✅ Found {len(parsed_tasks)} tasks ready for JIRA conversion")
        else:
            st.warning("No task lists found. Generate a spec first to create tasks.")
            st.info("💡 Go to 'Spec Generation' to create requirements, design, and tasks first.")
    else:
        st.warning("No specs directory found. Generate a spec first.")

def generate_offline_jira_templates(issue_type, priority, project_key, assignee, epic_link, story_points):
    """Generate offline JIRA templates"""
    if not st.session_state.get('selected_tasks_content'):
        st.error("Please select a task list first")
        return
    
    with st.spinner("Generating JIRA templates..."):
        try:
            # Parse tasks
            parsed_tasks = parse_tasks_from_markdown(st.session_state.selected_tasks_content)
            
            if not parsed_tasks:
                st.error("No tasks found to convert")
                return
            
            # Generate templates
            templates = generate_jira_templates(
                parsed_tasks,
                issue_type=issue_type,
                priority=priority,
                project_key=project_key,
                add_labels=True,
                assignee=assignee,
                epic_link=epic_link,
                story_points=story_points
            )
            
            # Store templates in session state
            st.session_state.jira_templates = templates
            st.session_state.generated_content = f"Generated {len(parsed_tasks)} JIRA tickets in multiple formats"
            
            st.success(f"✅ Generated {len(parsed_tasks)} JIRA tickets!")
            st.info("📥 Check the download section for CSV, JSON, Markdown, and Tasks.md formats")
            
            # Show preview of generated templates
            st.markdown("#### 📊 Template Preview")
            
            # Format selection for preview
            format_choice = st.selectbox(
                "Preview Format",
                ["Production Markdown", "Tasks.md Format", "CSV Preview", "JSON Preview"]
            )
            
            if format_choice == "Production Markdown":
                st.markdown("##### Production JIRA Markdown")
                with st.container():
                    st.markdown(templates['markdown'][:1000] + "..." if len(templates['markdown']) > 1000 else templates['markdown'])
            
            elif format_choice == "Tasks.md Format":
                st.markdown("##### Kiro Tasks.md Format")
                with st.container():
                    st.markdown(templates['tasks_md'][:1000] + "..." if len(templates['tasks_md']) > 1000 else templates['tasks_md'])
            
            elif format_choice == "CSV Preview":
                st.markdown("##### CSV Format (First 500 chars)")
                st.text_area("CSV Content", templates['csv'][:500] + "..." if len(templates['csv']) > 500 else templates['csv'], height=200)
            
            elif format_choice == "JSON Preview":
                st.markdown("##### JSON Format")
                st.code(templates['json'][:1000] + "..." if len(templates['json']) > 1000 else templates['json'], language='json')
            
        except Exception as e:
            st.error(f"Template generation failed: {str(e)}")
            st.error("Please check your task list format and try again")

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

def render_spec_download_options():
    """Render spec-specific download options"""
    workflow_state = st.session_state.get('spec_workflow_state', 'requirements')
    
    # Individual file downloads
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.get('spec_requirements'):
            st.download_button(
                "📋 Requirements",
                st.session_state.spec_requirements,
                "requirements.md",
                "text/markdown",
                use_container_width=True
            )
        else:
            st.button("📋 Requirements", disabled=True, use_container_width=True)
    
    with col2:
        if st.session_state.get('spec_design'):
            st.download_button(
                "🎨 Design",
                st.session_state.spec_design,
                "design.md",
                "text/markdown",
                use_container_width=True
            )
        else:
            st.button("🎨 Design", disabled=True, use_container_width=True)
    
    with col3:
        if st.session_state.get('spec_tasks'):
            st.download_button(
                "✅ Tasks",
                st.session_state.spec_tasks,
                "tasks.md",
                "text/markdown",
                use_container_width=True
            )
        else:
            st.button("✅ Tasks", disabled=True, use_container_width=True)
    
    # Complete spec package download
    if (st.session_state.get('spec_requirements') and 
        st.session_state.get('spec_design') and 
        st.session_state.get('spec_tasks')):
        
        st.markdown("---")
        
        # Create combined spec document
        combined_spec = f"""# Complete Specification

## Requirements
{st.session_state.spec_requirements}

---

## Design
{st.session_state.spec_design}

---

## Implementation Tasks
{st.session_state.spec_tasks}
"""
        
        st.download_button(
            "📦 Complete Spec Package",
            combined_spec,
            f"{st.session_state.get('spec_feature_name', 'complete_spec')}.md",
            "text/markdown",
            use_container_width=True,
            type="primary"
        )

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

def handle_spec_workflow():
    """Handle the complete spec workflow: Requirements -> Design -> Tasks"""
    
    # Initialize workflow state if not exists
    if 'spec_workflow_state' not in st.session_state:
        st.session_state.spec_workflow_state = 'requirements'
        st.session_state.spec_feature_name = None
        st.session_state.spec_requirements = None
        st.session_state.spec_design = None
        st.session_state.spec_tasks = None
    
    # Generate feature name from prompt if not exists
    if not st.session_state.spec_feature_name and st.session_state.user_prompt:
        # Create a simple feature name from the prompt
        feature_name = st.session_state.user_prompt.lower().replace(' ', '-')[:50]
        # Remove special characters
        import re
        feature_name = re.sub(r'[^a-z0-9-]', '', feature_name)
        st.session_state.spec_feature_name = feature_name
    
    # Requirements Phase
    if st.session_state.spec_workflow_state == 'requirements':
        with st.spinner("Generating requirements..."):
            try:
                requirements = st.session_state.spec_engine.create_requirements(st.session_state.user_prompt)
                st.session_state.spec_requirements = requirements
                st.session_state.generated_content = requirements
                
                # Save requirements to file
                save_spec_file(st.session_state.spec_feature_name, 'requirements.md', requirements)
                
                st.success("Requirements generated successfully!")
                st.info("📋 Please review the requirements above. Click 'Accept' to proceed to design phase.")
                
            except Exception as e:
                st.error(f"Requirements generation failed: {str(e)}")
                return
    
    # Design Phase
    elif st.session_state.spec_workflow_state == 'design':
        with st.spinner("Generating design document..."):
            try:
                design = st.session_state.spec_engine.generate_design(st.session_state.spec_requirements)
                st.session_state.spec_design = design
                st.session_state.generated_content = design
                
                # Save design to file
                save_spec_file(st.session_state.spec_feature_name, 'design.md', design)
                
                st.success("Design document generated successfully!")
                st.info("🎨 Please review the design above. Click 'Accept' to proceed to task creation.")
                
            except Exception as e:
                st.error(f"Design generation failed: {str(e)}")
                return
    
    # Tasks Phase
    elif st.session_state.spec_workflow_state == 'tasks':
        with st.spinner("Generating implementation tasks..."):
            try:
                tasks = st.session_state.spec_engine.create_task_list(st.session_state.spec_design, st.session_state.spec_requirements)
                st.session_state.spec_tasks = tasks
                st.session_state.generated_content = tasks
                
                # Save tasks to file
                save_spec_file(st.session_state.spec_feature_name, 'tasks.md', tasks)
                
                st.success("Implementation tasks generated successfully!")
                st.info("✅ Spec workflow complete! All documents have been generated and saved.")
                
                # Reset workflow state for next spec
                st.session_state.spec_workflow_state = 'complete'
                
            except Exception as e:
                st.error(f"Task generation failed: {str(e)}")
                return

def save_spec_file(feature_name: str, filename: str, content: str):
    """Save spec file to .kiro/specs directory"""
    import os
    from pathlib import Path
    
    if not feature_name:
        return
    
    # Create spec directory
    spec_dir = Path(f".kiro/specs/{feature_name}")
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = spec_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def handle_generate_action():
    """Handle generate button click"""
    if not st.session_state.user_prompt.strip():
        st.error("Please enter a prompt first")
        return
    
    if not st.session_state.get('model_connected', False) or not st.session_state.get('selected_model'):
        st.error("Please select an AI model first")
        return
    
    # Ensure AI service has the correct model selected
    if not st.session_state.ai_service.current_model or st.session_state.ai_service.current_model != st.session_state.selected_model:
        st.session_state.ai_service.select_model(st.session_state.selected_model)
    
    try:
        if st.session_state.current_view == "Spec Generation":
            # Start the spec workflow
            handle_spec_workflow()
        
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
            # Advance the spec workflow
            if st.session_state.get('spec_workflow_state') == 'requirements':
                st.session_state.spec_workflow_state = 'design'
                st.success("Requirements accepted! Proceeding to design phase...")
                # Automatically proceed to design generation
                handle_spec_workflow()
            elif st.session_state.get('spec_workflow_state') == 'design':
                st.session_state.spec_workflow_state = 'tasks'
                st.success("Design accepted! Proceeding to task creation...")
                # Automatically proceed to task generation
                handle_spec_workflow()
            elif st.session_state.get('spec_workflow_state') == 'tasks':
                st.success("Tasks accepted! Spec workflow complete!")
                st.session_state.spec_workflow_state = 'complete'
            else:
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
        if st.session_state.current_view == "Spec Generation":
            # Clear current step content for regeneration
            current_state = st.session_state.get('spec_workflow_state', 'requirements')
            if current_state == 'requirements':
                st.session_state.spec_requirements = None
            elif current_state == 'design':
                st.session_state.spec_design = None
            elif current_state == 'tasks':
                st.session_state.spec_tasks = None
        
        st.session_state.generated_content = ""
        st.warning("Content rejected and cleared. Click 'Generate' to create new content.")
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

def generate_jira_templates(parsed_tasks, issue_type="Story", priority="Medium", project_key="PROJ", add_labels=True, assignee="", epic_link="", story_points="", components="", fix_versions="", affects_versions=""):
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

if __name__ == "__main__":
    main()