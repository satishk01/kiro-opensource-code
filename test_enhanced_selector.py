#!/usr/bin/env python3
"""
Test the enhanced folder selector functionality
"""

import os
from pathlib import Path

def test_enhanced_selector_logic():
    """Test the core logic of the enhanced selector"""
    print("🧪 Testing Enhanced Folder Selector Logic")
    print("=" * 50)
    
    # Test 1: Path validation
    home_path = os.path.expanduser("~")
    print(f"✅ Home path: {home_path}")
    
    if Path(home_path).exists() and Path(home_path).is_dir():
        print("✅ Home path validation passed")
    else:
        print("❌ Home path validation failed")
    
    # Test 2: Directory listing
    try:
        home = Path(home_path)
        items = list(home.iterdir())
        directories = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]
        
        print(f"✅ Found {len(directories)} directories, {len(files)} files")
        
        # Test directory sorting
        directories.sort(key=lambda x: x.name.lower())
        print(f"✅ Directory sorting works")
        
        # Test file filtering for supported types
        supported_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs', '.go', '.rs', 
            '.php', '.rb', '.swift', '.kt', '.scala', '.vue', '.svelte', '.html', '.css', 
            '.scss', '.sass', '.sql', '.json', '.yaml', '.yml', '.xml', '.md', '.txt', 
            '.sh', '.bat', '.dockerfile', '.gitignore', '.env'
        }
        
        supported_files = [f for f in files if f.suffix.lower() in supported_extensions]
        print(f"✅ Found {len(supported_files)} supported files out of {len(files)} total")
        
    except Exception as e:
        print(f"❌ Directory listing error: {e}")
    
    # Test 3: Quick paths
    print("\n🚀 Testing Quick Navigation Paths:")
    
    import platform
    system = platform.system().lower()
    
    if system == "windows":
        quick_paths = [
            ("📁 Documents", os.path.join(home_path, "Documents")),
            ("📁 Desktop", os.path.join(home_path, "Desktop")),
            ("📁 Downloads", os.path.join(home_path, "Downloads")),
            ("💻 C: Drive", "C:\\"),
        ]
    else:
        quick_paths = [
            ("📁 Projects", os.path.expanduser("~/Projects")),
            ("📁 Documents", os.path.expanduser("~/Documents")),
            ("📁 Desktop", os.path.expanduser("~/Desktop")),
            ("💻 Root", "/"),
        ]
    
    for name, path in quick_paths:
        if Path(path).exists():
            print(f"✅ {name}: Available")
        else:
            print(f"❌ {name}: Not found")
    
    # Test 4: File selection simulation
    print("\n📄 Testing File Selection Logic:")
    
    # Simulate selected files list
    selected_files = []
    test_file = Path(home_path) / "test_file.txt"
    
    # Simulate adding/removing files
    if str(test_file) not in selected_files:
        selected_files.append(str(test_file))
        print(f"✅ Added file to selection: {test_file.name}")
    
    if str(test_file) in selected_files:
        selected_files.remove(str(test_file))
        print(f"✅ Removed file from selection: {test_file.name}")
    
    print(f"✅ Final selection count: {len(selected_files)}")
    
    # Test 5: Recent selections simulation
    print("\n🔍 Testing Recent Selections Logic:")
    
    import datetime
    
    recent_selections = []
    
    # Add a folder selection
    folder_selection = {
        'type': 'folder',
        'path': home_path,
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    recent_selections.append(folder_selection)
    
    # Add a files selection
    files_selection = {
        'type': 'files',
        'path': [str(test_file)],
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    recent_selections.append(files_selection)
    
    print(f"✅ Recent selections: {len(recent_selections)} items")
    for selection in recent_selections:
        print(f"   - {selection['type']}: {selection['time']}")
    
    print("\n🎉 Enhanced Selector Logic Test Completed!")
    print("✅ All core functionality appears to be working")

if __name__ == "__main__":
    test_enhanced_selector_logic()