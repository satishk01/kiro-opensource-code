#!/usr/bin/env python3
"""
Demo of the Enhanced Folder Selector
Shows all the new capabilities for folder and file selection
"""

import streamlit as st
from enhanced_folder_selector import EnhancedFolderSelector

def main():
    st.set_page_config(
        page_title="Enhanced Folder Selector Demo",
        page_icon="📁",
        layout="wide"
    )
    
    st.title("📁 Enhanced Folder & File Selector Demo")
    st.markdown("""
    This demo shows the enhanced folder and file selection capabilities that combine:
    - **Folder Selection**: Browse and select entire folders
    - **Multiple File Selection**: Select individual files from different locations
    - **Upload Methods**: Direct file upload and ZIP extraction
    - **Recent Selections**: Quick access to previous selections
    """)
    
    # Create the enhanced selector
    selector = EnhancedFolderSelector()
    
    # Show the selector interface
    result = selector.show_selector()
    
    # Display results
    if result:
        st.markdown("---")
        st.subheader("🎉 Selection Result")
        
        if isinstance(result, str):
            # Single folder or path
            st.success(f"✅ **Selected Folder/Path:** `{result}`")
            
            # Try to show some info about the selection
            from pathlib import Path
            path = Path(result)
            
            if path.exists():
                if path.is_dir():
                    try:
                        items = list(path.iterdir())
                        files = [item for item in items if item.is_file()]
                        dirs = [item for item in items if item.is_dir()]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📄 Files", len(files))
                        with col2:
                            st.metric("📁 Folders", len(dirs))
                        with col3:
                            st.metric("📊 Total Items", len(items))
                        
                        # Show some example files
                        if files:
                            st.markdown("**Sample Files:**")
                            for file in files[:5]:
                                st.text(f"📄 {file.name}")
                            if len(files) > 5:
                                st.text(f"... and {len(files) - 5} more files")
                                
                    except Exception as e:
                        st.warning(f"Could not analyze folder: {e}")
                else:
                    st.info("Selected path is a file")
            else:
                st.warning("Selected path no longer exists")
        
        elif isinstance(result, list):
            # Multiple files
            st.success(f"✅ **Selected {len(result)} Files:**")
            
            # Show file list
            for i, file_path in enumerate(result, 1):
                from pathlib import Path
                file_name = Path(file_path).name
                st.text(f"{i:2d}. 📄 {file_name}")
                
                # Show file size if accessible
                try:
                    file_size = Path(file_path).stat().st_size
                    if file_size < 1024:
                        size_str = f"{file_size} bytes"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    st.text(f"     Size: {size_str}")
                except:
                    pass
    
    # Show instructions
    st.markdown("---")
    st.subheader("📖 How to Use")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📁 Folder Selection:**
        1. Click "Browse & Select Folder" tab
        2. Navigate using folder buttons
        3. Use Home/Up/Refresh for navigation
        4. Click "Select This Folder" when ready
        
        **📄 File Selection:**
        1. Click "Browse & Select Files" tab
        2. Navigate to desired folder
        3. Click on files to select/deselect them
        4. Click "Confirm File Selection" when done
        """)
    
    with col2:
        st.markdown("""
        **📤 Upload Methods:**
        1. "Upload Multiple Files" - Direct file upload
        2. "Upload ZIP Folder" - Extract ZIP files
        
        **🔍 Recent Selections:**
        - Quick access to previous selections
        - Reuse folders and file sets
        - Automatic history tracking
        """)
    
    # Show technical details
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **Key Features:**
        - **Cross-platform**: Works on Windows, Mac, and Linux
        - **Security**: ZIP extraction with path traversal protection
        - **Performance**: Handles large directories efficiently
        - **Memory**: Smart file size limits to prevent memory issues
        - **Persistence**: Session state maintains selections across interactions
        
        **Supported File Types:**
        - Programming: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, etc.
        - Web: `.html`, `.css`, `.scss`, `.vue`, `.svelte`
        - Data: `.json`, `.yaml`, `.xml`, `.csv`
        - Documentation: `.md`, `.txt`, `.rst`
        - Configuration: `.env`, `.dockerfile`, `.gitignore`
        """)

if __name__ == "__main__":
    main()