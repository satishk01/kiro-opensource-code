#!/usr/bin/env python3
"""
Demo of the enhanced local folder browsing functionality
This simulates what you'll see in the Streamlit app
"""

import os
from pathlib import Path

class LocalFolderBrowser:
    def __init__(self):
        self.current_path = os.path.expanduser("~")
        
    def navigate_to(self, path):
        """Navigate to a specific path"""
        if Path(path).exists() and Path(path).is_dir():
            self.current_path = path
            return True
        return False
    
    def go_up(self):
        """Go up one directory level"""
        parent = str(Path(self.current_path).parent)
        if parent != self.current_path:  # Not at root
            self.current_path = parent
            return True
        return False
    
    def go_home(self):
        """Go to home directory"""
        self.current_path = os.path.expanduser("~")
    
    def list_contents(self):
        """List directories and files in current path"""
        try:
            current_path = Path(self.current_path)
            items = list(current_path.iterdir())
            
            directories = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            directories.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())
            
            return directories, files
        except (PermissionError, OSError):
            return [], []
    
    def get_quick_nav_options(self):
        """Get quick navigation options for Windows"""
        home = os.path.expanduser("~")
        options = [
            ("📁 Documents", os.path.join(home, "Documents")),
            ("📁 Desktop", os.path.join(home, "Desktop")),
            ("📁 Downloads", os.path.join(home, "Downloads")),
            ("💻 C: Drive", "C:\\"),
        ]
        
        # Filter to only existing paths
        return [(name, path) for name, path in options if Path(path).exists()]

def demo_browser():
    """Demo the browser functionality"""
    browser = LocalFolderBrowser()
    
    print("🚀 Enhanced Local Folder Browser Demo")
    print("=" * 50)
    
    while True:
        print(f"\n📍 Current location: {browser.current_path}")
        
        # List contents
        directories, files = browser.list_contents()
        
        if directories:
            print(f"\n📁 Folders ({len(directories)}):")
            for i, directory in enumerate(directories[:10]):  # Show first 10
                print(f"  {i+1:2d}. 📁 {directory.name}")
            if len(directories) > 10:
                print(f"      ... and {len(directories) - 10} more folders")
        
        if files:
            print(f"\n📄 Files ({len(files)}):")
            for i, file in enumerate(files[:5]):  # Show first 5
                print(f"      📄 {file.name}")
            if len(files) > 5:
                print(f"      ... and {len(files) - 5} more files")
        
        # Show options
        print(f"\n🎛️  Navigation Options:")
        print("  h) 🏠 Home")
        print("  u) ⬆️  Up")
        print("  s) ✅ Select this folder")
        print("  q) ❌ Quit")
        
        # Show quick navigation
        quick_options = browser.get_quick_nav_options()
        if quick_options:
            print("\n⚡ Quick Navigation:")
            for i, (name, path) in enumerate(quick_options):
                print(f"  {i+1}) {name}")
        
        # Show numbered directories for navigation
        if directories:
            print(f"\n🔢 Enter folder number (1-{min(len(directories), 10)}) to navigate")
        
        # Get user input
        choice = input("\n👉 Your choice: ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice == 'h':
            browser.go_home()
            print("🏠 Navigated to home")
        elif choice == 'u':
            if browser.go_up():
                print("⬆️  Navigated up")
            else:
                print("⚠️  Already at root level")
        elif choice == 's':
            print(f"✅ Selected folder: {browser.current_path}")
            print(f"📊 Contains: {len(files)} files, {len(directories)} folders")
            break
        elif choice.isdigit():
            folder_num = int(choice)
            if 1 <= folder_num <= min(len(directories), 10):
                target_dir = directories[folder_num - 1]
                if browser.navigate_to(str(target_dir)):
                    print(f"📁 Navigated to: {target_dir.name}")
                else:
                    print("❌ Cannot access that folder")
            else:
                print("❌ Invalid folder number")
        elif choice.isdigit() and quick_options:
            quick_num = int(choice)
            if 1 <= quick_num <= len(quick_options):
                name, path = quick_options[quick_num - 1]
                if browser.navigate_to(path):
                    print(f"⚡ Quick navigated to: {name}")
                else:
                    print("❌ Cannot access that location")
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    demo_browser()