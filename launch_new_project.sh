#!/bin/bash
# Shell script to launch New Project - Enhanced Kiro AI Assistant

echo ""
echo "========================================"
echo "  New Project - Enhanced Kiro AI"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.8 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if the main file exists
if [ ! -f "new_project_app.py" ]; then
    echo "Error: new_project_app.py not found"
    echo "Please run this script from the project directory"
    exit 1
fi

echo "Launching Enhanced Kiro AI Assistant..."
echo ""
echo "Features:"
echo "- Native folder selection dialogs"
echo "- Enhanced ZIP file support"
echo "- Coding standards integration"
echo "- Improved codebase analysis"
echo ""
echo "The application will open in your default browser"
echo "Press Ctrl+C to stop the application"
echo ""

# Make the script executable if it isn't already
chmod +x run_new_project.py

# Launch the application
$PYTHON_CMD run_new_project.py