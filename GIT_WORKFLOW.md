# Git Workflow Guide - NASA Space App

## 🔄 Git Integration

The NASA Space App project includes comprehensive git management through the unified management script.

## 📋 Quick Git Commands

### Using Management Script
```bash
# Check git status
python3 manage.py git status

# Add all important files
python3 manage.py git add

# Commit changes
python3 manage.py git commit --message "Your commit message"

# Check overall project status (includes git info)
python3 manage.py status
```

### Traditional Git Commands
```bash
# Standard git workflow
git status
git add .
git commit -m "Your commit message"
git push origin main
```

## 📁 What's Included/Excluded

### ✅ Included in Git
- **Source Code**: All Python, HTML, CSS, JavaScript files
- **Configuration**: Requirements, environment templates, Dockerfiles
- **Documentation**: README files, guides, licenses
- **Project Structure**: Directory structure with .gitkeep files
- **Management Tools**: manage.py, launcher.sh scripts

### ❌ Excluded from Git (via .gitignore)
- **Virtual Environments**: venv/, .venv/, env/
- **Databases**: *.db, *.sqlite, instance/
- **Large Data Files**: *.csv, *.h5, *.parquet, dataset content
- **Model Files**: *.pkl, *.joblib, *.h5 (ML models)
- **Logs & Temp**: *.log, __pycache__, .pytest_cache
- **Environment Files**: .env (contains secrets)
- **IDE Files**: .vscode/, .idea/, *.pyc
- **OS Files**: .DS_Store, Thumbs.db

## 🗂️ File Type Handling (.gitattributes)

### Text Files (normalized line endings)
- Python files (.py) → LF line endings
- Web files (.html, .css, .js) → LF line endings
- Config files (.json, .yml, .ini) → LF line endings
- Documentation (.md, .rst, .txt) → LF line endings

### Binary Files (no line ending conversion)
- Images (.png, .jpg, .gif, .svg)
- Data files (.h5, .nc, .parquet, .pkl)
- Archives (.zip, .tar.gz, .rar)
- Executables (.exe, .dll, .so)

### Special Handling
- **Jupyter Notebooks**: Text format with output stripping
- **Large Files**: Ready for Git LFS (commented examples)
- **Language Detection**: Proper GitHub language statistics

## 🚀 Initial Repository Setup

### For New Repository
```bash
# Initialize repository
python3 manage.py git init

# Add all files
python3 manage.py git add

# Initial commit
python3 manage.py git commit --message "Initial commit: NASA Space App with comprehensive structure"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/nasa-space-app.git

# Push to remote
git push -u origin main
```

### For Existing Repository (Current State)
```bash
# Add new management system and gitignore
python3 manage.py git add

# Commit comprehensive improvements
python3 manage.py git commit --message "feat: Add comprehensive project management system

- Add unified manage.py script with Flask, ML, and dataset operations
- Implement comprehensive .gitignore for all project components
- Add .gitattributes for proper file handling
- Create interactive launcher.sh for easy project management
- Add git integration and status monitoring
- Include detailed documentation and guides"

# Push changes
git push origin main
```

## 🔧 Common Workflows

### Daily Development
```bash
# Check what's changed
python3 manage.py status

# See git status
python3 manage.py git status

# Add and commit changes
python3 manage.py git add
python3 manage.py git commit --message "Update: your changes description"
```

### Before Major Changes
```bash
# Check project health
python3 manage.py status

# Commit current work
python3 manage.py git add
python3 manage.py git commit --message "Save current progress"

# Create new branch for feature
git checkout -b feature/new-feature
```

### Deployment Preparation
```bash
# Clean up development files
python3 manage.py clean --component all

# Rebuild environments
python3 manage.py setup

# Test everything
python3 manage.py flask test
python3 manage.py status

# Commit deployment-ready state
python3 manage.py git add
python3 manage.py git commit --message "Ready for deployment"
```

## 🎯 Git Best Practices

### Commit Messages
Use conventional commit format:
```
feat: add new feature
fix: resolve bug
docs: update documentation
style: formatting changes
refactor: code restructuring
test: add tests
chore: maintenance tasks
```

### Branch Strategy
```bash
# Main branches
main         # Production-ready code
develop      # Integration branch

# Feature branches
feature/flask-improvements
feature/ml-models
feature/data-processing

# Release branches
release/v1.0.0

# Hotfix branches
hotfix/critical-bug-fix
```

### File Organization
- **Keep sensitive data out**: Use .env.example templates
- **Separate environments**: Different .env files for dev/staging/prod
- **Document large files**: Use README in data directories
- **Use meaningful names**: Clear file and directory names

## 🛡️ Security Considerations

### Never Commit
- API keys and passwords (.env files)
- Database files with real data
- Personal SSH keys or certificates
- Large datasets (use Git LFS or external storage)
- Compiled binaries from development

### Always Include
- Configuration templates (.env.example)
- Requirements and dependency files
- Documentation and setup instructions
- License and legal files

## 📊 Repository Statistics

Current repository includes:
- **3 Main Components**: Flask app, ML project, Dataset management
- **Unified Management**: Single script for all operations
- **Comprehensive Ignores**: 200+ patterns in .gitignore
- **File Attributes**: Proper handling for 50+ file types
- **Cross-Platform**: Windows, macOS, Linux support

## 🔍 Troubleshooting

### Large Files
```bash
# If you accidentally commit large files
git filter-branch --tree-filter 'rm -f path/to/large/file' HEAD

# Or use git-filter-repo (modern approach)
git filter-repo --path path/to/large/file --invert-paths
```

### Line Ending Issues
```bash
# Reset line endings after adding .gitattributes
git add --renormalize .
git commit -m "Normalize line endings"
```

### Cleaning History
```bash
# Remove sensitive data from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all
```

---

**🔄 Ready for professional version control with comprehensive git integration! 📚**