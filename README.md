# ResearchNest - Student Research Archive System

A Flask-based research paper archive system that allows students to upload, search, and discover academic research papers with automatic metadata extraction and analytics.

## Features

### For Students
- **Authentication**: Secure login via Replit OAuth
- **Paper Upload**: Upload PDF research papers with automatic metadata extraction
- **Search & Discovery**: Advanced search by title, author, keywords, department, and year
- **Download Tracking**: Track paper downloads and view popular content
- **Personal Dashboard**: View uploaded papers and manage profile

### For Administrators
- **Analytics Dashboard**: Visual charts showing upload trends, popular topics, and department statistics
- **Paper Moderation**: Review, approve, or reject submitted papers
- **User Management**: View all users and manage admin privileges
- **System Statistics**: Monitor platform usage and engagement

## Technology Stack

- **Backend**: Flask 3.0, SQLAlchemy, PostgreSQL
- **Authentication**: Replit OAuth with Flask-Dance
- **PDF Processing**: PyMuPDF for metadata extraction
- **Frontend**: Bootstrap 5 with dark theme, Chart.js for analytics
- **File Storage**: Local file system with organized directory structure
- **Deployment**: Gunicorn WSGI server

## Installation Requirements

The following packages are automatically managed:
- Flask and extensions (SQLAlchemy, Login, WTF, Dance)
- Database drivers (psycopg2-binary)
- PDF processing (PyMuPDF)
- Authentication (PyJWT, oauthlib)
- Server (gunicorn)

## Authentication & Access Control

### Anonymous Users
- Browse and search research papers
- View paper details and abstracts
- See paper statistics and trends

### Signed-in Students
- All anonymous user features plus:
- Upload PDF research papers
- Download approved papers
- Access personal dashboard
- View upload history

### Administrators
- All student features plus:
- Access admin dashboard with analytics
- Moderate paper submissions (approve/reject)
- Manage user accounts and permissions
- View system-wide statistics

## File Organization

```
uploads/papers/
├── Computer_Science/
│   ├── 2024/
│   └── 2025/
├── Mathematics/
│   ├── 2024/
│   └── 2025/
└── [Department]/
    └── [Year]/
```

## Database Schema

### Core Tables
- **Users**: Student and admin accounts with profiles
- **Departments**: Academic departments (auto-created)
- **Research Papers**: Uploaded papers with metadata
- **Download Logs**: Track paper access and popularity
- **Keywords**: Trending research topics

## Security Features

- Secure file upload with type validation
- Login required for sensitive operations
- Admin-only access to moderation features
- File path sanitization and validation
- Session management with OAuth tokens

## Getting Started

1. **Access the Application**: Navigate to the running application URL
2. **Sign In**: Click "Sign In to Upload & Download" to authenticate
3. **Upload Papers**: Use the upload form with drag-and-drop support
4. **Search Research**: Use the advanced search filters
5. **Admin Access**: Administrators can access the dashboard at `/admin`

## API Endpoints

### Analytics APIs (Admin only)
- `/api/analytics/papers-by-department` - Department distribution
- `/api/analytics/uploads-by-month` - Upload trends
- `/api/analytics/downloads-by-month` - Download trends  
- `/api/analytics/top-keywords` - Popular research topics

## Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Flask session encryption key
- `REPL_ID` - Replit application identifier

### Upload Limits
- Maximum file size: 20MB
- Supported formats: PDF only
- Automatic metadata extraction from PDF content

## Features in Detail

### Automatic Metadata Extraction
- Title, authors, and keywords from PDF metadata
- Fallback keyword extraction from abstract text
- Form validation with extracted or manual data

### Search Capabilities  
- Full-text search across title, authors, abstract, keywords
- Filter by department, publication year range
- Keyword-based filtering with suggestions
- Pagination for large result sets

### Analytics Dashboard
- Interactive charts showing research trends
- Department-wise paper distribution
- Monthly upload and download statistics
- Popular keywords and topics tracking

## Browser Support

Optimized for modern browsers with:
- Responsive design for mobile and desktop
- Progressive enhancement for JavaScript features
- Accessible UI components with proper ARIA labels