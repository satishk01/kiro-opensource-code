#!/usr/bin/env python3
"""
Test script to verify the local folder browsing functionality
"""

import os
from pathlib import Path

def test_folder_browsing():
    """Test the folder browsing logic"""
    print("🧪 Testing Local Folder Browsing Logic")
    print("=" * 50)
    
    # Test 1: Get user home directory
    home_dir = os.path.expanduser("~")
    print(f"✅ Home directory: {home_dir}")
    
    # Test 2: Check if home directory exists and is accessible
    home_path = Path(home_dir)
    if home_path.exists() and home_path.is_dir():
        print(f"✅ Home directory is accessible")
        
        # Test 3: List some directories in home
        try:
            items = list(home_path.iterdir())
            directories = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            print(f"✅ Found {len(directories)} directories and {len(files)} files in home")
            
            # Show first 5 directories
            print("\n📁 First 5 directories:")
            for i, directory in enumerate(directories[:5]):
                print(f"  {i+1}. {directory.name}")
                
        except PermissionError:
            print("❌ Permission denied accessing home directory")
        except Exception as e:
            print(f"❌ Error accessing home directory: {e}")
    else:
        print(f"❌ Home directory not accessible")
    
    # Test 4: Test common Windows directories
    print("\n🪟 Testing Windows common directories:")
    windows_dirs = [
        ("Documents", os.path.join(home_dir, "Documents")),
        ("Desktop", os.path.join(home_dir, "Desktop")),
        ("Downloads", os.path.join(home_dir, "Downloads")),
        ("C: Drive", "C:\\"),
    ]
    
    for name, path in windows_dirs:
        if Path(path).exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (not found)")
    
    # Test 5: Test navigation logic
    print("\n🧭 Testing navigation logic:")
    current_path = home_dir
    print(f"Current: {current_path}")
    
    # Go up one level
    parent_path = str(Path(current_path).parent)
    if parent_path != current_path:
        print(f"✅ Parent: {parent_path}")
    else:
        print(f"⚠️  Already at root level")
    
    print("\n🎉 Folder browsing logic test completed!")

if __name__ == "__main__":
    test_folder_browsing()