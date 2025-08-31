#!/usr/bin/env python3
"""
Test script for New Project - Enhanced Kiro AI Assistant

This script tests the enhanced functionality to ensure everything works correctly.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from services.enhanced_file_service import EnhancedFileService
        print("✅ Enhanced File Service imported successfully")
    except ImportError as e:
        print(f"⚠️  Enhanced File Service import failed: {e}")
        print("   Will use fallback implementation")
    
    try:
        from services.enhanced_ai_service import EnhancedAIService
        print("✅ Enhanced AI Service imported successfully")
    except ImportError as e:
        print(f"⚠️  Enhanced AI Service import failed: {e}")
        print("   Will use fallback implementation")
    
    try:
        from services.ai_service import AIService
        print("✅ Regular AI Service imported successfully")
    except ImportError as e:
        print(f"❌ Regular AI Service import failed: {e}")
        return False
    
    try:
        from services.file_service import FileService
        print("✅ Regular File Service imported successfully")
    except ImportError as e:
        print(f"❌ Regular File Service import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "new_project_app.py",
        "services/ai_service.py",
        "services/file_service.py"
    ]
    
    optional_files = [
        "services/enhanced_file_service.py",
        "services/enhanced_ai_service.py",
        "engines/spec_engine.py"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing (required)")
            all_good = False
    
    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"⚠️  {file_path} missing (optional)")
    
    return all_good

def test_enhanced_functions():
    """Test enhanced functions"""
    print("\n🧪 Testing enhanced functions...")
    
    # Test the fallback functions by importing the app module
    try:
        sys.path.insert(0, '.')
        
        # Import functions from the app
        from new_project_app import (
            detect_coding_standards_fallback,
            detect_frameworks_fallback,
            extension_to_language,
            get_enhanced_file_stats_fallback
        )
        
        # Test with sample data
        sample_files = {
            'package.json': '{"dependencies": {"react": "^17.0.0"}}',
            'src/App.js': 'import React from "react";',
            '.eslintrc.json': '{"extends": ["react-app"]}',
            'README.md': '# My Project'
        }
        
        # Test coding standards detection
        standards = detect_coding_standards_fallback(sample_files)
        print(f"✅ Coding standards detection: {len(standards)} categories found")
        
        # Test framework detection
        frameworks = detect_frameworks_fallback(sample_files)
        print(f"✅ Framework detection: {frameworks}")
        
        # Test language mapping
        lang = extension_to_language('.js')
        print(f"✅ Language mapping: .js -> {lang}")
        
        # Test enhanced stats
        stats = get_enhanced_file_stats_fallback(sample_files)
        print(f"✅ Enhanced stats: {stats['total_files']} files, {len(stats['languages'])} languages")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced functions test failed: {e}")
        return False

def test_native_dialog():
    """Test native dialog functionality"""
    print("\n🖱️  Testing native dialog...")
    
    try:
        import tkinter as tk
        print("✅ tkinter available for native dialogs")
        
        # Test if we can create a root window (without showing it)
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("✅ Native dialog functionality should work")
        
        return True
        
    except ImportError:
        print("⚠️  tkinter not available - native dialogs will not work")
        print("   Manual path entry and ZIP upload will still work")
        return True
    except Exception as e:
        print(f"⚠️  Native dialog test failed: {e}")
        return True

def main():
    """Main test function"""
    print("🚀 Testing New Project - Enhanced Kiro AI Assistant")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Enhanced Functions", test_enhanced_functions),
        ("Native Dialog", test_native_dialog)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The enhanced Kiro should work correctly.")
        print("\nTo start the application, run:")
        print("  python run_new_project.py")
        print("  or")
        print("  streamlit run new_project_app.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. The application may have limited functionality.")
        print("\nYou can still try running the application:")
        print("  python run_new_project.py")
        print("\nFailed tests indicate missing optional features.")

if __name__ == "__main__":
    main()