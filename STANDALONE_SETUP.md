# ResearchNest - Standalone Local Setup

A complete Flask-based research paper archive system with no external dependencies.

## Quick Start

1. **Install Python dependencies:**
   ```bash
   pip install -r standalone_requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Access the application:**
   - Open browser: `http://localhost:5000`
   - Admin login: `admin@researchnest.local`
   - Student login: Any other email address

## Features Available

- PDF upload with automatic metadata extraction
- Advanced search and filtering
- Download tracking and analytics
- Admin dashboard with charts
- User management and paper moderation
- SQLite database (no setup required)

## File Structure

```
ResearchNest/
├── main.py                  # Application entry point
├── app.py                   # Flask app configuration
├── routes.py                # All route handlers
├── auth.py                  # Authentication system
├── models.py                # Database models
├── forms.py                 # Form definitions
├── utils.py                 # Utility functions
├── standalone_requirements.txt  # Dependencies
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── uploads/                 # Uploaded papers (auto-created)
```

## System Requirements

- Python 3.11+
- 50MB disk space
- No database setup required (uses SQLite)
- No external API keys needed

## Administration

- Demo admin user created automatically
- Access admin dashboard at `/admin`
- Manage users and moderate papers
- View analytics and system statistics

This is a completely self-contained system with no external dependencies or cloud services required.