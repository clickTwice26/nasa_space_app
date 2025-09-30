#!/usr/bin/env python3
"""
NASA Space App - Configuration Manager
======================================

Centralized configuration management for all applications.
Loads settings from the global .env file and provides easy access.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self, env_file: Optional[Path] = None):
        self.env_file = env_file or Path(__file__).parent / ".env"
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from .env file"""
        if not self.env_file.exists():
            return
        
        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Convert boolean strings
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    
                    # Convert numeric strings
                    elif value.isdigit():
                        value = int(value)
                    
                    self.config[key] = value
                    # Also set as environment variable
                    os.environ[key] = str(value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self.get(key, default)
        return int(value) if value is not None else default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value) if value is not None else default
    
    def get_list(self, key: str, separator: str = ',', default: list = None) -> list:
        """Get list configuration value"""
        value = self.get(key, '')
        if not value:
            return default or []
        return [item.strip() for item in str(value).split(separator)]
    
    def update(self, key: str, value: Any):
        """Update configuration value"""
        self.config[key] = value
        os.environ[key] = str(value)
    
    def save_config(self):
        """Save current configuration back to .env file"""
        lines = []
        
        # Read existing file to preserve comments and order
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line_strip = line.strip()
                    if line_strip and not line_strip.startswith('#') and '=' in line_strip:
                        key = line_strip.split('=', 1)[0].strip()
                        if key in self.config:
                            # Update with new value
                            value = self.config[key]
                            if isinstance(value, str) and (' ' in value or not value):
                                lines.append(f"{key}={value}\n")
                            else:
                                lines.append(f"{key}={value}\n")
                        else:
                            lines.append(line)
                    else:
                        lines.append(line)
        
        # Add new keys that weren't in the original file
        existing_keys = set()
        for line in lines:
            line_strip = line.strip()
            if line_strip and not line_strip.startswith('#') and '=' in line_strip:
                key = line_strip.split('=', 1)[0].strip()
                existing_keys.add(key)
        
        for key, value in self.config.items():
            if key not in existing_keys:
                if isinstance(value, str) and (' ' in value or not value):
                    lines.append(f"{key}={value}\n")
                else:
                    lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(self.env_file, 'w') as f:
            f.writelines(lines)
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask-specific configuration"""
        return {
            'port': self.get_int('FLASK_APP_PORT', 6767),
            'host': self.get('FLASK_APP_HOST', '0.0.0.0'),
            'debug': self.get_bool('FLASK_DEBUG', True),
            'secret_key': self.get('SECRET_KEY', 'dev-secret-key'),
            'database_url': self.get('DATABASE_URL', 'sqlite:///instance/nasa_space_app.db')
        }
    
    def get_team_website_config(self) -> Dict[str, Any]:
        """Get team website configuration"""
        return {
            'port': self.get_int('TEAM_WEBSITE_PORT', 8080),
            'host': self.get('TEAM_WEBSITE_HOST', '0.0.0.0'),
            'debug': self.get_bool('FLASK_DEBUG', True),
            'title': self.get('TEAM_WEBSITE_TITLE', 'TerraPulse'),
            'tagline': self.get('TEAM_WEBSITE_TAGLINE', 'NASA Space Apps Challenge')
        }
    
    def get_jupyter_config(self) -> Dict[str, Any]:
        """Get Jupyter configuration"""
        return {
            'port': self.get_int('JUPYTER_PORT', 8888),
            'host': self.get('JUPYTER_HOST', 'localhost')
        }
    
    def get_nginx_config(self) -> Dict[str, Any]:
        """Get Nginx configuration"""
        return {
            'proxy_port': self.get_int('NGINX_PROXY_PORT', 80),
            'flask_port': self.get_int('FLASK_APP_PORT', 6767),
            'team_port': self.get_int('TEAM_WEBSITE_PORT', 8080)
        }
    
    def show_config_summary(self):
        """Display configuration summary"""
        from manage import Colors, BoxDrawer, Logger
        
        config_info = [
            "🔧 Application Configuration",
            "",
            f"Main Flask App:     http://localhost:{self.get_int('FLASK_APP_PORT', 6767)}",
            f"Team Website:       http://localhost:{self.get_int('TEAM_WEBSITE_PORT', 8080)}",
            f"Jupyter Lab:        http://localhost:{self.get_int('JUPYTER_PORT', 8888)}",
            f"Nginx Proxy:        http://localhost:{self.get_int('NGINX_PROXY_PORT', 80)}",
            "",
            f"Environment:        {self.get('FLASK_ENV', 'development')}",
            f"Debug Mode:         {self.get_bool('FLASK_DEBUG', True)}",
            f"Team:               {self.get('TEAM_NAME', 'TerraPulse')}",
            f"Challenge:          {self.get('CHALLENGE_NAME', 'NASA Space Apps')} {self.get('CHALLENGE_YEAR', '2025')}"
        ]
        
        box = BoxDrawer.draw_box(config_info, title="Configuration Overview", width=70)
        print(f"{Colors.CYAN}{box}{Colors.ENDC}")

# Global configuration instance
config = ConfigManager()

if __name__ == "__main__":
    config.show_config_summary()