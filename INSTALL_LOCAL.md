# Local Installation Guide for ResearchNest

This guide will help you run the ResearchNest research paper archive system on your local machine.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional - SQLite will be used as fallback)
- Git

## Quick Start

1. **Clone or download the project files**
2. **Install Python dependencies:**
   ```bash
   pip install -r local_requirements.txt
   ```

3. **Set up environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings if using PostgreSQL
   ```

4. **Run the application:**
   ```bash
   python run_local.py
   ```

5. **Access the application:**
   - Open your browser to `http://localhost:5000`
   - The system will automatically create a demo user for testing

## Database Options

### Option 1: SQLite (Default - No Setup Required)
The application will automatically use SQLite database (`researchnest_local.db`) if no PostgreSQL connection is configured.

### Option 2: PostgreSQL (Recommended for Production)
1. Install PostgreSQL on your system
2. Create a database:
   ```sql
   CREATE DATABASE researchnest;
   CREATE USER researchnest_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE researchnest TO researchnest_user;
   ```
3. Set the DATABASE_URL in your `.env` file:
   ```
   DATABASE_URL=postgresql://researchnest_user:your_password@localhost:5432/researchnest
   ```

## Authentication

### Local Development Mode
- Authentication is simplified for local development
- A demo user (`demo@local.dev`) is automatically created with admin privileges
- Click "Sign In" to log in as the demo user
- No external OAuth setup required

### Production Mode (Optional)
To use Replit OAuth in production:
1. Set up a Replit application
2. Configure environment variables:
   ```
   REPL_ID=your-repl-id
   ISSUER_URL=https://replit.com/oidc
   ```

## File Structure

```
ResearchNest/
├── run_local.py              # Local development runner
├── local_app.py              # Flask app configuration for local
├── local_routes.py           # Routes with local adaptations
├── local_replit_auth.py      # Authentication for local development
├── local_requirements.txt    # Python dependencies
├── .env.example             # Environment variables template
├── models.py                # Database models
├── forms.py                 # Form definitions
├── utils.py                 # Utility functions
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── uploads/                 # Uploaded papers (auto-created)
```

## Features Available Locally

### All Core Features Work:
- ✓ PDF upload with metadata extraction
- ✓ Search and filtering
- ✓ Download tracking
- ✓ Admin dashboard with analytics
- ✓ User management
- ✓ Paper moderation

### Local Adaptations:
- Simplified authentication (demo user)
- SQLite database fallback
- Auto-approval of uploaded papers
- Local file storage

## Development Commands

```bash
# Install dependencies
pip install -r local_requirements.txt

# Run with debug mode
python run_local.py

# Access admin features
# Log in as demo@local.dev (auto-created with admin privileges)
# Visit http://localhost:5000/admin
```

## Configuration Files

### .env File (Optional)
```
DATABASE_URL=sqlite:///researchnest_local.db
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads/papers
MAX_CONTENT_LENGTH=20971520
```

## Troubleshooting

### Common Issues:

1. **Import Errors:**
   ```bash
   pip install -r local_requirements.txt
   ```

2. **Database Connection Issues:**
   - Default SQLite will be used automatically
   - Check DATABASE_URL in .env if using PostgreSQL

3. **File Upload Issues:**
   - Ensure `uploads/papers/` directory is writable
   - Check file size limits (default 20MB)

4. **Port Already in Use:**
   - Change port in `run_local.py` if 5000 is busy

### File Permissions:
```bash
# Make upload directory writable
mkdir -p uploads/papers
chmod 755 uploads/papers
```

## Testing the System

1. **Upload a Paper:**
   - Sign in as demo user
   - Go to Upload section
   - Drop a PDF file or use file picker
   - Metadata will be extracted automatically

2. **Search Papers:**
   - Use search box on homepage
   - Filter by department, year, keywords
   - View paper details and download

3. **Admin Features:**
   - Visit `/admin` after signing in
   - View analytics dashboard
   - Manage users and papers
   - Monitor system statistics

## Production Deployment

For production deployment:
1. Use PostgreSQL instead of SQLite
2. Set proper SECRET_KEY
3. Configure real OAuth provider
4. Use a production WSGI server like Gunicorn
5. Set up proper file storage and backups

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure Python 3.11+ is being used
4. Check file permissions for upload directory