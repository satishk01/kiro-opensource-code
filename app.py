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
    
    # Placeholder for JIRA integration
    st.info("JIRA integration functionality will be implemented in upcoming tasks")

if __name__ == "__main__":
    main()