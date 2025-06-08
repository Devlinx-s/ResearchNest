# ResearchNest - Academic Question Bank & Paper Generation System

A comprehensive Flask-based platform for educational institutions to manage question banks, generate custom question papers, and organize academic content by subjects, units, and topics.

![ResearchNest Banner](https://via.placeholder.com/1200x400/3498db/ffffff?text=ResearchNest+Platform)

## ✨ Key Features

### 📚 Question Bank Management
- **Document Processing**: Upload and process PDF question papers
- **Smart Extraction**: Automatically extract questions with metadata
- **Categorization**: Organize by department, subject, unit, and topic
- **Difficulty Classification**: Auto-classify questions by difficulty level

### 📝 Intelligent Paper Generation
- **Custom Papers**: Generate question papers based on criteria
- **Smart Distribution**: Control difficulty levels and mark allocation
- **Multiple Formats**: Support for various question types (MCQ, descriptive, etc.)
- **Branded Output**: Professional PDF generation with institutional branding

### 🏛️ Academic Organization
- **Structured Hierarchy**: Departments → Subjects → Units → Topics
- **Advanced Search**: Find questions by multiple criteria
- **User Management**: Role-based access control
- **Analytics Dashboard**: Track usage and generate reports

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git (for cloning the repository)
- SQLite (included) or PostgreSQL

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Devlinx-s/ResearchNest.git
   cd ResearchNest
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Create a `.env` file in the project root:
   ```env
   # Application
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   
   # Database
   DATABASE_URI=sqlite:///researchnest.db
   
   # File Uploads
   UPLOAD_FOLDER=uploads
   MAX_CONTENT_LENGTH=20971520  # 20MB
   
   # Email (optional)
   MAIL_SERVER=your-smtp-server.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@example.com
   MAIL_PASSWORD=your-email-password
   ```

5. **Initialize Database**
   ```bash
   flask db upgrade
   ```

6. **Run the Application**
   ```bash
   flask run
   ```

7. **Access the System**
   - Open your browser: `http://localhost:5000`
   - **Admin Login**: `admin@researchnest.local` / `admin123`
   - **Instructor/Student**: Register with your institutional email

## 📚 Documentation

### Project Structure

```
ResearchNest/
├── app/                      # Application package
│   ├── __init__.py          # App factory and extensions
│   ├── models/              # Database models
│   ├── routes/              # Application routes
│   ├── static/              # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/           # Jinja2 templates
│       ├── auth/            # Authentication templates
│       ├── admin/           # Admin interface templates
│       └── questions/       # Question management templates
├── migrations/              # Database migrations
├── tests/                   # Test files
├── uploads/                 # User uploads
├── .env.example            # Example environment variables
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Database Models

#### Core Models
- **User**: System users (Admin, Instructor, Student)
- **Department**: Academic departments
- **Subject**: Courses within departments
- **Unit**: Course units
- **Topic**: Specific topics within units
- **Question**: Individual questions with metadata
- **QuestionDocument**: Source documents for questions
- **GeneratedQuestionPaper**: Generated exam papers

### API Endpoints

#### Authentication
- `POST /login` - User login
- `POST /register` - New user registration
- `POST /logout` - User logout

#### Question Management
- `GET /questions` - List all questions
- `POST /questions` - Create new question
- `GET /questions/<id>` - Get question details
- `PUT /questions/<id>` - Update question
- `DELETE /questions/<id>` - Delete question

#### Paper Generation
- `POST /generate-paper` - Generate new question paper
- `GET /generated-papers` - List generated papers
- `GET /generated-papers/<id>/download` - Download paper

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Creating Migrations
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for better code clarity
- Write docstrings for all public methods

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for educational institutions
- Special thanks to all contributors and the open-source community

## 📧 Contact

For support or queries, please email: support@researchnest.local

---

<div align="center">
  <p>Made with ❤️ by the ResearchNest Team</p>
  <p>© 2025 ResearchNest. All rights reserved.</p>
</div>
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