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
        st.session_state.task_list = []
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
                if st.session_state.ai_service.initialize_bedrock_client():
                    st.success("✅ AWS Bedrock connection successful")
                else:
                    st.error("❌ AWS Bedrock connection failed")
        
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
    st.markdown("Generate requirements, design documents, and implementation plans")
    
    # Placeholder for spec generation
    st.info("Spec generation functionality will be implemented in upcoming tasks")

def show_diagrams():
    st.title("📊 Diagrams")
    st.markdown("Generate ER diagrams and data flow visualizations")
    
    # Placeholder for diagram generation
    st.info("Diagram generation functionality will be implemented in upcoming tasks")

def show_jira_integration():
    st.title("🎯 JIRA Integration")
    st.markdown("Create and manage JIRA tickets from generated tasks")
    
    # Placeholder for JIRA integration
    st.info("JIRA integration functionality will be implemented in upcoming tasks")

if __name__ == "__main__":
    main()