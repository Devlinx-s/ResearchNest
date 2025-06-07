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

with app.app_context():
    # Import models here so their tables are created
    from models import Department, User
    db.create_all()
    logging.info("Database tables created")
    
    # Initialize default departments if none exist
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
    
    # Create demo admin user for local development
    demo_user = User.query.filter_by(email='admin@researchnest.local').first()
    if not demo_user:
        demo_user = User(
            id='admin-demo',
            email='admin@researchnest.local',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        db.session.merge(demo_user)
        db.session.commit()
        logging.info("Demo admin user created: admin@researchnest.local")