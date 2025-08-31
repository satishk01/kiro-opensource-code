import streamlit as st
import os
from pathlib import Path
try:
    from services.enhanced_ai_service import EnhancedAIService as AIService
except ImportError:
    from services.ai_service import AIService
    
try:
    from services.enhanced_file_service import EnhancedFileService as FileService
except ImportError:
    from services.file_service import FileService
from engines.spec_engine import SpecEngine
import tkinter as tk
from tkinter import filedialog
import tempfile
import zipfile

# Configure Streamlit page
st.set_page_config(
    page_title="New Project - Kiro AI Assistant",
    page_icon="🚀",
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
        st.session_state.coding_standards = {}
    
    # Sidebar for navigation and model selection
    with st.sidebar:
        st.title("🚀 New Project - Kiro AI")
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
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Choose a page:",
            ["Home", "Enhanced Folder Selection", "Spec Generation", "Coding Standards", "Diagrams", "JIRA Integration"],
            key="navigation"
        )
    
    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Enhanced Folder Selection":
        show_enhanced_folder_selection()
    elif page == "Spec Generation":
        show_spec_generation()
    elif page == "Coding Standards":
        show_coding_standards()
    elif page == "Diagrams":
        show_diagrams()
    elif page == "JIRA Integration":
        show_jira_integration()

def show_home_page():
    st.title("Welcome to New Project - Enhanced Kiro AI Assistant")
    st.markdown("""
    This is an enhanced version of Kiro with improved folder selection capabilities and coding standards integration.
    
    ## 🆕 New Features:
    
    - **Enhanced Folder Selection**: Browse and select folders using native file dialogs
    - **ZIP File Support**: Upload and extract ZIP files with improved handling
    - **Coding Standards Integration**: Define and apply coding standards for spec generation
    - **Improved UI**: Better user experience with native file selection
    
    ## 🛠️ Core Features:
    
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
        standards_count = len(st.session_state.coding_standards) if st.session_state.coding_standards else 0
        st.metric("Coding Standards", f"{standards_count} rules", "Configured" if standards_count > 0 else "Not Set")
    
    # Quick start guide
    if not st.session_state.model_connected:
        st.info("🚀 **Quick Start**: Select an AI model from the sidebar to begin using the enhanced features.")
    elif not st.session_state.current_folder:
        st.info("📁 **Next Step**: Go to 'Enhanced Folder Selection' to select and analyze your project files.")
    else:
        st.success("🎉 **Ready to go!** You can now generate specs with coding standards, create diagrams, or integrate with JIRA.")

def show_enhanced_folder_selection():
    st.title("📁 Enhanced Folder Selection")
    st.markdown("Select and analyze your project folder using improved selection methods.")
    
    # Check if AI model is connected
    if not st.session_state.model_connected:
        st.warning("⚠️ Please select and connect to an AI model first from the sidebar.")
        return
    
    # Enhanced folder selection interface
    selected_folder = st.session_state.file_service.enhanced_folder_selection()
    
    # Process folder if selected and different from current
    if selected_folder and selected_folder != st.session_state.current_folder:
        st.session_state.current_folder = selected_folder
        
        # Read files from folder
        with st.spinner("📖 Reading project files..."):
            files_content = st.session_state.file_service.read_files(selected_folder)
            st.session_state.loaded_files = files_content
            
            # Auto-detect coding standards
            detected_standards = st.session_state.file_service.detect_coding_standards(files_content)
            if detected_standards:
                st.session_state.coding_standards.update(detected_standards)
                st.info(f"🔍 Auto-detected {len(detected_standards)} coding standards from your project")
        
        if files_content:
            st.rerun()
    
    # Display current folder info
    if st.session_state.current_folder:
        st.success(f"📂 **Current Folder:** {st.session_state.current_folder}")
        
        if st.session_state.loaded_files:
            # Show enhanced file statistics
            stats = st.session_state.file_service.get_enhanced_file_stats(st.session_state.loaded_files)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", stats["total_files"])
            
            with col2:
                st.metric("Total Size", f"{stats['total_size_mb']} MB")
            
            with col3:
                st.metric("Languages", len(stats["languages"]))
            
            with col4:
                st.metric("Frameworks", len(stats.get("frameworks", [])))
            
            # Enhanced analysis display
            col1, col2 = st.columns(2)
            
            with col1:
                # Language breakdown
                if stats["languages"]:
                    st.subheader("🔤 Detected Languages")
                    for lang, count in stats["language_files"].items():
                        st.write(f"• {lang}: {count} files")
                
                # Framework detection
                if stats.get("frameworks"):
                    st.subheader("🛠️ Detected Frameworks")
                    for framework in stats["frameworks"]:
                        st.write(f"• {framework}")
            
            with col2:
                # File type breakdown
                if stats["file_types"]:
                    st.subheader("📄 File Types")
                    file_type_data = []
                    for ext, count in sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                        file_type_data.append({"Extension": ext, "Count": count})
                    
                    if file_type_data:
                        st.dataframe(file_type_data, use_container_width=True)
            
            # Enhanced codebase analysis
            st.subheader("🔍 Enhanced AI Analysis")
            
            if st.button("🤖 Analyze Codebase with Standards", type="primary"):
                with st.spinner("🧠 AI is analyzing your codebase with coding standards..."):
                    try:
                        analysis = st.session_state.ai_service.analyze_codebase_with_standards(
                            st.session_state.loaded_files, 
                            st.session_state.coding_standards
                        )
                        
                        st.markdown("### 📊 Enhanced Analysis Results")
                        st.markdown(analysis["analysis"])
                        
                        if analysis.get("standards_compliance"):
                            st.markdown("### 📋 Coding Standards Compliance")
                            st.markdown(analysis["standards_compliance"])
                        
                        # Store analysis for later use
                        st.session_state.codebase_analysis = analysis
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
        
        else:
            st.warning("⚠️ No files found in the selected folder or unable to read files.")
    
    else:
        st.info("👆 Select a project folder above to begin analysis.")

def show_spec_generation():
    st.title("📋 Enhanced Spec Generation")
    st.markdown("Generate requirements, design documents, and implementation plans with coding standards integration")
    
    # Check if AI model is connected
    if not st.session_state.model_connected:
        st.warning("⚠️ Please select and connect to an AI model first from the sidebar.")
        return
    
    # Show coding standards integration status
    if st.session_state.coding_standards:
        st.info(f"🎯 Spec generation will use {len(st.session_state.coding_standards)} coding standards from your project")
    else:
        st.warning("⚠️ No coding standards detected. Consider setting them up in the 'Coding Standards' section for better spec generation.")
    
    # Rest of spec generation logic (similar to original but enhanced)
    st.markdown("Enhanced spec generation functionality with coding standards integration will be implemented here.")

def show_coding_standards():
    st.title("📋 Coding Standards Configuration")
    st.markdown("Define and manage coding standards that will be used during spec generation")
    
    # Display current standards
    if st.session_state.coding_standards:
        st.subheader("🎯 Current Coding Standards")
        
        for category, standards in st.session_state.coding_standards.items():
            with st.expander(f"📂 {category.title()} Standards"):
                if isinstance(standards, list):
                    for standard in standards:
                        st.write(f"• {standard}")
                elif isinstance(standards, dict):
                    for key, value in standards.items():
                        st.write(f"• **{key}**: {value}")
                else:
                    st.write(f"• {standards}")
    
    # Add new standards
    st.subheader("➕ Add New Standards")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Standard Category",
            ["Code Style", "Architecture", "Testing", "Documentation", "Security", "Performance", "Custom"]
        )
    
    with col2:
        if category == "Custom":
            custom_category = st.text_input("Custom Category Name")
            if custom_category:
                category = custom_category
    
    standard_text = st.text_area(
        "Standard Description",
        placeholder="Enter the coding standard or guideline...",
        height=100
    )
    
    if st.button("➕ Add Standard") and standard_text:
        if category not in st.session_state.coding_standards:
            st.session_state.coding_standards[category] = []
        
        if isinstance(st.session_state.coding_standards[category], list):
            st.session_state.coding_standards[category].append(standard_text)
        else:
            st.session_state.coding_standards[category] = [st.session_state.coding_standards[category], standard_text]
        
        st.success(f"✅ Added standard to {category}")
        st.rerun()
    
    # Import/Export standards
    st.subheader("📥📤 Import/Export Standards")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Import from Project"):
            if st.session_state.loaded_files:
                detected = st.session_state.file_service.detect_coding_standards(st.session_state.loaded_files)
                if detected:
                    st.session_state.coding_standards.update(detected)
                    st.success(f"✅ Imported {len(detected)} standards from project")
                    st.rerun()
                else:
                    st.info("No additional standards detected in project")
            else:
                st.warning("No project loaded. Please select a folder first.")
    
    with col2:
        if st.session_state.coding_standards:
            import json
            standards_json = json.dumps(st.session_state.coding_standards, indent=2)
            st.download_button(
                "📤 Export Standards",
                data=standards_json,
                file_name="coding_standards.json",
                mime="application/json"
            )

def show_diagrams():
    st.title("📊 Diagrams")
    st.markdown("Generate ER diagrams and data flow visualizations from your codebase")
    
    # Placeholder for diagram generation
    st.info("Enhanced diagram generation functionality will be implemented in upcoming tasks")

def show_jira_integration():
    st.title("🎯 JIRA Integration")
    st.markdown("Create and manage JIRA tickets from your specifications")
    
    # Placeholder for JIRA integration
    st.info("Enhanced JIRA integration functionality will be implemented in upcoming tasks")

if __name__ == "__main__":
    main()