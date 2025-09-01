import os
import streamlit as st
from pathlib import Path
from typing import Dict, List, Tuple
import mimetypes
import logging

class FileService:
    """Service for handling file and folder operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb',
            '.html', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml', '.yml',
            '.md', '.txt', '.sql', '.sh', '.bat', '.ps1', '.dockerfile', '.gitignore',
            '.env', '.ini', '.cfg', '.conf', '.toml', '.lock', '.log'
        }
        self.max_file_size = 1024 * 1024  # 1MB limit per file
        self.max_total_files = 1000  # Maximum files to process
    
    def select_folder(self) -> str:
        """Display folder selection interface"""
        st.subheader("📁 Select Project Folder")
        
        # Method 1: Manual path input
        st.markdown("**Method 1: Enter folder path**")
        folder_path = st.text_input(
            "Folder Path", 
            value=st.session_state.current_folder or "",
            placeholder="/path/to/your/project",
            help="Enter the full path to your project folder"
        )
        
        if folder_path and folder_path != st.session_state.current_folder:
            if self.validate_folder_path(folder_path):
                return folder_path
        
        # Method 2: File uploader for zip files
        st.markdown("**Method 2: Upload project as ZIP file**")
        uploaded_file = st.file_uploader(
            "Upload ZIP file", 
            type=['zip'],
            help="Upload your project as a ZIP file for analysis"
        )
        
        if uploaded_file:
            return self.handle_zip_upload(uploaded_file)
        
        # Method 3: Browse common locations
        st.markdown("**Method 3: Browse common locations**")
        common_paths = self.get_common_project_paths()
        
        if common_paths:
            selected_path = st.selectbox(
                "Select from common project locations:",
                ["Select a folder..."] + common_paths
            )
            
            if selected_path != "Select a folder...":
                return selected_path
        
        return st.session_state.current_folder
    
    def validate_folder_path(self, folder_path: str) -> bool:
        """Validate that the folder path exists and is accessible"""
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
            
            # Security check: prevent path traversal
            if self.is_safe_path(folder_path):
                st.success(f"✅ Valid folder: {folder_path}")
                return True
            else:
                st.error("❌ Invalid folder path for security reasons")
                return False
                
        except Exception as e:
            st.error(f"❌ Error validating folder: {e}")
            return False
    
    def is_safe_path(self, folder_path: str) -> bool:
        """Check if the path is safe (no path traversal attacks)"""
        try:
            # Resolve the path and check if it's within allowed boundaries
            resolved_path = Path(folder_path).resolve()
            
            # For security, we'll allow paths under /home, /opt, /var/www, /tmp
            # Adjust these based on your deployment requirements
            allowed_prefixes = ['/home', '/opt', '/var/www', '/tmp', '/app']
            
            path_str = str(resolved_path)
            return any(path_str.startswith(prefix) for prefix in allowed_prefixes)
            
        except Exception:
            return False
    
    def get_common_project_paths(self) -> List[str]:
        """Get list of common project folder locations"""
        common_paths = []
        
        # Check common development directories
        potential_paths = [
            '/home/ec2-user/projects',
            '/home/ubuntu/projects',
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
                    common_paths.extend(subdirs[:10])  # Limit to 10 per directory
                except PermissionError:
                    continue
        
        return common_paths[:20]  # Limit total results
    
    def handle_zip_upload(self, uploaded_file) -> str:
        """Handle ZIP file upload and extraction"""
        import zipfile
        import tempfile
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="openflux_project_")
            
            # Extract ZIP file
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            st.success(f"✅ Project extracted to: {temp_dir}")
            return temp_dir
            
        except zipfile.BadZipFile:
            st.error("❌ Invalid ZIP file")
            return None
        except Exception as e:
            st.error(f"❌ Error extracting ZIP file: {e}")
            return None
    
    def read_files(self, folder_path: str) -> Dict[str, str]:
        """Read all text files from the folder recursively"""
        if not folder_path:
            return {}
        
        files_content = {}
        file_count = 0
        
        try:
            folder = Path(folder_path)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Get all files first for progress calculation
            all_files = list(folder.rglob('*'))
            text_files = [f for f in all_files if f.is_file() and self.is_text_file(f)]
            
            if len(text_files) > self.max_total_files:
                st.warning(f"⚠️ Found {len(text_files)} files. Processing first {self.max_total_files} files.")
                text_files = text_files[:self.max_total_files]
            
            total_files = len(text_files)
            
            for i, file_path in enumerate(text_files):
                try:
                    # Update progress
                    progress = (i + 1) / total_files
                    progress_bar.progress(progress)
                    status_text.text(f"Reading file {i + 1}/{total_files}: {file_path.name}")
                    
                    # Check file size
                    if file_path.stat().st_size > self.max_file_size:
                        self.logger.warning(f"Skipping large file: {file_path}")
                        continue
                    
                    # Read file content
                    relative_path = str(file_path.relative_to(folder))
                    content = self.read_file_content(file_path)
                    
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
    
    def is_text_file(self, file_path: Path) -> bool:
        """Check if a file is a text file based on extension and content"""
        # Check extension
        if file_path.suffix.lower() in self.text_extensions:
            return True
        
        # Check if it's a text file without extension
        if not file_path.suffix:
            try:
                mime_type, _ = mimetypes.guess_type(str(file_path))
                if mime_type and mime_type.startswith('text/'):
                    return True
            except:
                pass
        
        # Skip common binary file patterns
        binary_patterns = [
            '.git/', '__pycache__/', 'node_modules/', '.vscode/',
            '.idea/', 'dist/', 'build/', 'target/', '.DS_Store'
        ]
        
        file_str = str(file_path)
        if any(pattern in file_str for pattern in binary_patterns):
            return False
        
        return False
    
    def read_file_content(self, file_path: Path) -> str:
        """Read content of a single file with encoding detection"""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading file {file_path} with {encoding}: {e}")
                break
        
        return None
    
    def filter_text_files(self, files: Dict[str, str]) -> Dict[str, str]:
        """Filter dictionary to only include text files"""
        # This method is mainly for additional filtering if needed
        # The main filtering is done in read_files method
        return files
    
    def get_file_stats(self, files: Dict[str, str]) -> Dict:
        """Get statistics about the loaded files"""
        if not files:
            return {
                "total_files": 0,
                "total_size": 0,
                "languages": [],
                "largest_file": None,
                "file_types": {}
            }
        
        total_size = sum(len(content) for content in files.values())
        
        # Analyze file types
        file_types = {}
        for file_path in files.keys():
            if '.' in file_path:
                ext = Path(file_path).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        # Find largest file
        largest_file = max(files.items(), key=lambda x: len(x[1]))
        
        # Detect languages
        languages = self.detect_languages(files)
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "languages": languages,
            "largest_file": {
                "path": largest_file[0],
                "size": len(largest_file[1])
            },
            "file_types": file_types
        }
    
    def detect_languages(self, files: Dict[str, str]) -> List[str]:
        """Detect programming languages from file extensions"""
        extensions = set()
        for file_path in files.keys():
            if '.' in file_path:
                ext = Path(file_path).suffix.lower()
                extensions.add(ext)
        
        # Map extensions to languages
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby',
            '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass',
            '.sql': 'SQL', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
            '.xml': 'XML', '.md': 'Markdown', '.sh': 'Shell', '.bat': 'Batch',
            '.dockerfile': 'Docker', '.tf': 'Terraform'
        }
        
        detected_languages = []
        for ext in extensions:
            if ext in lang_map:
                detected_languages.append(lang_map[ext])
        
        return sorted(detected_languages)