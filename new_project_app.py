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

def show_enhanced_folder_selection_fallback():
    """Enhanced folder selection fallback implementation"""
    st.subheader("📁 Enhanced Project Folder Selection")
    
    # Create tabs for different selection methods
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖱️ Browse EC2", "📝 Manual Path", "💻 Local to EC2", "📦 ZIP Upload", "🔍 Recent Projects"])
    
    with tab1:
        st.markdown("**Web-Based Folder Browser**")
        st.markdown("Browse and select folders using the web interface.")
        st.info("💡 Native OS dialogs don't work in web-based Streamlit. Use this web browser instead!")
        
        # Initialize current browse path
        if 'browse_path' not in st.session_state:
            st.session_state.browse_path = os.path.expanduser("~")
        
        # Show current path
        st.text(f"Current location: {st.session_state.browse_path}")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🏠 Home", key="home_btn"):
                st.session_state.browse_path = os.path.expanduser("~")
                st.rerun()
        
        with col2:
            if st.button("⬆️ Up", key="up_btn"):
                parent = str(Path(st.session_state.browse_path).parent)
                if parent != st.session_state.browse_path:  # Prevent going above root
                    st.session_state.browse_path = parent
                    st.rerun()
        
        with col3:
            # Quick navigation to common directories
            import platform
            system = platform.system().lower()
            if system == "windows":
                common_dirs = [
                    ("📁 Documents", os.path.join(os.path.expanduser("~"), "Documents")),
                    ("📁 Desktop", os.path.join(os.path.expanduser("~"), "Desktop")),
                    ("📁 Downloads", os.path.join(os.path.expanduser("~"), "Downloads"))
                ]
            else:
                common_dirs = [
                    ("📁 Projects", os.path.expanduser("~/Projects")),
                    ("📁 Documents", os.path.expanduser("~/Documents")),
                    ("📁 Desktop", os.path.expanduser("~/Desktop"))
                ]
            
            for name, path in common_dirs:
                if Path(path).exists() and st.button(name, key=f"quick_{path}"):
                    st.session_state.browse_path = path
                    st.rerun()
        
        # List directories in current path
        try:
            current_path = Path(st.session_state.browse_path)
            if current_path.exists() and current_path.is_dir():
                directories = [item for item in current_path.iterdir() if item.is_dir()]
                directories.sort(key=lambda x: x.name.lower())
                
                st.markdown("**📁 Directories:**")
                
                if directories:
                    # Create columns for directory listing
                    cols_per_row = 3
                    for i in range(0, len(directories), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, directory in enumerate(directories[i:i+cols_per_row]):
                            with cols[j]:
                                if st.button(f"📁 {directory.name}", key=f"dir_{directory}"):
                                    st.session_state.browse_path = str(directory)
                                    st.rerun()
                else:
                    st.info("No subdirectories found")
                
                # Select current directory button
                st.markdown("---")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("✅ Select This Folder", type="primary", key="select_current"):
                        if validate_folder_path(st.session_state.browse_path):
                            st.success(f"✅ Selected: {st.session_state.browse_path}")
                            return st.session_state.browse_path
                
                with col2:
                    st.info(f"Will select: {st.session_state.browse_path}")
            
            else:
                st.error(f"❌ Cannot access: {st.session_state.browse_path}")
                st.session_state.browse_path = os.path.expanduser("~")
                st.rerun()
                
        except PermissionError:
            st.error(f"❌ Permission denied: {st.session_state.browse_path}")
            st.session_state.browse_path = os.path.expanduser("~")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error browsing directory: {e}")
            st.session_state.browse_path = os.path.expanduser("~")
            st.rerun()
    
    with tab2:
        st.markdown("**Manual Path Entry**")
        folder_path = st.text_input(
            "Folder Path", 
            value=st.session_state.current_folder or "",
            placeholder="C:\\Users\\YourName\\Projects\\MyProject or /home/user/projects/myproject",
            help="Enter the full path to your project folder",
            key="manual_path"
        )
        
        if folder_path and folder_path != st.session_state.current_folder:
            if validate_folder_path(folder_path):
                return folder_path
    
    with tab3:
        st.markdown("**Transfer Local Project to EC2**")
        st.markdown("Multiple ways to get your local laptop project onto this EC2 instance.")
        
        # Method selection
        method = st.selectbox(
            "Choose transfer method:",
            [
                "Select a method...",
                "📦 Upload ZIP file (Recommended)",
                "📁 Upload individual files",
                "🔄 SSH/SCP Commands",
                "☁️ Git Clone from Repository"
            ],
            key="transfer_method_fallback"
        )
        
        if method == "📦 Upload ZIP file (Recommended)":
            st.markdown("### 📦 ZIP File Upload")
            st.markdown("**Step 1:** Create a ZIP file of your local project")
            st.code("""
# On your laptop:
# 1. Right-click your project folder
# 2. Select "Send to" > "Compressed folder" (Windows)
# 3. Or use: zip -r myproject.zip /path/to/project (Linux/Mac)
            """)
            
            st.markdown("**Step 2:** Upload the ZIP file")
            uploaded_zip = st.file_uploader(
                "Choose ZIP file from your laptop",
                type=['zip'],
                help="Select the ZIP file containing your project",
                key="local_zip_upload_fallback"
            )
            
            if uploaded_zip:
                if st.button("🚀 Extract and Use Project", type="primary", key="extract_fallback"):
                    extracted_path = handle_zip_upload(uploaded_zip)
                    if extracted_path:
                        st.success(f"✅ Project uploaded and extracted!")
                        st.info(f"📁 Project location: {extracted_path}")
                        return extracted_path
        
        elif method == "🔄 SSH/SCP Commands":
            st.markdown("### 🔄 SSH/SCP Transfer Commands")
            st.markdown("Use these commands on your laptop to transfer files:")
            
            # Get EC2 instance info
            import socket
            hostname = socket.gethostname()
            
            st.code(f"""
# From your laptop terminal:

# Option 1: SCP (Secure Copy)
scp -r /path/to/your/project ec2-user@{hostname}:~/uploaded-projects/

# Option 2: rsync (if available)
rsync -avz /path/to/your/project/ ec2-user@{hostname}:~/uploaded-projects/myproject/

# Then in this interface, browse to ~/uploaded-projects/myproject
            """)
            
            st.info("💡 After running these commands, use the 'Browse EC2' tab to navigate to ~/uploaded-projects/")
    
    with tab4:
        st.markdown("**ZIP File Upload**")
        uploaded_file = st.file_uploader(
            "Upload ZIP file", 
            type=['zip'],
            help="Upload your project as a ZIP file for analysis",
            key="zip_upload"
        )
        
        if uploaded_file:
            extracted_path = handle_zip_upload(uploaded_file)
            if extracted_path:
                return extracted_path
    
    with tab5:
        st.markdown("**Recent and Common Locations**")
        
        # Recent projects (stored in session state)
        if 'recent_projects' not in st.session_state:
            st.session_state.recent_projects = []
        
        if st.session_state.recent_projects:
            st.markdown("**Recent Projects:**")
            for recent_path in st.session_state.recent_projects[-5:]:  # Show last 5
                if st.button(f"📁 {recent_path}", key=f"recent_{recent_path}"):
                    if validate_folder_path(recent_path):
                        return recent_path
        
        # Common project locations
        st.markdown("**Common Locations:**")
        common_paths = get_common_project_paths()
        
        if common_paths:
            selected_path = st.selectbox(
                "Select from common project locations:",
                ["Select a folder..."] + common_paths,
                key="common_paths"
            )
            
            if selected_path != "Select a folder...":
                return selected_path
    
    return st.session_state.current_folder

def open_native_folder_dialog():
    """Open native folder selection dialog"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title="Select Project Folder",
            initialdir=os.path.expanduser("~")
        )
        
        root.destroy()
        return folder_path if folder_path else None
        
    except ImportError:
        st.error("❌ tkinter not available. Please use manual path entry.")
        return None
    except Exception as e:
        st.error(f"❌ Error opening dialog: {e}")
        return None

def validate_folder_path(folder_path):
    """Validate folder path"""
    try:
        path = Path(folder_path)
        
        if not path.exists():
            st.error(f"❌ Folder does not exist: {folder_path}")
            return False
        
        if not path.is_dir():
            st.error(f"❌ Path is not a directory: {folder_path}")
            return False
        
        # Check if we can read the directory
        try:
            list(path.iterdir())
        except PermissionError:
            st.error(f"❌ Permission denied: Cannot read folder {folder_path}")
            return False
        
        st.success(f"✅ Valid folder: {folder_path}")
        
        # Add to recent projects
        if 'recent_projects' not in st.session_state:
            st.session_state.recent_projects = []
        
        if folder_path not in st.session_state.recent_projects:
            st.session_state.recent_projects.append(folder_path)
            # Keep only last 10 recent projects
            st.session_state.recent_projects = st.session_state.recent_projects[-10:]
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error validating folder: {e}")
        return False

def handle_zip_upload(uploaded_file):
    """Handle ZIP file upload and extraction"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix=f"kiro_project_{uploaded_file.name.replace('.zip', '')}_")
        
        # Show progress for large files
        file_size = len(uploaded_file.getvalue())
        
        with st.spinner(f"Extracting {uploaded_file.name} ({file_size // 1024} KB)..."):
            # Extract ZIP file
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # Security check: prevent path traversal
                for file_path in file_list:
                    if '..' in file_path or file_path.startswith('/'):
                        st.error("❌ Security risk detected in ZIP file")
                        return None
                
                # Extract with progress
                progress_bar = st.progress(0)
                for i, file_info in enumerate(zip_ref.filelist):
                    zip_ref.extract(file_info, temp_dir)
                    progress_bar.progress((i + 1) / len(zip_ref.filelist))
                
                progress_bar.empty()
        
        st.success(f"✅ Project extracted to: {temp_dir}")
        
        # If ZIP contains a single root directory, use that instead
        extracted_items = list(Path(temp_dir).iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            return str(extracted_items[0])
        
        return temp_dir
        
    except zipfile.BadZipFile:
        st.error("❌ Invalid ZIP file")
        return None
    except Exception as e:
        st.error(f"❌ Error extracting ZIP file: {e}")
        return None

def get_enhanced_file_stats_fallback(files):
    """Enhanced file statistics fallback implementation"""
    if not files:
        return {
            "total_files": 0,
            "total_size": 0,
            "total_size_mb": 0,
            "languages": [],
            "language_files": {},
            "frameworks": [],
            "file_types": {}
        }
    
    total_size = sum(len(content) for content in files.values())
    
    # Enhanced file type analysis
    file_types = {}
    language_files = {}
    
    for file_path in files.keys():
        if '.' in file_path:
            ext = Path(file_path).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            
            # Map to languages
            lang = extension_to_language(ext)
            if lang:
                language_files[lang] = language_files.get(lang, 0) + 1
    
    # Detect frameworks
    frameworks = detect_frameworks_fallback(files)
    
    return {
        "total_files": len(files),
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "languages": list(language_files.keys()),
        "language_files": language_files,
        "frameworks": frameworks,
        "file_types": file_types
    }

def extension_to_language(ext):
    """Map file extension to programming language"""
    lang_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript',
        '.jsx': 'JavaScript', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
        '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift',
        '.kt': 'Kotlin', '.scala': 'Scala', '.vue': 'Vue.js', '.svelte': 'Svelte',
        '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass',
        '.sql': 'SQL', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
        '.xml': 'XML', '.md': 'Markdown', '.sh': 'Shell', '.bat': 'Batch'
    }
    
    return lang_map.get(ext.lower())

def detect_coding_standards_fallback(files):
    """Auto-detect coding standards from project files"""
    standards = {}
    
    # Check for linting configurations
    linting_standards = []
    if '.eslintrc.json' in files or '.eslintrc.js' in files or '.eslintrc' in files:
        linting_standards.append("ESLint configuration detected")
    if '.pylintrc' in files or 'pylint.cfg' in files:
        linting_standards.append("Pylint configuration detected")
    if '.rubocop.yml' in files:
        linting_standards.append("RuboCop configuration detected")
    
    if linting_standards:
        standards["Linting"] = linting_standards
    
    # Check for formatting configurations
    formatting_standards = []
    if '.prettierrc' in files or 'prettier.config.js' in files or '.prettierrc.json' in files:
        formatting_standards.append("Prettier code formatting")
    if 'pyproject.toml' in files and 'black' in files.get('pyproject.toml', ''):
        formatting_standards.append("Black Python formatter")
    if '.editorconfig' in files:
        formatting_standards.append("EditorConfig for consistent formatting")
    
    if formatting_standards:
        standards["Code Formatting"] = formatting_standards
    
    # Check for testing frameworks
    testing_standards = []
    if 'jest.config.js' in files or ('"jest"' in files.get('package.json', '')):
        testing_standards.append("Jest testing framework")
    if 'pytest.ini' in files or ('pytest' in files.get('requirements.txt', '')):
        testing_standards.append("Pytest testing framework")
    if 'Gemfile' in files and 'rspec' in files.get('Gemfile', ''):
        testing_standards.append("RSpec testing framework")
    
    if testing_standards:
        standards["Testing"] = testing_standards
    
    # Check for documentation standards
    documentation_standards = []
    if 'README.md' in files or 'readme.md' in files:
        documentation_standards.append("README documentation")
    if any('docs/' in path for path in files.keys()):
        documentation_standards.append("Dedicated documentation directory")
    if 'CONTRIBUTING.md' in files:
        documentation_standards.append("Contribution guidelines")
    
    if documentation_standards:
        standards["Documentation"] = documentation_standards
    
    return standards

def detect_frameworks_fallback(files):
    """Detect frameworks used in the project"""
    frameworks = []
    
    # Simple framework detection based on key files
    if 'package.json' in files:
        package_content = files.get('package.json', '')
        if 'react' in package_content.lower():
            frameworks.append('React')
        if 'vue' in package_content.lower():
            frameworks.append('Vue.js')
        if 'angular' in package_content.lower():
            frameworks.append('Angular')
        if 'next' in package_content.lower():
            frameworks.append('Next.js')
        if 'express' in package_content.lower():
            frameworks.append('Express.js')
    
    if 'requirements.txt' in files:
        req_content = files.get('requirements.txt', '')
        if 'django' in req_content.lower():
            frameworks.append('Django')
        if 'flask' in req_content.lower():
            frameworks.append('Flask')
        if 'fastapi' in req_content.lower():
            frameworks.append('FastAPI')
    
    if 'pom.xml' in files:
        frameworks.append('Spring Boot')
    
    if 'Gemfile' in files:
        frameworks.append('Ruby on Rails')
    
    if 'composer.json' in files:
        frameworks.append('Laravel')
    
    return frameworks

def get_common_project_paths():
    """Get common project folder locations"""
    common_paths = []
    
    # System-specific paths
    if os.name == 'nt':  # Windows
        potential_paths = [
            os.path.expanduser("~/Documents/Projects"),
            os.path.expanduser("~/Projects"),
            os.path.expanduser("~/Source"),
            os.path.expanduser("~/Desktop"),
            "C:\\Projects",
            "C:\\Dev"
        ]
    else:  # Unix-like (Linux, macOS)
        potential_paths = [
            os.path.expanduser("~/Projects"),
            os.path.expanduser("~/Development"),
            os.path.expanduser("~/Code"),
            os.path.expanduser("~/src"),
            os.path.expanduser("~/workspace"),
            os.path.expanduser("~/Desktop")
        ]
    
    for path in potential_paths:
        if Path(path).exists() and Path(path).is_dir():
            try:
                # List subdirectories
                subdirs = [str(p) for p in Path(path).iterdir() if p.is_dir()]
                common_paths.extend(subdirs[:5])  # Limit to 5 per directory
            except PermissionError:
                continue
    
    return common_paths[:15]  # Limit total results

def show_enhanced_folder_selection():
    st.title("📁 Enhanced Folder Selection")
    st.markdown("Select and analyze your project folder using improved selection methods.")
    
    # Check if AI model is connected
    if not st.session_state.model_connected:
        st.warning("⚠️ Please select and connect to an AI model first from the sidebar.")
        return
    
    # Enhanced folder selection interface
    if hasattr(st.session_state.file_service, 'enhanced_folder_selection'):
        selected_folder = st.session_state.file_service.enhanced_folder_selection()
    else:
        # Fallback to enhanced selection implemented here
        selected_folder = show_enhanced_folder_selection_fallback()
    
    # Process folder if selected and different from current
    if selected_folder and selected_folder != st.session_state.current_folder:
        st.session_state.current_folder = selected_folder
        
        # Read files from folder
        with st.spinner("📖 Reading project files..."):
            files_content = st.session_state.file_service.read_files(selected_folder)
            st.session_state.loaded_files = files_content
            
            # Auto-detect coding standards
            if hasattr(st.session_state.file_service, 'detect_coding_standards'):
                detected_standards = st.session_state.file_service.detect_coding_standards(files_content)
            else:
                detected_standards = detect_coding_standards_fallback(files_content)
            
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
            if hasattr(st.session_state.file_service, 'get_enhanced_file_stats'):
                stats = st.session_state.file_service.get_enhanced_file_stats(st.session_state.loaded_files)
            else:
                stats = get_enhanced_file_stats_fallback(st.session_state.loaded_files)
            
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
                        if hasattr(st.session_state.ai_service, 'analyze_codebase_with_standards'):
                            analysis = st.session_state.ai_service.analyze_codebase_with_standards(
                                st.session_state.loaded_files, 
                                st.session_state.coding_standards
                            )
                        else:
                            # Fallback to regular analysis
                            analysis = st.session_state.ai_service.analyze_codebase(st.session_state.loaded_files)
                            analysis["standards_compliance"] = "Enhanced AI service not available. Using basic analysis."
                        
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
                if hasattr(st.session_state.file_service, 'detect_coding_standards'):
                    detected = st.session_state.file_service.detect_coding_standards(st.session_state.loaded_files)
                else:
                    detected = detect_coding_standards_fallback(st.session_state.loaded_files)
                
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