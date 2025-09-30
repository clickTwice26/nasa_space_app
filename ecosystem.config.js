module.exports = {
  apps: [
    {
      name: 'nasa-space-app',
      script: 'app.py',
      cwd: '/home/raju/nasa_space_app/flask-app',
      interpreter: '/home/raju/nasa_space_app/flask-app/venv/bin/python',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        FLASK_ENV: 'production',
        FLASK_DEBUG: 'false',
        FLASK_PORT: '8080',
        FLASK_HOST: '0.0.0.0'
      },
      env_staging: {
        NODE_ENV: 'staging',
        FLASK_ENV: 'staging',
        FLASK_DEBUG: 'true',
        FLASK_PORT: '8080',
        FLASK_HOST: '0.0.0.0'
      },
      error_file: './logs/nasa-space-app-error.log',
      out_file: './logs/nasa-space-app-out.log',
      log_file: './logs/nasa-space-app-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      min_uptime: '10s',
      max_restarts: 10
    },
    {
      name: 'terrapulse-team-website',
      script: 'app.py',
      cwd: '/home/raju/nasa_space_app/team-flask-app',
      interpreter: '/home/raju/nasa_space_app/team-flask-app/venv/bin/python',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        FLASK_ENV: 'production',
        FLASK_DEBUG: 'false',
        FLASK_PORT: '6767',
        FLASK_HOST: '0.0.0.0'
      },
      env_staging: {
        NODE_ENV: 'staging',
        FLASK_ENV: 'staging',
        FLASK_DEBUG: 'true',
        FLASK_PORT: '6767',
        FLASK_HOST: '0.0.0.0'
      },
      error_file: './logs/team-website-error.log',
      out_file: './logs/team-website-out.log',
      log_file: './logs/team-website-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      min_uptime: '10s',
      max_restarts: 10
    }
  ]
};