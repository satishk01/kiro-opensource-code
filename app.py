import streamlit as st
import os
from pathlib import Path
from services.ai_service import AIService
from services.file_service import FileService
from engines.spec_engine import SpecEngine

# Configure Streamlit page
st.set_page_config(
    page_title="Kiro AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom CSS for Kiro styling
def load_css():
    css_file = Path("styles/kiro_theme.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    load_css()
    
    # Initialize session state
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
    
    # Sidebar for navigation and model selection
    with st.sidebar:
        st.title("🤖 Kiro AI Assistant")
        st.markdown("---")
        
        # Model selection
        st.subheader("🧠 AI Model")
        model_options = ["Select a model...", "Claude Sonnet 3.5 v2", "Amazon Nova Pro"]
        
        current_selection = st.session_state.selected_model if st.session_state.selected_model else "Select a model..."
        selected_model = st.selectbox("Choose AI Model", model_options, 
                                    index=model_options.index(current_selection) if current_selection in model_options else 0,
                                    key="model_selector")
        
        # Handle model selection change
        if selected_model != "Select a model..." and selected_model != st.session_state.selected_model:
            with st.spinner(f"Connecting to {selected_model}..."):
                if st.session_state.ai_service.select_model(selected_model):
                    st.session_state.selected_model = selected_model
                    st.session_state.model_connected = True
                    st.rerun()
                else:
                    st.session_state.model_connected = False
        
        # Show connection status
        if st.session_state.selected_model and st.session_state.model_connected:
            st.success(f"✅ Connected to {st.session_state.selected_model}")
        elif st.session_state.selected_model:
            st.error("❌ Connection failed")
        else:
            st.info("👆 Select a model to get started")
        
        # Model availability check button
        if st.button("🔄 Test Connection", help="Test AWS Bedrock connectivity"):
            with st.spinner("Testing connection..."):
                try:
                    if st.session_state.ai_service.initialize_bedrock_client():
                        st.success("✅ AWS Bedrock connection successful")
                        # Try to get available models
                        available_models = st.session_state.ai_service.get_available_models()
                        if available_models:
                            st.info(f"Available models: {', '.join(available_models)}")
                    else:
                        st.error("❌ AWS Bedrock connection failed")
                except Exception as e:
                    st.error(f"❌ Connection test failed: {str(e)}")
                    st.info("💡 Make sure your EC2 instance has the proper IAM role with Bedrock permissions.")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Choose a page:",
            ["Home", "Folder Analysis", "Spec Generation", "Diagrams", "JIRA Integration"],
            key="navigation"
        )
    
    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Folder Analysis":
        show_folder_analysis()
    elif page == "Spec Generation":
        show_spec_generation()
    elif page == "Diagrams":
        show_diagrams()
    elif page == "JIRA Integration":
        show_jira_integration()

def show_home_page():
    st.title("Welcome to Kiro AI Assistant")
    st.markdown("""
    I'm Kiro, your AI-powered development companion. I'm here to help you with:
    
    - **Codebase Analysis**: Select folders and analyze your project files
    - **Spec Generation**: Create requirements, designs, and implementation plans
    - **Diagram Creation**: Generate ER diagrams and data flow visualizations
    - **JIRA Integration**: Create and manage development tasks
    
    Get started by selecting an AI model from the sidebar, then choose a specific feature to begin.
    """)
    
    # Show current status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.model_connected:
            st.metric("AI Model", st.session_state.selected_model, "Connected ✅")
        else:
            st.metric("AI Model", "None", "Not Connected ❌")
    
    with col2:
        folder_status = "Selected" if st.session_state.current_folder else "None"
        file_count = len(st.session_state.loaded_files) if st.session_state.loaded_files else 0
        st.metric("Project Folder", folder_status, f"{file_count} files")
    
    with col3:
        spec_status = "Active" if st.session_state.active_spec else "None"
        st.metric("Active Spec", spec_status)
    
    # Quick start guide
    if not st.session_state.model_connected:
        st.info("🚀 **Quick Start**: Select an AI model from the sidebar to begin using Kiro's features.")
    elif not st.session_state.current_folder:
        st.info("📁 **Next Step**: Go to 'Folder Analysis' to select and analyze your project files.")
    else:
        st.success("🎉 **Ready to go!** You can now generate specs, create diagrams, or integrate with JIRA.")
    
    # Feature overview
    st.markdown("---")
    st.subheader("🛠️ Available Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        **📊 Analysis & Planning**
        - Codebase structure analysis
        - Requirements generation (EARS format)
        - High-level and low-level design documents
        - Implementation task planning
        """)
    
    with feature_col2:
        st.markdown("""
        **🔧 Integration & Visualization**
        - ER diagram generation
        - Data flow visualization
        - JIRA ticket creation
        - Project management integration
        """)

def show_folder_analysis():
    st.title("📁 Folder Analysis")
    st.markdown("Select and analyze your project folder to get started with Kiro's AI assistance.")
    
    # Check if AI model is connected
    if not st.session_state.model_connected:
        st.warning("⚠️ Please select and connect to an AI model first from the sidebar.")
        return
    
    # Folder selection
    selected_folder = st.session_state.file_service.select_folder()
    
    # Process folder if selected and different from current
    if selected_folder and selected_folder != st.session_state.current_folder:
        st.session_state.current_folder = selected_folder
        
        # Read files from folder
        with st.spinner("📖 Reading project files..."):
            files_content = st.session_state.file_service.read_files(selected_folder)
            st.session_state.loaded_files = files_content
        
        if files_content:
            st.rerun()
    
    # Display current folder info
    if st.session_state.current_folder:
        st.success(f"📂 **Current Folder:** {st.session_state.current_folder}")
        
        if st.session_state.loaded_files:
            # Show file statistics
            stats = st.session_state.file_service.get_file_stats(st.session_state.loaded_files)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", stats["total_files"])
            
            with col2:
                st.metric("Total Size", f"{stats['total_size_mb']} MB")
            
            with col3:
                st.metric("Languages", len(stats["languages"]))
            
            with col4:
                st.metric("File Types", len(stats["file_types"]))
            
            # Language breakdown
            if stats["languages"]:
                st.subheader("🔤 Detected Languages")
                language_cols = st.columns(min(len(stats["languages"]), 4))
                for i, lang in enumerate(stats["languages"]):
                    with language_cols[i % 4]:
                        st.write(f"• {lang}")
            
            # File type breakdown
            if stats["file_types"]:
                st.subheader("📄 File Types")
                file_type_data = []
                for ext, count in sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                    file_type_data.append({"Extension": ext, "Count": count})
                
                if file_type_data:
                    st.dataframe(file_type_data, use_container_width=True)
            
            # Codebase analysis
            st.subheader("🔍 AI Analysis")
            
            if st.button("🤖 Analyze Codebase", type="primary"):
                with st.spinner("🧠 AI is analyzing your codebase..."):
                    try:
                        analysis = st.session_state.ai_service.analyze_codebase(st.session_state.loaded_files)
                        
                        st.markdown("### 📊 Analysis Results")
                        st.markdown(analysis["analysis"])
                        
                        # Store analysis for later use
                        st.session_state.codebase_analysis = analysis
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
            
            # Show previous analysis if available
            if hasattr(st.session_state, 'codebase_analysis'):
                with st.expander("📋 Previous Analysis Results"):
                    st.markdown(st.session_state.codebase_analysis["analysis"])
        
        else:
            st.warning("⚠️ No files found in the selected folder or unable to read files.")
    
    else:
        st.info("👆 Select a project folder above to begin analysis.")

def show_spec_generation():
    st.title("📋 Spec Generation")
    st.markdown("Generate requirements, design documents, and implementation plans using Kiro's methodology")
    
    # Check if AI model is connected
    if not st.session_state.model_connected:
        st.warning("⚠️ Please select and connect to an AI model first from the sidebar.")
        return
    
    # Initialize spec workflow state
    if 'spec_workflow_state' not in st.session_state:
        st.session_state.spec_workflow_state = {
            'current_phase': 'input',
            'feature_description': '',
            'requirements_approved': False,
            'design_approved': False,
            'tasks_approved': False,
            'requirements_content': '',
            'design_content': '',
            'tasks_content': ''
        }
    
    workflow_state = st.session_state.spec_workflow_state
    
    # Progress indicator
    st.subheader("🔄 Spec Generation Workflow")
    
    phases = ['Input', 'Requirements', 'Design', 'Tasks', 'Complete']
    current_phase_index = phases.index(workflow_state['current_phase'].title()) if workflow_state['current_phase'].title() in phases else 0
    
    # Create progress bar
    progress_cols = st.columns(len(phases))
    for i, phase in enumerate(phases):
        with progress_cols[i]:
            if i < current_phase_index:
                st.success(f"✅ {phase}")
            elif i == current_phase_index:
                st.info(f"🔄 {phase}")
            else:
                st.write(f"⏳ {phase}")
    
    st.markdown("---")
    
    # Phase 1: Feature Description Input
    if workflow_state['current_phase'] == 'input':
        st.subheader("1️⃣ Feature Description")
        st.markdown("Describe the feature you want to build. Be as detailed as possible.")
        
        feature_description = st.text_area(
            "Feature Description",
            value=workflow_state['feature_description'],
            height=150,
            placeholder="Example: User authentication system with login, registration, password reset, and role-based access control...",
            help="Provide a comprehensive description of the feature including its purpose, main functionality, and any specific requirements."
        )
        
        # Optional: Include codebase context
        include_codebase = st.checkbox(
            "Include current codebase context",
            value=False,
            help="Include analysis of your current codebase to inform the spec generation"
        )
        
        codebase_context = None
        if include_codebase and st.session_state.loaded_files:
            st.info(f"📁 Will include context from {len(st.session_state.loaded_files)} files in your project")
            codebase_context = st.session_state.loaded_files
        elif include_codebase and not st.session_state.loaded_files:
            st.warning("⚠️ No codebase loaded. Go to 'Folder Analysis' first to load your project files.")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 Generate Requirements", type="primary", disabled=not feature_description.strip()):
                workflow_state['feature_description'] = feature_description
                
                with st.spinner("🧠 Generating requirements document..."):
                    try:
                        requirements = st.session_state.ai_service.generate_requirements(
                            feature_description, 
                            codebase_context
                        )
                        
                        # Format as proper requirements document
                        formatted_requirements = f"""# Requirements Document

## Introduction

{feature_description}

## Requirements

{requirements}
"""
                        
                        workflow_state['requirements_content'] = formatted_requirements
                        workflow_state['current_phase'] = 'requirements'
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate requirements: {str(e)}")
        
        with col2:
            if feature_description.strip():
                st.success("✅ Ready to generate requirements")
            else:
                st.info("👆 Enter a feature description to continue")
    
    # Phase 2: Requirements Review and Approval
    elif workflow_state['current_phase'] == 'requirements':
        st.subheader("2️⃣ Requirements Review")
        st.markdown("Review the generated requirements and approve or request changes.")
        
        # Display requirements
        st.markdown("### 📋 Generated Requirements")
        
        # Editable requirements
        updated_requirements = st.text_area(
            "Requirements Document",
            value=workflow_state['requirements_content'],
            height=400,
            help="Review and edit the requirements as needed. Use EARS format (WHEN/IF...THEN...SHALL)."
        )
        
        workflow_state['requirements_content'] = updated_requirements
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Approve Requirements", type="primary"):
                workflow_state['requirements_approved'] = True
                workflow_state['current_phase'] = 'design_generation'
                st.success("✅ Requirements approved! Generating design...")
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate"):
                with st.spinner("🧠 Regenerating requirements..."):
                    try:
                        requirements = st.session_state.ai_service.generate_requirements(
                            workflow_state['feature_description']
                        )
                        formatted_requirements = f"""# Requirements Document

## Introduction

{workflow_state['feature_description']}

## Requirements

{requirements}
"""
                        workflow_state['requirements_content'] = formatted_requirements
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to regenerate requirements: {str(e)}")
        
        with col3:
            if st.button("⬅️ Back to Input"):
                workflow_state['current_phase'] = 'input'
                st.rerun()
    
    # Phase 2.5: Design Generation (intermediate step)
    elif workflow_state['current_phase'] == 'design_generation':
        st.subheader("🔄 Generating Design Document...")
        
        with st.spinner("🧠 Creating design document based on requirements..."):
            try:
                codebase_context = st.session_state.loaded_files if st.session_state.loaded_files else None
                design = st.session_state.ai_service.create_design(
                    workflow_state['requirements_content'],
                    codebase_context
                )
                
                # Format as proper design document
                formatted_design = f"""# Design Document

## Overview

This design document outlines the technical approach for implementing the feature described in the requirements.

{design}
"""
                
                workflow_state['design_content'] = formatted_design
                workflow_state['current_phase'] = 'design'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to generate design: {str(e)}")
                workflow_state['current_phase'] = 'requirements'
                st.rerun()
    
    # Phase 3: Design Review and Approval
    elif workflow_state['current_phase'] == 'design':
        st.subheader("3️⃣ Design Review")
        st.markdown("Review the generated design document and approve or request changes.")
        
        # Display design
        st.markdown("### 🏗️ Generated Design")
        
        # Editable design
        updated_design = st.text_area(
            "Design Document",
            value=workflow_state['design_content'],
            height=400,
            help="Review and edit the design document as needed."
        )
        
        workflow_state['design_content'] = updated_design
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Approve Design", type="primary"):
                workflow_state['design_approved'] = True
                workflow_state['current_phase'] = 'tasks_generation'
                st.success("✅ Design approved! Generating tasks...")
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate"):
                workflow_state['current_phase'] = 'design_generation'
                st.rerun()
        
        with col3:
            if st.button("⬅️ Back to Requirements"):
                workflow_state['current_phase'] = 'requirements'
                st.rerun()
    
    # Phase 3.5: Tasks Generation (intermediate step)
    elif workflow_state['current_phase'] == 'tasks_generation':
        st.subheader("🔄 Generating Implementation Tasks...")
        
        with st.spinner("🧠 Creating implementation task list..."):
            try:
                tasks_md = st.session_state.spec_engine.create_task_list(
                    workflow_state['design_content'],
                    workflow_state.get('requirements_content', '')
                )
                
                workflow_state['tasks_content'] = tasks_md
                workflow_state['current_phase'] = 'tasks'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to generate tasks: {str(e)}")
                workflow_state['current_phase'] = 'design'
                st.rerun()
    
    # Phase 4: Tasks Review and Approval
    elif workflow_state['current_phase'] == 'tasks':
        st.subheader("4️⃣ Implementation Tasks Review")
        st.markdown("Review the generated implementation tasks and approve or request changes.")
        
        # Display tasks
        st.markdown("### ✅ Generated Tasks")
        
        # Editable tasks
        updated_tasks = st.text_area(
            "Implementation Tasks",
            value=workflow_state['tasks_content'],
            height=400,
            help="Review and edit the implementation tasks as needed."
        )
        
        workflow_state['tasks_content'] = updated_tasks
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Approve Tasks", type="primary"):
                workflow_state['tasks_approved'] = True
                workflow_state['current_phase'] = 'complete'
                st.success("✅ Tasks approved! Spec generation complete!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate"):
                workflow_state['current_phase'] = 'tasks_generation'
                st.rerun()
        
        with col3:
            if st.button("⬅️ Back to Design"):
                workflow_state['current_phase'] = 'design'
                st.rerun()
    
    # Phase 5: Complete
    elif workflow_state['current_phase'] == 'complete':
        st.subheader("🎉 Spec Generation Complete!")
        st.markdown("Your feature specification has been successfully generated.")
        
        # Summary
        st.success("✅ All phases completed successfully!")
        
        # Download options
        st.markdown("### 📥 Download Documents")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📋 Download Requirements",
                data=workflow_state['requirements_content'],
                file_name="requirements.md",
                mime="text/markdown"
            )
        
        with col2:
            st.download_button(
                label="🏗️ Download Design",
                data=workflow_state['design_content'],
                file_name="design.md",
                mime="text/markdown"
            )
        
        with col3:
            st.download_button(
                label="✅ Download Tasks",
                data=workflow_state['tasks_content'],
                file_name="tasks.md",
                mime="text/markdown"
            )
        
        # Preview tabs
        st.markdown("### 👀 Document Preview")
        
        tab1, tab2, tab3 = st.tabs(["📋 Requirements", "🏗️ Design", "✅ Tasks"])
        
        with tab1:
            st.markdown(workflow_state['requirements_content'])
        
        with tab2:
            st.markdown(workflow_state['design_content'])
        
        with tab3:
            st.markdown(workflow_state['tasks_content'])
        
        # Actions
        st.markdown("### 🚀 Next Steps")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Start New Spec"):
                # Reset workflow state
                st.session_state.spec_workflow_state = {
                    'current_phase': 'input',
                    'feature_description': '',
                    'requirements_approved': False,
                    'design_approved': False,
                    'tasks_approved': False,
                    'requirements_content': '',
                    'design_content': '',
                    'tasks_content': ''
                }
                st.rerun()
        
        with col2:
            if st.button("🎯 Create JIRA Tickets"):
                st.info("💡 Go to the 'JIRA Integration' tab to create tickets from these tasks")
        
        # Store completed spec for other features
        st.session_state.completed_spec = {
            'requirements': workflow_state['requirements_content'],
            'design': workflow_state['design_content'],
            'tasks': workflow_state['tasks_content'],
            'feature_description': workflow_state['feature_description']
        }

def show_diagrams():
    st.title("📊 Diagrams")
    st.markdown("Generate ER diagrams and data flow visualizations from your codebase")
    
    # Placeholder for diagram generation
    st.info("Diagram generation functionality will be implemented in upcoming tasks")

def show_jira_integration():
    st.title("🎯 JIRA Integration")
    st.markdown("Create and manage JIRA tickets from generated tasks")
    
    # Initialize JIRA client if not exists
    if 'jira_client' not in st.session_state:
        from integrations.jira_client import JiraClient
        st.session_state.jira_client = JiraClient()
    
    # JIRA Configuration Section
    st.subheader("⚙️ JIRA Configuration")
    
    with st.expander("🔧 Configure JIRA Connection", expanded=not st.session_state.get('jira_configured', False)):
        col1, col2 = st.columns(2)
        
        with col1:
            jira_url = st.text_input(
                "JIRA Base URL",
                value=st.session_state.get('jira_url', ''),
                placeholder="https://yourcompany.atlassian.net",
                help="Your JIRA instance URL"
            )
            
            username = st.text_input(
                "Username/Email",
                value=st.session_state.get('jira_username', ''),
                placeholder="your.email@company.com",
                help="Your JIRA username or email"
            )
        
        with col2:
            api_token = st.text_input(
                "API Token",
                type="password",
                value=st.session_state.get('jira_api_token', ''),
                help="Generate an API token from your JIRA account settings"
            )
            
            project_key = st.text_input(
                "Project Key",
                value=st.session_state.get('jira_project_key', ''),
                placeholder="PROJ",
                help="The key of the JIRA project where tickets will be created"
            )
        
        if st.button("🔗 Connect to JIRA", type="primary"):
            if all([jira_url, username, api_token, project_key]):
                with st.spinner("Testing JIRA connection..."):
                    if st.session_state.jira_client.configure(jira_url, username, api_token, project_key):
                        st.session_state.jira_configured = True
                        st.session_state.jira_url = jira_url
                        st.session_state.jira_username = username
                        st.session_state.jira_api_token = api_token
                        st.session_state.jira_project_key = project_key
                        st.rerun()
                    else:
                        st.session_state.jira_configured = False
            else:
                st.error("❌ Please fill in all JIRA configuration fields")
    
    # Show connection status
    if st.session_state.get('jira_configured', False):
        st.success(f"✅ Connected to JIRA project: {st.session_state.get('jira_project_key', 'Unknown')}")
        
        # Test connection button
        if st.button("🔄 Test Connection"):
            st.session_state.jira_client.test_connection()
    else:
        st.warning("⚠️ Please configure JIRA connection above to create tickets")
        return
    
    st.markdown("---")
    
    # Ticket Creation Section
    st.subheader("🎫 Create Tickets from Tasks")
    
    # Check if we have completed spec with tasks
    if hasattr(st.session_state, 'completed_spec') and st.session_state.completed_spec.get('tasks'):
        st.markdown("### 📋 Available Tasks")
        
        # Show preview of tasks
        with st.expander("👀 Preview Tasks", expanded=False):
            st.markdown(st.session_state.completed_spec['tasks'])
        
        # Ticket creation options
        col1, col2 = st.columns(2)
        
        with col1:
            # Get available issue types
            issue_types = st.session_state.jira_client.get_issue_types()
            issue_type_names = [it['name'] for it in issue_types] if issue_types else ['Task', 'Story', 'Bug']
            
            selected_issue_type = st.selectbox(
                "Issue Type",
                issue_type_names,
                index=0,
                help="Type of JIRA tickets to create"
            )
        
        with col2:
            priority_options = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
            default_priority = st.selectbox(
                "Default Priority",
                priority_options,
                index=2,  # Medium
                help="Default priority for created tickets"
            )
        
        # Additional options
        add_labels = st.checkbox("Add Kiro labels", value=True, help="Add 'kiro-generated' and 'implementation' labels")
        
        # Create tickets button
        if st.button("🚀 Create JIRA Tickets", type="primary"):
            with st.spinner("Creating JIRA tickets from tasks..."):
                try:
                    created_tickets = st.session_state.jira_client.create_tickets_from_tasks(
                        st.session_state.completed_spec['tasks'],
                        selected_issue_type
                    )
                    
                    if created_tickets:
                        st.success(f"✅ Successfully created {len(created_tickets)} JIRA tickets!")
                        
                        # Store created tickets for tracking
                        st.session_state.created_tickets = created_tickets
                        
                        # Show created tickets
                        st.markdown("### 🎫 Created Tickets")
                        
                        for item in created_tickets:
                            ticket = item['ticket']
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{ticket['key']}**: {item['task']}")
                            
                            with col2:
                                st.markdown(f"[View Ticket]({ticket['url']})")
                            
                            with col3:
                                st.code(ticket['key'])
                    else:
                        st.error("❌ No tickets were created. Check the error messages above.")
                        
                except Exception as e:
                    st.error(f"❌ Failed to create tickets: {e}")
    
    elif hasattr(st.session_state, 'spec_workflow_state') and st.session_state.spec_workflow_state.get('tasks_content'):
        # Use tasks from current workflow
        st.markdown("### 📋 Current Workflow Tasks")
        
        with st.expander("👀 Preview Tasks", expanded=False):
            st.markdown(st.session_state.spec_workflow_state['tasks_content'])
        
        # Similar ticket creation interface
        col1, col2 = st.columns(2)
        
        with col1:
            issue_types = st.session_state.jira_client.get_issue_types()
            issue_type_names = [it['name'] for it in issue_types] if issue_types else ['Task', 'Story', 'Bug']
            
            selected_issue_type = st.selectbox(
                "Issue Type",
                issue_type_names,
                index=0
            )
        
        with col2:
            priority_options = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
            default_priority = st.selectbox(
                "Default Priority",
                priority_options,
                index=2
            )
        
        if st.button("🚀 Create JIRA Tickets from Current Tasks", type="primary"):
            with st.spinner("Creating JIRA tickets..."):
                try:
                    created_tickets = st.session_state.jira_client.create_tickets_from_tasks(
                        st.session_state.spec_workflow_state['tasks_content'],
                        selected_issue_type
                    )
                    
                    if created_tickets:
                        st.success(f"✅ Successfully created {len(created_tickets)} JIRA tickets!")
                        st.session_state.created_tickets = created_tickets
                        
                        # Show created tickets
                        for item in created_tickets:
                            ticket = item['ticket']
                            st.markdown(f"**{ticket['key']}**: {item['task']} - [View]({ticket['url']})")
                    else:
                        st.error("❌ No tickets were created.")
                        
                except Exception as e:
                    st.error(f"❌ Failed to create tickets: {e}")
    
    else:
        st.info("📋 No tasks available. Generate a spec first in the 'Spec Generation' tab.")
    
    # Ticket Management Section
    if st.session_state.get('created_tickets'):
        st.markdown("---")
        st.subheader("📊 Ticket Management")
        
        # Show created tickets with status
        st.markdown("### 🎫 Your Created Tickets")
        
        for item in st.session_state.created_tickets:
            ticket = item['ticket']
            
            with st.expander(f"🎫 {ticket['key']} - {item['task']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Ticket Key:** {ticket['key']}")
                    st.markdown(f"**Task:** {item['task']}")
                    st.markdown(f"**URL:** [View in JIRA]({ticket['url']})")
                
                with col2:
                    if st.button(f"🔄 Refresh Status", key=f"refresh_{ticket['key']}"):
                        status = st.session_state.jira_client.get_ticket_status(ticket['key'])
                        if status:
                            st.info(f"Status: {status['status']}")
                            st.info(f"Assignee: {status['assignee']}")
                        else:
                            st.error("Failed to get ticket status")
    
    # Bulk Operations
    if st.session_state.get('created_tickets'):
        st.markdown("---")
        st.subheader("🔧 Bulk Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Export Ticket List"):
                ticket_list = []
                for item in st.session_state.created_tickets:
                    ticket = item['ticket']
                    ticket_list.append(f"{ticket['key']}: {item['task']} - {ticket['url']}")
                
                ticket_text = "\n".join(ticket_list)
                st.download_button(
                    label="💾 Download Ticket List",
                    data=ticket_text,
                    file_name="jira_tickets.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🗑️ Clear Ticket History"):
                del st.session_state.created_tickets
                st.rerun()

if __name__ == "__main__":
    main()