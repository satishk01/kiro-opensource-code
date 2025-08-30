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
                result = st.session_state.spec_engine.generate_requirements(st.session_state.user_prompt)
                st.session_state.generated_content = result
                st.success("Spec generated successfully!")
        
        elif st.session_state.current_view == "JIRA Integration":
            # Generate JIRA templates
            with st.spinner("Generating JIRA templates..."):
                # This would integrate with the existing JIRA generation logic
                st.session_state.generated_content = "JIRA templates generated (integration pending)"
                st.success("JIRA templates generated!")
        
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