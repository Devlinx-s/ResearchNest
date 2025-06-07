# ResearchNest - Academic Question Bank & Paper Generation System

A comprehensive Flask-based platform for educational institutions to manage question banks, generate custom question papers, and organize academic content by subjects, units, and topics.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### 1. Clone the Repository
```bash
git clone https://github.com/Devlinx-s/ResearchNest.git
cd ResearchNest
```

### 2. Set Up Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following content:
```
# Database Configuration
DATABASE_URI=sqlite:///researchnest.db

# Flask Configuration
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=20971520  # 20MB
```

### 5. Initialize the Database
```bash
# Create database tables
python -c "from app import app, db; with app.app_context(): db.create_all()"
```

### 6. Run the Application
```bash
python main.py
```

### 7. Access the System
- Open your browser and go to: `http://localhost:5000`
- **Admin login:** `admin@researchnest.local` (password: admin123)
- **Student login:** Any email (auto-creates account on first login)

## ✨ Core Features

### Question Bank Management
- **Document Upload**: Upload question papers, assignments, and quizzes
- **Automatic Question Extraction**: Extract questions from PDFs with metadata
- **Question Categorization**: Organize by subject, unit, and topic
- **Difficulty Level**: Tag questions by difficulty (easy, medium, hard)

### Paper Generation
- **Custom Paper Creation**: Generate question papers based on criteria
- **Smart Distribution**: Control difficulty levels and mark distribution
- **Multiple Question Types**: Support for text, image, and formula-based questions
- **Export Options**: Download generated papers in various formats

### Academic Organization
- **Subject Hierarchy**: Structured by departments → subjects → units → topics
- **Search & Filter**: Find questions by multiple criteria
- **User Management**: Role-based access control (Admin/Instructor/Student)
- **Analytics**: Track question usage and paper generation history

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Flask 3.1, SQLAlchemy
- **Database**: SQLite (default) or PostgreSQL
- **PDF Processing**: PyMuPDF (fitz), OpenCV for image processing
- **NLP**: NLTK for text processing and analysis
- **Frontend**: Bootstrap 5, Chart.js, Feather Icons
- **AI/ML**: scikit-learn for text similarity and classification

## 📂 Project Structure

```
ResearchNest/
├── app.py                   # Flask application setup
├── auth.py                  # Authentication and authorization
├── models.py                # Database models (User, Subject, Unit, Topic, Question, etc.)
├── question_processor.py    # Core question extraction and paper generation logic
├── routes.py                # Application routes and views
├── forms.py                 # Form definitions using Flask-WTF
├── utils.py                 # Helper functions and utilities
├── requirements.txt         # Python dependencies
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
└── templates/              # Jinja2 templates
    ├── admin/              # Admin interface templates
    ├── questions/          # Question management templates
    └── ...
```

## 🔧 System Requirements

- Python 3.11 or higher
- SQLite (included) or PostgreSQL
- 1GB RAM minimum, 2GB+ recommended
- 100MB free disk space (plus space for uploaded files)

## 🔒 Security Features

- Secure password hashing with Werkzeug
- CSRF protection
- File type validation
- Role-based access control
- Session management
- Input sanitization

## 📚 Documentation

### For Administrators
- Manage departments, subjects, and courses
- Set up academic structures
- Monitor system usage
- Generate reports

### For Instructors
- Upload and organize question banks
- Create custom question papers
- Track question usage and difficulty
- Manage class materials

### For Students
- Access question banks
- Practice with past papers
- Download study materials
- Track progress

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for educational institutions
- Special thanks to all contributors
- Inspired by the need for better academic resource management