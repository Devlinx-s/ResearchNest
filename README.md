# ResearchNest - Research Paper Archive System

A standalone Flask-based research paper archive system for students and researchers to upload, search, and discover academic papers with automatic metadata extraction and analytics.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r standalone_requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Access the system:**
   - Open browser: `http://localhost:5000`
   - Admin login: `admin@researchnest.local`
   - Student login: Any other email address

## Core Features

- **PDF Upload**: Automatic metadata extraction (title, authors, keywords)
- **Advanced Search**: Filter by department, year, keywords, full-text
- **Download Tracking**: Monitor paper popularity and usage
- **Analytics Dashboard**: Visual charts for trends and statistics
- **User Management**: Role-based access (Students vs Administrators)
- **Paper Moderation**: Admin approval workflow

## Technology Stack

- **Backend**: Flask 3.1, SQLAlchemy, SQLite/PostgreSQL
- **PDF Processing**: PyMuPDF for metadata extraction  
- **Frontend**: Bootstrap 5 dark theme, Chart.js analytics
- **Authentication**: Simple email-based demo system
- **File Storage**: Local organized directory structure

## File Structure

```
ResearchNest/
├── main.py                  # Application entry point
├── app.py                   # Flask configuration
├── routes.py                # Route handlers
├── auth.py                  # Authentication system
├── models.py                # Database models
├── forms.py                 # Form definitions
├── utils.py                 # Utility functions
├── standalone_requirements.txt
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── uploads/                 # Uploaded papers
```

## System Requirements

- Python 3.11+
- SQLite (included) or PostgreSQL (optional)
- 50MB disk space minimum
- No external API keys required

## Database

- **Default**: SQLite (no setup required)
- **Optional**: PostgreSQL for production
- Auto-creates all tables and sample data
- Organized file storage by department/year

## Authentication

- Demo system for local development
- Admin user: `admin@researchnest.local` 
- Any email creates a student account
- No external OAuth dependencies

## Administration

- Access admin dashboard at `/admin`
- View analytics and system statistics
- Moderate paper submissions
- Manage user accounts and permissions
- Export data and generate reports

## Security

- File type validation (PDF only)
- Role-based access control
- Secure file storage and validation
- Session management
- Admin-only sensitive operations

This is a completely self-contained system suitable for academic institutions, research groups, or local deployment without external dependencies.