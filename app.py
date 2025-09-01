import streamlit as st
import os
import re
from pathlib import Path
from datetime import datetime
from services.ai_service import AIService
from services.file_service import FileService
from engines.spec_engine import SpecEngine

# Configure Streamlit page
st.set_page_config(
    page_title="OpenFlux AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom CSS for OpenFlux styling
def load_css():
    css_file = Path("styles/openflux_theme.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def validate_mermaid_diagram(diagram_code: str) -> tuple[bool, str]:
    """Validate Mermaid diagram syntax and structure"""
    if not diagram_code or not diagram_code.strip():
        return False, "Empty diagram code"
    
    lines = diagram_code.strip().split('\n')
    
    # Check for valid diagram type
    valid_types = ['graph', 'flowchart', 'sequenceDiagram', 'erDiagram', 'classDiagram', 'gitgraph', 'pie', 'journey']
    first_line = lines[0].strip()
    has_valid_type = any(first_line.startswith(diagram_type) for diagram_type in valid_types)
    
    if not has_valid_type:
        return False, f"Invalid or missing diagram type. Found: '{first_line}'"
    
    # Check for common syntax issues
    issues = []
    
    # Check for unmatched brackets
    bracket_count = 0
    for line in lines:
        bracket_count += line.count('[') - line.count(']')
    if bracket_count != 0:
        issues.append("Unmatched square brackets")
    
    # Check for invalid characters in node IDs
    for line in lines:
        if '-->' in line or '->' in line:
            # Extract node IDs from connection lines
            parts = re.split(r'-->|->|\s+', line.strip())
            for part in parts:
                if part and not re.match(r'^[a-zA-Z0-9_\-\[\](){}":;,\s<>|&%]*$', part):
                    issues.append(f"Invalid characters in line: {line.strip()}")
                    break
    
    # Check for proper subgraph closure
    subgraph_count = sum(1 for line in lines if line.strip().startswith('subgraph'))
    end_count = sum(1 for line in lines if line.strip() == 'end')
    if subgraph_count > end_count:
        issues.append("Unclosed subgraph(s)")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, "Diagram syntax is valid"

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
        st.title("🤖 OpenFlux AI Assistant")
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
    st.title("Welcome to OpenFlux AI Assistant")
    st.markdown("""
    I'm OpenFlux, your AI-powered development companion. I'm here to help you with:
    
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
        st.info("🚀 **Quick Start**: Select an AI model from the sidebar to begin using OpenFlux's features.")
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
    st.markdown("Select and analyze your project folder to get started with OpenFlux's AI assistance.")
    
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
    st.markdown("Generate requirements, design documents, and implementation plans using OpenFlux's methodology")
    
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
    st.markdown("Generate various types of diagrams from your codebase analysis")
    
    # Check if we have analyzed files
    if 'analyzed_files' not in st.session_state or not st.session_state.analyzed_files:
        st.warning("⚠️ No analyzed files found. Please go to 'Folder Analysis' first to analyze your codebase.")
        return
    
    # Initialize services
    if 'ai_service' not in st.session_state:
        st.session_state.ai_service = AIService()
    
    if 'diagram_generator' not in st.session_state:
        from generators.diagram_generator import DiagramGenerator
        st.session_state.diagram_generator = DiagramGenerator(st.session_state.ai_service)
    
    # Diagram type selection
    diagram_types = {
        "ER Diagram": "Entity-Relationship diagram showing data models and relationships",
        "Data Flow Diagram": "Flow diagram showing data movement through the system",
        "Architecture Diagram": "High-level system architecture and components",
        "Class Diagram": "Object-oriented class structures and relationships",
        "AWS Architecture": "AWS cloud architecture with services and connections",
        "Sequence Diagram": "Interaction flows and API communications"
    }
    
    selected_type = st.selectbox(
        "Select Diagram Type:",
        options=list(diagram_types.keys()),
        help="Choose the type of diagram to generate from your codebase"
    )
    
    st.info(f"📋 {diagram_types[selected_type]}")
    
    # Generate diagram button
    if st.button(f"🎨 Generate {selected_type}", type="primary"):
        with st.spinner(f"Generating {selected_type.lower()}..."):
            try:
                codebase = st.session_state.analyzed_files
                analysis = st.session_state.get('analysis_results', {})
                
                # Generate the selected diagram type
                if selected_type == "ER Diagram":
                    diagram_code = st.session_state.diagram_generator.generate_er_diagram(codebase, analysis)
                elif selected_type == "Data Flow Diagram":
                    diagram_code = st.session_state.diagram_generator.generate_data_flow_diagram(codebase, analysis)
                elif selected_type == "Architecture Diagram":
                    diagram_code = st.session_state.diagram_generator.generate_architecture_diagram(codebase, analysis)
                elif selected_type == "Class Diagram":
                    diagram_code = st.session_state.diagram_generator.generate_class_diagram(codebase, analysis)
                elif selected_type == "AWS Architecture":
                    diagram_code = st.session_state.diagram_generator.generate_aws_architecture_diagram(codebase, analysis)
                elif selected_type == "Sequence Diagram":
                    diagram_code = st.session_state.diagram_generator.generate_sequence_diagram(codebase, analysis)
                
                # Store the generated diagram
                st.session_state.current_diagram = {
                    'type': selected_type,
                    'code': diagram_code
                }
                
                st.success(f"✅ {selected_type} generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating diagram: {str(e)}")
    
    # Display generated diagram
    if 'current_diagram' in st.session_state:
        diagram = st.session_state.current_diagram
        
        st.subheader(f"📊 {diagram['type']}")
        
<<<<<<< HEAD
        # Show data source info
        source_info = diagram.get('source', 'Unknown')
        st.info(f"📋 Generated from: **{source_info}**")
        
        # Display the Mermaid diagram with validation
=======
        # Display the Mermaid diagram
>>>>>>> parent of b0b6632 (diagrams gen1)
        try:
            # Validate diagram before displaying
            is_valid, validation_message = validate_mermaid_diagram(diagram['code'])
            
            if not is_valid:
                st.warning(f"⚠️ Diagram validation warning: {validation_message}")
            else:
                st.success("✅ Diagram syntax validated successfully")
            
            st.code(diagram['code'], language='mermaid')
            
            # Render the diagram using Streamlit's built-in support
            with st.expander("🖼️ Rendered Diagram", expanded=True):
                # Show validation status
                if is_valid:
                    st.success("✅ Diagram ready for export and viewing")
                else:
                    st.warning(f"⚠️ {validation_message}")
                
                # Note: Streamlit doesn't have native Mermaid support, so we show the code
                st.markdown("```mermaid\n" + diagram['code'] + "\n```")
                
                # Provide helpful links
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("🔗 [Mermaid Live Editor](https://mermaid.live)")
                with col2:
                    st.markdown("🔗 [GitHub Mermaid Docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)")
                with col3:
                    st.markdown("🔗 [Mermaid Documentation](https://mermaid.js.org/)")
                
                st.info("💡 Copy the code above and paste it into any of these Mermaid viewers to see the rendered diagram.")
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download Mermaid Code",
                    data=diagram['code'],
                    file_name=f"{diagram['type'].lower().replace(' ', '_')}.mmd",
                    mime="text/plain"
                )
            
            with col2:
                # Create a robust HTML file with error handling
                from datetime import datetime
                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{diagram['type']} - OpenFlux Generated</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #FF9900;
        }}
        .header h1 {{
            color: #232F3E;
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .diagram-container {{
            text-align: center;
            margin: 20px 0;
            padding: 25px;
            background: #fafafa;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }}
        .mermaid {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            max-width: 100%;
            overflow-x: auto;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #888;
            font-size: 0.9em;
        }}
        .error-message {{
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(255,107,107,0.3);
        }}
        .error-message h3 {{
            margin-top: 0;
            color: white;
        }}
        .error-code {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .links a {{
            color: #3498db;
            text-decoration: none;
            padding: 8px 16px;
            background: #ecf0f1;
            border-radius: 5px;
            transition: all 0.3s ease;
        }}
        .links a:hover {{
            background: #3498db;
            color: white;
            transform: translateY(-2px);
        }}
        .loading {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #FF9900;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {diagram['type']}</h1>
            <p>Generated by OpenFlux from {diagram.get('source', 'Unknown Source')}</p>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Rendering diagram...</p>
        </div>
        
        <div class="diagram-container" id="diagram-container" style="display: none;">
            <div class="mermaid" id="diagram">
{diagram['code']}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered by OpenFlux & Mermaid.js v10.6.1</p>
        </div>
    </div>

    <script>
        // Configure Mermaid with comprehensive error handling
        mermaid.initialize({{
            startOnLoad: false,
            theme: 'default',
            themeVariables: {{
                primaryColor: '#FF9900',
                primaryTextColor: '#232F3E',
                primaryBorderColor: '#FF9900',
                lineColor: '#232F3E',
                secondaryColor: '#f8f9fa',
                tertiaryColor: '#ffffff',
                background: '#ffffff',
                mainBkg: '#ffffff',
                secondBkg: '#f8f9fa',
                tertiaryBkg: '#ffffff'
            }},
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            sequence: {{
                useMaxWidth: true,
                wrap: true,
                width: 150
            }},
            er: {{
                useMaxWidth: true
            }},
            class: {{
                useMaxWidth: true
            }},
            securityLevel: 'loose',
            maxTextSize: 50000,
            maxEdges: 500,
            fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif'
        }});

        // Enhanced diagram rendering with comprehensive error handling
        async function renderDiagram() {{
            const loadingElement = document.getElementById('loading');
            const containerElement = document.getElementById('diagram-container');
            const diagramElement = document.getElementById('diagram');
            
            try {{
                // Show loading state
                loadingElement.style.display = 'block';
                containerElement.style.display = 'none';
                
                // Get the diagram code
                const diagramCode = diagramElement.textContent.trim();
                
                // Validate diagram code before rendering
                if (!diagramCode) {{
                    throw new Error('Empty diagram code');
                }}
                
                // Render the diagram
                const {{ svg }} = await mermaid.render('generatedDiagram', diagramCode);
                
                // Successfully rendered
                diagramElement.innerHTML = svg;
                loadingElement.style.display = 'none';
                containerElement.style.display = 'block';
                
                // Add click handlers for better interactivity
                const svgElement = diagramElement.querySelector('svg');
                if (svgElement) {{
                    svgElement.style.maxWidth = '100%';
                    svgElement.style.height = 'auto';
                }}
                
            }} catch (error) {{
                console.error('Mermaid rendering error:', error);
                
                // Hide loading and show error
                loadingElement.style.display = 'none';
                containerElement.style.display = 'block';
                
                // Create comprehensive error display
                diagramElement.innerHTML = `
                    <div class="error-message">
                        <h3>⚠️ Diagram Rendering Error</h3>
                        <p><strong>Error:</strong> ${{error.message || 'Unknown rendering error'}}</p>
                        <p>The diagram could not be rendered due to a syntax or compatibility issue. The raw Mermaid code is shown below:</p>
                        <div class="error-code">{diagram['code'].replace('<', '&lt;').replace('>', '&gt;')}</div>
                        <div class="links">
                            <a href="https://mermaid.live" target="_blank">🔗 Try in Mermaid Live Editor</a>
                            <a href="https://mermaid.js.org/syntax/" target="_blank">📚 Mermaid Documentation</a>
                            <a href="https://github.com/mermaid-js/mermaid/issues" target="_blank">🐛 Report Issue</a>
                        </div>
                        <p><small><strong>Tip:</strong> Copy the code above and paste it into the Mermaid Live Editor to debug and fix any syntax issues.</small></p>
                    </div>
                `;
            }}
        }}

        // Start rendering when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            // Add a small delay to ensure everything is loaded
            setTimeout(renderDiagram, 100);
        }});
        
        // Handle window resize for responsive diagrams
        window.addEventListener('resize', function() {{
            const svgElement = document.querySelector('#diagram svg');
            if (svgElement) {{
                svgElement.style.maxWidth = '100%';
                svgElement.style.height = 'auto';
            }}
        }});
    </script>
</body>
</html>"""
                st.download_button(
                    label="📄 Download HTML",
                    data=html_content,
                    file_name=f"{diagram['type'].lower().replace(' ', '_')}.html",
                    mime="text/html"
                )
        
        except Exception as e:
            st.error(f"❌ Error displaying diagram: {str(e)}")
    
    # AWS Labs MCP Server Status
    with st.expander("🔧 AWS Labs MCP Server Status"):
        if st.button("🔍 Check AWS Labs MCP Server Status"):
            try:
                from services.mcp_service import MCPService
                mcp_service = MCPService()
                
                # Test the AWS Labs MCP server
                test_result = mcp_service.test_aws_labs_mcp_server()
                
                if test_result["available"]:
                    st.success("✅ AWS Labs MCP Server is available and ready")
                    if test_result["version"]:
                        st.info(f"📦 Version: {test_result['version']}")
                    
                    if "diagram_generation" in test_result["capabilities"]:
                        st.success("🎨 Diagram generation capability confirmed")
                        st.info("💡 AWS Architecture diagrams will use AWS Labs MCP server for enhanced generation")
                    else:
                        st.warning("⚠️ Diagram generation capability not confirmed")
                        st.info("🔄 Will use enhanced fallback diagram generation")
                else:
                    st.warning("⚠️ AWS Labs MCP Server not available")
                    if test_result["error"]:
                        st.error(f"Error: {test_result['error']}")
                    
                    st.info("💡 Install with: `pip install uv && uvx awslabs.aws-documentation-mcp-server@latest --help`")
                    st.info("🔄 Enhanced fallback diagram generation will be used")
                    
            except Exception as e:
                st.error(f"❌ Error checking AWS Labs MCP server: {str(e)}")
        
        st.markdown("""
        **AWS Labs MCP Configuration:**
        - Server: `awslabs.aws-documentation-mcp-server@latest`
        - Purpose: Generate comprehensive AWS architecture diagrams
        - Features: AWS best practices, service recommendations, proper connections
        
        **Installation:**
        ```bash
        # Install uv and uvx
        pip install uv
        
        # Test AWS Labs MCP server
        uvx awslabs.aws-documentation-mcp-server@latest --help
        ```
        - Command: `uvx awslabs.aws-diagram-mcp-server`
        - Status: Auto-configured in `.openflux/settings/mcp.json`
        """)
    
    # Help section
    with st.expander("❓ Diagram Types Help"):
        st.markdown("""
        **Available Diagram Types:**
        
        - **ER Diagram**: Shows database entities, attributes, and relationships
        - **Data Flow Diagram**: Illustrates how data moves through your system
        - **Architecture Diagram**: High-level view of system components and layers
        - **Class Diagram**: Object-oriented classes, methods, and inheritance
        - **AWS Architecture**: Cloud infrastructure with AWS services (uses MCP server)
        - **Sequence Diagram**: Time-ordered interactions between components
        
        **Tips:**
        - Ensure your codebase is analyzed first in 'Folder Analysis'
        - AWS diagrams work best with cloud-native applications
        - Sequence diagrams are great for API-heavy applications
        - All diagrams are generated in Mermaid format for easy sharing
        """)

def generate_jira_templates(parsed_tasks, issue_type, priority, project_key, add_labels, assignee="", epic_link="", story_points="", components="", fix_versions="", affects_versions=""):
    """Generate production-grade JIRA ticket templates in different formats"""
    import json
    import csv
    from io import StringIO
    from datetime import datetime, timedelta
    
    # Prepare template data with comprehensive JIRA fields
    template_data = []
    
    for i, task in enumerate(parsed_tasks, 1):
        labels = ["openflux-generated", "implementation"] if add_labels else []
        
        # Estimate story points based on task complexity
        estimated_points = len(task.get("subtasks", [])) + 2 if not story_points else story_points
        
        # Create comprehensive ticket data
        ticket_data = {
            # Core fields
            "summary": task["title"],
            "description": task["description"] if task["description"] else f"Implementation task: {task['title']}",
            "issue_type": issue_type,
            "priority": priority,
            "project_key": project_key,
            
            # Assignment and ownership
            "assignee": assignee,
            "reporter": "openflux-ai-assistant",
            
            # Planning fields
            "story_points": estimated_points,
            "epic_link": epic_link,
            "original_estimate": f"{estimated_points * 4}h",  # 4 hours per story point
            "remaining_estimate": f"{estimated_points * 4}h",
            
            # Versioning
            "fix_versions": fix_versions.split(",") if fix_versions else [],
            "affects_versions": affects_versions.split(",") if affects_versions else [],
            
            # Components and labels
            "components": components.split(",") if components else ["Development"],
            "labels": labels,
            
            # Custom fields
            "environment": "Development",
            "due_date": (datetime.now() + timedelta(days=estimated_points * 2)).strftime("%Y-%m-%d"),
            
            # OpenFlux-specific fields
            "requirements": task.get("requirements", []),
            "subtasks": [st["title"] for st in task.get("subtasks", [])],
            "acceptance_criteria": [
                f"Complete implementation of {task['title']}",
                "Code review passed",
                "Unit tests written and passing",
                "Documentation updated"
            ],
            
            # Status and workflow
            "status": "To Do",
            "resolution": "",
            
            # Additional metadata
            "created_by": "OpenFlux AI Assistant",
            "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_number": task.get("number", str(i))
        }
        
        template_data.append(ticket_data)
    
    # Generate CSV format with comprehensive fields
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    
    # Comprehensive CSV headers
    csv_writer.writerow([
        "Summary", "Description", "Issue Type", "Priority", "Project Key", 
        "Assignee", "Reporter", "Story Points", "Epic Link", "Original Estimate",
        "Components", "Fix Versions", "Affects Versions", "Labels", "Environment",
        "Due Date", "Status", "Requirements", "Subtasks", "Acceptance Criteria",
        "Created By", "Creation Date", "Task Number"
    ])
    
    # CSV data
    for ticket in template_data:
        csv_writer.writerow([
            ticket["summary"],
            ticket["description"],
            ticket["issue_type"],
            ticket["priority"],
            ticket["project_key"],
            ticket["assignee"],
            ticket["reporter"],
            ticket["story_points"],
            ticket["epic_link"],
            ticket["original_estimate"],
            "; ".join(ticket["components"]),
            "; ".join(ticket["fix_versions"]),
            "; ".join(ticket["affects_versions"]),
            "; ".join(ticket["labels"]),
            ticket["environment"],
            ticket["due_date"],
            ticket["status"],
            "; ".join(ticket["requirements"]),
            "; ".join(ticket["subtasks"]),
            "; ".join(ticket["acceptance_criteria"]),
            ticket["created_by"],
            ticket["creation_date"],
            ticket["task_number"]
        ])
    
    csv_content = csv_buffer.getvalue()
    
    # Generate JSON format (JIRA API ready) with comprehensive fields
    json_tickets = []
    for ticket in template_data:
        json_ticket = {
            "fields": {
                "project": {"key": ticket["project_key"]},
                "summary": ticket["summary"],
                "description": ticket["description"],
                "issuetype": {"name": ticket["issue_type"]},
                "priority": {"name": ticket["priority"]},
                "reporter": {"name": ticket["reporter"]},
                "environment": ticket["environment"],
                "duedate": ticket["due_date"]
            }
        }
        
        # Add optional fields if they exist
        if ticket["assignee"]:
            json_ticket["fields"]["assignee"] = {"name": ticket["assignee"]}
        
        if ticket["story_points"]:
            json_ticket["fields"]["customfield_10016"] = ticket["story_points"]  # Common story points field
        
        if ticket["epic_link"]:
            json_ticket["fields"]["customfield_10014"] = ticket["epic_link"]  # Common epic link field
        
        if ticket["original_estimate"]:
            json_ticket["fields"]["timetracking"] = {
                "originalEstimate": ticket["original_estimate"],
                "remainingEstimate": ticket["remaining_estimate"]
            }
        
        if ticket["components"]:
            json_ticket["fields"]["components"] = [{"name": comp.strip()} for comp in ticket["components"]]
        
        if ticket["fix_versions"]:
            json_ticket["fields"]["fixVersions"] = [{"name": ver.strip()} for ver in ticket["fix_versions"]]
        
        if ticket["affects_versions"]:
            json_ticket["fields"]["versions"] = [{"name": ver.strip()} for ver in ticket["affects_versions"]]
        
        if ticket["labels"]:
            json_ticket["fields"]["labels"] = ticket["labels"]
        
        json_tickets.append(json_ticket)
    
    json_content = json.dumps({"issues": json_tickets}, indent=2)
    
    # Generate comprehensive Markdown format
    md_content = "# JIRA Ticket Templates\n\n"
    md_content += f"**Project:** {project_key}\n"
    md_content += f"**Issue Type:** {issue_type}\n"
    md_content += f"**Priority:** {priority}\n"
    md_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, ticket in enumerate(template_data, 1):
        md_content += f"## Ticket {i}: {ticket['summary']}\n\n"
        
        # Core information
        md_content += f"**Summary:** {ticket['summary']}\n\n"
        md_content += f"**Description:**\n{ticket['description']}\n\n"
        
        # Planning information
        md_content += f"**Issue Type:** {ticket['issue_type']}\n"
        md_content += f"**Priority:** {ticket['priority']}\n"
        md_content += f"**Story Points:** {ticket['story_points']}\n"
        md_content += f"**Original Estimate:** {ticket['original_estimate']}\n"
        md_content += f"**Due Date:** {ticket['due_date']}\n\n"
        
        # Assignment
        if ticket["assignee"]:
            md_content += f"**Assignee:** {ticket['assignee']}\n"
        md_content += f"**Reporter:** {ticket['reporter']}\n\n"
        
        # Components and versions
        if ticket["components"]:
            md_content += f"**Components:** {', '.join(ticket['components'])}\n"
        if ticket["fix_versions"]:
            md_content += f"**Fix Versions:** {', '.join(ticket['fix_versions'])}\n"
        if ticket["affects_versions"]:
            md_content += f"**Affects Versions:** {', '.join(ticket['affects_versions'])}\n"
        
        # OpenFlux-specific information
        if ticket["requirements"]:
            md_content += f"**Requirements:** {', '.join(ticket['requirements'])}\n"
        
        if ticket["subtasks"]:
            md_content += f"**Subtasks:**\n"
            for subtask in ticket["subtasks"]:
                md_content += f"- {subtask}\n"
            md_content += "\n"
        
        # Acceptance criteria
        md_content += f"**Acceptance Criteria:**\n"
        for criteria in ticket["acceptance_criteria"]:
            md_content += f"- {criteria}\n"
        md_content += "\n"
        
        # Labels and metadata
        if ticket["labels"]:
            md_content += f"**Labels:** {', '.join(ticket['labels'])}\n"
        md_content += f"**Environment:** {ticket['environment']}\n"
        md_content += f"**Status:** {ticket['status']}\n\n"
        
        md_content += "---\n\n"
    
    # Generate Tasks.md format (OpenFlux-style)
    tasks_md_content = "# Implementation Tasks (JIRA Export)\n\n"
    tasks_md_content += f"Generated from OpenFlux on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, ticket in enumerate(template_data, 1):
        # Main task checkbox
        tasks_md_content += f"- [ ] {ticket['task_number']}. {ticket['summary']}\n"
        
        # Task details
        tasks_md_content += f"  - **Priority:** {ticket['priority']}\n"
        tasks_md_content += f"  - **Story Points:** {ticket['story_points']}\n"
        tasks_md_content += f"  - **Estimate:** {ticket['original_estimate']}\n"
        tasks_md_content += f"  - **Due Date:** {ticket['due_date']}\n"
        
        if ticket["assignee"]:
            tasks_md_content += f"  - **Assignee:** {ticket['assignee']}\n"
        
        # Description
        if ticket["description"]:
            desc_lines = ticket["description"].split('\n')
            for line in desc_lines:
                if line.strip():
                    tasks_md_content += f"  - {line.strip()}\n"
        
        # Subtasks
        if ticket["subtasks"]:
            for j, subtask in enumerate(ticket["subtasks"], 1):
                tasks_md_content += f"  - [ ] {ticket['task_number']}.{j} {subtask}\n"
        
        # Requirements reference
        if ticket["requirements"]:
            tasks_md_content += f"  - _Requirements: {', '.join(ticket['requirements'])}_\n"
        
        # Acceptance criteria
        tasks_md_content += f"  - **Acceptance Criteria:**\n"
        for criteria in ticket["acceptance_criteria"]:
            tasks_md_content += f"    - {criteria}\n"
        
        tasks_md_content += "\n"
    
    return {
        "csv": csv_content,
        "json": json_content,
        "markdown": md_content,
        "tasks_md": tasks_md_content,
        "count": len(template_data)
    }

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
        st.info("💡 You can create tickets online (with JIRA connection) or offline (download templates)")
    
    st.markdown("---")
    
    # Mode Selection
    st.subheader("🎯 Ticket Creation Mode")
    
    mode_col1, mode_col2 = st.columns(2)
    
    with mode_col1:
        online_mode = st.button(
            "🌐 Online Mode (Connect to JIRA)",
            disabled=not st.session_state.get('jira_configured', False),
            help="Create tickets directly in your JIRA instance" if st.session_state.get('jira_configured', False) else "Configure JIRA connection first",
            type="primary" if st.session_state.get('jira_configured', False) else "secondary"
        )
    
    with mode_col2:
        offline_mode = st.button(
            "📱 Offline Mode (Download Templates)",
            help="Generate JIRA ticket templates and download them",
            type="primary"
        )
    
    # Set mode in session state
    if online_mode:
        st.session_state.jira_mode = 'online'
    elif offline_mode:
        st.session_state.jira_mode = 'offline'
    
    # Default to offline if no JIRA connection
    if not st.session_state.get('jira_mode') and not st.session_state.get('jira_configured', False):
        st.session_state.jira_mode = 'offline'
    elif not st.session_state.get('jira_mode'):
        st.session_state.jira_mode = 'online'
    
    # Show current mode
    current_mode = st.session_state.get('jira_mode', 'offline')
    if current_mode == 'online':
        st.info("🌐 **Online Mode**: Tickets will be created directly in JIRA")
    else:
        st.info("📱 **Offline Mode**: Ticket templates will be generated for download")
    
    st.markdown("---")
    
    # Ticket Creation Section
    st.subheader("🎫 Create Tickets from Tasks")
    
    # Get tasks from either completed spec or current workflow
    tasks_content = None
    tasks_source = None
    
    if hasattr(st.session_state, 'completed_spec') and st.session_state.completed_spec.get('tasks'):
        tasks_content = st.session_state.completed_spec['tasks']
        tasks_source = "Completed Spec"
    elif hasattr(st.session_state, 'spec_workflow_state') and st.session_state.spec_workflow_state.get('tasks_content'):
        tasks_content = st.session_state.spec_workflow_state['tasks_content']
        tasks_source = "Current Workflow"
    
    if tasks_content:
        st.markdown(f"### 📋 Available Tasks ({tasks_source})")
        
        # Show preview of tasks
        with st.expander("👀 Preview Tasks", expanded=False):
            st.markdown(tasks_content)
        
        # Production-grade JIRA ticket configuration
        st.markdown("### ⚙️ JIRA Ticket Configuration")
        
        # Core ticket fields
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get available issue types (only for online mode)
            if current_mode == 'online' and st.session_state.get('jira_configured', False):
                issue_types = st.session_state.jira_client.get_issue_types()
                issue_type_names = [it['name'] for it in issue_types] if issue_types else ['Task', 'Story', 'Bug']
            else:
                issue_type_names = ['Task', 'Story', 'Bug', 'Epic', 'Sub-task', 'Improvement']
            
            selected_issue_type = st.selectbox(
                "Issue Type",
                issue_type_names,
                index=0,
                help="Type of JIRA tickets to create"
            )
        
        with col2:
            priority_options = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
            default_priority = st.selectbox(
                "Priority",
                priority_options,
                index=2,  # Medium
                help="Priority level for tickets"
            )
        
        with col3:
            story_points = st.selectbox(
                "Story Points (Auto-estimated)",
                ["Auto", "1", "2", "3", "5", "8", "13", "21"],
                index=0,
                help="Story points for estimation (Auto calculates based on complexity)"
            )
        
        # Assignment and ownership
        col1, col2 = st.columns(2)
        
        with col1:
            assignee = st.text_input(
                "Assignee (Optional)",
                placeholder="john.doe",
                help="JIRA username to assign tickets to"
            )
        
        with col2:
            epic_link = st.text_input(
                "Epic Link (Optional)",
                placeholder="PROJ-123",
                help="Link tickets to an existing epic"
            )
        
        # Versioning and components
        col1, col2 = st.columns(2)
        
        with col1:
            components = st.text_input(
                "Components",
                value="Development",
                placeholder="Development, Backend, Frontend",
                help="Comma-separated list of components"
            )
        
        with col2:
            fix_versions = st.text_input(
                "Fix Versions (Optional)",
                placeholder="v1.0.0, v1.1.0",
                help="Comma-separated list of target versions"
            )
        
        # Additional fields
        with st.expander("🔧 Advanced Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                affects_versions = st.text_input(
                    "Affects Versions (Optional)",
                    placeholder="v0.9.0",
                    help="Versions affected by this issue"
                )
                
                add_labels = st.checkbox(
                    "Add OpenFlux Labels", 
                    value=True, 
                    help="Add 'openflux-generated' and 'implementation' labels"
                )
            
            with col2:
                environment = st.selectbox(
                    "Environment",
                    ["Development", "Testing", "Staging", "Production"],
                    index=0,
                    help="Target environment for the work"
                )
        
        # Project key for offline mode
        if current_mode == 'offline':
            offline_project_key = st.text_input(
                "Project Key (for templates)",
                value="PROJ",
                help="Project key to use in ticket templates"
            )
        
        # Create tickets button - different behavior based on mode
        if current_mode == 'online':
            button_text = "🌐 Create JIRA Tickets Online"
            button_help = "Create tickets directly in your JIRA instance"
        else:
            button_text = "📱 Generate Ticket Templates"
            button_help = "Generate JIRA ticket templates for download"
        
        if st.button(button_text, type="primary", help=button_help):
            if current_mode == 'online':
                # Online mode - create actual JIRA tickets
                with st.spinner("Creating JIRA tickets online..."):
                    try:
                        created_tickets = st.session_state.jira_client.create_tickets_from_tasks(
                            tasks_content,
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
            
            else:
                # Offline mode - generate templates
                with st.spinner("Generating JIRA ticket templates..."):
                    try:
                        # Parse tasks and generate templates
                        parsed_tasks = st.session_state.jira_client.parse_tasks_from_markdown(tasks_content)
                        
                        if parsed_tasks:
                            # Generate different template formats with comprehensive fields
                            templates = generate_jira_templates(
                                parsed_tasks, 
                                selected_issue_type, 
                                default_priority,
                                offline_project_key,
                                add_labels,
                                assignee=assignee,
                                epic_link=epic_link,
                                story_points=story_points if story_points != "Auto" else "",
                                components=components,
                                fix_versions=fix_versions,
                                affects_versions=affects_versions
                            )
                            
                            st.success(f"✅ Generated templates for {len(parsed_tasks)} tickets!")
                            
                            # Store templates for display and download
                            st.session_state.jira_templates = templates
                            
                            # Show templates
                            st.markdown("### 📄 Generated Templates")
                            
                            # Template format selection
                            template_format = st.radio(
                                "Choose template format:",
                                ["CSV (Production JIRA)", "JSON (API ready)", "Markdown (Human readable)", "Tasks.md (OpenFlux format)"],
                                horizontal=True
                            )
                            
                            # Display and download templates
                            if template_format == "CSV (Production JIRA)":
                                csv_content = templates['csv']
                                st.markdown("#### Production JIRA CSV with 23+ Fields")
                                st.text_area("CSV Template (Production-grade with all JIRA fields)", csv_content, height=200)
                                st.download_button(
                                    "💾 Download Production CSV",
                                    csv_content,
                                    "jira_production_tickets.csv",
                                    "text/csv",
                                    help="Excel-compatible CSV with all production JIRA fields"
                                )
                            
                            elif template_format == "JSON (API ready)":
                                json_content = templates['json']
                                st.markdown("#### JIRA REST API Format")
                                st.code(json_content, language='json')
                                st.download_button(
                                    "💾 Download API JSON",
                                    json_content,
                                    "jira_api_tickets.json",
                                    "application/json",
                                    help="Ready for JIRA REST API bulk import"
                                )
                            
                            elif template_format == "Markdown (Human readable)":
                                md_content = templates['markdown']
                                st.markdown("#### Production JIRA Markdown")
                                with st.container():
                                    st.markdown(md_content)
                                st.download_button(
                                    "💾 Download Production Markdown",
                                    md_content,
                                    "jira_production_tickets.md",
                                    "text/markdown",
                                    help="Human-readable format with all JIRA fields"
                                )
                            
                            else:  # Tasks.md format
                                tasks_md_content = templates['tasks_md']
                                st.markdown("#### OpenFlux Tasks.md Format")
                                st.markdown("Perfect for continuing work in OpenFlux or importing back into specs:")
                                with st.container():
                                    st.markdown(tasks_md_content)
                                st.download_button(
                                    "💾 Download Tasks.md",
                                    tasks_md_content,
                                    "implementation_tasks.md",
                                    "text/markdown",
                                    help="OpenFlux-compatible tasks format for specs"
                                )
                            
                            # Quick download section for all formats
                            st.markdown("---")
                            st.markdown("#### 📥 Quick Downloads - All Formats")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.download_button(
                                    "📊 Production CSV",
                                    templates['csv'],
                                    "jira_production.csv",
                                    "text/csv",
                                    help="23+ JIRA fields for Excel import"
                                )
                            
                            with col2:
                                st.download_button(
                                    "🔗 API JSON",
                                    templates['json'],
                                    "jira_api.json",
                                    "application/json",
                                    help="JIRA REST API ready"
                                )
                            
                            with col3:
                                st.download_button(
                                    "📝 Production MD",
                                    templates['markdown'],
                                    "jira_production.md",
                                    "text/markdown",
                                    help="Human-readable documentation"
                                )
                            
                            with col4:
                                st.download_button(
                                    "✅ Tasks.md",
                                    templates['tasks_md'],
                                    "tasks.md",
                                    "text/markdown",
                                    help="OpenFlux spec format"
                                )
                        
                        else:
                            st.error("❌ No tasks found to generate templates.")
                            
                    except Exception as e:
                        st.error(f"❌ Failed to generate templates: {e}")
    
    else:
        st.info("📋 No tasks available. Generate a spec first in the 'Spec Generation' tab.")
    
    # Management Section - different for online vs offline
    if st.session_state.get('created_tickets') or st.session_state.get('jira_templates'):
        st.markdown("---")
        st.subheader("📊 Management & History")
        
        # Online tickets management
        if st.session_state.get('created_tickets'):
            st.markdown("### 🌐 Online Tickets (Created in JIRA)")
            
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
        
        # Offline templates management
        if st.session_state.get('jira_templates'):
            st.markdown("### 📱 Offline Templates (Generated)")
            
            templates = st.session_state.jira_templates
            
            # Metrics
            st.metric("Templates Generated", templates['count'])
            
            # Download options for all formats
            st.markdown("#### 📥 Download Templates")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    "📊 Production CSV",
                    templates['csv'],
                    "jira_production_tickets.csv",
                    "text/csv",
                    help="23+ JIRA fields for Excel import"
                )
            
            with col2:
                st.download_button(
                    "🔗 API JSON",
                    templates['json'],
                    "jira_api_tickets.json",
                    "application/json",
                    help="JIRA REST API ready format"
                )
            
            with col3:
                st.download_button(
                    "📝 Production MD",
                    templates['markdown'],
                    "jira_production_tickets.md",
                    "text/markdown",
                    help="Human-readable documentation"
                )
            
            with col4:
                st.download_button(
                    "✅ Tasks.md",
                    templates['tasks_md'],
                    "implementation_tasks.md",
                    "text/markdown",
                    help="OpenFlux-compatible tasks format"
                )
            
            # Show template preview
            with st.expander("👀 Template Preview", expanded=False):
                format_choice = st.selectbox(
                    "Preview format:",
                    ["Production Markdown", "Tasks.md Format", "CSV", "JSON"],
                    key="preview_format"
                )
                
                if format_choice == "Production Markdown":
                    st.markdown(templates['markdown'])
                elif format_choice == "Tasks.md Format":
                    st.markdown(templates['tasks_md'])
                elif format_choice == "CSV":
                    st.text(templates['csv'])
                else:
                    st.code(templates['json'], language='json')
                
                # Additional download for the previewed format
                if format_choice == "Tasks.md Format":
                    st.download_button(
                        "💾 Download This Tasks.md",
                        templates['tasks_md'],
                        "preview_tasks.md",
                        "text/markdown",
                        key="preview_download_tasks"
                    )
                elif format_choice == "Production Markdown":
                    st.download_button(
                        "💾 Download This Markdown",
                        templates['markdown'],
                        "preview_production.md",
                        "text/markdown",
                        key="preview_download_markdown"
                    )
        
        # Bulk Operations
        st.markdown("---")
        st.subheader("🔧 Bulk Operations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.get('created_tickets') and st.button("📋 Export Online Tickets"):
                ticket_list = []
                for item in st.session_state.created_tickets:
                    ticket = item['ticket']
                    ticket_list.append(f"{ticket['key']}: {item['task']} - {ticket['url']}")
                
                ticket_text = "\n".join(ticket_list)
                st.download_button(
                    label="💾 Download Online Tickets",
                    data=ticket_text,
                    file_name="online_jira_tickets.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.session_state.get('jira_templates') and st.button("📱 Re-download Templates"):
                st.info("Use the download buttons above to get your templates again")
        
        with col3:
            if st.button("🗑️ Clear All History"):
                if 'created_tickets' in st.session_state:
                    del st.session_state.created_tickets
                if 'jira_templates' in st.session_state:
                    del st.session_state.jira_templates
                st.success("✅ History cleared!")
                st.rerun()
    
    # Help Section
    st.markdown("---")
    st.subheader("💡 How to Use")
    
    help_col1, help_col2 = st.columns(2)
    
    with help_col1:
        st.markdown("""
        **🌐 Online Mode:**
        1. Configure JIRA connection above
        2. Select "Online Mode"
        3. Choose issue type and priority
        4. Click "Create JIRA Tickets Online"
        5. Tickets are created directly in JIRA
        """)
    
    with help_col2:
        st.markdown("""
        **📱 Offline Mode:**
        1. Select "Offline Mode" (no JIRA connection needed)
        2. Choose issue type and priority
        3. Enter project key for templates
        4. Click "Generate Ticket Templates"
        5. Download templates in CSV, JSON, or Markdown format
        """)
    
    st.info("💡 **Tip:** Use offline mode to prepare tickets for review before creating them in JIRA, or when you don't have JIRA access.")

if __name__ == "__main__":
    main()