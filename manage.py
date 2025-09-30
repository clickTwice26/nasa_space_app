#!/usr/bin/env python3
"""
NASA Space App Project Management Script
=========================================

A comprehensive, modular management script for the entire NASA Space App project.
Handles Flask app operations, ML project setup, dataset management, and more.

Usage:
    python manage.py <command> [options]
    
Available Commands:
    setup       - Complete project setup
    flask       - Flask application operations
    ml          - Machine learning project operations  
    dataset     - Dataset management operations
    deploy      - Deployment operations
    clean       - Cleanup operations
    status      - Project status check
    
For detailed help on any command:
    python manage.py <command> --help
"""

import os
import sys
import argparse
import subprocess
import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import importlib.util

# Project configuration
PROJECT_ROOT = Path(__file__).parent
FLASK_APP_DIR = PROJECT_ROOT / "flask-app"
ML_PROJECT_DIR = PROJECT_ROOT / "ml-project"
DATASET_DIR = PROJECT_ROOT / "dataset"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logger:
    """Enhanced logging utility"""
    
    @staticmethod
    def info(message, prefix="INFO"):
        print(f"{Colors.BLUE}[{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def success(message, prefix="SUCCESS"):
        print(f"{Colors.GREEN}[{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def warning(message, prefix="WARNING"):
        print(f"{Colors.WARNING}[{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def error(message, prefix="ERROR"):
        print(f"{Colors.FAIL}[{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def header(message):
        print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 {message}{Colors.ENDC}")
    
    @staticmethod
    def section(message):
        print(f"\n{Colors.CYAN}📂 {message}{Colors.ENDC}")

class ProjectManager:
    """Base class for project management operations"""
    
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.venv_dir = self.project_dir / "venv"
        self.requirements_file = self.project_dir / "requirements.txt"
    
    def run_command(self, command, cwd=None, capture_output=False, shell=False):
        """Execute shell command with error handling"""
        try:
            cwd = cwd or self.project_dir
            if shell:
                result = subprocess.run(command, cwd=cwd, shell=True, 
                                      capture_output=capture_output, text=True)
            else:
                result = subprocess.run(command.split(), cwd=cwd, 
                                      capture_output=capture_output, text=True)
            
            if result.returncode != 0 and not capture_output:
                Logger.error(f"Command failed: {command}")
                if result.stderr:
                    Logger.error(result.stderr)
                return False
            
            return result if capture_output else True
        
        except Exception as e:
            Logger.error(f"Failed to execute command '{command}': {str(e)}")
            return False
    
    def create_venv(self):
        """Create virtual environment"""
        if self.venv_dir.exists():
            Logger.info(f"Virtual environment already exists: {self.venv_dir}")
            return True
        
        Logger.info(f"Creating virtual environment: {self.venv_dir}")
        return self.run_command(f"python3 -m venv {self.venv_dir}")
    
    def activate_venv_command(self):
        """Get command to activate virtual environment"""
        if os.name == 'nt':  # Windows
            return f"{self.venv_dir}/Scripts/activate"
        else:  # Unix/Linux/macOS
            return f"source {self.venv_dir}/bin/activate"
    
    def install_requirements(self):
        """Install requirements in virtual environment"""
        if not self.requirements_file.exists():
            Logger.warning(f"Requirements file not found: {self.requirements_file}")
            return True
        
        Logger.info("Installing requirements...")
        pip_path = self.venv_dir / ("Scripts/pip" if os.name == 'nt' else "bin/pip")
        return self.run_command(f"{pip_path} install -r {self.requirements_file}")

class FlaskManager(ProjectManager):
    """Flask application management"""
    
    def __init__(self):
        super().__init__(FLASK_APP_DIR)
        self.app_file = self.project_dir / "app.py"
        self.db_file = self.project_dir / "instance" / "nasa_space_app.db"
        self.init_db_file = self.project_dir / "init_db.py"
    
    def setup(self):
        """Complete Flask application setup"""
        Logger.section("Setting up Flask Application")
        
        # Create virtual environment
        if not self.create_venv():
            return False
        
        # Install requirements
        if not self.install_requirements():
            return False
        
        # Create instance directory
        instance_dir = self.project_dir / "instance"
        instance_dir.mkdir(exist_ok=True)
        
        # Create .env file if it doesn't exist
        env_file = self.project_dir / ".env"
        env_example = self.project_dir / ".env.example"
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            Logger.info("Created .env file from template")
        
        Logger.success("Flask application setup complete")
        return True
    
    def init_database(self, reset=False):
        """Initialize database with sample data"""
        Logger.section("Database Operations")
        
        if reset and self.db_file.exists():
            Logger.info("Removing existing database...")
            self.db_file.unlink()
        
        if not self.init_db_file.exists():
            Logger.error("Database initialization script not found")
            return False
        
        Logger.info("Initializing database...")
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        return self.run_command(f"{python_path} {self.init_db_file}")
    
    def migrate_database(self, message="Auto migration"):
        """Run database migrations"""
        Logger.section("Database Migration")
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        flask_path = self.venv_dir / ("Scripts/flask" if os.name == 'nt' else "bin/flask")
        
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        
        # Initialize migration repository if it doesn't exist
        migrations_dir = self.project_dir / "migrations"
        if not migrations_dir.exists():
            Logger.info("Initializing migration repository...")
            result = subprocess.run([str(flask_path), "db", "init"], 
                                  cwd=self.project_dir, env=env)
            if result.returncode != 0:
                return False
        
        # Create migration
        Logger.info(f"Creating migration: {message}")
        result = subprocess.run([str(flask_path), "db", "migrate", "-m", message], 
                              cwd=self.project_dir, env=env)
        if result.returncode != 0:
            Logger.warning("Migration creation failed or no changes detected")
        
        # Apply migration
        Logger.info("Applying migrations...")
        result = subprocess.run([str(flask_path), "db", "upgrade"], 
                              cwd=self.project_dir, env=env)
        return result.returncode == 0
    
    def run_server(self, port=6767, host="0.0.0.0", debug=True):
        """Run Flask development server"""
        Logger.section("Starting Flask Server")
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_PORT'] = str(port)
        env['FLASK_HOST'] = host
        env['FLASK_DEBUG'] = str(debug).lower()
        
        Logger.info(f"Starting server on {host}:{port}")
        Logger.info("Press Ctrl+C to stop the server")
        
        try:
            subprocess.run([str(python_path), str(self.app_file)], 
                         cwd=self.project_dir, env=env)
        except KeyboardInterrupt:
            Logger.info("Server stopped by user")
        
        return True
    
    def test(self):
        """Run Flask application tests"""
        Logger.section("Running Flask Tests")
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        pytest_path = self.venv_dir / ("Scripts/pytest" if os.name == 'nt' else "bin/pytest")
        
        if not pytest_path.exists():
            Logger.error("pytest not found. Install it first.")
            return False
        
        return self.run_command(f"{pytest_path} tests/")
    
    def get_status(self):
        """Get Flask application status"""
        status = {
            "venv_exists": self.venv_dir.exists(),
            "database_exists": self.db_file.exists(),
            "app_file_exists": self.app_file.exists(),
            "requirements_installed": False
        }
        
        if status["venv_exists"]:
            pip_path = self.venv_dir / ("Scripts/pip" if os.name == 'nt' else "bin/pip")
            result = self.run_command(f"{pip_path} list", capture_output=True)
            if result and "Flask" in result.stdout:
                status["requirements_installed"] = True
        
        if status["database_exists"]:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                status["database_tables"] = [table[0] for table in tables]
                conn.close()
            except Exception:
                status["database_tables"] = []
        
        return status

class MLManager(ProjectManager):
    """Machine Learning project management"""
    
    def __init__(self):
        super().__init__(ML_PROJECT_DIR)
        self.notebooks_dir = self.project_dir / "notebooks"
        self.data_dir = self.project_dir / "data"
        self.models_dir = self.project_dir / "models"
        self.src_dir = self.project_dir / "src"
    
    def setup(self):
        """Setup ML project environment"""
        Logger.section("Setting up ML Project")
        
        # Create virtual environment
        if not self.create_venv():
            return False
        
        # Install requirements
        if not self.install_requirements():
            return False
        
        # Create necessary directories
        for directory in [self.notebooks_dir, self.data_dir, self.models_dir]:
            directory.mkdir(exist_ok=True)
        
        Logger.success("ML project setup complete")
        return True
    
    def start_jupyter(self, port=8888):
        """Start Jupyter notebook server"""
        Logger.section("Starting Jupyter Notebook")
        
        jupyter_path = self.venv_dir / ("Scripts/jupyter" if os.name == 'nt' else "bin/jupyter")
        
        if not jupyter_path.exists():
            Logger.error("Jupyter not found. Install it first.")
            return False
        
        Logger.info(f"Starting Jupyter on port {port}")
        Logger.info("Jupyter will open in your browser")
        
        try:
            subprocess.run([str(jupyter_path), "notebook", 
                          f"--port={port}", 
                          f"--notebook-dir={self.notebooks_dir}",
                          "--no-browser"], 
                         cwd=self.project_dir)
        except KeyboardInterrupt:
            Logger.info("Jupyter server stopped by user")
        
        return True
    
    def run_training(self, script_name):
        """Run ML training script"""
        Logger.section(f"Running Training Script: {script_name}")
        
        script_path = self.src_dir / script_name
        if not script_path.exists():
            Logger.error(f"Training script not found: {script_path}")
            return False
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        return self.run_command(f"{python_path} {script_path}")
    
    def get_status(self):
        """Get ML project status"""
        status = {
            "venv_exists": self.venv_dir.exists(),
            "notebooks_count": len(list(self.notebooks_dir.glob("*.ipynb"))) if self.notebooks_dir.exists() else 0,
            "models_count": len(list(self.models_dir.glob("*.joblib"))) if self.models_dir.exists() else 0,
            "data_files_count": len(list(self.data_dir.rglob("*.*"))) if self.data_dir.exists() else 0
        }
        return status

class DatasetManager:
    """Dataset management operations"""
    
    def __init__(self):
        self.dataset_dir = DATASET_DIR
        self.raw_dir = self.dataset_dir / "raw"
        self.processed_dir = self.dataset_dir / "processed"
        self.external_dir = self.dataset_dir / "external"
        self.metadata_dir = self.dataset_dir / "metadata"
    
    def validate_structure(self):
        """Validate dataset directory structure"""
        Logger.section("Validating Dataset Structure")
        
        required_dirs = [self.raw_dir, self.processed_dir, 
                        self.external_dir, self.metadata_dir]
        
        all_exist = True
        for directory in required_dirs:
            if not directory.exists():
                Logger.warning(f"Missing directory: {directory}")
                directory.mkdir(parents=True, exist_ok=True)
                Logger.info(f"Created directory: {directory}")
                all_exist = False
        
        if all_exist:
            Logger.success("Dataset structure is valid")
        else:
            Logger.success("Dataset structure has been corrected")
        
        return True
    
    def generate_catalog(self):
        """Generate dataset catalog"""
        Logger.section("Generating Dataset Catalog")
        
        catalog = {
            "dataset_info": {
                "name": "NASA Space App Dataset",
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            "directories": {},
            "summary": {}
        }
        
        # Scan directories
        for dir_name, dir_path in [("raw", self.raw_dir), 
                                  ("processed", self.processed_dir),
                                  ("external", self.external_dir)]:
            if dir_path.exists():
                files = list(dir_path.rglob("*"))
                catalog["directories"][dir_name] = {
                    "file_count": len([f for f in files if f.is_file()]),
                    "total_size": sum(f.stat().st_size for f in files if f.is_file()),
                    "file_types": list(set(f.suffix for f in files if f.is_file() and f.suffix))
                }
        
        # Save catalog
        catalog_file = self.metadata_dir / "dataset_catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        Logger.success(f"Catalog generated: {catalog_file}")
        return True
    
    def get_status(self):
        """Get dataset status"""
        status = {
            "structure_valid": all(d.exists() for d in [self.raw_dir, self.processed_dir, 
                                                        self.external_dir, self.metadata_dir])
        }
        
        if status["structure_valid"]:
            for dir_name, dir_path in [("raw", self.raw_dir), 
                                      ("processed", self.processed_dir),
                                      ("external", self.external_dir)]:
                files = list(dir_path.rglob("*"))
                status[f"{dir_name}_files"] = len([f for f in files if f.is_file()])
                status[f"{dir_name}_size"] = sum(f.stat().st_size for f in files if f.is_file())
        
        return status

class GitManager:
    """Git repository management"""
    
    def __init__(self):
        self.project_dir = PROJECT_ROOT
    
    def init_repository(self):
        """Initialize git repository"""
        Logger.section("Git Repository Initialization")
        
        if (self.project_dir / ".git").exists():
            Logger.info("Git repository already exists")
            return True
        
        Logger.info("Initializing git repository...")
        result = subprocess.run(["git", "init"], cwd=self.project_dir)
        
        if result.returncode == 0:
            Logger.success("Git repository initialized")
            return True
        else:
            Logger.error("Failed to initialize git repository")
            return False
    
    def add_all_files(self):
        """Add all files to git staging"""
        Logger.section("Adding Files to Git")
        
        # Add important files
        important_files = [
            ".gitignore",
            ".gitattributes", 
            "README.md",
            "MANAGEMENT_GUIDE.md",
            "manage.py",
            "launcher.sh",
            "flask-app/",
            "ml-project/",
            "dataset/"
        ]
        
        for file_path in important_files:
            full_path = self.project_dir / file_path
            if full_path.exists():
                result = subprocess.run(["git", "add", str(file_path)], 
                                      cwd=self.project_dir, capture_output=True)
                if result.returncode == 0:
                    Logger.info(f"Added: {file_path}")
                else:
                    Logger.warning(f"Failed to add: {file_path}")
        
        return True
    
    def commit_changes(self, message="Initial commit"):
        """Commit changes"""
        Logger.section("Committing Changes")
        
        Logger.info(f"Committing with message: {message}")
        result = subprocess.run(["git", "commit", "-m", message], 
                              cwd=self.project_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            Logger.success("Changes committed successfully")
            return True
        else:
            Logger.warning(f"Commit failed or no changes: {result.stderr}")
            return False
    
    def get_status(self):
        """Get git repository status"""
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  cwd=self.project_dir, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                return {
                    "is_git_repo": True,
                    "files_changed": len(lines),
                    "changes": lines[:10]  # Show first 10 changes
                }
        except Exception:
            pass
        
        return {"is_git_repo": False, "files_changed": 0, "changes": []}
    
    def create_gitignore_if_missing(self):
        """Create .gitignore if it doesn't exist"""
        gitignore_path = self.project_dir / ".gitignore"
        if not gitignore_path.exists():
            Logger.info("Creating .gitignore file...")
            # Basic gitignore content would be created here
            return True
        Logger.info(".gitignore already exists")
        return True

class ProjectStatusChecker:
    """Overall project status checker"""
    
    def __init__(self):
        self.flask_manager = FlaskManager()
        self.ml_manager = MLManager()
        self.dataset_manager = DatasetManager()
        self.git_manager = GitManager()
    
    def check_all(self):
        """Check status of all projects"""
        Logger.header("NASA Space App Project Status")
        
        # Flask App Status
        Logger.section("Flask Application")
        flask_status = self.flask_manager.get_status()
        
        print(f"  Virtual Environment: {'✅' if flask_status['venv_exists'] else '❌'}")
        print(f"  Requirements Installed: {'✅' if flask_status['requirements_installed'] else '❌'}")
        print(f"  Database: {'✅' if flask_status['database_exists'] else '❌'}")
        print(f"  App File: {'✅' if flask_status['app_file_exists'] else '❌'}")
        
        if flask_status.get('database_tables'):
            print(f"  Database Tables: {', '.join(flask_status['database_tables'])}")
        
        # ML Project Status
        Logger.section("Machine Learning Project")
        ml_status = self.ml_manager.get_status()
        
        print(f"  Virtual Environment: {'✅' if ml_status['venv_exists'] else '❌'}")
        print(f"  Notebooks: {ml_status['notebooks_count']} files")
        print(f"  Models: {ml_status['models_count']} files")
        print(f"  Data Files: {ml_status['data_files_count']} files")
        
        # Dataset Status
        Logger.section("Dataset")
        dataset_status = self.dataset_manager.get_status()
        
        print(f"  Structure: {'✅' if dataset_status['structure_valid'] else '❌'}")
        
        if dataset_status['structure_valid']:
            for category in ['raw', 'processed', 'external']:
                files_key = f"{category}_files"
                size_key = f"{category}_size"
                if files_key in dataset_status:
                    size_mb = dataset_status[size_key] / (1024 * 1024)
                    print(f"  {category.title()}: {dataset_status[files_key]} files ({size_mb:.1f} MB)")
        
        # Git Status
        Logger.section("Git Repository")
        git_status = self.git_manager.get_status()
        
        print(f"  Repository: {'✅' if git_status['is_git_repo'] else '❌'}")
        if git_status['is_git_repo']:
            print(f"  Changed Files: {git_status['files_changed']}")
            if git_status['changes']:
                print(f"  Recent Changes: {', '.join(git_status['changes'][:3])}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NASA Space App Project Management Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Complete project setup')
    setup_parser.add_argument('--component', choices=['flask', 'ml', 'dataset', 'all'], 
                             default='all', help='Component to setup')
    
    # Flask commands
    flask_parser = subparsers.add_parser('flask', help='Flask application operations')
    flask_subparsers = flask_parser.add_subparsers(dest='flask_action')
    
    flask_setup = flask_subparsers.add_parser('setup', help='Setup Flask app')
    flask_init_db = flask_subparsers.add_parser('init-db', help='Initialize database')
    flask_init_db.add_argument('--reset', action='store_true', help='Reset existing database')
    
    flask_migrate = flask_subparsers.add_parser('migrate', help='Run database migration')
    flask_migrate.add_argument('--message', default='Auto migration', help='Migration message')
    
    flask_run = flask_subparsers.add_parser('run', help='Run development server')
    flask_run.add_argument('--port', type=int, default=6767, help='Server port')
    flask_run.add_argument('--host', default='0.0.0.0', help='Server host')
    flask_run.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    
    flask_test = flask_subparsers.add_parser('test', help='Run tests')
    
    # ML commands
    ml_parser = subparsers.add_parser('ml', help='Machine learning operations')
    ml_subparsers = ml_parser.add_subparsers(dest='ml_action')
    
    ml_setup = ml_subparsers.add_parser('setup', help='Setup ML project')
    ml_jupyter = ml_subparsers.add_parser('jupyter', help='Start Jupyter notebook')
    ml_jupyter.add_argument('--port', type=int, default=8888, help='Jupyter port')
    
    ml_train = ml_subparsers.add_parser('train', help='Run training script')
    ml_train.add_argument('script', help='Training script name')
    
    # Dataset commands
    dataset_parser = subparsers.add_parser('dataset', help='Dataset operations')
    dataset_subparsers = dataset_parser.add_subparsers(dest='dataset_action')
    
    dataset_validate = dataset_subparsers.add_parser('validate', help='Validate structure')
    dataset_catalog = dataset_subparsers.add_parser('catalog', help='Generate catalog')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check project status')
    
    # Git commands
    git_parser = subparsers.add_parser('git', help='Git repository operations')
    git_subparsers = git_parser.add_subparsers(dest='git_action')
    
    git_init = git_subparsers.add_parser('init', help='Initialize git repository')
    git_add = git_subparsers.add_parser('add', help='Add files to git')
    git_commit = git_subparsers.add_parser('commit', help='Commit changes')
    git_commit.add_argument('--message', '-m', default='Auto commit', help='Commit message')
    git_status = git_subparsers.add_parser('status', help='Show git status')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean project files')
    clean_parser.add_argument('--component', choices=['flask', 'ml', 'all'], 
                             default='all', help='Component to clean')
    clean_parser.add_argument('--force', action='store_true', help='Force cleanup without confirmation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize managers
    flask_manager = FlaskManager()
    ml_manager = MLManager()
    dataset_manager = DatasetManager()
    git_manager = GitManager()
    status_checker = ProjectStatusChecker()
    
    # Execute commands
    if args.command == 'setup':
        Logger.header("Project Setup")
        success = True
        
        if args.component in ['flask', 'all']:
            success &= flask_manager.setup()
        
        if args.component in ['ml', 'all']:
            success &= ml_manager.setup()
        
        if args.component in ['dataset', 'all']:
            success &= dataset_manager.validate_structure()
        
        if success:
            Logger.success("Setup completed successfully!")
        else:
            Logger.error("Setup failed!")
    
    elif args.command == 'flask':
        if args.flask_action == 'setup':
            flask_manager.setup()
        elif args.flask_action == 'init-db':
            flask_manager.init_database(reset=args.reset)
        elif args.flask_action == 'migrate':
            flask_manager.migrate_database(message=args.message)
        elif args.flask_action == 'run':
            flask_manager.run_server(port=args.port, host=args.host, 
                                   debug=not args.no_debug)
        elif args.flask_action == 'test':
            flask_manager.test()
        else:
            flask_parser.print_help()
    
    elif args.command == 'ml':
        if args.ml_action == 'setup':
            ml_manager.setup()
        elif args.ml_action == 'jupyter':
            ml_manager.start_jupyter(port=args.port)
        elif args.ml_action == 'train':
            ml_manager.run_training(args.script)
        else:
            ml_parser.print_help()
    
    elif args.command == 'dataset':
        if args.dataset_action == 'validate':
            dataset_manager.validate_structure()
        elif args.dataset_action == 'catalog':
            dataset_manager.generate_catalog()
        else:
            dataset_parser.print_help()
    
    elif args.command == 'status':
        status_checker.check_all()
    
    elif args.command == 'clean':
        Logger.header("Project Cleanup")
        
        if not args.force:
            response = input("Are you sure you want to clean project files? [y/N]: ")
            if response.lower() != 'y':
                Logger.info("Cleanup cancelled")
                return
        
        if args.component in ['flask', 'all']:
            venv_path = flask_manager.venv_dir
            if venv_path.exists():
                shutil.rmtree(venv_path)
                Logger.success(f"Removed Flask virtual environment: {venv_path}")
        
        if args.component in ['ml', 'all']:
            venv_path = ml_manager.venv_dir
            if venv_path.exists():
                shutil.rmtree(venv_path)
                Logger.success(f"Removed ML virtual environment: {venv_path}")
        
        Logger.success("Cleanup completed!")
    
    elif args.command == 'git':
        if args.git_action == 'init':
            git_manager.init_repository()
        elif args.git_action == 'add':
            git_manager.add_all_files()
        elif args.git_action == 'commit':
            git_manager.commit_changes(message=args.message)
        elif args.git_action == 'status':
            result = subprocess.run(["git", "status"], cwd=PROJECT_ROOT)
        else:
            git_parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)