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
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    downloads = db.relationship('DownloadLog', backref='paper', lazy=True)

class DownloadLog(db.Model):
    __tablename__ = 'download_logs'
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('research_papers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    downloaded_at = db.Column(db.DateTime, default=datetime.now)

class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    frequency = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    units = db.relationship('Unit', backref='subject', lazy=True, cascade='all, delete-orphan')
    question_documents = db.relationship('QuestionDocument', backref='subject', lazy=True)

class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    order_index = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    topics = db.relationship('Topic', backref='unit', lazy=True, cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='unit', lazy=True)

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)
    difficulty_level = db.Column(db.String(20), default='medium')  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    questions = db.relationship('Question', backref='topic', lazy=True)

class QuestionDocument(db.Model):
    __tablename__ = 'question_documents'
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_EXTRACTING = 'extracting'
    STATUS_SAVING = 'saving'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    document_type = db.Column(db.String(50), default='question_paper')
    academic_year = db.Column(db.String(20))
    semester = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    extraction_status = db.Column(db.String(20), default=STATUS_PENDING)
    extraction_progress = db.Column(db.Integer, default=0)  # 0-100
    extraction_message = db.Column(db.String(255), nullable=True)
    total_questions = db.Column(db.Integer, default=0)
    total_pages = db.Column(db.Integer, default=0)
    processed_pages = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    extraction_started_at = db.Column(db.DateTime, nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    questions = db.relationship('Question', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def update_status(self, status, message=None, progress=None):
        """Update the extraction status and log the change."""
        self.extraction_status = status
        if message:
            self.extraction_message = message
        if progress is not None:
            self.extraction_progress = progress
        
        # Update timestamps for status changes
        if status == self.STATUS_PROCESSING and not self.extraction_started_at:
            self.extraction_started_at = datetime.now()
        elif status in [self.STATUS_COMPLETED, self.STATUS_FAILED]:
            self.processed_at = datetime.now()
        
        db.session.commit()
    
    def get_status_info(self):
        """Get the current status information as a dictionary."""
        return {
            'status': self.extraction_status,
            'progress': self.extraction_progress,
            'message': self.extraction_message or self.extraction_status.capitalize(),
            'total_questions': self.total_questions,
            'total_pages': self.total_pages,
            'processed_pages': self.processed_pages,
            'is_complete': self.extraction_status == self.STATUS_COMPLETED,
            'is_failed': self.extraction_status == self.STATUS_FAILED,
            'started_at': self.extraction_started_at.isoformat() if self.extraction_started_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __repr__(self):
        return f'<QuestionDocument {self.title} ({self.extraction_status})>'

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='text')  # text, image, formula, mixed
    difficulty_level = db.Column(db.String(20), default='medium')  # easy, medium, hard
    marks = db.Column(db.Integer, default=1)
    
    # Question content
    has_image = db.Column(db.Boolean, default=False)
    has_formula = db.Column(db.Boolean, default=False)
    image_paths = db.Column(db.Text)  # JSON array of image file paths
    
    # Categorization
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    document_id = db.Column(db.Integer, db.ForeignKey('question_documents.id'), nullable=False)
    
    # Position in document
    page_number = db.Column(db.Integer)
    question_number = db.Column(db.String(10))
    
    # Auto-categorization confidence
    topic_confidence = db.Column(db.Float, default=0.0)
    unit_confidence = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.now)

class GeneratedQuestionPaper(db.Model):
    __tablename__ = 'generated_question_papers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Generation parameters
    unit_ids = db.Column(db.Text)  # JSON array of unit IDs
    topic_ids = db.Column(db.Text)  # JSON array of topic IDs
    total_marks = db.Column(db.Integer, default=100)
    duration_minutes = db.Column(db.Integer, default=180)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # Metadata
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.now)
    download_count = db.Column(db.Integer, default=0)
    
    # Relationships
    generator = db.relationship('User', backref='generated_papers', lazy=True)
    subject = db.relationship('Subject', backref='generated_papers', lazy=True)
