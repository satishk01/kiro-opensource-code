#!/usr/bin/env python3
"""
Test ZIP extraction functionality
"""

import zipfile
import tempfile
import os
from pathlib import Path

def create_test_zip():
    """Create a test ZIP file for testing"""
    # Create a temporary directory with some test files
    test_dir = tempfile.mkdtemp(prefix="test_project_")
    
    # Create some test files
    test_files = {
        "README.md": "# Test Project\nThis is a test project for ZIP extraction.",
        "main.py": "#!/usr/bin/env python3\nprint('Hello, World!')",
        "config.json": '{"name": "test", "version": "1.0"}',
        "src/app.py": "# Main application file\nclass App:\n    pass",
        "src/utils.py": "# Utility functions\ndef helper():\n    return True",
        "tests/test_main.py": "# Test file\nimport unittest\nclass TestMain(unittest.TestCase):\n    pass"
    }
    
    # Create files and directories
    for file_path, content in test_files.items():
        full_path = Path(test_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    # Create ZIP file
    zip_path = tempfile.mktemp(suffix='.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for file_path, content in test_files.items():
            full_path = Path(test_dir) / file_path
            # Add file to ZIP with relative path
            zip_ref.write(full_path, file_path)
    
    print(f"✅ Created test ZIP: {zip_path}")
    print(f"📁 Test directory: {test_dir}")
    
    return zip_path, test_dir

def test_zip_extraction():
    """Test the ZIP extraction logic"""
    print("🧪 Testing ZIP Extraction Logic")
    print("=" * 50)
    
    # Create test ZIP
    zip_path, original_dir = create_test_zip()
    
    try:
        # Test 1: Validate ZIP file
        print("\n📦 Test 1: ZIP File Validation")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"✅ ZIP contains {len(file_list)} files")
            
            # Show contents
            for filename in file_list:
                print(f"  📄 {filename}")
            
            # Test integrity
            bad_files = zip_ref.testzip()
            if bad_files:
                print(f"❌ Corrupted files: {bad_files}")
            else:
                print("✅ ZIP integrity check passed")
        
        # Test 2: Extract ZIP
        print("\n📂 Test 2: ZIP Extraction")
        
        extract_dir = tempfile.mkdtemp(prefix="extracted_")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"✅ Extracted to: {extract_dir}")
        
        # Verify extraction
        extracted_items = list(Path(extract_dir).iterdir())
        print(f"✅ Found {len(extracted_items)} top-level items")
        
        # Count all files
        all_files = list(Path(extract_dir).rglob('*'))
        files = [f for f in all_files if f.is_file()]
        dirs = [f for f in all_files if f.is_dir()]
        
        print(f"✅ Total files: {len(files)}")
        print(f"✅ Total directories: {len(dirs)}")
        
        # Test 3: Verify file contents
        print("\n📄 Test 3: File Content Verification")
        
        readme_path = Path(extract_dir) / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
                if "Test Project" in content:
                    print("✅ README.md content verified")
                else:
                    print("❌ README.md content mismatch")
        else:
            print("❌ README.md not found")
        
        # Test 4: Directory structure
        print("\n📁 Test 4: Directory Structure")
        
        src_dir = Path(extract_dir) / "src"
        tests_dir = Path(extract_dir) / "tests"
        
        if src_dir.exists() and src_dir.is_dir():
            print("✅ src/ directory found")
        else:
            print("❌ src/ directory missing")
        
        if tests_dir.exists() and tests_dir.is_dir():
            print("✅ tests/ directory found")
        else:
            print("❌ tests/ directory missing")
        
        print("\n🎉 ZIP Extraction Test Completed!")
        
        # Cleanup
        import shutil
        shutil.rmtree(original_dir, ignore_errors=True)
        shutil.rmtree(extract_dir, ignore_errors=True)
        os.unlink(zip_path)
        
        print("🧹 Cleanup completed")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"Debug info: {traceback.format_exc()}")

if __name__ == "__main__":
    test_zip_extraction()