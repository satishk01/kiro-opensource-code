# New Project - Enhanced Kiro AI Assistant

An enhanced version of Kiro AI Assistant with improved folder selection capabilities, coding standards integration, and better user experience.

## 🆕 New Features

### Enhanced Folder Selection
- **Native File Dialogs**: Use your operating system's native folder selection dialogs
- **Multiple Selection Methods**: Browse, manual path entry, ZIP upload, or recent projects
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Recent Projects**: Quick access to recently used project folders

### Improved ZIP File Support
- **Enhanced Extraction**: Better handling of ZIP files with progress tracking
- **Security Checks**: Protection against zip bombs and path traversal attacks
- **Smart Directory Detection**: Automatically handles single-root-directory ZIPs
- **Progress Indicators**: Visual feedback during extraction process

### Coding Standards Integration
- **Auto-Detection**: Automatically detect coding standards from your project files
- **Standards-Aware Analysis**: Codebase analysis considers your coding standards
- **Compliance Reporting**: Get reports on how well your code follows standards
- **Spec Generation**: Requirements and design generation aligned with your standards

### Enhanced User Experience
- **Better Progress Tracking**: Detailed progress indicators for all operations
- **Improved File Filtering**: Smarter filtering of relevant files
- **Framework Detection**: Automatic detection of frameworks and technologies
- **Enhanced Statistics**: More detailed project analysis and statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- AWS credentials configured (for AI features)
- Required Python packages (see requirements.txt)

### Installation

1. **Clone or copy the enhanced files**:
   ```bash
   # The new files are:
   # - new_project_app.py
   # - services/enhanced_file_service.py
   # - services/enhanced_ai_service.py
   # - run_new_project.py
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit boto3 pathlib
   ```

3. **Optional dependencies for native dialogs**:
   ```bash
   # For Windows/Linux (usually included with Python)
   pip install tkinter
   
   # For Linux systems, you might need:
   sudo apt-get install python3-tk zenity  # Ubuntu/Debian
   sudo yum install tkinter zenity         # CentOS/RHEL
   ```

### Running the Application

#### Method 1: Using the launcher script
```bash
python run_new_project.py
```

#### Method 2: Direct streamlit command
```bash
streamlit run new_project_app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📁 Enhanced Folder Selection

### Native Folder Browser
Click the "🗂️ Open Folder Browser" button to use your operating system's native folder selection dialog:

- **Windows**: Uses Windows Explorer folder dialog
- **macOS**: Uses Finder folder selection
- **Linux**: Uses zenity, kdialog, or yad (falls back to tkinter)

### Manual Path Entry
Enter the full path to your project folder:
- Windows: `C:\Users\YourName\Projects\MyProject`
- macOS/Linux: `/home/user/projects/myproject`

### ZIP File Upload
Upload your project as a ZIP file:
- Drag and drop or browse for ZIP files
- Automatic extraction with progress tracking
- Security validation to prevent malicious files

### Recent Projects
Quick access to your recently used project folders for faster workflow.

## 🎯 Coding Standards Integration

### Auto-Detection
The system automatically detects coding standards from your project:
- **Linting configurations**: ESLint, Pylint, RuboCop
- **Formatting tools**: Prettier, Black, EditorConfig
- **Testing frameworks**: Jest, Pytest, RSpec
- **Documentation standards**: README, contribution guidelines

### Manual Configuration
Add custom coding standards in the "Coding Standards" section:
1. Select a category (Code Style, Architecture, Testing, etc.)
2. Enter your standard or guideline
3. Standards are automatically applied to spec generation

### Standards-Aware Features
- **Codebase Analysis**: Analysis considers your coding standards
- **Requirements Generation**: Requirements align with your standards
- **Design Documents**: Designs follow your architectural guidelines
- **Compliance Reports**: Get reports on standards compliance

## 🛠️ Technical Improvements

### Enhanced File Service (`services/enhanced_file_service.py`)
- Native dialog integration for all major operating systems
- Better file filtering and processing
- Framework and technology detection
- Enhanced security checks
- Improved progress tracking

### Enhanced AI Service (`services/enhanced_ai_service.py`)
- Coding standards integration in all AI operations
- Enhanced prompts for better results
- Compliance reporting capabilities
- Backward compatibility with original service

### Cross-Platform Compatibility
- Windows: PowerShell and tkinter fallbacks
- macOS: AppleScript integration
- Linux: Multiple dialog tool support (zenity, kdialog, yad)

## 📊 Enhanced Analysis Features

### Project Statistics
- Total files and size analysis
- Programming language detection
- Framework identification
- Project structure analysis
- File type breakdown

### Framework Detection
Automatic detection of popular frameworks:
- **Frontend**: React, Vue.js, Angular, Next.js, Nuxt.js, Gatsby, Svelte
- **Backend**: Django, Flask, FastAPI, Express.js, Spring Boot, Laravel, Rails
- **Mobile**: React Native, Flutter (Dart)
- **And many more...**

### Coding Standards Compliance
- Linting configuration detection
- Testing framework identification
- Documentation standards checking
- Code formatting tool detection

## 🔧 Configuration

### AWS Configuration
Ensure your AWS credentials are configured for AI features:
```bash
# Using AWS CLI
aws configure

# Or using environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Coding Standards Configuration
Standards can be configured in multiple ways:
1. **Auto-detection**: Automatically detected from project files
2. **Manual entry**: Add custom standards through the UI
3. **Import/Export**: Save and load standards configurations

## 🚨 Troubleshooting

### Native Dialog Issues
If native dialogs don't work:
1. **Windows**: Ensure tkinter is installed or use PowerShell fallback
2. **macOS**: Check AppleScript permissions
3. **Linux**: Install dialog tools: `sudo apt-get install zenity`

### File Access Issues
If you can't access certain folders:
1. Check file permissions
2. Ensure the path exists and is readable
3. Try running with appropriate permissions

### AI Service Issues
If AI features don't work:
1. Verify AWS credentials are configured
2. Check AWS Bedrock permissions
3. Ensure the selected model is available in your region

## 📝 Usage Examples

### Analyzing a React Project
1. Use native dialog to select your React project folder
2. The system automatically detects React, ESLint, Prettier configurations
3. Get enhanced analysis with React-specific recommendations
4. Generate specs that follow React best practices

### Working with Python Projects
1. Select your Python project (Django/Flask/FastAPI)
2. Auto-detection finds pytest, black, pylint configurations
3. Analysis includes Python-specific patterns and standards
4. Spec generation follows Python conventions

### Enterprise Projects
1. Configure custom coding standards for your organization
2. Use standards-aware analysis for compliance checking
3. Generate specs that align with enterprise guidelines
4. Export standards configuration for team sharing

## 🔄 Migration from Original Kiro

The enhanced version is designed to be backward compatible:
1. All original features are preserved
2. Enhanced services extend original functionality
3. Original AI service methods are still available
4. Gradual migration path available

## 🤝 Contributing

To contribute to the enhanced version:
1. Follow the detected coding standards
2. Add tests for new features
3. Update documentation
4. Ensure cross-platform compatibility

## 📄 License

Same license as the original Kiro project.

## 🆘 Support

For issues with the enhanced features:
1. Check the troubleshooting section
2. Verify system requirements
3. Test with the original version to isolate issues
4. Report bugs with system information and error logs