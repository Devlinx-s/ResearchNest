import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Configure database - use SQLite by default
database_url = os.environ.get("DATABASE_URL", "sqlite:///researchnest.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB
app.config['UPLOAD_FOLDER'] = 'uploads/papers'

# Initialize the app with the extension
db.init_app(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def initialize_database():
    """Initialize database with fresh schema and sample data."""
    from models import Department, User
    
    # Create all tables
    db.create_all()
    logging.info("Database tables created")
    
    # Check if already initialized
    if Department.query.count() > 0:
        logging.info("Database already initialized")
        return
    
    # Initialize default departments
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
    
    # Create demo admin user
    demo_user = User(
        email='admin@researchnest.local',
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    demo_user.set_password('admin123')
    db.session.add(demo_user)
    
    try:
        db.session.commit()
        logging.info("Database initialized successfully")
        logging.info("Demo admin: admin@researchnest.local / password: admin123")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database initialization failed: {e}")

with app.app_context():
    initialize_database()