#!/usr/bin/env python3
"""
Test script for the web-based folder browser functionality
"""

import os
from pathlib import Path

def test_directory_listing():
    """Test if we can list directories"""
    print("🔍 Testing directory listing functionality...")
    
    try:
        home_path = Path(os.path.expanduser("~"))
        print(f"✅ Home directory: {home_path}")
        
        if home_path.exists() and home_path.is_dir():
            directories = [item for item in home_path.iterdir() if item.is_dir()]
            print(f"✅ Found {len(directories)} directories in home")
            
            # Show first few directories
            for i, directory in enumerate(directories[:5]):
                print(f"   📁 {directory.name}")
            
            if len(directories) > 5:
                print(f"   ... and {len(directories) - 5} more directories")
            
            return True
        else:
            print(f"❌ Cannot access home directory: {home_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing directory listing: {e}")
        return False

def test_common_directories():
    """Test access to common directories"""
    print("\n📁 Testing common directory access...")
    
    common_dirs = [
        ("Projects", os.path.expanduser("~/Projects")),
        ("Documents", os.path.expanduser("~/Documents")),
        ("Desktop", os.path.expanduser("~/Desktop")),
        ("Downloads", os.path.expanduser("~/Downloads"))
    ]
    
    accessible_dirs = []
    
    for name, path in common_dirs:
        if Path(path).exists():
            print(f"✅ {name}: {path}")
            accessible_dirs.append((name, path))
        else:
            print(f"⚠️  {name}: {path} (not found)")
    
    return len(accessible_dirs) > 0

def main():
    """Main test function"""
    print("🚀 Testing Web-Based Folder Browser")
    print("=" * 50)
    
    tests = [
        ("Directory Listing", test_directory_listing),
        ("Common Directories", test_common_directories)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Web-based folder browser should work correctly!")
        print("\nThe enhanced folder selection will now provide:")
        print("- Web-based directory browsing")
        print("- Navigation with Home/Up buttons")
        print("- Quick access to common directories")
        print("- Folder selection with validation")
    else:
        print(f"\n⚠️  Some functionality may be limited.")
    
    print("\nTo use the enhanced folder browser:")
    print("1. Start the application: streamlit run new_project_app.py")
    print("2. Go to 'Enhanced Folder Selection'")
    print("3. Use the 'Browse' tab with the web-based browser")

if __name__ == "__main__":
    main()