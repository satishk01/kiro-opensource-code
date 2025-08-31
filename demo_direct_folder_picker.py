#!/usr/bin/env python3
"""
Demo of Direct Folder Picker - Just like ZIP file selection but for folders!
"""

import streamlit as st
from enhanced_folder_selector import EnhancedFolderSelector

def main():
    st.set_page_config(
        page_title="Direct Folder Picker Demo",
        page_icon="📁",
        layout="wide"
    )
    
    st.title("📁 Direct Folder Picker Demo")
    st.markdown("""
    ## 🎯 **This is exactly what you requested!**
    
    Just like when you click "Browse files" for a ZIP upload and get a file picker dialog,
    this gives you a **folder picker dialog** where you can select an entire folder
    and automatically get all files in that folder.
    """)
    
    # Highlight the key feature
    st.success("""
    ✨ **Key Feature:** Click "Browse files" → Select entire folder → All files automatically included!
    
    This works exactly like ZIP file selection, but instead of selecting a single ZIP file,
    you select a folder and get all the files inside it.
    """)
    
    # Create the enhanced selector
    selector = EnhancedFolderSelector()
    
    # Show only the direct folder selector tab
    st.subheader("📁 Direct Folder Selection")
    result = selector.show_direct_folder_selector()
    
    # Show result
    if result:
        st.markdown("---")
        st.success(f"🎉 **Success!** Folder processed and saved to: `{result}`")
        
        # Show what happens next
        st.info("""
        **What happens next:**
        1. ✅ All files from your folder are now available for analysis
        2. 📊 Kiro can analyze your entire project structure
        3. 🚀 You can generate specs, documentation, and more
        4. 🔍 The folder is added to your recent selections for quick reuse
        """)
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 Step-by-Step Instructions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🖱️ **How to Use (Simple!)**
        
        1. **Click** the "Browse files" button above
        2. **Look for** "Select Folder" or "Upload Folder" option in the dialog
        3. **Navigate** to your project folder
        4. **Click** "Select Folder" or "Open"
        5. **Done!** All files are automatically selected
        
        💡 **It's that simple!** Just like selecting a ZIP file.
        """)
    
    with col2:
        st.markdown("""
        ### 🌐 **Browser Support**
        
        **✅ Works Great:**
        - Chrome/Edge (recommended)
        - Firefox (may show "Select Files" but works for folders)
        - Opera
        
        **⚠️ Alternative Needed:**
        - Safari: Use ZIP upload instead
        - Older browsers: Use individual file selection
        """)
    
    # Comparison with ZIP method
    st.markdown("---")
    st.subheader("📦 Comparison: Folder Selection vs ZIP Upload")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📁 **Direct Folder Selection** (This Method)
        
        **Steps:**
        1. Click "Browse files"
        2. Select folder in dialog
        3. All files automatically included
        
        **Pros:**
        - ✅ No need to create ZIP file
        - ✅ Preserves folder structure
        - ✅ Real-time file analysis
        - ✅ Faster workflow
        """)
    
    with col2:
        st.markdown("""
        ### 📦 **ZIP Upload Method** (Alternative)
        
        **Steps:**
        1. Create ZIP file of your folder
        2. Upload ZIP file
        3. Extract and analyze
        
        **Pros:**
        - ✅ Works in all browsers
        - ✅ Good for sharing/backup
        - ✅ Smaller file size (compressed)
        """)
    
    # Technical details
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **How it works:**
        - Uses HTML5 `webkitdirectory` attribute
        - Enables native folder selection in modern browsers
        - Preserves complete folder structure and file paths
        - Provides real-time analysis of selected files
        - Integrates seamlessly with Streamlit file uploader
        
        **Security:**
        - Only reads files you explicitly select
        - No access to other parts of your computer
        - Files are processed locally in your browser first
        - Same security model as regular file uploads
        
        **Performance:**
        - Handles large folders efficiently
        - Shows progress during processing
        - Provides immediate feedback on selection
        - Optimized for typical project sizes
        """)

if __name__ == "__main__":
    main()