import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)

# Configuration for local development
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# For local development, you might not need ProxyFix
if os.environ.get("FLASK_ENV") != "development":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - fallback to SQLite for local development
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Use SQLite for local development if PostgreSQL not available
    database_url = "sqlite:///researchnest.db"
    logging.info("Using SQLite database for local development")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 20 * 1024 * 1024))  # 20MB
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads/papers')

# Initialize the app with the extension
db.init_app(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    # Import models here so their tables are created
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")
    
    # Initialize default departments if none exist
    from models import Department
    if Department.query.count() == 0:
        departments = [
            'Computer Science',
            'Mathematics',
            'Physics',
            'Chemistry',
            'Biology',
            'Engineering',
            'Business Administration',
            'Psychology',
            'Education',
            'Literature'
        ]
        
        for dept_name in departments:
            dept = Department(name=dept_name)
            db.session.add(dept)
        
        db.session.commit()
        logging.info("Default departments created")