import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'researchnest.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-123'
app.config['DEBUG'] = True

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# File handler for logging
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)

# Console handler for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Set Werkzeug logger level
logging.getLogger('werkzeug').setLevel(logging.INFO)

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
migrate = Migrate(app, db)

# Configure logging for SocketIO
socketio_log = logging.getLogger('socketio')
socketio_log.setLevel(logging.ERROR)
engineio_log = logging.getLogger('engineio')
engineio_log.setLevel(logging.ERROR)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def initialize_database():
    """Initialize database with fresh schema and sample data."""
    from models import Department, User, Subject, Unit, Topic
    
    # Create all tables
    db.create_all()
    logging.info("Database tables created")
    
    # Check if already initialized
    if Department.query.count() > 0:
        logging.info("Database already initialized")
        return
    
    # Initialize default departments
    departments_data = [
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
    
    departments = {}
    for dept_name in departments_data:
        dept = Department(name=dept_name)
        db.session.add(dept)
        departments[dept_name] = dept
    
    db.session.flush()  # Get department IDs
    
    # Initialize sample subjects for Computer Science
    cs_dept = departments['Computer Science']
    subjects_data = [
        {'name': 'Data Structures and Algorithms', 'code': 'CS201', 'dept': cs_dept},
        {'name': 'Database Management Systems', 'code': 'CS301', 'dept': cs_dept},
        {'name': 'Operating Systems', 'code': 'CS302', 'dept': cs_dept},
        {'name': 'Computer Networks', 'code': 'CS401', 'dept': cs_dept},
    ]
    
    # Initialize sample subjects for Mathematics
    math_dept = departments['Mathematics']
    subjects_data.extend([
        {'name': 'Calculus I', 'code': 'MATH101', 'dept': math_dept},
        {'name': 'Linear Algebra', 'code': 'MATH201', 'dept': math_dept},
        {'name': 'Statistics', 'code': 'MATH301', 'dept': math_dept},
    ])
    
    subjects = {}
    for subj_data in subjects_data:
        subject = Subject(
            name=subj_data['name'],
            code=subj_data['code'],
            department_id=subj_data['dept'].id
        )
        db.session.add(subject)
        subjects[subj_data['code']] = subject
    
    db.session.flush()  # Get subject IDs
    
    # Initialize sample units and topics for CS201 (Data Structures)
    dsa_subject = subjects['CS201']
    units_data = [
        {
            'name': 'Arrays and Linked Lists',
            'description': 'Basic data structures for storing collections of data',
            'topics': [
                {'name': 'Array Operations', 'difficulty': 'easy'},
                {'name': 'Singly Linked Lists', 'difficulty': 'medium'},
                {'name': 'Doubly Linked Lists', 'difficulty': 'medium'},
                {'name': 'Circular Linked Lists', 'difficulty': 'hard'}
            ]
        },
        {
            'name': 'Stacks and Queues',
            'description': 'Linear data structures with specific access patterns',
            'topics': [
                {'name': 'Stack Implementation', 'difficulty': 'easy'},
                {'name': 'Queue Implementation', 'difficulty': 'easy'},
                {'name': 'Priority Queues', 'difficulty': 'medium'},
                {'name': 'Deque Operations', 'difficulty': 'medium'}
            ]
        },
        {
            'name': 'Trees and Graphs',
            'description': 'Hierarchical and network data structures',
            'topics': [
                {'name': 'Binary Trees', 'difficulty': 'medium'},
                {'name': 'Binary Search Trees', 'difficulty': 'medium'},
                {'name': 'Graph Traversal', 'difficulty': 'hard'},
                {'name': 'Shortest Path Algorithms', 'difficulty': 'hard'}
            ]
        }
    ]
    
    for idx, unit_data in enumerate(units_data):
        unit = Unit(
            name=unit_data['name'],
            description=unit_data['description'],
            subject_id=dsa_subject.id,
            order_index=idx + 1
        )
        db.session.add(unit)
        db.session.flush()  # Get unit ID
        
        for topic_data in unit_data['topics']:
            topic = Topic(
                name=topic_data['name'],
                unit_id=unit.id,
                difficulty_level=topic_data['difficulty']
            )
            db.session.add(topic)
    
    # Initialize sample units for DBMS (CS301)
    dbms_subject = subjects['CS301']
    dbms_units = [
        {
            'name': 'Relational Model',
            'description': 'Foundation of relational databases',
            'topics': [
                {'name': 'Tables and Relations', 'difficulty': 'easy'},
                {'name': 'Primary and Foreign Keys', 'difficulty': 'medium'},
                {'name': 'Normalization', 'difficulty': 'hard'}
            ]
        },
        {
            'name': 'SQL Queries',
            'description': 'Structured Query Language for database operations',
            'topics': [
                {'name': 'SELECT Statements', 'difficulty': 'easy'},
                {'name': 'JOIN Operations', 'difficulty': 'medium'},
                {'name': 'Subqueries', 'difficulty': 'hard'}
            ]
        }
    ]
    
    for idx, unit_data in enumerate(dbms_units):
        unit = Unit(
            name=unit_data['name'],
            description=unit_data['description'],
            subject_id=dbms_subject.id,
            order_index=idx + 1
        )
        db.session.add(unit)
        db.session.flush()
        
        for topic_data in unit_data['topics']:
            topic = Topic(
                name=topic_data['name'],
                unit_id=unit.id,
                difficulty_level=topic_data['difficulty']
            )
            db.session.add(topic)
    
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
        logging.info("Sample subjects, units, and topics created")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database initialization failed: {e}")

# Add custom Jinja2 filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert a JSON string to a Python object."""
    import json
    if not value:
        return []
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []

# Import routes after app initialization
from routes import *  # noqa: E402, F403
from auth import *  # noqa: E402, F403

with app.app_context():
    initialize_database()