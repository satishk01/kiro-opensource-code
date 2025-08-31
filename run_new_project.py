#!/usr/bin/env python3
"""
Launcher script for the New Project - Enhanced Kiro AI Assistant

This script provides an enhanced version of Kiro with:
- Native folder selection dialogs
- Enhanced ZIP file support
- Coding standards integration
- Improved user experience

Usage:
    python run_new_project.py
    
    or
    
    streamlit run new_project_app.py
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'boto3',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_optional_dependencies():
    """Check optional dependencies and provide installation guidance"""
    optional_packages = {
        'tkinter': 'For native file dialogs (usually included with Python)',
    }
    
    missing_optional = []
    
    for package, description in optional_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_optional.append((package, description))
    
    if missing_optional:
        print("⚠️  Optional packages not found:")
        for package, description in missing_optional:
            print(f"  - {package}: {description}")
        print()

def main():
    """Main launcher function"""
    print("🚀 Starting New Project - Enhanced Kiro AI Assistant")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("new_project_app.py").exists():
        print("❌ Error: new_project_app.py not found in current directory")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    check_optional_dependencies()
    
    print("✅ All required dependencies found")
    print()
    
    # Check for enhanced services
    enhanced_services = [
        "services/enhanced_file_service.py",
        "services/enhanced_ai_service.py"
    ]
    
    missing_services = []
    for service in enhanced_services:
        if not Path(service).exists():
            missing_services.append(service)
    
    if missing_services:
        print("⚠️  Enhanced services not found:")
        for service in missing_services:
            print(f"  - {service}")
        print("The application may fall back to basic functionality")
        print()
    
    # Launch the application
    print("🎯 Launching Enhanced Kiro AI Assistant...")
    print("📱 The application will open in your default web browser")
    print("🔗 Default URL: http://localhost:8501")
    print()
    print("💡 Features available:")
    print("  - Native folder selection dialogs")
    print("  - Enhanced ZIP file support")
    print("  - Coding standards integration")
    print("  - Improved codebase analysis")
    print("  - Standards-aware spec generation")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "new_project_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        print("\nTry running manually with:")
        print("streamlit run new_project_app.py")

if __name__ == "__main__":
    main()