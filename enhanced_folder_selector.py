#!/usr/bin/env python3
"""
Enhanced Folder and File Selector for Streamlit
Combines folder browsing with multiple file selection capabilities
"""

import streamlit as st
import os
from pathlib import Path
import tempfile
import zipfile
from typing import List, Dict, Optional, Union

class EnhancedFolderSelector:
    """Enhanced folder and file selector with multiple selection modes"""
    
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'browse_path' not in st.session_state:
            st.session_state.browse_path = os.path.expanduser("~")
        if 'selected_files' not in st.session_state:
            st.session_state.selected_files = []
        if 'selected_folders' not in st.session_state:
            st.session_state.selected_folders = []
        if 'selection_mode' not in st.session_state:
            st.session_state.selection_mode = "folder"
        if 'recent_selections' not in st.session_state:
            st.session_state.recent_selections = []
    
    def show_selector(self) -> Optional[Union[str, List[str]]]:
        """Main selector interface"""
        st.subheader("📁 Enhanced Folder & File Selector")
        
        # Selection mode tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📁 Select Folder (Direct)", 
            "📁 Browse & Select Folder", 
            "📄 Browse & Select Files", 
            "📤 Upload Multiple Files",
            "📦 Upload ZIP Folder",
            "🔍 Recent Selections"
        ])
        
        with tab1:
            return self.show_direct_folder_selector()
        
        with tab2:
            return self.show_folder_browser()
        
        with tab3:
            return self.show_file_browser()
        
        with tab4:
            return self.show_multiple_file_upload()
        
        with tab5:
            return self.show_zip_upload()
        
        with tab6:
            return self.show_recent_selections()
    
    def show_direct_folder_selector(self) -> Optional[str]:
        """Direct folder selection using file uploader with webkitdirectory"""
        st.markdown("**📁 Direct Folder Selection**")
        st.markdown("💡 **This works like ZIP file selection but for folders!** Click below to open a folder picker.")
        
        # Create a custom CSS to style the folder uploader
        st.markdown("""
        <style>
        .folder-uploader {
            border: 2px dashed #007bff;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #f8f9fa;
            margin: 10px 0;
        }
        .folder-uploader:hover {
            background-color: #e9ecef;
            border-color: #0056b3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Instructions
        st.info("""
        🎯 **How this works:**
        1. Click "Browse files" below
        2. In the file dialog, look for "Select Folder" or "Upload Folder" option
        3. Navigate to your project folder and select it
        4. ALL files in the folder will be automatically selected
        5. Click "Open" or "Select" to confirm
        
        ✨ **This is exactly like selecting a ZIP file, but for folders!**
        """)
        
        # Folder uploader with special attributes
        st.markdown('<div class="folder-uploader">', unsafe_allow_html=True)
        
        folder_files = st.file_uploader(
            "📁 Click here to select a folder (all files will be included)",
            accept_multiple_files=True,
            help="This will open a folder picker dialog - select your entire project folder",
            key="direct_folder_upload",
            type=None  # Accept all file types
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add JavaScript to enable folder selection
        st.markdown("""
        <script>
        // Try to enable folder selection on the file input
        setTimeout(function() {
            const fileInputs = document.querySelectorAll('input[type="file"][data-testid*="stFileUploader"]');
            fileInputs.forEach(input => {
                if (input.getAttribute('multiple') !== null) {
                    input.setAttribute('webkitdirectory', '');
                    input.setAttribute('directory', '');
                    
                    // Update the label to indicate folder selection
                    const label = input.closest('div').querySelector('label');
                    if (label && !label.textContent.includes('📁')) {
                        label.textContent = '📁 ' + label.textContent;
                    }
                }
            });
        }, 500);
        </script>
        """, unsafe_allow_html=True)
        
        # Process selected folder
        if folder_files:
            st.success(f"🎉 **Folder Selected!** Found {len(folder_files)} files")
            
            # Analyze the folder structure
            folder_analysis = self.analyze_folder_structure(folder_files)
            
            # Show folder information
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📄 Total Files", folder_analysis['total_files'])
            
            with col2:
                size_mb = folder_analysis['total_size'] / (1024 * 1024)
                st.metric("💾 Total Size", f"{size_mb:.1f} MB")
            
            with col3:
                st.metric("📁 Subfolders", len(folder_analysis['subfolders']))
            
            # Show folder details
            with st.expander("📊 Folder Details"):
                if folder_analysis['root_folder']:
                    st.write(f"**📁 Root Folder:** {folder_analysis['root_folder']}")
                
                if folder_analysis['file_types']:
                    st.write("**📄 File Types:**")
                    sorted_types = sorted(folder_analysis['file_types'].items(), key=lambda x: x[1], reverse=True)
                    for ext, count in sorted_types[:10]:
                        st.write(f"  • {ext}: {count} files")
                    if len(sorted_types) > 10:
                        st.write(f"  • ... and {len(sorted_types) - 10} more types")
                
                if folder_analysis['subfolders']:
                    st.write("**📁 Folder Structure:**")
                    for folder in sorted(folder_analysis['subfolders'])[:15]:
                        st.write(f"  📁 {folder}")
                    if len(folder_analysis['subfolders']) > 15:
                        st.write(f"  📁 ... and {len(folder_analysis['subfolders']) - 15} more folders")
            
            # Show sample files
            with st.expander("📄 Sample Files"):
                for i, file in enumerate(folder_files[:20]):
                    file_path = file.name
                    file_size = file.size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    
                    st.write(f"{i+1:2d}. 📄 {file_path} ({size_str})")
                
                if len(folder_files) > 20:
                    st.write(f"... and {len(folder_files) - 20} more files")
            
            # Confirm selection
            if st.button("✅ Use This Folder", type="primary", key="confirm_direct_folder"):
                return self.process_uploaded_files(folder_files, "direct_folder")
        
        # Browser compatibility info
        st.markdown("---")
        st.markdown("### 🌐 Browser Compatibility")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **✅ Full Support:**
            - Chrome/Chromium
            - Microsoft Edge
            - Opera
            
            **⚠️ Partial Support:**
            - Firefox (may need manual selection)
            """)
        
        with col2:
            st.markdown("""
            **❌ Limited Support:**
            - Safari (use ZIP upload instead)
            - Internet Explorer (not supported)
            
            **💡 Alternative:**
            If folder selection doesn't work, use the "📦 Upload ZIP Folder" tab
            """)
        
        return None
    
    def analyze_folder_structure(self, uploaded_files) -> dict:
        """Analyze the structure of uploaded folder files"""
        structure = {
            'root_folder': None,
            'subfolders': set(),
            'file_types': {},
            'total_size': 0,
            'total_files': len(uploaded_files)
        }
        
        # Detect root folder name
        if uploaded_files:
            first_file = uploaded_files[0].name
            if '/' in first_file:
                structure['root_folder'] = first_file.split('/')[0]
            elif '\\' in first_file:
                structure['root_folder'] = first_file.split('\\')[0]
            else:
                structure['root_folder'] = "Root"
        
        # Analyze each file
        for file in uploaded_files:
            # Track file size
            structure['total_size'] += file.size
            
            # Track file extension
            file_path = Path(file.name)
            ext = file_path.suffix.lower() if file_path.suffix else 'no extension'
            structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
            
            # Track subfolders
            if '/' in file.name:
                parts = file.name.split('/')[:-1]  # Exclude filename
                for i in range(len(parts)):
                    subfolder = '/'.join(parts[:i+1])
                    structure['subfolders'].add(subfolder)
            elif '\\' in file.name:
                parts = file.name.split('\\')[:-1]  # Exclude filename
                for i in range(len(parts)):
                    subfolder = '\\'.join(parts[:i+1])
                    structure['subfolders'].add(subfolder)
        
        return structure

    def show_folder_browser(self) -> Optional[str]:
        """Folder browsing and selection interface"""
        st.markdown("**Browse and select an entire folder from your computer**")
        
        # Current path display
        st.text(f"📍 Current location: {st.session_state.browse_path}")
        
        # Navigation controls
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("🏠 Home", key="folder_home"):
                st.session_state.browse_path = os.path.expanduser("~")
                st.rerun()
        
        with col2:
            if st.button("⬆️ Up", key="folder_up"):
                parent = str(Path(st.session_state.browse_path).parent)
                if parent != st.session_state.browse_path:
                    st.session_state.browse_path = parent
                    st.rerun()
        
        with col3:
            if st.button("🔄 Refresh", key="folder_refresh"):
                st.rerun()
        
        with col4:
            # Quick navigation
            quick_paths = self.get_quick_paths()
            selected_quick = st.selectbox(
                "Quick navigation:",
                ["Select..."] + [name for name, _ in quick_paths],
                key="folder_quick_nav"
            )
            
            if selected_quick != "Select...":
                for name, path in quick_paths:
                    if name == selected_quick and Path(path).exists():
                        st.session_state.browse_path = path
                        st.rerun()
        
        # Directory listing
        try:
            current_path = Path(st.session_state.browse_path)
            if current_path.exists() and current_path.is_dir():
                directories, files = self.get_directory_contents(current_path)
                
                # Show directories
                if directories:
                    st.markdown("**📁 Folders:**")
                    self.display_directories(directories, "folder_nav")
                
                # Show file count for context
                if files:
                    st.markdown(f"**📄 Files in this folder: {len(files)}**")
                    # Show first few files as preview
                    preview_files = files[:5]
                    for file in preview_files:
                        st.text(f"📄 {file.name}")
                    if len(files) > 5:
                        st.text(f"... and {len(files) - 5} more files")
                
                # Folder selection
                st.markdown("---")
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if st.button("✅ Select This Folder", type="primary", key="select_folder"):
                        if self.validate_folder_selection(current_path):
                            self.add_to_recent_selections("folder", str(current_path))
                            st.success(f"✅ Selected folder: {current_path}")
                            return str(current_path)
                
                with col2:
                    st.info(f"📊 {len(files)} files, {len(directories)} folders")
            
            else:
                st.error(f"❌ Cannot access: {st.session_state.browse_path}")
                st.session_state.browse_path = os.path.expanduser("~")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.session_state.browse_path = os.path.expanduser("~")
            st.rerun()
        
        return None
    
    def show_file_browser(self) -> Optional[List[str]]:
        """File browsing and multiple selection interface"""
        st.markdown("**Browse and select multiple files from your computer**")
        
        # Current path display
        st.text(f"📍 Current location: {st.session_state.browse_path}")
        
        # Navigation controls (reuse from folder browser)
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🏠 Home", key="file_home"):
                st.session_state.browse_path = os.path.expanduser("~")
                st.rerun()
        
        with col2:
            if st.button("⬆️ Up", key="file_up"):
                parent = str(Path(st.session_state.browse_path).parent)
                if parent != st.session_state.browse_path:
                    st.session_state.browse_path = parent
                    st.rerun()
        
        with col3:
            if st.button("🔄 Clear Selection", key="clear_files"):
                st.session_state.selected_files = []
                st.rerun()
        
        # Directory and file listing
        try:
            current_path = Path(st.session_state.browse_path)
            if current_path.exists() and current_path.is_dir():
                directories, files = self.get_directory_contents(current_path)
                
                # Show directories for navigation
                if directories:
                    st.markdown("**📁 Navigate to folder:**")
                    self.display_directories(directories, "file_nav")
                
                # Show files for selection
                if files:
                    st.markdown("**📄 Select files:**")
                    self.display_files_for_selection(files)
                
                # Show selected files
                if st.session_state.selected_files:
                    st.markdown("---")
                    st.markdown(f"**✅ Selected Files ({len(st.session_state.selected_files)}):**")
                    
                    # Show selected files with remove option
                    for i, file_path in enumerate(st.session_state.selected_files):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.text(f"📄 {Path(file_path).name}")
                        with col2:
                            if st.button("❌", key=f"remove_file_{i}"):
                                st.session_state.selected_files.remove(file_path)
                                st.rerun()
                    
                    # Confirm selection
                    if st.button("✅ Confirm File Selection", type="primary", key="confirm_files"):
                        self.add_to_recent_selections("files", st.session_state.selected_files.copy())
                        st.success(f"✅ Selected {len(st.session_state.selected_files)} files")
                        return st.session_state.selected_files.copy()
                
                else:
                    st.info("👆 Click on files above to select them")
            
            else:
                st.error(f"❌ Cannot access: {st.session_state.browse_path}")
                st.session_state.browse_path = os.path.expanduser("~")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.session_state.browse_path = os.path.expanduser("~")
            st.rerun()
        
        return None
    
    def show_multiple_file_upload(self) -> Optional[str]:
        """Multiple file upload interface with folder selection"""
        st.markdown("**Upload files from your computer**")
        
        # Create two columns for different upload methods
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📁 Select Entire Folder")
            st.markdown("💡 Click to open folder picker and select all files in a folder")
            
            # Use HTML5 webkitdirectory attribute for folder selection
            folder_files = st.file_uploader(
                "📁 Choose Folder (All Files)",
                accept_multiple_files=True,
                help="This will select ALL files in the chosen folder",
                key="folder_upload",
                label_visibility="collapsed"
            )
            
            # Add JavaScript to enable folder selection
            st.markdown("""
            <script>
            // Enable folder selection for the file input
            setTimeout(function() {
                const fileInputs = document.querySelectorAll('input[type="file"]');
                fileInputs.forEach(input => {
                    if (input.getAttribute('data-testid') === 'stFileUploader') {
                        input.setAttribute('webkitdirectory', '');
                        input.setAttribute('directory', '');
                        input.setAttribute('multiple', '');
                    }
                });
            }, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            if st.button("📁 Open Folder Picker", key="open_folder_picker", type="primary"):
                st.info("👆 Use the file uploader above - it will open a folder picker!")
                st.markdown("""
                **Instructions:**
                1. Click "Browse files" above
                2. In the dialog, look for "Select Folder" or similar option
                3. Navigate to your project folder
                4. Click "Select Folder" or "Upload"
                5. All files in the folder will be selected automatically
                """)
        
        with col2:
            st.markdown("### 📄 Select Individual Files")
            st.markdown("💡 Select specific files from different locations")
            
            individual_files = st.file_uploader(
                "📄 Choose Individual Files",
                accept_multiple_files=True,
                help="Hold Ctrl/Cmd and select multiple files, or drag and drop",
                key="individual_file_upload"
            )
        
        # Process folder files
        if folder_files:
            st.success(f"✅ Selected folder with {len(folder_files)} files")
            
            # Analyze folder structure
            folder_structure = self.analyze_folder_structure(folder_files)
            
            # Show folder analysis
            with st.expander(f"📁 Folder Analysis ({len(folder_files)} files)"):
                st.write(f"**Root folder detected:** {folder_structure['root_folder']}")
                st.write(f"**Subfolders:** {len(folder_structure['subfolders'])}")
                st.write(f"**File types:** {len(folder_structure['file_types'])}")
                
                # Show file types breakdown
                if folder_structure['file_types']:
                    st.write("**File types breakdown:**")
                    for ext, count in sorted(folder_structure['file_types'].items()):
                        st.write(f"  - {ext}: {count} files")
                
                # Show folder structure
                if folder_structure['subfolders']:
                    st.write("**Folder structure:**")
                    for folder in sorted(folder_structure['subfolders'])[:10]:
                        st.write(f"  📁 {folder}")
                    if len(folder_structure['subfolders']) > 10:
                        st.write(f"  ... and {len(folder_structure['subfolders']) - 10} more folders")
            
            if st.button("🚀 Process Folder Files", type="primary", key="process_folder_files"):
                return self.process_uploaded_files(folder_files, "folder")
        
        # Process individual files
        elif individual_files:
            st.success(f"✅ Selected {len(individual_files)} individual files")
            
            # Show file list
            with st.expander(f"📄 View {len(individual_files)} files"):
                for file in individual_files:
                    st.write(f"📄 {file.name} ({file.size} bytes)")
            
            if st.button("🚀 Process Individual Files", type="primary", key="process_individual_files"):
                return self.process_uploaded_files(individual_files, "individual")
        
        # Instructions
        st.markdown("---")
        st.markdown("### 💡 How to Select Folders:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Method 1: Folder Picker (Recommended)**
            1. Click "📁 Choose Folder" above
            2. In the file dialog, look for "Select Folder" option
            3. Navigate to your project folder
            4. Click "Select Folder" - all files will be included
            
            **Supported Browsers:**
            - ✅ Chrome/Edge: Full folder support
            - ✅ Firefox: Folder support available
            - ⚠️ Safari: Limited support
            """)
        
        with col2:
            st.markdown("""
            **Method 2: Drag & Drop Folder**
            1. Open your file manager/explorer
            2. Navigate to your project folder
            3. Select all files in the folder (Ctrl+A / Cmd+A)
            4. Drag and drop them into the file uploader
            
            **Method 3: Individual Selection**
            1. Use "📄 Choose Individual Files"
            2. Hold Ctrl/Cmd and select multiple files
            3. Click "Open" to upload selected files
            """)
        
        return None
    

    
    def process_uploaded_files(self, uploaded_files, upload_type: str) -> str:
        """Process uploaded files and create project directory"""
        # Create temporary directory
        if upload_type == "folder":
            temp_dir = tempfile.mkdtemp(prefix="kiro_folder_")
        else:
            temp_dir = tempfile.mkdtemp(prefix="kiro_files_")
        
        with st.spinner(f"Processing {len(uploaded_files)} files..."):
            progress_bar = st.progress(0)
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Preserve folder structure
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                # Create subdirectories if needed
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Save file
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            progress_bar.empty()
        
        st.success(f"✅ Files processed and saved to: {temp_dir}")
        self.add_to_recent_selections(upload_type, temp_dir)
        return temp_dir
    
    def show_zip_upload(self) -> Optional[str]:
        """ZIP file upload and extraction interface"""
        st.markdown("**Upload a ZIP file containing your project folder**")
        st.markdown("💡 Upload a ZIP of your entire project folder")
        
        uploaded_zip = st.file_uploader(
            "Select ZIP file",
            type=['zip'],
            help="Select a ZIP file containing your project",
            key="zip_folder_upload"
        )
        
        if uploaded_zip:
            st.success(f"✅ ZIP file selected: {uploaded_zip.name}")
            
            if st.button("📦 Extract ZIP File", type="primary", key="extract_zip"):
                extracted_path = self.extract_zip_file(uploaded_zip)
                if extracted_path:
                    st.success(f"✅ ZIP extracted to: {extracted_path}")
                    self.add_to_recent_selections("zip", extracted_path)
                    return extracted_path
        
        return None
    
    def show_recent_selections(self) -> Optional[Union[str, List[str]]]:
        """Show recent selections for quick access"""
        st.markdown("**Quick access to recent selections**")
        
        if not st.session_state.recent_selections:
            st.info("No recent selections. Make a selection first to see it here.")
            return None
        
        st.markdown("**Recent Selections:**")
        for i, selection in enumerate(reversed(st.session_state.recent_selections[-10:])):
            selection_type = selection['type']
            selection_path = selection['path']
            selection_time = selection['time']
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if selection_type == "folder":
                    st.text(f"📁 {Path(selection_path).name}")
                elif selection_type == "files":
                    st.text(f"📄 {len(selection_path)} files")
                else:
                    st.text(f"📦 {Path(selection_path).name}")
            
            with col2:
                st.text(f"🕒 {selection_time}")
            
            with col3:
                if st.button("🔄", key=f"reuse_{i}"):
                    if selection_type == "folder" and Path(selection_path).exists():
                        st.success(f"✅ Reselected folder: {selection_path}")
                        return selection_path
                    elif selection_type == "files":
                        # Validate files still exist
                        valid_files = [f for f in selection_path if Path(f).exists()]
                        if valid_files:
                            st.success(f"✅ Reselected {len(valid_files)} files")
                            return valid_files
                        else:
                            st.error("❌ Files no longer exist")
                    else:
                        if Path(selection_path).exists():
                            st.success(f"✅ Reselected: {selection_path}")
                            return selection_path
                        else:
                            st.error("❌ Path no longer exists")
        
        return None
    
    def get_quick_paths(self) -> List[tuple]:
        """Get quick navigation paths based on OS"""
        home = os.path.expanduser("~")
        
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            paths = [
                ("📁 Documents", os.path.join(home, "Documents")),
                ("📁 Desktop", os.path.join(home, "Desktop")),
                ("📁 Downloads", os.path.join(home, "Downloads")),
                ("💻 C: Drive", "C:\\"),
                ("📁 Program Files", "C:\\Program Files"),
            ]
        else:
            paths = [
                ("📁 Projects", os.path.expanduser("~/Projects")),
                ("📁 Documents", os.path.expanduser("~/Documents")),
                ("📁 Desktop", os.path.expanduser("~/Desktop")),
                ("📁 Downloads", os.path.expanduser("~/Downloads")),
                ("💻 Root", "/"),
            ]
        
        # Filter to existing paths
        return [(name, path) for name, path in paths if Path(path).exists()]
    
    def get_directory_contents(self, path: Path) -> tuple:
        """Get directories and files in the given path"""
        try:
            items = list(path.iterdir())
            directories = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            directories.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())
            
            return directories, files
        except PermissionError:
            return [], []
    
    def display_directories(self, directories: List[Path], key_prefix: str):
        """Display directories in a grid layout"""
        cols_per_row = 3
        for i in range(0, len(directories), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, directory in enumerate(directories[i:i+cols_per_row]):
                with cols[j]:
                    display_name = directory.name
                    if len(display_name) > 20:
                        display_name = display_name[:17] + "..."
                    
                    if st.button(f"📁 {display_name}", key=f"{key_prefix}_{directory}", help=directory.name):
                        st.session_state.browse_path = str(directory)
                        st.rerun()
    
    def display_files_for_selection(self, files: List[Path]):
        """Display files with selection checkboxes"""
        cols_per_row = 2
        for i in range(0, len(files), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, file in enumerate(files[i:i+cols_per_row]):
                with cols[j]:
                    file_path = str(file)
                    is_selected = file_path in st.session_state.selected_files
                    
                    display_name = file.name
                    if len(display_name) > 25:
                        display_name = display_name[:22] + "..."
                    
                    if st.button(
                        f"{'✅' if is_selected else '📄'} {display_name}", 
                        key=f"file_select_{file}",
                        help=f"{'Remove from' if is_selected else 'Add to'} selection: {file.name}"
                    ):
                        if is_selected:
                            st.session_state.selected_files.remove(file_path)
                        else:
                            st.session_state.selected_files.append(file_path)
                        st.rerun()
    
    def validate_folder_selection(self, path: Path) -> bool:
        """Validate folder selection"""
        try:
            if not path.exists():
                st.error(f"❌ Folder does not exist: {path}")
                return False
            
            if not path.is_dir():
                st.error(f"❌ Path is not a directory: {path}")
                return False
            
            # Check if we can read the directory
            try:
                list(path.iterdir())
            except PermissionError:
                st.error(f"❌ Permission denied: {path}")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error validating folder: {e}")
            return False
    
    def extract_zip_file(self, uploaded_file) -> Optional[str]:
        """Extract ZIP file and return path"""
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"kiro_zip_{uploaded_file.name.replace('.zip', '')}_")
            
            with st.spinner(f"Extracting {uploaded_file.name}..."):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    # Security check
                    for file_path in zip_ref.namelist():
                        if '..' in file_path or file_path.startswith('/'):
                            st.error("❌ Security risk detected in ZIP file")
                            return None
                    
                    zip_ref.extractall(temp_dir)
            
            # If ZIP contains single root directory, use that
            extracted_items = list(Path(temp_dir).iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                return str(extracted_items[0])
            
            return temp_dir
            
        except Exception as e:
            st.error(f"❌ Error extracting ZIP: {e}")
            return None
    
    def add_to_recent_selections(self, selection_type: str, path: Union[str, List[str]]):
        """Add selection to recent selections"""
        import datetime
        
        selection = {
            'type': selection_type,
            'path': path,
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        st.session_state.recent_selections.append(selection)
        # Keep only last 20 selections
        st.session_state.recent_selections = st.session_state.recent_selections[-20:]

# Example usage function
def demo_enhanced_selector():
    """Demo function to show how to use the enhanced selector"""
    st.title("🚀 Enhanced Folder & File Selector Demo")
    
    selector = EnhancedFolderSelector()
    result = selector.show_selector()
    
    if result:
        if isinstance(result, str):
            st.success(f"✅ Selected folder/path: {result}")
        elif isinstance(result, list):
            st.success(f"✅ Selected {len(result)} files:")
            for file_path in result:
                st.write(f"📄 {file_path}")

if __name__ == "__main__":
    demo_enhanced_selector()