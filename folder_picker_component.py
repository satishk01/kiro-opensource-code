#!/usr/bin/env python3
"""
Advanced Folder Picker Component for Streamlit
Uses modern web APIs to enable native folder selection
"""

import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
from pathlib import Path
import json

def create_folder_picker():
    """Create an advanced folder picker using HTML5 File API"""
    
    # HTML and JavaScript for folder picker
    folder_picker_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .folder-picker-container {
                padding: 20px;
                border: 2px dashed #ccc;
                border-radius: 10px;
                text-align: center;
                background-color: #f9f9f9;
                margin: 10px 0;
                transition: all 0.3s ease;
            }
            
            .folder-picker-container:hover {
                border-color: #007bff;
                background-color: #f0f8ff;
            }
            
            .folder-picker-container.dragover {
                border-color: #28a745;
                background-color: #f0fff0;
            }
            
            .folder-input {
                display: none;
            }
            
            .folder-button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
                transition: background-color 0.3s;
            }
            
            .folder-button:hover {
                background-color: #0056b3;
            }
            
            .file-list {
                max-height: 300px;
                overflow-y: auto;
                text-align: left;
                margin-top: 20px;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            
            .file-item {
                padding: 5px;
                border-bottom: 1px solid #eee;
                font-family: monospace;
                font-size: 12px;
            }
            
            .folder-stats {
                background-color: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                text-align: left;
            }
            
            .success-message {
                color: #28a745;
                font-weight: bold;
                margin: 10px 0;
            }
            
            .error-message {
                color: #dc3545;
                font-weight: bold;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="folder-picker-container" id="folderContainer">
            <h3>📁 Select Project Folder</h3>
            <p>Choose a folder to automatically select all files within it</p>
            
            <!-- Folder input (hidden) -->
            <input type="file" id="folderInput" class="folder-input" webkitdirectory directory multiple>
            
            <!-- Visible button -->
            <button class="folder-button" onclick="selectFolder()">
                📁 Choose Folder
            </button>
            
            <p><strong>OR</strong></p>
            
            <!-- File input for individual files -->
            <input type="file" id="fileInput" class="folder-input" multiple>
            <button class="folder-button" onclick="selectFiles()">
                📄 Choose Individual Files
            </button>
            
            <p style="color: #666; font-size: 14px;">
                💡 Tip: You can also drag and drop a folder or files here
            </p>
            
            <!-- Results area -->
            <div id="results"></div>
        </div>

        <script>
            let selectedFiles = [];
            
            // Folder selection
            function selectFolder() {
                document.getElementById('folderInput').click();
            }
            
            // Individual file selection
            function selectFiles() {
                document.getElementById('fileInput').click();
            }
            
            // Handle folder selection
            document.getElementById('folderInput').addEventListener('change', function(e) {
                handleFileSelection(e.target.files, 'folder');
            });
            
            // Handle individual file selection
            document.getElementById('fileInput').addEventListener('change', function(e) {
                handleFileSelection(e.target.files, 'files');
            });
            
            // Handle drag and drop
            const container = document.getElementById('folderContainer');
            
            container.addEventListener('dragover', function(e) {
                e.preventDefault();
                container.classList.add('dragover');
            });
            
            container.addEventListener('dragleave', function(e) {
                e.preventDefault();
                container.classList.remove('dragover');
            });
            
            container.addEventListener('drop', function(e) {
                e.preventDefault();
                container.classList.remove('dragover');
                
                const items = e.dataTransfer.items;
                const files = [];
                
                // Check if it's a folder drop
                if (items && items.length > 0) {
                    for (let i = 0; i < items.length; i++) {
                        const item = items[i];
                        if (item.kind === 'file') {
                            const entry = item.webkitGetAsEntry();
                            if (entry && entry.isDirectory) {
                                // It's a folder - read all files
                                readDirectory(entry, files);
                            } else {
                                // It's individual files
                                files.push(item.getAsFile());
                            }
                        }
                    }
                } else {
                    // Fallback to regular files
                    for (let file of e.dataTransfer.files) {
                        files.push(file);
                    }
                }
                
                if (files.length > 0) {
                    handleFileSelection(files, 'drop');
                }
            });
            
            // Read directory recursively
            function readDirectory(dirEntry, fileList) {
                const dirReader = dirEntry.createReader();
                dirReader.readEntries(function(entries) {
                    for (let entry of entries) {
                        if (entry.isFile) {
                            entry.file(function(file) {
                                fileList.push(file);
                                // Update display when we have files
                                if (fileList.length > 0) {
                                    handleFileSelection(fileList, 'folder');
                                }
                            });
                        } else if (entry.isDirectory) {
                            readDirectory(entry, fileList);
                        }
                    }
                });
            }
            
            // Handle file selection
            function handleFileSelection(files, selectionType) {
                selectedFiles = Array.from(files);
                
                if (selectedFiles.length === 0) {
                    document.getElementById('results').innerHTML = 
                        '<div class="error-message">No files selected</div>';
                    return;
                }
                
                // Analyze files
                const analysis = analyzeFiles(selectedFiles);
                
                // Display results
                displayResults(analysis, selectionType);
                
                // Send data to Streamlit (if available)
                if (window.parent && window.parent.postMessage) {
                    const fileData = selectedFiles.map(file => ({
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        lastModified: file.lastModified,
                        webkitRelativePath: file.webkitRelativePath || file.name
                    }));
                    
                    window.parent.postMessage({
                        type: 'folderSelected',
                        files: fileData,
                        selectionType: selectionType,
                        analysis: analysis
                    }, '*');
                }
            }
            
            // Analyze selected files
            function analyzeFiles(files) {
                const analysis = {
                    totalFiles: files.length,
                    totalSize: 0,
                    fileTypes: {},
                    folders: new Set(),
                    rootFolder: null
                };
                
                files.forEach(file => {
                    analysis.totalSize += file.size;
                    
                    // File extension
                    const ext = file.name.split('.').pop().toLowerCase();
                    analysis.fileTypes[ext] = (analysis.fileTypes[ext] || 0) + 1;
                    
                    // Folder structure
                    const path = file.webkitRelativePath || file.name;
                    if (path.includes('/')) {
                        const parts = path.split('/');
                        if (!analysis.rootFolder) {
                            analysis.rootFolder = parts[0];
                        }
                        for (let i = 0; i < parts.length - 1; i++) {
                            analysis.folders.add(parts.slice(0, i + 1).join('/'));
                        }
                    }
                });
                
                analysis.folders = Array.from(analysis.folders);
                return analysis;
            }
            
            // Display results
            function displayResults(analysis, selectionType) {
                const resultsDiv = document.getElementById('results');
                
                let html = `
                    <div class="success-message">
                        ✅ Selected ${analysis.totalFiles} files 
                        (${(analysis.totalSize / 1024 / 1024).toFixed(2)} MB)
                    </div>
                    
                    <div class="folder-stats">
                        <strong>Selection Type:</strong> ${selectionType}<br>
                        ${analysis.rootFolder ? `<strong>Root Folder:</strong> ${analysis.rootFolder}<br>` : ''}
                        <strong>Folders:</strong> ${analysis.folders.length}<br>
                        <strong>File Types:</strong> ${Object.keys(analysis.fileTypes).length}
                    </div>
                `;
                
                // File types breakdown
                if (Object.keys(analysis.fileTypes).length > 0) {
                    html += '<div class="folder-stats"><strong>File Types:</strong><br>';
                    Object.entries(analysis.fileTypes)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 10)
                        .forEach(([ext, count]) => {
                            html += `${ext}: ${count} files<br>`;
                        });
                    html += '</div>';
                }
                
                // File list (first 20 files)
                html += '<div class="file-list">';
                html += '<strong>Files (showing first 20):</strong><br>';
                selectedFiles.slice(0, 20).forEach(file => {
                    const path = file.webkitRelativePath || file.name;
                    html += `<div class="file-item">📄 ${path}</div>`;
                });
                if (selectedFiles.length > 20) {
                    html += `<div class="file-item">... and ${selectedFiles.length - 20} more files</div>`;
                }
                html += '</div>';
                
                resultsDiv.innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    
    return folder_picker_html

def show_advanced_folder_picker():
    """Show the advanced folder picker component"""
    st.markdown("### 🚀 Advanced Folder Picker")
    st.markdown("This uses modern web APIs to provide native folder selection capabilities.")
    
    # Create the folder picker component
    folder_picker_html = create_folder_picker()
    
    # Display the component
    result = components.html(folder_picker_html, height=600, scrolling=True)
    
    # Handle the result (this would need additional integration)
    if result:
        st.write("Folder picker result:", result)
    
    return result

def demo_folder_picker():
    """Demo the advanced folder picker"""
    st.title("📁 Advanced Folder Picker Demo")
    
    st.markdown("""
    This demonstrates an advanced folder picker that provides:
    - **Native folder selection** using HTML5 File API
    - **Drag and drop support** for folders and files
    - **Real-time analysis** of selected files
    - **Visual feedback** during selection
    """)
    
    # Show the folder picker
    result = show_advanced_folder_picker()
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Folder Selection:**
        1. Click "📁 Choose Folder"
        2. In the dialog, select a folder
        3. All files in the folder will be selected automatically
        4. See real-time analysis of selected files
        """)
    
    with col2:
        st.markdown("""
        **Drag & Drop:**
        1. Open your file manager
        2. Drag a folder into the picker area
        3. Files will be analyzed automatically
        4. Works with both folders and individual files
        """)

if __name__ == "__main__":
    demo_folder_picker()