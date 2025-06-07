from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    
    # Additional fields for research system
    department = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    papers = db.relationship('ResearchPaper', backref='uploader', lazy=True)
    downloads = db.relationship('DownloadLog', backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    papers = db.relationship('ResearchPaper', backref='dept', lazy=True)

class ResearchPaper(db.Model):
    __tablename__ = 'research_papers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.Text, nullable=False)  # Comma-separated or JSON
    abstract = db.Column(db.Text)
    keywords = db.Column(db.Text)  # Comma-separated tags
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    
    # Metadata
    publication_year = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Status and tracking
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    download_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign keys
    uploader_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    downloads = db.relationship('DownloadLog', backref='paper', lazy=True)

class DownloadLog(db.Model):
    __tablename__ = 'download_logs'
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('research_papers.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    downloaded_at = db.Column(db.DateTime, default=datetime.now)

class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    frequency = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
