# Flask configuration
import os
from datetime import timedelta

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'instance', 'researchnest.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# File uploads
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'

# Session lifetime
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Debug mode
DEBUG = True

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'

# Email configuration
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@researchnest.local')

# Admin email
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@researchnest.local')
