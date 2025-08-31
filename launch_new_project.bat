@echo off
REM Windows batch script to launch New Project - Enhanced Kiro AI Assistant

echo.
echo ========================================
echo  New Project - Enhanced Kiro AI
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if the main file exists
if not exist "new_project_app.py" (
    echo Error: new_project_app.py not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Launching Enhanced Kiro AI Assistant...
echo.
echo Features:
echo - Native folder selection dialogs
echo - Enhanced ZIP file support  
echo - Coding standards integration
echo - Improved codebase analysis
echo.
echo The application will open in your default browser
echo Press Ctrl+C to stop the application
echo.

REM Launch the application
python run_new_project.py

pause