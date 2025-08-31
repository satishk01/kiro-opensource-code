# -*- coding: utf-8 -*-
import os
import streamlit as st
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import mimetypes
import logging
import json
import tempfile
import zipfile
import subprocess
import platform

class EnhancedFileService:
    """Enhanced service for handling file and folder operations with native dialogs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb',
            '.html', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml', '.yml',
            '.md', '.txt', '.sql', '.sh', '.bat', '.ps1', '.dockerfile', '.gitignore',
            '.env', '.ini', '.cfg', '.conf', '.toml', '.lock', '.log', '.vue', '.svelte',
            '.kt', '.swift', '.dart', '.r', '.scala', '.clj', '.hs', '.elm', '.ex', '.exs'
        }
        self.max_file_size = 2 * 1024 * 1024  # 2MB limit per file
        self.max_total_files = 2000  # Maximum files to process
        
        # Framework detection patterns
        self.framework_patterns = {
            'React': ['package.json', 'src/App.js', 'src/App.tsx', 'public/index.html'],
            'Vue.js': ['package.json', 'src/App.vue', 'vue.config.js'],
            'Angular': ['package.json', 'angular.json', 'src/app/app.module.ts'],
            'Django': ['manage.py', 'settings.py', 'urls.py', 'requirements.txt'],
            'Flask': ['app.py', 'requirements.txt', 'templates/'],
            'FastAPI': ['main.py', 'requirements.txt', 'app/'],
            'Spring Boot': ['pom.xml', 'src/main/java/', 'application.properties'],
            'Express.js': ['package.json', 'server.js', 'app.js'],
            'Next.js': ['package.json', 'next.config.js', 'pages/'],
            'Nuxt.js': ['package.json', 'nuxt.config.js', 'pages/'],
            'Laravel': ['composer.json', 'artisan', 'app/Http/'],
            'Ruby on Rails': ['Gemfile', 'config/routes.rb', 'app/controllers/'],
            'ASP.NET Core': ['*.csproj', 'Program.cs', 'Startup.cs'],
            'Gatsby': ['package.json', 'gatsby-config.js', 'src/pages/'],
            'Svelte': ['package.json', 'src/App.svelte', 'rollup.config.js']
        }
    
    def enhanced_folder_selection(self) -> Optional[str]:
        """Enhanced folder selection with multiple methods including native dialogs"""
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
                system = platform.system().lower()
                if system == "windows":
                    common_dirs = [
                        ("📁 Documents", os.path.join(os.path.expanduser("~"), "Documents")),
                        ("📁 Desktop", os.path.join(os.path.expanduser("~"), "Desktop")),
                        ("📁 Downloads", os.path.join(os.path.expanduser("~"), "Downloads")),
                        ("📁 Projects", "C:\\Projects"),
                        ("📁 Dev", "C:\\Dev")
                    ]
                else:
                    common_dirs = [
                        ("📁 Projects", os.path.expanduser("~/Projects")),
                        ("📁 Documents", os.path.expanduser("~/Documents")),
                        ("📁 Desktop", os.path.expanduser("~/Desktop")),
                        ("📁 Downloads", os.path.expanduser("~/Downloads"))
                    ]
                
                for name, path in common_dirs:
                    if Path(path).exists() and st.button(name, key=f"quick_{path}"):
                        st.session_state.browse_path = path
                        st.rerun()
            
            # List directories in current path
            try:
                current_path = Path(st.session_state.browse_path)
                if current_path.exists() and current_path.is_dir():
                    directories = []
                    files = []
                    
                    for item in current_path.iterdir():
                        if item.is_dir():
                            directories.append(item)
                        elif item.is_file() and item.suffix.lower() in ['.zip']:
                            files.append(item)
                    
                    # Sort directories and files
                    directories.sort(key=lambda x: x.name.lower())
                    files.sort(key=lambda x: x.name.lower())
                    
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
                            if self.validate_folder_path(st.session_state.browse_path):
                                st.success(f"✅ Selected: {st.session_state.browse_path}")
                                return st.session_state.browse_path
                    
                    with col2:
                        st.info(f"Will select: {st.session_state.browse_path}")
                    
                    # Show ZIP files if any
                    if files:
                        st.markdown("**📦 ZIP Files in this directory:**")
                        for zip_file in files:
                            if st.button(f"📦 Extract {zip_file.name}", key=f"zip_{zip_file}"):
                                # Handle ZIP extraction
                                extracted_path = self._extract_zip_file(zip_file)
                                if extracted_path:
                                    return extracted_path
                
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
                if self.validate_folder_path(folder_path):
                    return folder_path
        
        with tab3:
            st.markdown("**ZIP File Upload**")
            uploaded_file = st.file_uploader(
                "Upload ZIP file", 
                type=['zip'],
                help="Upload your project as a ZIP file for analysis",
                key="zip_upload"
            )
            
            if uploaded_file:
                extracted_path = self.handle_enhanced_zip_upload(uploaded_file)
                if extracted_path:
                    return extracted_path
        
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
                    "☁️ Git Clone from Repository",
                    "🌐 Download from URL"
                ],
                key="transfer_method"
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
                    key="local_zip_upload"
                )
                
                if uploaded_zip:
                    if st.button("🚀 Extract and Use Project", type="primary"):
                        extracted_path = self.handle_enhanced_zip_upload(uploaded_zip)
                        if extracted_path:
                            st.success(f"✅ Project uploaded and extracted!")
                            st.info(f"📁 Project location: {extracted_path}")
                            return extracted_path
            
            elif method == "📁 Upload individual files":
                st.markdown("### 📁 Individual File Upload")
                st.warning("⚠️ This method is suitable for small projects only (< 20 files)")
                
                uploaded_files = st.file_uploader(
                    "Choose files from your laptop",
                    accept_multiple_files=True,
                    help="Select multiple files from your project",
                    key="individual_files_upload"
                )
                
                if uploaded_files:
                    if st.button("📁 Create Project from Files", type="primary"):
                        project_path = self._create_project_from_files(uploaded_files)
                        if project_path:
                            return project_path
            
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
                
                # Quick navigation to uploaded projects
                uploaded_projects_path = os.path.expanduser("~/uploaded-projects")
                if st.button("📁 Go to Uploaded Projects Folder"):
                    if not Path(uploaded_projects_path).exists():
                        Path(uploaded_projects_path).mkdir(parents=True, exist_ok=True)
                    return uploaded_projects_path
            
            elif method == "☁️ Git Clone from Repository":
                st.markdown("### ☁️ Git Clone from Repository")
                st.markdown("Clone your project directly from a Git repository:")
                
                repo_url = st.text_input(
                    "Git Repository URL",
                    placeholder="https://github.com/username/repository.git",
                    help="Enter the URL of your Git repository",
                    key="git_repo_url"
                )
                
                clone_path = st.text_input(
                    "Clone to directory",
                    value=os.path.expanduser("~/git-projects"),
                    help="Directory where the project will be cloned",
                    key="git_clone_path"
                )
                
                if repo_url and st.button("🔄 Clone Repository", type="primary"):
                    cloned_path = self._clone_git_repository(repo_url, clone_path)
                    if cloned_path:
                        return cloned_path
            
            elif method == "🌐 Download from URL":
                st.markdown("### 🌐 Download from URL")
                st.markdown("Download a ZIP file from a URL (e.g., GitHub releases):")
                
                download_url = st.text_input(
                    "Download URL",
                    placeholder="https://github.com/user/repo/archive/main.zip",
                    help="Enter the URL of a ZIP file to download",
                    key="download_url"
                )
                
                if download_url and st.button("⬇️ Download and Extract", type="primary"):
                    downloaded_path = self._download_and_extract(download_url)
                    if downloaded_path:
                        return downloaded_path
        
        with tab5:
            st.markdown("**Recent and Common Locations**")
            
            # Recent projects (stored in session state)
            if 'recent_projects' not in st.session_state:
                st.session_state.recent_projects = []
            
            if st.session_state.recent_projects:
                st.markdown("**Recent Projects:**")
                for recent_path in st.session_state.recent_projects[-5:]:  # Show last 5
                    if st.button(f"📁 {recent_path}", key=f"recent_{recent_path}"):
                        if self.validate_folder_path(recent_path):
                            return recent_path
            
            # Common project locations
            st.markdown("**Common Locations:**")
            common_paths = self.get_enhanced_common_paths()
            
            if common_paths:
                selected_path = st.selectbox(
                    "Select from common project locations:",
                    ["Select a folder..."] + common_paths,
                    key="common_paths"
                )
                
                if selected_path != "Select a folder...":
                    return selected_path
        
        return st.session_state.current_folder
    
    def _extract_zip_file(self, zip_file_path: Path) -> Optional[str]:
        """Extract a ZIP file and return the extracted directory path"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f"kiro_project_{zip_file_path.stem}_")
            
            with st.spinner(f"Extracting {zip_file_path.name}..."):
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    
                    # Security check
                    for file_path in file_list:
                        if '..' in file_path or file_path.startswith('/'):
                            st.error("❌ Security risk detected in ZIP file")
                            return None
                    
                    # Extract files
                    zip_ref.extractall(temp_dir)
            
            st.success(f"✅ Extracted to: {temp_dir}")
            
            # If ZIP contains a single root directory, use that
            extracted_items = list(Path(temp_dir).iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                return str(extracted_items[0])
            
            return temp_dir
            
        except Exception as e:
            st.error(f"❌ Error extracting ZIP: {e}")
            return None

    def _open_native_folder_dialog(self) -> Optional[str]:
        """Open native folder selection dialog based on the operating system"""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                return self._open_windows_folder_dialog()
            elif system == "darwin":  # macOS
                return self._open_macos_folder_dialog()
            elif system == "linux":
                return self._open_linux_folder_dialog()
            else:
                raise Exception(f"Unsupported operating system: {system}")
        except Exception as e:
            self.logger.error(f"Error opening native dialog: {e}")
            return None
    
    def _open_windows_folder_dialog(self) -> Optional[str]:
        """Open Windows folder selection dialog"""
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
            # Fallback to PowerShell dialog
            try:
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
                $folderBrowser.Description = "Select Project Folder"
                $folderBrowser.RootFolder = "MyComputer"
                $result = $folderBrowser.ShowDialog()
                if ($result -eq "OK") {
                    Write-Output $folderBrowser.SelectedPath
                }
                '''
                
                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                
            except Exception as e:
                self.logger.error(f"PowerShell fallback failed: {e}")
            
            return None
    
    def _open_macos_folder_dialog(self) -> Optional[str]:
        """Open macOS folder selection dialog"""
        try:
            # Use AppleScript to open folder dialog
            applescript = '''
            tell application "System Events"
                activate
                set folderPath to choose folder with prompt "Select Project Folder"
                return POSIX path of folderPath
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().rstrip('/')
                
        except Exception as e:
            self.logger.error(f"AppleScript dialog failed: {e}")
        
        return None
    
    def _open_linux_folder_dialog(self) -> Optional[str]:
        """Open Linux folder selection dialog"""
        try:
            # Try different Linux dialog tools in order of preference
            dialog_commands = [
                ["zenity", "--file-selection", "--directory", "--title=Select Project Folder"],
                ["kdialog", "--getexistingdirectory", ".", "--title", "Select Project Folder"],
                ["yad", "--file-selection", "--directory", "--title=Select Project Folder"]
            ]
            
            for cmd in dialog_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                        
                except FileNotFoundError:
                    continue  # Try next dialog tool
                    
        except Exception as e:
            self.logger.error(f"Linux dialog failed: {e}")
        
        # Fallback to tkinter if available
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            folder_path = filedialog.askdirectory(
                title="Select Project Folder",
                initialdir=os.path.expanduser("~")
            )
            
            root.destroy()
            return folder_path if folder_path else None
            
        except ImportError:
            pass
        
        return None
    
    def validate_folder_path(self, folder_path: str) -> bool:
        """Enhanced folder path validation"""
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
            
            # Enhanced security check
            if self.is_safe_path(folder_path):
                st.success(f"✅ Valid folder: {folder_path}")
                
                # Add to recent projects
                if 'recent_projects' not in st.session_state:
                    st.session_state.recent_projects = []
                
                if folder_path not in st.session_state.recent_projects:
                    st.session_state.recent_projects.append(folder_path)
                    # Keep only last 10 recent projects
                    st.session_state.recent_projects = st.session_state.recent_projects[-10:]
                
                return True
            else:
                st.error("❌ Invalid folder path for security reasons")
                return False
                
        except Exception as e:
            st.error(f"❌ Error validating folder: {e}")
            return False
    
    def is_safe_path(self, folder_path: str) -> bool:
        """Enhanced path safety check"""
        try:
            resolved_path = Path(folder_path).resolve()
            path_str = str(resolved_path)
            
            # System-specific allowed paths
            system = platform.system().lower()
            
            if system == "windows":
                # Allow paths under user directories and common development locations
                allowed_patterns = [
                    r"C:\Users",
                    r"C:\Projects",
                    r"C:\Dev",
                    r"C:\Source",
                    r"D:",
                    r"E:",
                    r"F:"
                ]
                return any(path_str.startswith(pattern) for pattern in allowed_patterns)
            
            elif system in ["linux", "darwin"]:
                # Allow paths under home, opt, var, tmp, and common dev directories
                allowed_prefixes = [
                    '/home', '/Users', '/opt', '/var/www', '/tmp', '/app',
                    '/workspace', '/projects', '/dev', '/src'
                ]
                return any(path_str.startswith(prefix) for prefix in allowed_prefixes)
            
            return True  # Default to allowing if we can't determine system
            
        except Exception:
            return False
    
    def get_enhanced_common_paths(self) -> List[str]:
        """Get enhanced list of common project folder locations"""
        common_paths = []
        system = platform.system().lower()
        
        if system == "windows":
            potential_paths = [
                os.path.expanduser("~/Documents/Projects"),
                os.path.expanduser("~/Projects"),
                os.path.expanduser("~/Source"),
                os.path.expanduser("~/Desktop"),
                "C:\\Projects",
                "C:\\Dev",
                "C:\\Source"
            ]
        else:
            potential_paths = [
                os.path.expanduser("~/Projects"),
                os.path.expanduser("~/Development"),
                os.path.expanduser("~/Code"),
                os.path.expanduser("~/src"),
                os.path.expanduser("~/workspace"),
                os.path.expanduser("~/Desktop"),
                '/opt/projects',
                '/var/www',
                '/app',
                '/workspace'
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
    
    def handle_enhanced_zip_upload(self, uploaded_file) -> Optional[str]:
        """Enhanced ZIP file upload and extraction"""
        try:
            # Create temporary directory with better naming
            temp_dir = tempfile.mkdtemp(prefix=f"kiro_project_{uploaded_file.name.replace('.zip', '')}_")
            
            # Show progress for large files
            file_size = len(uploaded_file.getvalue())
            
            with st.spinner(f"Extracting {uploaded_file.name} ({file_size // 1024} KB)..."):
                # Extract ZIP file with progress tracking
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    
                    # Security check: prevent zip bombs and path traversal
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
    
    def read_files(self, folder_path: str) -> Dict[str, str]:
        """Enhanced file reading with better progress tracking and filtering"""
        if not folder_path:
            return {}
        
        files_content = {}
        file_count = 0
        
        try:
            folder = Path(folder_path)
            
            # Enhanced progress tracking
            with st.spinner("Scanning project structure..."):
                all_files = list(folder.rglob('*'))
                text_files = [f for f in all_files if f.is_file() and self.is_enhanced_text_file(f)]
            
            # Filter out unwanted files more aggressively
            text_files = self.filter_unwanted_files(text_files)
            
            if len(text_files) > self.max_total_files:
                st.warning(f"⚠️ Found {len(text_files)} files. Processing first {self.max_total_files} files.")
                text_files = text_files[:self.max_total_files]
            
            total_files = len(text_files)
            
            if total_files == 0:
                st.warning("⚠️ No readable text files found in the selected folder.")
                return {}
            
            # Enhanced progress display
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file_path in enumerate(text_files):
                try:
                    # Update progress with more details
                    progress = (i + 1) / total_files
                    progress_bar.progress(progress)
                    status_text.text(f"Reading {i + 1}/{total_files}: {file_path.name} ({file_path.suffix})")
                    
                    # Enhanced file size check
                    file_size = file_path.stat().st_size
                    if file_size > self.max_file_size:
                        self.logger.warning(f"Skipping large file ({file_size} bytes): {file_path}")
                        continue
                    
                    # Read file content with enhanced encoding detection
                    relative_path = str(file_path.relative_to(folder))
                    content = self.read_file_content_enhanced(file_path)
                    
                    if content is not None:
                        files_content[relative_path] = content
                        file_count += 1
                
                except Exception as e:
                    self.logger.error(f"Error reading file {file_path}: {e}")
                    continue
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ Successfully read {file_count} files from {folder_path}")
            
        except Exception as e:
            st.error(f"❌ Error reading folder: {e}")
            self.logger.error(f"Error reading folder {folder_path}: {e}")
        
        return files_content
    
    def is_enhanced_text_file(self, file_path: Path) -> bool:
        """Enhanced text file detection with better patterns"""
        # Check extension
        if file_path.suffix.lower() in self.text_extensions:
            return True
        
        # Check common files without extensions
        filename = file_path.name.lower()
        no_ext_text_files = {
            'dockerfile', 'makefile', 'rakefile', 'gemfile', 'procfile',
            'readme', 'license', 'changelog', 'authors', 'contributors',
            'copying', 'install', 'news', 'todo', 'version'
        }
        
        if filename in no_ext_text_files:
            return True
        
        # Skip binary and unwanted file patterns
        skip_patterns = [
            '.git/', '__pycache__/', 'node_modules/', '.vscode/', '.idea/',
            'dist/', 'build/', 'target/', '.DS_Store', 'Thumbs.db',
            '.pytest_cache/', '.coverage', '.nyc_output/', 'coverage/',
            '.next/', '.nuxt/', 'vendor/', 'bower_components/'
        ]
        
        file_str = str(file_path)
        if any(pattern in file_str for pattern in skip_patterns):
            return False
        
        return False
    
    def filter_unwanted_files(self, files: List[Path]) -> List[Path]:
        """Filter out unwanted files more aggressively"""
        filtered_files = []
        
        for file_path in files:
            file_str = str(file_path).lower()
            
            # Skip test files if there are too many
            if 'test' in file_str and len(files) > 100:
                continue
            
            # Skip minified files
            if '.min.' in file_str:
                continue
            
            # Skip lock files for large projects
            if file_path.name in ['package-lock.json', 'yarn.lock', 'composer.lock'] and len(files) > 50:
                continue
            
            filtered_files.append(file_path)
        
        return filtered_files
    
    def read_file_content_enhanced(self, file_path: Path) -> Optional[str]:
        """Enhanced file content reading with better encoding detection"""
        encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    
                    # Basic content validation
                    if len(content.strip()) == 0:
                        return None
                    
                    # Skip files that are mostly binary
                    if self.is_likely_binary_content(content):
                        return None
                    
                    return content
                    
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                self.logger.error(f"Error reading file {file_path} with {encoding}: {e}")
                break
        
        return None
    
    def is_likely_binary_content(self, content: str) -> bool:
        """Check if content is likely binary"""
        if len(content) == 0:
            return True
        
        # Check for null bytes
        if '\x00' in content:
            return True
        
        # Check ratio of printable characters
        printable_chars = sum(1 for c in content if c.isprintable() or c.isspace())
        ratio = printable_chars / len(content)
        
        return ratio < 0.7  # If less than 70% printable, consider binary
    
    def get_enhanced_file_stats(self, files: Dict[str, str]) -> Dict:
        """Get enhanced statistics about the loaded files"""
        if not files:
            return {
                "total_files": 0,
                "total_size": 0,
                "total_size_mb": 0,
                "languages": [],
                "language_files": {},
                "frameworks": [],
                "file_types": {},
                "largest_file": None,
                "project_structure": {}
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
                lang = self.extension_to_language(ext)
                if lang:
                    language_files[lang] = language_files.get(lang, 0) + 1
        
        # Detect frameworks
        frameworks = self.detect_frameworks(files)
        
        # Find largest file
        largest_file = max(files.items(), key=lambda x: len(x[1])) if files else None
        
        # Analyze project structure
        project_structure = self.analyze_project_structure(files)
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "languages": list(language_files.keys()),
            "language_files": language_files,
            "frameworks": frameworks,
            "file_types": file_types,
            "largest_file": {
                "path": largest_file[0],
                "size": len(largest_file[1]),
                "size_kb": round(len(largest_file[1]) / 1024, 2)
            } if largest_file else None,
            "project_structure": project_structure
        }
    
    def extension_to_language(self, ext: str) -> Optional[str]:
        """Map file extension to programming language"""
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript',
            '.jsx': 'JavaScript', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift',
            '.kt': 'Kotlin', '.scala': 'Scala', '.clj': 'Clojure', '.hs': 'Haskell',
            '.elm': 'Elm', '.ex': 'Elixir', '.exs': 'Elixir', '.dart': 'Dart',
            '.vue': 'Vue.js', '.svelte': 'Svelte', '.html': 'HTML', '.css': 'CSS',
            '.scss': 'SCSS', '.sass': 'Sass', '.less': 'Less', '.sql': 'SQL',
            '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML', '.xml': 'XML',
            '.md': 'Markdown', '.sh': 'Shell', '.bat': 'Batch', '.ps1': 'PowerShell',
            '.dockerfile': 'Docker', '.tf': 'Terraform', '.r': 'R'
        }
        
        return lang_map.get(ext.lower())
    
    def detect_frameworks(self, files: Dict[str, str]) -> List[str]:
        """Detect frameworks used in the project"""
        detected_frameworks = []
        
        for framework, patterns in self.framework_patterns.items():
            framework_score = 0
            
            for pattern in patterns:
                if pattern.endswith('/'):
                    # Directory pattern
                    if any(file_path.startswith(pattern) for file_path in files.keys()):
                        framework_score += 1
                else:
                    # File pattern
                    if pattern in files or any(pattern in file_path for file_path in files.keys()):
                        framework_score += 1
            
            # If we match at least half the patterns, consider it detected
            if framework_score >= len(patterns) * 0.5:
                detected_frameworks.append(framework)
        
        return detected_frameworks
    
    def analyze_project_structure(self, files: Dict[str, str]) -> Dict:
        """Analyze the project structure"""
        structure = {
            "directories": set(),
            "depth": 0,
            "common_patterns": []
        }
        
        for file_path in files.keys():
            path_parts = Path(file_path).parts
            
            # Track directories
            for i in range(len(path_parts) - 1):
                dir_path = '/'.join(path_parts[:i+1])
                structure["directories"].add(dir_path)
            
            # Track maximum depth
            structure["depth"] = max(structure["depth"], len(path_parts) - 1)
        
        # Convert set to list for JSON serialization
        structure["directories"] = list(structure["directories"])
        
        # Detect common patterns
        if "src/" in structure["directories"]:
            structure["common_patterns"].append("Source directory structure")
        if "test/" in structure["directories"] or "tests/" in structure["directories"]:
            structure["common_patterns"].append("Dedicated test directory")
        if "docs/" in structure["directories"] or "documentation/" in structure["directories"]:
            structure["common_patterns"].append("Documentation directory")
        
        return structure
    
    def detect_coding_standards(self, files: Dict[str, str]) -> Dict[str, List[str]]:
        """Auto-detect coding standards from project files"""
        standards = {}
        
        # Check for linting configurations
        linting_standards = []
        if '.eslintrc.json' in files or '.eslintrc.js' in files:
            linting_standards.append("ESLint configuration detected")
        if '.pylintrc' in files or 'pylint.cfg' in files:
            linting_standards.append("Pylint configuration detected")
        if '.rubocop.yml' in files:
            linting_standards.append("RuboCop configuration detected")
        
        if linting_standards:
            standards["Linting"] = linting_standards
        
        # Check for formatting configurations
        formatting_standards = []
        if '.prettierrc' in files or 'prettier.config.js' in files:
            formatting_standards.append("Prettier code formatting")
        if 'pyproject.toml' in files and 'black' in files.get('pyproject.toml', ''):
            formatting_standards.append("Black Python formatter")
        if '.editorconfig' in files:
            formatting_standards.append("EditorConfig for consistent formatting")
        
        if formatting_standards:
            standards["Code Formatting"] = formatting_standards
        
        # Check for testing frameworks
        testing_standards = []
        if 'jest.config.js' in files or '"jest"' in files.get('package.json', ''):
            testing_standards.append("Jest testing framework")
        if 'pytest.ini' in files or 'pytest' in files.get('requirements.txt', ''):
            testing_standards.append("Pytest testing framework")
        if 'Gemfile' in files and 'rspec' in files.get('Gemfile', ''):
            testing_standards.append("RSpec testing framework")
        
        if testing_standards:
            standards["Testing"] = testing_standards
        
        # Check for documentation standards
        documentation_standards = []
        if 'README.md' in files:
            documentation_standards.append("README documentation")
        if any('docs/' in path for path in files.keys()):
            documentation_standards.append("Dedicated documentation directory")
        if 'CONTRIBUTING.md' in files:
            documentation_standards.append("Contribution guidelines")
        
        if documentation_standards:
            standards["Documentation"] = documentation_standards
        
        return standards
    
    def _create_project_from_files(self, uploaded_files) -> Optional[str]:
        """Create a project directory from uploaded individual files"""
        try:
            # Create project directory
            project_name = f"uploaded_project_{len(uploaded_files)}_files"
            project_path = os.path.join(tempfile.gettempdir(), project_name)
            Path(project_path).mkdir(parents=True, exist_ok=True)
            
            with st.spinner(f"Creating project from {len(uploaded_files)} files..."):
                for uploaded_file in uploaded_files:
                    # Save each file
                    file_path = os.path.join(project_path, uploaded_file.name)
                    
                    # Create subdirectories if needed
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Created project with {len(uploaded_files)} files")
            st.info(f"📁 Project location: {project_path}")
            return project_path
            
        except Exception as e:
            st.error(f"❌ Error creating project from files: {e}")
            return None
    
    def _clone_git_repository(self, repo_url: str, clone_path: str) -> Optional[str]:
        """Clone a Git repository"""
        try:
            import subprocess
            
            # Ensure clone directory exists
            Path(clone_path).mkdir(parents=True, exist_ok=True)
            
            # Extract repository name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            full_clone_path = os.path.join(clone_path, repo_name)
            
            with st.spinner(f"Cloning repository {repo_name}..."):
                # Run git clone command
                result = subprocess.run(
                    ["git", "clone", repo_url, full_clone_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    st.success(f"✅ Successfully cloned repository!")
                    st.info(f"📁 Repository location: {full_clone_path}")
                    return full_clone_path
                else:
                    st.error(f"❌ Git clone failed: {result.stderr}")
                    return None
                    
        except subprocess.TimeoutExpired:
            st.error("❌ Git clone timed out (5 minutes)")
            return None
        except FileNotFoundError:
            st.error("❌ Git is not installed on this system")
            st.info("💡 Use the ZIP upload method instead")
            return None
        except Exception as e:
            st.error(f"❌ Error cloning repository: {e}")
            return None
    
    def _download_and_extract(self, download_url: str) -> Optional[str]:
        """Download and extract a ZIP file from URL"""
        try:
            import urllib.request
            import tempfile
            
            with st.spinner("Downloading file..."):
                # Download the file
                temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
                urllib.request.urlretrieve(download_url, temp_zip.name)
                
                # Extract the ZIP
                extract_dir = tempfile.mkdtemp(prefix="downloaded_project_")
                
                with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Clean up temp ZIP
                os.unlink(temp_zip.name)
                
                st.success("✅ Downloaded and extracted successfully!")
                
                # If there's a single root directory, use that
                extracted_items = list(Path(extract_dir).iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    final_path = str(extracted_items[0])
                else:
                    final_path = extract_dir
                
                st.info(f"📁 Project location: {final_path}")
                return final_path
                
        except Exception as e:
            st.error(f"❌ Error downloading file: {e}")
            return None