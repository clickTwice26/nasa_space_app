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
import time
import threading
import signal
from pathlib import Path
from datetime import datetime
import importlib.util
from contextlib import contextmanager

# Import configuration manager
try:
    from config import config
except ImportError:
    # Fallback if config.py is not available
    class DummyConfig:
        def get_int(self, key, default): return default
        def get(self, key, default): return default
        def get_bool(self, key, default): return default
        def get_flask_config(self): return {'port': 6767, 'host': '0.0.0.0', 'debug': True}
        def get_team_website_config(self): return {'port': 8080, 'host': '0.0.0.0', 'debug': True}
        def get_jupyter_config(self): return {'port': 8888, 'host': 'localhost'}
    config = DummyConfig()

# Project configuration
PROJECT_ROOT = Path(__file__).parent
FLASK_APP_DIR = PROJECT_ROOT / "flask-app"
TEAM_FLASK_APP_DIR = PROJECT_ROOT / "team-flask-app"
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
    DIM = '\033[2m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Extended colors
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;135m'
    PINK = '\033[38;5;207m'
    LIME = '\033[38;5;154m'
    NAVY = '\033[38;5;17m'
    
    @staticmethod
    def strip_colors(text):
        """Remove ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

class Spinner:
    """Animated spinner for long-running operations"""
    def __init__(self, message="Processing", delay=0.1):
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.delay = delay
        self.message = message
        self.running = False
        self.thread = None

    def spin(self):
        idx = 0
        while self.running:
            print(f'\r{Colors.CYAN}{self.spinner_chars[idx]} {self.message}...{Colors.ENDC}', end='', flush=True)
            idx = (idx + 1) % len(self.spinner_chars)
            time.sleep(self.delay)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self, success_message=None, error_message=None):
        self.running = False
        if self.thread:
            self.thread.join()
        print('\r' + ' ' * (len(self.message) + 20), end='\r')  # Clear line
        if success_message:
            Logger.success(success_message)
        elif error_message:
            Logger.error(error_message)

class ProgressBar:
    """Console progress bar"""
    def __init__(self, total, width=50, prefix='Progress'):
        self.total = total
        self.width = width
        self.prefix = prefix
        self.current = 0

    def update(self, current, suffix=''):
        self.current = current
        percent = (current / self.total) * 100
        filled = int(self.width * current / self.total)
        bar = '█' * filled + '▒' * (self.width - filled)
        
        print(f'\r{Colors.CYAN}{self.prefix}{Colors.ENDC} |{Colors.GREEN}{bar}{Colors.ENDC}| '
              f'{percent:.1f}% {suffix}', end='', flush=True)
        
        if current >= self.total:
            print()  # New line when complete

class BoxDrawer:
    """Draw fancy boxes around text"""
    
    @staticmethod
    def draw_box(content, title=None, width=80, style='double'):
        """Draw a box around content"""
        if style == 'double':
            top_left, top_right = '╔', '╗'
            bottom_left, bottom_right = '╚', '╝'
            horizontal, vertical = '═', '║'
            title_left, title_right = '╠', '╣'
        else:  # single
            top_left, top_right = '┌', '┐'
            bottom_left, bottom_right = '└', '┘'
            horizontal, vertical = '─', '│'
            title_left, title_right = '├', '┤'
        
        lines = content.split('\n') if isinstance(content, str) else content
        
        # Calculate actual width needed
        max_line_length = max(len(Colors.strip_colors(line)) for line in lines) if lines else 0
        box_width = max(width, max_line_length + 4, len(title) + 6 if title else 0)
        
        result = []
        
        # Top border
        if title:
            title_start = f"{top_left}{horizontal * 2} {Colors.BOLD}{title}{Colors.ENDC} "
            title_padding = box_width - len(Colors.strip_colors(title_start)) - 1
            result.append(f"{title_start}{horizontal * title_padding}{top_right}")
        else:
            result.append(f"{top_left}{horizontal * (box_width - 2)}{top_right}")
        
        # Content
        for line in lines:
            clean_line = Colors.strip_colors(line)
            padding = box_width - len(clean_line) - 4
            result.append(f"{vertical} {line}{' ' * padding} {vertical}")
        
        # Bottom border
        result.append(f"{bottom_left}{horizontal * (box_width - 2)}{bottom_right}")
        
        return '\n'.join(result)

class InteractiveMenu:
    """Interactive menu system"""
    
    def __init__(self, title, options, show_numbers=True):
        self.title = title
        self.options = options
        self.show_numbers = show_numbers
    
    def display(self):
        """Display menu and get user choice"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}🎯 {self.title}{Colors.ENDC}")
        print(f"{Colors.DIM}{'─' * (len(self.title) + 4)}{Colors.ENDC}")
        
        for i, option in enumerate(self.options, 1):
            if isinstance(option, dict):
                key = option.get('key', str(i))
                text = option.get('text', f'Option {i}')
                desc = option.get('desc', '')
                icon = option.get('icon', '•')
            else:
                key = str(i)
                text = option
                desc = ''
                icon = '•'
            
            if self.show_numbers:
                print(f"  {Colors.CYAN}{key}{Colors.ENDC}. {icon} {text}")
            else:
                print(f"  {icon} {text}")
            
            if desc:
                print(f"     {Colors.DIM}{desc}{Colors.ENDC}")
        
        print(f"\n{Colors.WARNING}Enter your choice: {Colors.ENDC}", end='')
        
        try:
            choice = input().strip()
            return choice
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.WARNING}Operation cancelled{Colors.ENDC}")
            return None

class Logger:
    """Enhanced logging utility with better formatting"""
    
    @staticmethod
    def info(message, prefix="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.DIM}[{timestamp}]{Colors.ENDC} {Colors.BLUE}[{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def success(message, prefix="SUCCESS"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.DIM}[{timestamp}]{Colors.ENDC} {Colors.GREEN}✅ [{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def warning(message, prefix="WARNING"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.DIM}[{timestamp}]{Colors.ENDC} {Colors.WARNING}⚠️  [{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def error(message, prefix="ERROR"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.DIM}[{timestamp}]{Colors.ENDC} {Colors.FAIL}❌ [{prefix}]{Colors.ENDC} {message}")
    
    @staticmethod
    def header(message):
        box = BoxDrawer.draw_box(f"🚀 {message}", width=80, style='double')
        print(f"\n{Colors.HEADER}{box}{Colors.ENDC}")
    
    @staticmethod
    def section(message):
        print(f"\n{Colors.CYAN}{Colors.BOLD}� {message}{Colors.ENDC}")
        print(f"{Colors.DIM}{'─' * (len(message) + 4)}{Colors.ENDC}")
    
    @staticmethod
    def step(step_num, total_steps, message):
        """Show step progress"""
        print(f"{Colors.PURPLE}[{step_num}/{total_steps}]{Colors.ENDC} {message}")
    
    @staticmethod
    def separator():
        """Print a visual separator"""
        print(f"{Colors.DIM}{'═' * 80}{Colors.ENDC}")
    
    @staticmethod
    def banner():
        """Show application banner"""
        banner_text = [
            "███╗   ██╗ █████╗ ███████╗ █████╗     ███████╗██████╗  █████╗  ██████╗███████╗",
            "████╗  ██║██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝",
            "██╔██╗ ██║███████║███████╗███████║    ███████╗██████╔╝███████║██║     █████╗  ",
            "██║╚██╗██║██╔══██║╚════██║██╔══██║    ╚════██║██╔═══╝ ██╔══██║██║     ██╔══╝  ",
            "██║ ╚████║██║  ██║███████║██║  ██║    ███████║██║     ██║  ██║╚██████╗███████╗",
            "╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝",
            "",
            "              � NASA Space App Management System 🛸",
            "                     Professional Project Manager",
            "",
            f"                Version 2.0 | {datetime.now().strftime('%Y-%m-%d')}"
        ]
        
        box = BoxDrawer.draw_box(banner_text, width=85, style='double')
        print(f"{Colors.CYAN}{box}{Colors.ENDC}")

@contextmanager
def spinner_context(message, success_msg=None, error_msg=None):
    """Context manager for spinner operations"""
    spinner = Spinner(message)
    spinner.start()
    try:
        yield spinner
        spinner.stop(success_message=success_msg)
    except Exception as e:
        spinner.stop(error_message=error_msg or f"Failed: {str(e)}")
        raise

class ProjectManager:
    """Base class for project management operations"""
    
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.venv_dir = self.project_dir / "venv"
        self.requirements_file = self.project_dir / "requirements.txt"
    
    def run_command(self, command, cwd=None, capture_output=False, shell=False, timeout=300):
        """Execute shell command with enhanced error handling and timeout"""
        try:
            cwd = cwd or self.project_dir
            
            if shell:
                process = subprocess.Popen(
                    command, cwd=cwd, shell=True, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                    text=True, universal_newlines=True
                )
            else:
                process = subprocess.Popen(
                    command.split(), cwd=cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, universal_newlines=True
                )
            
            if not capture_output:
                # Real-time output for interactive commands
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
                
                rc = process.poll()
                return rc == 0
            else:
                # Capture output with timeout
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    result = subprocess.CompletedProcess(
                        command.split() if not shell else command,
                        process.returncode, stdout, stderr
                    )
                    
                    if result.returncode != 0:
                        Logger.error(f"Command failed: {command}")
                        if result.stderr:
                            Logger.error(f"Error output: {result.stderr}")
                        return False
                    
                    return result
                    
                except subprocess.TimeoutExpired:
                    process.kill()
                    Logger.error(f"Command timed out after {timeout}s: {command}")
                    return False
        
        except Exception as e:
            Logger.error(f"Failed to execute command '{command}': {str(e)}")
            return False
    
    def create_venv(self):
        """Create virtual environment with progress tracking"""
        if self.venv_dir.exists():
            Logger.info(f"Virtual environment already exists: {self.venv_dir}")
            return True
        
        with spinner_context(
            f"Creating virtual environment at {self.venv_dir}",
            "Virtual environment created successfully",
            "Failed to create virtual environment"
        ):
            time.sleep(0.5)  # Small delay for spinner visibility
            return self.run_command(f"python3 -m venv {self.venv_dir}", capture_output=True)
    
    def activate_venv_command(self):
        """Get command to activate virtual environment"""
        if os.name == 'nt':  # Windows
            return f"{self.venv_dir}/Scripts/activate"
        else:  # Unix/Linux/macOS
            return f"source {self.venv_dir}/bin/activate"
    
    def install_requirements(self):
        """Install requirements with progress tracking"""
        if not self.requirements_file.exists():
            Logger.warning(f"Requirements file not found: {self.requirements_file}")
            return True
        
        with spinner_context(
            "Installing Python dependencies",
            "Dependencies installed successfully",
            "Failed to install dependencies"
        ):
            pip_path = self.venv_dir / ("Scripts/pip" if os.name == 'nt' else "bin/pip")
            # Add progress and upgrade pip first
            self.run_command(f"{pip_path} install --upgrade pip", capture_output=True)
            return self.run_command(f"{pip_path} install -r {self.requirements_file}", capture_output=True)
    
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        if not self.venv_dir.exists():
            return False
        
        pip_path = self.venv_dir / ("Scripts/pip" if os.name == 'nt' else "bin/pip")
        result = self.run_command(f"{pip_path} list", capture_output=True)
        
        if not result:
            return False
        
        # Check for common required packages
        installed_packages = result.stdout.lower()
        required_checks = ['flask', 'sqlalchemy'] if 'flask' in str(self.project_dir) else ['numpy', 'pandas']
        
        return any(pkg in installed_packages for pkg in required_checks)

class FlaskManager(ProjectManager):
    """Flask application management"""
    
    def __init__(self):
        super().__init__(FLASK_APP_DIR)
        self.app_file = self.project_dir / "app.py"
        self.db_file = self.project_dir / "instance" / "nasa_space_app.db"
        self.init_db_file = self.project_dir / "init_db.py"
    """Team website Flask application management"""
    
    def __init__(self):
        super().__init__(TEAM_FLASK_APP_DIR)
        self.app_file = self.project_dir / "app.py"
        self.index_file = self.project_dir / "index.html"
    
    def setup(self):
        """Setup team Flask application"""
        Logger.section("Setting up Team Website")
        
        total_steps = 4
        
        # Step 1: Create virtual environment
        Logger.step(1, total_steps, "Creating virtual environment")
        if not self.create_venv():
            Logger.error("Failed to create virtual environment")
            return False
        
        # Step 2: Install requirements
        Logger.step(2, total_steps, "Installing dependencies")
        if not self.install_requirements():
            Logger.error("Failed to install requirements")
            return False
        
        # Step 3: Validate files
        Logger.step(3, total_steps, "Validating website files")
        if not self.index_file.exists():
            Logger.error("Website index.html not found")
            return False
        
        if not self.app_file.exists():
            Logger.error("Flask app.py not found")
            return False
        
        # Step 4: Validation
        Logger.step(4, total_steps, "Validating setup")
        if self.validate_setup():
            Logger.success("Team website setup completed successfully! 🎉")
            self._show_setup_summary()
            return True
        else:
            Logger.error("Setup validation failed")
            return False
    
    def validate_setup(self):
        """Validate team website setup"""
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Dependencies installed", self.check_dependencies()),
            ("App file exists", self.app_file.exists()),
            ("Website file exists", self.index_file.exists())
        ]
        
        all_good = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_good = False
        
        return all_good
    
    def _show_setup_summary(self):
        """Show setup summary for team website"""
        summary = [
            "🎯 TerraPulse Team Website Ready!",
            "",
            "Next steps:",
            "  1. Start team website: python3 manage.py team run",
            "  2. Open browser: http://localhost:5000",
            "  3. Share your team story with the world!",
            "",
            "Available commands:",
            "  • team run       - Start team website server",
            "  • team setup     - Setup team website environment"
        ]
        
        box = BoxDrawer.draw_box(summary, title="Team Website Ready", width=60)
        print(f"\n{Colors.GREEN}{box}{Colors.ENDC}")
    
    def run_server(self, port=5000, host="0.0.0.0", debug=True):
        """Run team website server"""
        Logger.section("Starting TerraPulse Team Website")
        
        # Pre-flight checks
        if not self._pre_flight_check():
            return False
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_PORT'] = str(port)
        env['FLASK_HOST'] = host
        env['FLASK_DEBUG'] = str(debug).lower()
        
        # Show server info
        server_info = [
            f"🌐 Team Website URL: http://{host}:{port}",
            f"🔧 Debug mode: {'ON' if debug else 'OFF'}",
            f"📁 Working directory: {self.project_dir}",
            "",
            "🚀 TerraPulse Team Website - NASA Space Apps Challenge 2025",
            "",
            "Press Ctrl+C to stop the server",
            "Server logs will appear below:"
        ]
        
        box = BoxDrawer.draw_box(server_info, title="TerraPulse Team Website", width=70)
        print(f"{Colors.GREEN}{box}{Colors.ENDC}")
        
        Logger.separator()
        
        try:
            # Use signal handler for graceful shutdown
            def signal_handler(sig, frame):
                print(f"\n{Colors.WARNING}🛑 Team website shutdown requested{Colors.ENDC}")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # Start server
            subprocess.run([str(python_path), str(self.app_file)], 
                         cwd=self.project_dir, env=env)
        except KeyboardInterrupt:
            Logger.info("Team website stopped by user")
        except Exception as e:
            Logger.error(f"Server error: {str(e)}")
        
        return True
    
    def _pre_flight_check(self):
        """Check if everything is ready to run the team website"""
        Logger.info("Running pre-flight checks...")
        
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Application file", self.app_file.exists()),
            ("Website HTML file", self.index_file.exists()),
            ("Dependencies", self.check_dependencies())
        ]
        
        progress = ProgressBar(len(checks), prefix="Checking")
        
        all_good = True
        for i, (check_name, result) in enumerate(checks):
            progress.update(i + 1, f"- {check_name}")
            time.sleep(0.2)
            
            if not result:
                Logger.error(f"❌ {check_name} check failed")
                all_good = False
            else:
                Logger.success(f"✅ {check_name} check passed")
        
        if not all_good:
            Logger.error("Pre-flight checks failed. Please run setup first.")
            return False
        
        Logger.success("All pre-flight checks passed! 🚀")
        return True
    
    def get_status(self):
        """Get team website status"""
        status = {
            "venv_exists": self.venv_dir.exists(),
            "app_file_exists": self.app_file.exists(),
            "index_file_exists": self.index_file.exists(),
            "requirements_installed": self.check_dependencies(),
            "port_available": self._check_port_available(5000)
        }
        
        return status
    
    def _check_port_available(self, port):
        """Check if port is available"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    """Flask application management"""
    
    def __init__(self):
        super().__init__(FLASK_APP_DIR)
        self.app_file = self.project_dir / "app.py"
        self.db_file = self.project_dir / "instance" / "nasa_space_app.db"
        self.init_db_file = self.project_dir / "init_db.py"
    
    def setup(self):
        """Complete Flask application setup with enhanced progress tracking"""
        Logger.section("Setting up Flask Application")
        
        total_steps = 5
        
        # Step 1: Create virtual environment
        Logger.step(1, total_steps, "Creating virtual environment")
        if not self.create_venv():
            Logger.error("Failed to create virtual environment")
            return False
        
        # Step 2: Install requirements
        Logger.step(2, total_steps, "Installing dependencies")
        if not self.install_requirements():
            Logger.error("Failed to install requirements")
            return False
        
        # Step 3: Create instance directory
        Logger.step(3, total_steps, "Setting up project structure")
        instance_dir = self.project_dir / "instance"
        instance_dir.mkdir(exist_ok=True)
        Logger.info(f"Instance directory ready: {instance_dir}")
        
        # Step 4: Environment configuration
        Logger.step(4, total_steps, "Configuring environment")
        env_file = self.project_dir / ".env"
        env_example = self.project_dir / ".env.example"
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            Logger.info("Created .env file from template")
        elif not env_file.exists():
            # Create basic .env file
            env_content = """# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/nasa_space_app.db
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            Logger.info("Created basic .env file")
        
        # Step 5: Validation
        Logger.step(5, total_steps, "Validating setup")
        if self.validate_setup():
            Logger.success("Flask application setup completed successfully! 🎉")
            self._show_setup_summary()
            return True
        else:
            Logger.error("Setup validation failed")
            return False
    
    def validate_setup(self):
        """Validate Flask setup"""
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Requirements installed", self.check_dependencies()),
            ("App file exists", self.app_file.exists()),
            ("Instance directory", (self.project_dir / "instance").exists())
        ]
        
        all_good = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_good = False
        
        return all_good
    
    def _show_setup_summary(self):
        """Show setup summary"""
        summary = [
            "🎯 Flask Application Ready!",
            "",
            "Next steps:",
            "  1. Initialize database: python3 manage.py flask init-db",
            "  2. Start development server: python3 manage.py flask run",
            "  3. Open browser: http://localhost:6767",
            "",
            "Available commands:",
            "  • flask run      - Start development server",
            "  • flask init-db  - Initialize database",
            "  • flask migrate  - Run database migrations",
            "  • flask test     - Run application tests"
        ]
        
        box = BoxDrawer.draw_box(summary, title="Setup Complete", width=60)
        print(f"\n{Colors.GREEN}{box}{Colors.ENDC}")
    
    def init_database(self, reset=False):
        """Initialize database with enhanced feedback"""
        Logger.section("Database Operations")
        
        if reset and self.db_file.exists():
            Logger.warning("Removing existing database...")
            self.db_file.unlink()
            Logger.info("Existing database removed")
        
        if not self.init_db_file.exists():
            Logger.error("Database initialization script not found")
            return False
        
        with spinner_context(
            "Initializing database with sample data",
            "Database initialized successfully with NASA sample data",
            "Failed to initialize database"
        ):
            python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
            result = self.run_command(f"{python_path} {self.init_db_file}", capture_output=True)
            
        if result:
            self._show_database_info()
        
        return bool(result)
    
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
    
    def _show_database_info(self):
        """Show database information after initialization"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            info = ["📊 Database Information", ""]
            for table_name in [t[0] for t in tables]:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                info.append(f"  • {table_name}: {count} records")
            
            conn.close()
            
            info.extend([
                "",
                "🔗 Database location:",
                f"  {self.db_file}"
            ])
            
            box = BoxDrawer.draw_box(info, title="Database Ready", width=50)
            print(f"\n{Colors.BLUE}{box}{Colors.ENDC}")
            
        except Exception as e:
            Logger.error(f"Could not read database info: {str(e)}")
    
    def run_server(self, port=None, host=None, debug=None):
        """Run Flask development server with centralized configuration"""
        Logger.section("Starting Flask Development Server")
        
        # Use centralized config with fallbacks
        flask_config = config.get_flask_config()
        port = port or flask_config['port']
        host = host or flask_config['host'] 
        debug = debug if debug is not None else flask_config['debug']
        
        # Pre-flight checks
        if not self._pre_flight_check():
            return False
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_PORT'] = str(port)
        env['FLASK_HOST'] = host
        env['FLASK_DEBUG'] = str(debug).lower()
        
        # Show server info
        server_info = [
            f"🌐 Server URL: http://{host}:{port}",
            f"🔧 Debug mode: {'ON' if debug else 'OFF'}",
            f"📁 Working directory: {self.project_dir}",
            f"⚙️  Configuration: Global .env",
            "",
            "Press Ctrl+C to stop the server",
            "Server logs will appear below:"
        ]
        
        box = BoxDrawer.draw_box(server_info, title="NASA Space App Server", width=60)
        print(f"{Colors.GREEN}{box}{Colors.ENDC}")
        
        Logger.separator()
        
        try:
            # Use signal handler for graceful shutdown
            def signal_handler(sig, frame):
                print(f"\n{Colors.WARNING}🛑 Server shutdown requested{Colors.ENDC}")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # Start server
            subprocess.run([str(python_path), str(self.app_file)], 
                         cwd=self.project_dir, env=env)
        except KeyboardInterrupt:
            Logger.info("Server stopped by user")
        except Exception as e:
            Logger.error(f"Server error: {str(e)}")
        
        return True
    
    def _pre_flight_check(self):
        """Check if everything is ready to run the server"""
        Logger.info("Running pre-flight checks...")
        
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Application file", self.app_file.exists()),
            ("Dependencies", self.check_dependencies()),
            ("Database", self.db_file.exists())
        ]
        
        progress = ProgressBar(len(checks), prefix="Checking")
        
        all_good = True
        for i, (check_name, result) in enumerate(checks):
            progress.update(i + 1, f"- {check_name}")
            time.sleep(0.2)  # Small delay for visual effect
            
            if not result:
                Logger.error(f"❌ {check_name} check failed")
                all_good = False
            else:
                Logger.success(f"✅ {check_name} check passed")
        
        if not all_good:
            Logger.error("Pre-flight checks failed. Please run setup first.")
            return False
        
        Logger.success("All pre-flight checks passed! 🚀")
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
        """Get Flask application status with detailed information"""
        flask_config = config.get_flask_config()
        status = {
            "venv_exists": self.venv_dir.exists(),
            "database_exists": self.db_file.exists(),
            "app_file_exists": self.app_file.exists(),
            "requirements_installed": self.check_dependencies(),
            "port_available": self._check_port_available(flask_config['port'])
        }
        
        if status["database_exists"]:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                status["database_tables"] = [table[0] for table in tables]
                
                # Get record counts
                status["table_counts"] = {}
                for table_name in status["database_tables"]:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    status["table_counts"][table_name] = cursor.fetchone()[0]
                
                conn.close()
            except Exception:
                status["database_tables"] = []
                status["table_counts"] = {}
        
        return status
    
    def _check_port_available(self, port=None):
        """Check if port is available"""
        import socket
        if port is None:
            port = config.get_int('FLASK_APP_PORT', 6767)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False

class TeamFlaskManager(ProjectManager):
    """Team website Flask application management"""
    
    def __init__(self):
        super().__init__(TEAM_FLASK_APP_DIR)
        self.app_file = self.project_dir / "app.py"
        self.index_file = self.project_dir / "index.html"
    
    def setup(self):
        """Setup team Flask application"""
        Logger.section("Setting up Team Website")
        
        total_steps = 4
        
        # Step 1: Create virtual environment
        Logger.step(1, total_steps, "Creating virtual environment")
        if not self.create_venv():
            Logger.error("Failed to create virtual environment")
            return False
        
        # Step 2: Install requirements
        Logger.step(2, total_steps, "Installing dependencies")
        if not self.install_requirements():
            Logger.error("Failed to install requirements")
            return False
        
        # Step 3: Validate files
        Logger.step(3, total_steps, "Validating website files")
        if not self.index_file.exists():
            Logger.error("Website index.html not found")
            return False
        
        if not self.app_file.exists():
            Logger.error("Flask app.py not found")
            return False
        
        # Step 4: Validation
        Logger.step(4, total_steps, "Validating setup")
        if self.validate_setup():
            Logger.success("Team website setup completed successfully! 🎉")
            self._show_setup_summary()
            return True
        else:
            Logger.error("Setup validation failed")
            return False
    
    def validate_setup(self):
        """Validate team website setup"""
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Dependencies installed", self.check_dependencies()),
            ("App file exists", self.app_file.exists()),
            ("Website file exists", self.index_file.exists())
        ]
        
        all_good = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_good = False
        
        return all_good
    
    def _show_setup_summary(self):
        """Show setup summary for team website"""
        summary = [
            "🎯 TerraPulse Team Website Ready!",
            "",
            "Next steps:",
            "  1. Start team website: python3 manage.py team run",
            "  2. Open browser: http://localhost:5000",
            "  3. Share your team story with the world!",
            "",
            "Available commands:",
            "  • team run       - Start team website server",
            "  • team setup     - Setup team website environment"
        ]
        
        box = BoxDrawer.draw_box(summary, title="Team Website Ready", width=60)
        print(f"\n{Colors.GREEN}{box}{Colors.ENDC}")
    
    def run_server(self, port=None, host=None, debug=None):
        """Run team website server with centralized configuration"""
        Logger.section("Starting TerraPulse Team Website")
        
        # Use centralized config with fallbacks
        team_config = config.get_team_website_config()
        port = port or team_config['port']
        host = host or team_config['host']
        debug = debug if debug is not None else team_config['debug']
        
        Logger.section("Starting TerraPulse Team Website")
        
        # Pre-flight checks
        if not self._pre_flight_check():
            return False
        
        python_path = self.venv_dir / ("Scripts/python" if os.name == 'nt' else "bin/python")
        
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_PORT'] = str(port)
        env['FLASK_HOST'] = host
        env['FLASK_DEBUG'] = str(debug).lower()
        
        # Show server info
        server_info = [
            f"🌐 Team Website URL: http://{host}:{port}",
            f"🔧 Debug mode: {'ON' if debug else 'OFF'}",
            f"📁 Working directory: {self.project_dir}",
            "",
            "🚀 TerraPulse Team Website - NASA Space Apps Challenge 2025",
            "",
            "Press Ctrl+C to stop the server",
            "Server logs will appear below:"
        ]
        
        box = BoxDrawer.draw_box(server_info, title="TerraPulse Team Website", width=70)
        print(f"{Colors.GREEN}{box}{Colors.ENDC}")
        
        Logger.separator()
        
        try:
            # Use signal handler for graceful shutdown
            def signal_handler(sig, frame):
                print(f"\n{Colors.WARNING}🛑 Team website shutdown requested{Colors.ENDC}")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # Start server
            subprocess.run([str(python_path), str(self.app_file)], 
                         cwd=self.project_dir, env=env)
        except KeyboardInterrupt:
            Logger.info("Team website stopped by user")
        except Exception as e:
            Logger.error(f"Server error: {str(e)}")
        
        return True
    
    def _pre_flight_check(self):
        """Check if everything is ready to run the team website"""
        Logger.info("Running pre-flight checks...")
        
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Application file", self.app_file.exists()),
            ("Website HTML file", self.index_file.exists()),
            ("Dependencies", self.check_dependencies())
        ]
        
        progress = ProgressBar(len(checks), prefix="Checking")
        
        all_good = True
        for i, (check_name, result) in enumerate(checks):
            progress.update(i + 1, f"- {check_name}")
            time.sleep(0.2)
            
            if not result:
                Logger.error(f"❌ {check_name} check failed")
                all_good = False
            else:
                Logger.success(f"✅ {check_name} check passed")
        
        if not all_good:
            Logger.error("Pre-flight checks failed. Please run setup first.")
            return False
        
        Logger.success("All pre-flight checks passed! 🚀")
        return True
    
    def get_status(self):
        """Get team website status"""
        status = {
            "venv_exists": self.venv_dir.exists(),
            "app_file_exists": self.app_file.exists(),
            "index_file_exists": self.index_file.exists(),
            "requirements_installed": self.check_dependencies(),
            "port_available": self._check_port_available(5000)
        }
        
        return status
    
    def _check_port_available(self, port):
        """Check if port is available"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False

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
    
    def start_jupyter(self, port=None):
        """Start Jupyter notebook server with centralized configuration"""
        Logger.section("Starting Jupyter Notebook")
        
        # Use centralized config with fallback
        jupyter_config = config.get_jupyter_config()
        port = port or jupyter_config['port']
        
        jupyter_path = self.venv_dir / ("Scripts/jupyter" if os.name == 'nt' else "bin/jupyter")
        
        if not jupyter_path.exists():
            Logger.error("Jupyter not found. Install it first.")
            return False
        
        Logger.info(f"Starting Jupyter on port {port}")
        Logger.info("Configuration loaded from global .env")
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

class PM2Manager:
    """PM2 production process management"""
    
    def __init__(self):
        self.project_dir = PROJECT_ROOT
        self.flask_manager = FlaskManager()
        self.team_manager = TeamFlaskManager()
        self.ecosystem_file = self.project_dir / "ecosystem.config.js"
    
    def check_pm2_installed(self):
        """Check if PM2 is installed"""
        try:
            result = subprocess.run(["pm2", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_pm2(self):
        """Install PM2 globally"""
        Logger.section("Installing PM2")
        
        if self.check_pm2_installed():
            Logger.info("PM2 is already installed")
            return True
        
        with spinner_context(
            "Installing PM2 globally with npm",
            "PM2 installed successfully",
            "Failed to install PM2"
        ):
            result = subprocess.run(["npm", "install", "-g", "pm2"], capture_output=True)
            return result.returncode == 0
    
    def generate_ecosystem_config(self):
        """Generate PM2 ecosystem configuration file"""
        Logger.section("Generating PM2 Configuration")
        
        # Get configuration from centralized config
        flask_config = config.get_flask_config()
        team_config = config.get_team_website_config()
        
        ecosystem_config = f"""module.exports = {{
  apps: [
    {{
      name: 'nasa-space-app',
      script: 'app.py',
      cwd: '{FLASK_APP_DIR}',
      interpreter: '{FLASK_APP_DIR}/venv/bin/python',
      instances: 1,
      exec_mode: 'fork',
      env: {{
        NODE_ENV: 'production',
        FLASK_ENV: 'production',
        FLASK_DEBUG: 'false',
        FLASK_PORT: '{flask_config['port']}',
        FLASK_HOST: '{flask_config['host']}'
      }},
      env_staging: {{
        NODE_ENV: 'staging',
        FLASK_ENV: 'staging',
        FLASK_DEBUG: 'true',
        FLASK_PORT: '{flask_config['port']}',
        FLASK_HOST: '{flask_config['host']}'
      }},
      error_file: './logs/nasa-space-app-error.log',
      out_file: './logs/nasa-space-app-out.log',
      log_file: './logs/nasa-space-app-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      min_uptime: '10s',
      max_restarts: 10
    }},
    {{
      name: 'terrapulse-team-website',
      script: 'app.py',
      cwd: '{TEAM_FLASK_APP_DIR}',
      interpreter: '{TEAM_FLASK_APP_DIR}/venv/bin/python',
      instances: 1,
      exec_mode: 'fork',
      env: {{
        NODE_ENV: 'production',
        FLASK_ENV: 'production',
        FLASK_DEBUG: 'false',
        FLASK_PORT: '{team_config['port']}',
        FLASK_HOST: '{team_config['host']}'
      }},
      env_staging: {{
        NODE_ENV: 'staging',
        FLASK_ENV: 'staging',
        FLASK_DEBUG: 'true',
        FLASK_PORT: '{team_config['port']}',
        FLASK_HOST: '{team_config['host']}'
      }},
      error_file: './logs/team-website-error.log',
      out_file: './logs/team-website-out.log',
      log_file: './logs/team-website-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      min_uptime: '10s',
      max_restarts: 10
    }}
  ]
}};"""
        
        with open(self.ecosystem_file, 'w') as f:
            f.write(ecosystem_config)
        
        Logger.success(f"PM2 ecosystem config generated: {self.ecosystem_file}")
        return True
    
    def setup_production_environment(self):
        """Setup production environment for PM2"""
        Logger.section("Setting up Production Environment")
        
        # Create logs directory
        logs_dir = self.project_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        Logger.info(f"Logs directory ready: {logs_dir}")
        
        # Ensure both apps are set up
        Logger.step(1, 4, "Setting up Flask application")
        if not self.flask_manager.validate_setup():
            Logger.error("Flask app setup validation failed")
            return False
        
        Logger.step(2, 4, "Setting up Team website")
        if not self.team_manager.validate_setup():
            Logger.error("Team website setup validation failed")
            return False
        
        # Install PM2 if needed
        Logger.step(3, 4, "Checking PM2 installation")
        if not self.install_pm2():
            Logger.error("Failed to install PM2")
            return False
        
        # Generate ecosystem config
        Logger.step(4, 4, "Generating PM2 configuration")
        if not self.generate_ecosystem_config():
            Logger.error("Failed to generate PM2 configuration")
            return False
        
        Logger.success("Production environment setup complete! 🚀")
        self._show_production_summary()
        return True
    
    def start_applications(self, app='all', env='production'):
        """Start applications with PM2"""
        Logger.section(f"Starting Applications in {env.title()} Mode")
        
        if not self.check_pm2_installed():
            Logger.error("PM2 is not installed. Run 'python3 manage.py pm2 setup' first.")
            return False
        
        if not self.ecosystem_file.exists():
            Logger.error("PM2 ecosystem config not found. Run 'python3 manage.py pm2 setup' first.")
            return False
        
        # Determine which apps to start
        if app == 'all':
            apps_to_start = ['nasa-space-app', 'terrapulse-team-website']
        elif app == 'flask':
            apps_to_start = ['nasa-space-app']
        elif app == 'team':
            apps_to_start = ['terrapulse-team-website']
        
        success = True
        for app_name in apps_to_start:
            Logger.info(f"Starting {app_name}...")
            result = subprocess.run([
                "pm2", "start", str(self.ecosystem_file),
                "--only", app_name,
                "--env", env
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                Logger.success(f"{app_name} started successfully")
            else:
                Logger.error(f"Failed to start {app_name}: {result.stderr}")
                success = False
        
        if success:
            self._show_running_status()
        
        return success
    
    def stop_applications(self, app='all'):
        """Stop PM2 applications"""
        Logger.section("Stopping Applications")
        
        if app == 'all':
            result = subprocess.run(["pm2", "stop", "all"], capture_output=True, text=True)
        elif app == 'flask':
            result = subprocess.run(["pm2", "stop", "nasa-space-app"], capture_output=True, text=True)
        elif app == 'team':
            result = subprocess.run(["pm2", "stop", "terrapulse-team-website"], capture_output=True, text=True)
        
        if result.returncode == 0:
            Logger.success("Applications stopped successfully")
            return True
        else:
            Logger.error(f"Failed to stop applications: {result.stderr}")
            return False
    
    def restart_applications(self, app='all'):
        """Restart PM2 applications (only NASA Space App ones)"""
        Logger.section("Restarting NASA Space App Applications")
        
        # Define our specific applications to avoid restarting others
        if app == 'all':
            apps_to_restart = ['nasa-space-app', 'terrapulse-team-website']
        elif app == 'flask':
            apps_to_restart = ['nasa-space-app']
        elif app == 'team':
            apps_to_restart = ['terrapulse-team-website']
        else:
            apps_to_restart = []
        
        success = True
        
        for app_name in apps_to_restart:
            Logger.info(f"Restarting {app_name}...")
            result = subprocess.run(["pm2", "restart", app_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                Logger.success(f"✅ {app_name} restarted successfully")
            else:
                # Check if the app doesn't exist (which is not an error for restart in some cases)
                if "Process or Namespace" in result.stderr and "not found" in result.stderr:
                    Logger.warning(f"⚠️  {app_name} was not running (cannot restart)")
                    success = False
                else:
                    Logger.error(f"❌ Failed to restart {app_name}: {result.stderr}")
                    success = False
        
        if success:
            Logger.success("🎉 NASA Space App applications restarted successfully")
            Logger.info("✋ Other PM2 applications were left untouched")
            self._show_running_status()
        else:
            Logger.error("Some restarts failed")
        
        return success
    
    def delete_applications(self, app='all'):
        """Delete PM2 applications (only NASA Space App ones)"""
        Logger.section("Deleting NASA Space App Applications")
        
        # Define our specific applications to avoid deleting others
        if app == 'all':
            apps_to_delete = ['nasa-space-app', 'terrapulse-team-website']
        elif app == 'flask':
            apps_to_delete = ['nasa-space-app']
        elif app == 'team':
            apps_to_delete = ['terrapulse-team-website']
        else:
            apps_to_delete = []
        
        success = True
        
        for app_name in apps_to_delete:
            Logger.info(f"Deleting {app_name}...")
            result = subprocess.run(["pm2", "delete", app_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                Logger.success(f"✅ {app_name} deleted successfully")
            else:
                # Check if the app doesn't exist (which is not an error)
                if "Process or Namespace" in result.stderr and "not found" in result.stderr:
                    Logger.info(f"ℹ️  {app_name} was not running (already deleted)")
                else:
                    Logger.error(f"❌ Failed to delete {app_name}: {result.stderr}")
                    success = False
        
        if success:
            Logger.success("🎉 NASA Space App applications deleted successfully")
            Logger.info("✋ Other PM2 applications were left untouched")
        else:
            Logger.error("Some deletions failed")
        
        return success
    
    def show_status(self):
        """Show PM2 application status"""
        Logger.section("PM2 Application Status")
        
        if not self.check_pm2_installed():
            Logger.error("PM2 is not installed")
            return False
        
        result = subprocess.run(["pm2", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            Logger.error(f"Failed to get PM2 status: {result.stderr}")
            return False
    
    def show_logs(self, app='all', lines=50):
        """Show PM2 application logs"""
        Logger.section(f"PM2 Application Logs (last {lines} lines)")
        
        if not self.check_pm2_installed():
            Logger.error("PM2 is not installed")
            return False
        
        if app == 'all':
            cmd = ["pm2", "logs", "--lines", str(lines)]
        elif app == 'flask':
            cmd = ["pm2", "logs", "nasa-space-app", "--lines", str(lines)]
        elif app == 'team':
            cmd = ["pm2", "logs", "terrapulse-team-website", "--lines", str(lines)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            Logger.error(f"Failed to get PM2 logs: {result.stderr}")
            return False
    
    def _show_production_summary(self):
        """Show production setup summary"""
        flask_config = config.get_flask_config()
        team_config = config.get_team_website_config()
        
        summary = [
            "🚀 Production Environment Ready!",
            "",
            "Applications configured:",
            f"  • NASA Space App: http://localhost:{flask_config['port']}",
            f"  • TerraPulse Team Website: http://localhost:{team_config['port']}",
            "",
            "PM2 Commands:",
            "  • Start all: python3 manage.py pm2 start",
            "  • Stop all: python3 manage.py pm2 stop",
            "  • Restart all: python3 manage.py pm2 restart",
            "  • View status: python3 manage.py pm2 status",
            "  • View logs: python3 manage.py pm2 logs",
            "",
            "Individual app control:",
            "  • Start Flask: python3 manage.py pm2 start --app flask",
            "  • Start Team: python3 manage.py pm2 start --app team",
            "",
            "Ready for production deployment! 🌟"
        ]
        
        box = BoxDrawer.draw_box(summary, title="Production Ready", width=65)
        print(f"\n{Colors.GREEN}{box}{Colors.ENDC}")
    
    def _show_running_status(self):
        """Show running applications status"""
        flask_config = config.get_flask_config()
        team_config = config.get_team_website_config()
        
        status_info = [
            "🟢 Applications Running",
            "",
            "Access your applications:",
            f"  🌐 NASA Space App: http://localhost:{flask_config['port']}",
            f"  👥 TerraPulse Team: http://localhost:{team_config['port']}",
            "",
            "Monitor with:",
            "  • pm2 status",
            "  • pm2 logs",
            "  • pm2 monit"
        ]
        
        box = BoxDrawer.draw_box(status_info, title="Applications Running", width=55)
        print(f"\n{Colors.GREEN}{box}{Colors.ENDC}")

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
    """Enhanced project status checker with beautiful output"""
    
    def __init__(self):
        self.flask_manager = FlaskManager()
        self.team_flask_manager = TeamFlaskManager()
        self.ml_manager = MLManager()
        self.dataset_manager = DatasetManager()
        self.git_manager = GitManager()
    
    def check_all(self):
        """Check status of all projects with enhanced display"""
        # Show banner first
        Logger.banner()
        
        Logger.header("Project Status Overview")
        
        # Flask App Status
        self._show_flask_status()
        
        # Team Website Status
        self._show_team_status()
        
        # ML Project Status  
        self._show_ml_status()
        
        # Dataset Status
        self._show_dataset_status()
        
        # Git Status
        self._show_git_status()
        
        # Overall health score
        self._show_health_score()
    
    def _show_flask_status(self):
        """Show Flask application status"""
        Logger.section("Flask Application")
        flask_status = self.flask_manager.get_status()
        
        status_items = [
            ("Virtual Environment", flask_status['venv_exists']),
            ("Dependencies", flask_status['requirements_installed']),
            ("Database", flask_status['database_exists']),
            ("Application File", flask_status['app_file_exists']),
            ("Port 6767 Available", flask_status.get('port_available', True))
        ]
        
        for item, status in status_items:
            icon = "✅" if status else "❌"
            color = Colors.GREEN if status else Colors.FAIL
            print(f"  {color}{icon} {item}{Colors.ENDC}")
        
        # Database details
        if flask_status.get('database_tables'):
            print(f"\n  {Colors.CYAN}📊 Database Tables:{Colors.ENDC}")
            for table in flask_status['database_tables']:
                count = flask_status.get('table_counts', {}).get(table, 0)
                print(f"    • {table}: {count} records")
    
    def _show_team_status(self):
        """Show team website status"""
        Logger.section("Team Website")
        team_status = self.team_flask_manager.get_status()
        
        status_items = [
            ("Virtual Environment", team_status['venv_exists']),
            ("Dependencies", team_status['requirements_installed']),
            ("Flask App File", team_status['app_file_exists']),
            ("Website HTML", team_status['index_file_exists']),
            ("Port 5000 Available", team_status.get('port_available', True))
        ]
        
        for item, status in status_items:
            icon = "✅" if status else "❌"
            color = Colors.GREEN if status else Colors.FAIL
            print(f"  {color}{icon} {item}{Colors.ENDC}")
    
    def _show_ml_status(self):
        """Show ML project status"""
        Logger.section("Machine Learning Project")
        ml_status = self.ml_manager.get_status()
        
        venv_icon = "✅" if ml_status['venv_exists'] else "❌"
        venv_color = Colors.GREEN if ml_status['venv_exists'] else Colors.FAIL
        print(f"  {venv_color}{venv_icon} Virtual Environment{Colors.ENDC}")
        
        # File counts with icons
        items = [
            ("📓 Notebooks", ml_status['notebooks_count']),
            ("🧠 Models", ml_status['models_count']),
            ("📈 Data Files", ml_status['data_files_count'])
        ]
        
        for icon_name, count in items:
            color = Colors.GREEN if count > 0 else Colors.DIM
            print(f"  {color}{icon_name}: {count} files{Colors.ENDC}")
    
    def _show_dataset_status(self):
        """Show dataset status"""
        Logger.section("Dataset Management")
        dataset_status = self.dataset_manager.get_status()
        
        structure_icon = "✅" if dataset_status['structure_valid'] else "❌"
        structure_color = Colors.GREEN if dataset_status['structure_valid'] else Colors.FAIL
        print(f"  {structure_color}{structure_icon} Directory Structure{Colors.ENDC}")
        
        if dataset_status['structure_valid']:
            for category in ['raw', 'processed', 'external']:
                files_key = f"{category}_files"
                size_key = f"{category}_size"
                if files_key in dataset_status:
                    files = dataset_status[files_key]
                    size_mb = dataset_status[size_key] / (1024 * 1024)
                    color = Colors.GREEN if files > 0 else Colors.DIM
                    print(f"  {color}📁 {category.title()}: {files} files ({size_mb:.1f} MB){Colors.ENDC}")
    
    def _show_git_status(self):
        """Show git repository status"""
        Logger.section("Git Repository")
        git_status = self.git_manager.get_status()
        
        repo_icon = "✅" if git_status['is_git_repo'] else "❌"
        repo_color = Colors.GREEN if git_status['is_git_repo'] else Colors.FAIL
        print(f"  {repo_color}{repo_icon} Repository Initialized{Colors.ENDC}")
        
        if git_status['is_git_repo']:
            changes = git_status['files_changed']
            if changes > 0:
                print(f"  {Colors.WARNING}⚠️  {changes} changed files{Colors.ENDC}")
                # Show first few changes
                for change in git_status.get('changes', [])[:3]:
                    print(f"    {Colors.DIM}• {change}{Colors.ENDC}")
                if len(git_status.get('changes', [])) > 3:
                    print(f"    {Colors.DIM}... and {len(git_status['changes']) - 3} more{Colors.ENDC}")
            else:
                print(f"  {Colors.GREEN}✅ Working directory clean{Colors.ENDC}")
    
    def _show_health_score(self):
        """Calculate and show overall project health"""
        flask_status = self.flask_manager.get_status()
        team_status = self.team_flask_manager.get_status()
        ml_status = self.ml_manager.get_status()
        dataset_status = self.dataset_manager.get_status()
        git_status = self.git_manager.get_status()
        
        # Calculate health score
        max_score = 12  # Increased for team website
        score = 0
        
        # Flask checks (4 points)
        if flask_status['venv_exists']: score += 1
        if flask_status['requirements_installed']: score += 1
        if flask_status['database_exists']: score += 1
        if flask_status['app_file_exists']: score += 1
        
        # Team website checks (2 points)
        if team_status['venv_exists']: score += 1
        if team_status['index_file_exists']: score += 1
        
        # ML checks (2 points)
        if ml_status['venv_exists']: score += 1
        if ml_status['notebooks_count'] > 0 or ml_status['models_count'] > 0: score += 1
        
        # Dataset checks (2 points)
        if dataset_status['structure_valid']: score += 1
        if any(dataset_status.get(f"{cat}_files", 0) > 0 for cat in ['raw', 'processed', 'external']): score += 1
        
        # Git checks (2 points)
        if git_status['is_git_repo']: score += 1
        if git_status['files_changed'] == 0: score += 1
        
        # Health percentage
        health_percent = (score / max_score) * 100
        
        # Determine health status
        if health_percent >= 90:
            health_status = "Excellent"
            health_color = Colors.GREEN
            health_icon = "🟢"
        elif health_percent >= 70:
            health_status = "Good"
            health_color = Colors.LIME
            health_icon = "🟡"
        elif health_percent >= 50:
            health_status = "Fair"
            health_color = Colors.WARNING
            health_icon = "🟠"
        else:
            health_status = "Poor"
            health_color = Colors.FAIL
            health_icon = "🔴"
        
        # Show health summary
        health_info = [
            f"{health_icon} Project Health: {health_status}",
            f"Score: {score}/{max_score} ({health_percent:.0f}%)",
            "",
            "Quick Actions:"
        ]
        
        # Add recommendations
        if not flask_status['venv_exists']:
            health_info.append("  • Run: python3 manage.py flask setup")
        if not flask_status['database_exists']:
            health_info.append("  • Run: python3 manage.py flask init-db")
        if not team_status['venv_exists']:
            health_info.append("  • Run: python3 manage.py team setup")
        if git_status['files_changed'] > 0:
            health_info.append("  • Run: python3 manage.py git add && python3 manage.py git commit")
        
        if score == max_score:
            health_info.extend([
                "",
                "🎉 All systems operational!",
                "Ready for NASA space exploration! 🚀"
            ])
        
        box = BoxDrawer.draw_box(health_info, title="Project Health", width=60)
        print(f"\n{health_color}{box}{Colors.ENDC}")
    
    def quick_start_menu(self):
        """Show interactive quick start menu"""
        options = [
            {
                'key': '1',
                'text': 'Check Project Status',
                'desc': 'View detailed status of all components',
                'icon': '🔍'
            },
            {
                'key': '2', 
                'text': 'Setup Everything',
                'desc': 'Complete setup for all project components',
                'icon': '⚙️'
            },
            {
                'key': '3',
                'text': 'Start Flask Server',
                'desc': f'Launch the main application (port {config.get_int("FLASK_APP_PORT", 6767)})',
                'icon': '🌐'
            },
            {
                'key': '4',
                'text': 'Start Team Website',
                'desc': f'Launch the team promotion website (port {config.get_int("TEAM_WEBSITE_PORT", 8080)})',
                'icon': '👥'
            },
            {
                'key': '5',
                'text': 'Initialize Database',
                'desc': 'Setup database with NASA sample data',
                'icon': '🗄️'
            },
            {
                'key': '6',
                'text': 'Start Jupyter Lab',
                'desc': f'Launch ML development environment (port {config.get_int("JUPYTER_PORT", 8888)})',
                'icon': '📓'
            },
            {
                'key': '7',
                'text': 'View Configuration',
                'desc': 'Show current application configuration',
                'icon': '⚙️'
            },
            {
                'key': '8',
                'text': 'Git Operations',
                'desc': 'Manage version control',
                'icon': '📦'
            },
            {
                'key': '9',
                'text': 'PM2 Production',
                'desc': 'Production deployment with PM2',
                'icon': '🚀'
            },
            {
                'key': 'q',
                'text': 'Quit',
                'desc': 'Exit the management system',
                'icon': '🚪'
            }
        ]
        
        menu = InteractiveMenu("NASA Space App Quick Start", options)
        choice = menu.display()
        
        return choice

def main():
    """Enhanced main entry point with interactive features"""
    
    # Handle no arguments - show interactive menu
    if len(sys.argv) == 1:
        status_checker = ProjectStatusChecker()
        
        while True:
            try:
                choice = status_checker.quick_start_menu()
                
                if choice == '1':
                    status_checker.check_all()
                elif choice == '2':
                    # Setup everything
                    Logger.header("Complete Project Setup")
                    flask_manager = FlaskManager()
                    team_flask_manager = TeamFlaskManager()
                    ml_manager = MLManager()
                    dataset_manager = DatasetManager()
                    
                    with spinner_context("Setting up all components", "Setup completed successfully"):
                        flask_manager.setup()
                        team_flask_manager.setup()
                        ml_manager.setup()
                        dataset_manager.validate_structure()
                elif choice == '3':
                    # Start Flask server
                    flask_manager = FlaskManager()
                    flask_manager.run_server()
                elif choice == '4':
                    # Start team website
                    team_flask_manager = TeamFlaskManager()
                    team_flask_manager.run_server()
                elif choice == '5':
                    # Initialize database
                    flask_manager = FlaskManager()
                    flask_manager.init_database()
                elif choice == '6':
                    # Start Jupyter
                    ml_manager = MLManager()
                    ml_manager.start_jupyter()
                elif choice == '7':
                    # View Configuration
                    config.show_config_summary()
                elif choice == '8':
                    # Git operations submenu
                    git_menu = InteractiveMenu("Git Operations", [
                        {'key': '1', 'text': 'Show Status', 'icon': '📊'},
                        {'key': '2', 'text': 'Add All Files', 'icon': '➕'},
                        {'key': '3', 'text': 'Commit Changes', 'icon': '💾'},
                        {'key': 'b', 'text': 'Back to Main Menu', 'icon': '↩️'}
                    ])
                    git_choice = git_menu.display()
                    
                    git_manager = GitManager()
                    if git_choice == '1':
                        subprocess.run(["git", "status"], cwd=PROJECT_ROOT)
                    elif git_choice == '2':
                        git_manager.add_all_files()
                    elif git_choice == '3':
                        message = input(f"{Colors.CYAN}Enter commit message: {Colors.ENDC}")
                        if message.strip():
                            git_manager.commit_changes(message)
                
                elif choice == '9':
                    # PM2 Production submenu
                    pm2_menu = InteractiveMenu("PM2 Production Management", [
                        {'key': '1', 'text': 'Setup Production Environment', 'desc': 'Configure PM2 for production', 'icon': '⚙️'},
                        {'key': '2', 'text': 'Start All Applications', 'desc': 'Start both Flask app and team website', 'icon': '🚀'},
                        {'key': '3', 'text': 'Start Flask App Only', 'desc': 'Start main application only', 'icon': '🌐'},
                        {'key': '4', 'text': 'Start Team Website Only', 'desc': 'Start team website only', 'icon': '👥'},
                        {'key': '5', 'text': 'Stop All Applications', 'desc': 'Stop all running apps', 'icon': '🛑'},
                        {'key': '6', 'text': 'Restart All Applications', 'desc': 'Restart all apps', 'icon': '🔄'},
                        {'key': '7', 'text': 'View PM2 Status', 'desc': 'Show application status', 'icon': '📊'},
                        {'key': '8', 'text': 'View Application Logs', 'desc': 'Show recent logs', 'icon': '📝'},
                        {'key': '9', 'text': 'Delete All Applications', 'desc': 'Remove apps from PM2', 'icon': '🗑️'},
                        {'key': 'b', 'text': 'Back to Main Menu', 'icon': '↩️'}
                    ])
                    pm2_choice = pm2_menu.display()
                    
                    pm2_manager = PM2Manager()
                    if pm2_choice == '1':
                        pm2_manager.setup_production_environment()
                    elif pm2_choice == '2':
                        pm2_manager.start_applications('all', 'production')
                    elif pm2_choice == '3':
                        pm2_manager.start_applications('flask', 'production')
                    elif pm2_choice == '4':
                        pm2_manager.start_applications('team', 'production')
                    elif pm2_choice == '5':
                        pm2_manager.stop_applications('all')
                    elif pm2_choice == '6':
                        pm2_manager.restart_applications('all')
                    elif pm2_choice == '7':
                        pm2_manager.show_status()
                    elif pm2_choice == '8':
                        lines = input(f"{Colors.CYAN}Number of log lines to show (default 50): {Colors.ENDC}") or "50"
                        pm2_manager.show_logs('all', int(lines))
                    elif pm2_choice == '9':
                        confirm = input(f"{Colors.WARNING}Are you sure you want to delete all PM2 apps? (y/N): {Colors.ENDC}")
                        if confirm.lower() == 'y':
                            pm2_manager.delete_applications('all')
                elif choice == 'q' or choice is None:
                    print(f"\n{Colors.GREEN}Thanks for using NASA Space App Manager! 🚀{Colors.ENDC}")
                    break
                else:
                    Logger.warning("Invalid choice. Please try again.")
                
                if choice not in ['q', None]:
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
                break
            except Exception as e:
                Logger.error(f"Unexpected error: {str(e)}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
        
        return
    
    # Original command-line interface
    parser = argparse.ArgumentParser(
        description="NASA Space App Project Management Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 manage.py status                    # Check project status
  python3 manage.py flask run                 # Start Flask server
  python3 manage.py flask init-db --reset     # Reset and initialize database
  python3 manage.py ml jupyter --port 8888    # Start Jupyter on port 8888
  python3 manage.py setup --component flask   # Setup only Flask component
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Complete project setup')
    setup_parser.add_argument('--component', choices=['flask', 'team', 'ml', 'dataset', 'all'], 
                             default='all', help='Component to setup')
    
    # Team commands
    team_parser = subparsers.add_parser('team', help='Team website operations')
    team_subparsers = team_parser.add_subparsers(dest='team_action')
    
    team_setup = team_subparsers.add_parser('setup', help='Setup team website')
    team_run = team_subparsers.add_parser('run', help='Run team website server')
    team_run.add_argument('--port', type=int, default=None, help='Server port (default: from .env config)')
    team_run.add_argument('--host', default=None, help='Server host (default: from .env config)')
    team_run.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    
    # Flask commands
    flask_parser = subparsers.add_parser('flask', help='Flask application operations')
    flask_subparsers = flask_parser.add_subparsers(dest='flask_action')
    
    flask_setup = flask_subparsers.add_parser('setup', help='Setup Flask app')
    flask_init_db = flask_subparsers.add_parser('init-db', help='Initialize database')
    flask_init_db.add_argument('--reset', action='store_true', help='Reset existing database')
    
    flask_migrate = flask_subparsers.add_parser('migrate', help='Run database migration')
    flask_migrate.add_argument('--message', default='Auto migration', help='Migration message')
    
    flask_run = flask_subparsers.add_parser('run', help='Run development server')
    flask_run.add_argument('--port', type=int, default=None, help='Server port (default: from .env config)')
    flask_run.add_argument('--host', default=None, help='Server host (default: from .env config)')
    flask_run.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    
    flask_test = flask_subparsers.add_parser('test', help='Run tests')
    
    # ML commands
    ml_parser = subparsers.add_parser('ml', help='Machine learning operations')
    ml_subparsers = ml_parser.add_subparsers(dest='ml_action')
    
    ml_setup = ml_subparsers.add_parser('setup', help='Setup ML project')
    ml_jupyter = ml_subparsers.add_parser('jupyter', help='Start Jupyter notebook')
    ml_jupyter.add_argument('--port', type=int, default=None, help='Jupyter port (default: from .env config)')
    
    ml_train = ml_subparsers.add_parser('train', help='Run training script')
    ml_train.add_argument('script', help='Training script name')
    
    # Dataset commands
    dataset_parser = subparsers.add_parser('dataset', help='Dataset operations')
    dataset_subparsers = dataset_parser.add_subparsers(dest='dataset_action')
    
    dataset_validate = dataset_subparsers.add_parser('validate', help='Validate structure')
    dataset_catalog = dataset_subparsers.add_parser('catalog', help='Generate catalog')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check project status')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_show = config_subparsers.add_parser('show', help='Show configuration')
    config_set = config_subparsers.add_parser('set', help='Set configuration value')
    config_set.add_argument('key', help='Configuration key')
    config_set.add_argument('value', help='Configuration value')
    
    # PM2 production commands
    pm2_parser = subparsers.add_parser('pm2', help='PM2 production management')
    pm2_subparsers = pm2_parser.add_subparsers(dest='pm2_action')
    
    pm2_start = pm2_subparsers.add_parser('start', help='Start applications with PM2')
    pm2_start.add_argument('--app', choices=['flask', 'team', 'all'], default='all', help='Application to start')
    pm2_start.add_argument('--env', choices=['production', 'staging'], default='production', help='Environment')
    
    pm2_stop = pm2_subparsers.add_parser('stop', help='Stop PM2 applications')
    pm2_stop.add_argument('--app', choices=['flask', 'team', 'all'], default='all', help='Application to stop')
    
    pm2_restart = pm2_subparsers.add_parser('restart', help='Restart PM2 applications')
    pm2_restart.add_argument('--app', choices=['flask', 'team', 'all'], default='all', help='Application to restart')
    
    pm2_status = pm2_subparsers.add_parser('status', help='Show PM2 application status')
    pm2_logs = pm2_subparsers.add_parser('logs', help='Show PM2 application logs')
    pm2_logs.add_argument('--app', choices=['flask', 'team', 'all'], default='all', help='Application logs to show')
    pm2_logs.add_argument('--lines', type=int, default=50, help='Number of lines to show')
    
    pm2_setup = pm2_subparsers.add_parser('setup', help='Setup PM2 configuration')
    pm2_delete = pm2_subparsers.add_parser('delete', help='Delete PM2 applications')
    pm2_delete.add_argument('--app', choices=['flask', 'team', 'all'], default='all', help='Application to delete')
    
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
    clean_parser.add_argument('--component', choices=['flask', 'team', 'ml', 'all'], 
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
        
        components = {
            'flask': ('Flask Application', FlaskManager()),
            'team': ('Team Website', TeamFlaskManager()),
            'ml': ('Machine Learning Project', MLManager()),
            'dataset': ('Dataset Management', DatasetManager())
        }
        
        if args.component == 'all':
            total_components = len(components)
            Logger.info(f"Setting up {total_components} components...")
            
            for i, (comp_name, (comp_title, manager)) in enumerate(components.items(), 1):
                Logger.step(i, total_components, f"Setting up {comp_title}")
                
                if comp_name == 'dataset':
                    success = manager.validate_structure()
                else:
                    success = manager.setup()
                
                if not success:
                    Logger.error(f"Failed to setup {comp_title}")
                    return
            
            Logger.success("🎉 All components setup successfully!")
            
            # Show next steps
            next_steps = [
                "🎯 Setup Complete! Next Steps:",
                "",
                "1. Initialize database:",
                "   python3 manage.py flask init-db",
                "",
                "2. Start main application:",
                "   python3 manage.py flask run",
                "",
                "3. Start team website:",
                "   python3 manage.py team run",
                "",
                "4. Open browsers:",
                "   Main App: http://localhost:6767",
                "   Team Site: http://localhost:5000",
                "",
                "5. Start Jupyter for ML work:",
                "   python3 manage.py ml jupyter"
            ]
            
            box = BoxDrawer.draw_box(next_steps, title="Ready to Launch", width=70)
            print(f"\n{Colors.GREEN}{box}{Colors.ENDC}")
        
        else:
            if args.component in components:
                comp_title, manager = components[args.component]
                Logger.info(f"Setting up {comp_title}...")
                
                if args.component == 'dataset':
                    success = manager.validate_structure()
                else:
                    success = manager.setup()
                
                if success:
                    Logger.success(f"✅ {comp_title} setup complete!")
                else:
                    Logger.error(f"❌ {comp_title} setup failed!")
            else:
                Logger.error(f"Unknown component: {args.component}")
    
    elif args.command == 'team':
        team_flask_manager = TeamFlaskManager()
        
        if args.team_action == 'setup':
            team_flask_manager.setup()
        elif args.team_action == 'run':
            team_flask_manager.run_server(port=args.port, host=args.host, 
                                        debug=not args.no_debug)
        else:
            team_parser.print_help()
    
    elif args.command == 'flask':
        flask_manager = FlaskManager()
        
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
        ml_manager = MLManager()
        
        if args.ml_action == 'setup':
            ml_manager.setup()
        elif args.ml_action == 'jupyter':
            ml_manager.start_jupyter(port=args.port)
        elif args.ml_action == 'train':
            ml_manager.run_training(args.script)
        else:
            ml_parser.print_help()
    
    elif args.command == 'dataset':
        dataset_manager = DatasetManager()
        
        if args.dataset_action == 'validate':
            dataset_manager.validate_structure()
        elif args.dataset_action == 'catalog':
            dataset_manager.generate_catalog()
        else:
            dataset_parser.print_help()
    
    elif args.command == 'status':
        status_checker = ProjectStatusChecker()
        status_checker.check_all()
    
    elif args.command == 'config':
        if args.config_action == 'show':
            config.show_config_summary()
        elif args.config_action == 'set':
            config.update(args.key, args.value)
            config.save_config()
            Logger.success(f"Configuration updated: {args.key} = {args.value}")
        else:
            config_parser.print_help()
    
    elif args.command == 'pm2':
        pm2_manager = PM2Manager()
        
        if args.pm2_action == 'setup':
            pm2_manager.setup_production_environment()
        elif args.pm2_action == 'start':
            pm2_manager.start_applications(args.app, args.env)
        elif args.pm2_action == 'stop':
            pm2_manager.stop_applications(args.app)
        elif args.pm2_action == 'restart':
            pm2_manager.restart_applications(args.app)
        elif args.pm2_action == 'delete':
            pm2_manager.delete_applications(args.app)
        elif args.pm2_action == 'status':
            pm2_manager.show_status()
        elif args.pm2_action == 'logs':
            pm2_manager.show_logs(args.app, args.lines)
        else:
            pm2_parser.print_help()
    
    elif args.command == 'clean':
        Logger.header("Project Cleanup")
        
        if not args.force:
            warning_msg = [
                "⚠️  WARNING: This will remove virtual environments",
                "and temporary files. This action cannot be undone.",
                "",
                "Components to clean:",
                f"  • Flask virtual environment" if args.component in ['flask', 'all'] else "",
                f"  • Team website virtual environment" if args.component in ['team', 'all'] else "",
                f"  • ML virtual environment" if args.component in ['ml', 'all'] else "",
                "",
                "Continue? (y/N)"
            ]
            
            warning_msg = [msg for msg in warning_msg if msg]  # Remove empty strings
            
            box = BoxDrawer.draw_box(warning_msg, title="Cleanup Confirmation", width=60)
            print(f"{Colors.WARNING}{box}{Colors.ENDC}")
            
            response = input(f"{Colors.WARNING}Enter your choice: {Colors.ENDC}")
            if response.lower() != 'y':
                Logger.info("Cleanup cancelled")
                return
        
        components_cleaned = []
        
        if args.component in ['flask', 'all']:
            flask_manager = FlaskManager()
            venv_path = flask_manager.venv_dir
            if venv_path.exists():
                with spinner_context("Removing Flask virtual environment"):
                    shutil.rmtree(venv_path)
                components_cleaned.append("Flask")
        
        if args.component in ['team', 'all']:
            team_flask_manager = TeamFlaskManager()
            venv_path = team_flask_manager.venv_dir
            if venv_path.exists():
                with spinner_context("Removing Team website virtual environment"):
                    shutil.rmtree(venv_path)
                components_cleaned.append("Team Website")
        
        if args.component in ['ml', 'all']:
            ml_manager = MLManager()
            venv_path = ml_manager.venv_dir
            if venv_path.exists():
                with spinner_context("Removing ML virtual environment"):
                    shutil.rmtree(venv_path)
                components_cleaned.append("ML")
        
        if components_cleaned:
            Logger.success(f"🧹 Cleaned up: {', '.join(components_cleaned)} components")
        else:
            Logger.info("Nothing to clean")
    
    elif args.command == 'git':
        git_manager = GitManager()
        
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
        print(f"\n{Colors.WARNING}🛑 Operation cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        Logger.error(f"💥 Unexpected error: {str(e)}")
        
        # Show error details in debug mode
        if '--debug' in sys.argv or os.getenv('DEBUG'):
            import traceback
            print(f"\n{Colors.DIM}Debug traceback:{Colors.ENDC}")
            traceback.print_exc()
        
        print(f"\n{Colors.FAIL}If this error persists, please check:{Colors.ENDC}")
        print(f"  • Your Python environment is properly configured")
        print(f"  • All required dependencies are installed")
        print(f"  • You have sufficient permissions")
        print(f"  • Run with --debug for more details")
        
        sys.exit(1)