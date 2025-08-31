# 💻 Local to EC2 Project Transfer Guide

This guide shows you how to get your local laptop project onto the EC2 instance for analysis with Kiro.

## 🚀 Quick Start Options

### Option 1: ZIP Upload (Recommended) ⭐
**Best for:** Most projects, easy and secure

1. **On your laptop:**
   - Right-click your project folder
   - Select "Send to" > "Compressed folder" (Windows)
   - Or use command: `zip -r myproject.zip /path/to/project` (Linux/Mac)

2. **In Kiro:**
   - Go to "Enhanced Folder Selection"
   - Click "Local to EC2" tab
   - Select "📦 Upload ZIP file"
   - Upload your ZIP file
   - Click "Extract and Use Project"

### Option 2: Git Clone ⭐
**Best for:** Projects already in Git repositories

1. **In Kiro:**
   - Go to "Enhanced Folder Selection"
   - Click "Local to EC2" tab
   - Select "☁️ Git Clone from Repository"
   - Enter your repository URL (e.g., `https://github.com/username/repo.git`)
   - Click "Clone Repository"

### Option 3: Individual Files
**Best for:** Small projects (< 20 files)

1. **In Kiro:**
   - Go to "Enhanced Folder Selection"
   - Click "Local to EC2" tab
   - Select "📁 Upload individual files"
   - Select multiple files from your project
   - Click "Create Project from Files"

### Option 4: SSH/SCP Transfer
**Best for:** Advanced users with SSH access

1. **On your laptop terminal:**
   ```bash
   # Replace with your actual paths and EC2 details
   scp -r /path/to/your/project ec2-user@your-ec2-instance:~/uploaded-projects/
   ```

2. **In Kiro:**
   - Use "Browse EC2" tab
   - Navigate to `~/uploaded-projects/`
   - Select your uploaded project

## 📋 Detailed Instructions

### ZIP Upload Method

#### Step 1: Create ZIP on Your Laptop

**Windows:**
1. Navigate to your project folder in File Explorer
2. Right-click on the project folder
3. Select "Send to" > "Compressed (zipped) folder"
4. Wait for ZIP creation to complete

**macOS:**
1. Right-click your project folder in Finder
2. Select "Compress [folder name]"
3. A ZIP file will be created

**Linux:**
```bash
cd /path/to/parent/directory
zip -r myproject.zip myproject/
```

#### Step 2: Upload in Kiro
1. Open Kiro in your browser
2. Go to "Enhanced Folder Selection" page
3. Click the "💻 Local to EC2" tab
4. Select "📦 Upload ZIP file (Recommended)"
5. Click "Choose ZIP file from your laptop"
6. Select your ZIP file
7. Click "🚀 Extract and Use Project"

### Git Clone Method

#### Prerequisites
- Your project must be in a Git repository (GitHub, GitLab, etc.)
- Repository must be publicly accessible or you have access

#### Steps
1. Get your repository URL:
   - GitHub: Click "Code" button, copy HTTPS URL
   - GitLab: Click "Clone" button, copy HTTPS URL

2. In Kiro:
   - Go to "Enhanced Folder Selection"
   - Click "💻 Local to EC2" tab
   - Select "☁️ Git Clone from Repository"
   - Paste your repository URL
   - Optionally change the clone directory
   - Click "🔄 Clone Repository"

### SSH/SCP Transfer Method

#### Prerequisites
- SSH access to the EC2 instance
- SSH key or password authentication set up

#### Commands

**Using SCP (Secure Copy):**
```bash
# Copy entire project folder
scp -r /local/path/to/project ec2-user@your-ec2-host:~/uploaded-projects/

# Copy with specific SSH key
scp -i ~/.ssh/your-key.pem -r /local/path/to/project ec2-user@your-ec2-host:~/uploaded-projects/
```

**Using rsync (if available):**
```bash
# Sync project folder (more efficient for updates)
rsync -avz /local/path/to/project/ ec2-user@your-ec2-host:~/uploaded-projects/myproject/

# With SSH key
rsync -avz -e "ssh -i ~/.ssh/your-key.pem" /local/path/to/project/ ec2-user@your-ec2-host:~/uploaded-projects/myproject/
```

## 🔍 After Transfer: Finding Your Project

Once you've transferred your project using any method:

1. **Go to "Enhanced Folder Selection"**
2. **Click "🖱️ Browse EC2" tab**
3. **Navigate to the project location:**
   - ZIP uploads: Usually in `/tmp/kiro_project_*`
   - Git clones: In `~/git-projects/` by default
   - SCP uploads: In `~/uploaded-projects/`
   - Individual files: In `/tmp/uploaded_project_*`

4. **Click "✅ Select This Folder"** when you find your project

## 💡 Tips and Best Practices

### For ZIP Uploads
- ✅ **Do:** Keep ZIP files under 100MB for faster upload
- ✅ **Do:** Exclude unnecessary files (node_modules, .git, build folders)
- ❌ **Don't:** Include sensitive files (passwords, API keys)

### For Git Repositories
- ✅ **Do:** Use HTTPS URLs for public repositories
- ✅ **Do:** Ensure repository is accessible without authentication
- ❌ **Don't:** Use SSH URLs unless SSH keys are configured

### For Large Projects
- 🔄 **Use:** Git clone for projects > 100MB
- 🔄 **Use:** SCP/rsync for very large projects
- 🔄 **Consider:** Excluding large binary files

### Security Considerations
- 🔒 **Remove:** API keys, passwords, secrets before upload
- 🔒 **Use:** `.gitignore` or exclude sensitive files from ZIP
- 🔒 **Verify:** File permissions after transfer

## 🚨 Troubleshooting

### ZIP Upload Issues
**Problem:** "File too large" error
**Solution:** 
- Exclude large files (node_modules, build folders)
- Use Git clone method instead

**Problem:** "Invalid ZIP file" error
**Solution:**
- Recreate ZIP file
- Ensure ZIP is not corrupted
- Try different compression tool

### Git Clone Issues
**Problem:** "Repository not found"
**Solution:**
- Verify repository URL is correct
- Ensure repository is public or accessible
- Check internet connection on EC2

**Problem:** "Git not installed"
**Solution:**
- Use ZIP upload method instead
- Contact administrator to install Git

### SSH/SCP Issues
**Problem:** "Permission denied"
**Solution:**
- Verify SSH key is correct
- Check EC2 security group allows SSH (port 22)
- Ensure correct username (usually `ec2-user`)

**Problem:** "Host not found"
**Solution:**
- Verify EC2 instance public IP/hostname
- Check if instance is running
- Verify network connectivity

## 📞 Need Help?

If you encounter issues:
1. Try the ZIP upload method first (most reliable)
2. Check the error messages in Kiro
3. Verify your project structure is correct
4. Ensure files are not corrupted during transfer

The enhanced folder selection now supports all these methods to make it easy to work with your local projects on the EC2 instance!