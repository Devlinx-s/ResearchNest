# Configuration Guide

This guide explains how to configure the ResearchNest application to suit your needs.

## Environment Variables

The application is configured using environment variables. Here are the available options:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_APP` | Main application module | `app.py` |
| `FLASK_ENV` | Application environment | `development` or `production` |
| `SECRET_KEY` | Secret key for session security | `your-secret-key-here` |
| `DATABASE_URL` | Database connection URL | `postgresql://user:pass@localhost/dbname` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `UPLOAD_FOLDER` | Directory for file uploads | `uploads` |
| `MAX_CONTENT_LENGTH` | Max upload size in bytes | `16 * 1024 * 1024` (16MB) |
| `CELERY_BROKER_URL` | Celery broker URL | `REDIS_URL` value |
| `CELERY_RESULT_BACKEND` | Celery result backend | `REDIS_URL` value |

## Database Configuration

The application uses SQLAlchemy for database operations. The database connection is configured using the `DATABASE_URL` environment variable.

### Example PostgreSQL Configuration

```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/researchnest
```

## Redis Configuration

Redis is used for task queuing and caching. Configure using the `REDIS_URL` environment variable.

```bash
export REDIS_URL=redis://localhost:6379/0
```

## Email Configuration (Optional)

To enable email notifications, configure these variables:

```bash
export MAIL_SERVER=smtp.example.com
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=your-email@example.com
export MAIL_PASSWORD=your-email-password
```

## Production Configuration

For production deployments, make sure to:

1. Set `FLASK_ENV=production`
2. Set `DEBUG=False`
3. Use a strong `SECRET_KEY`
4. Configure a production database
5. Set up HTTPS
6. Configure proper logging

## Example .env File

```env
# Core Settings
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/prod_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (optional)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=noreply@example.com
MAIL_PASSWORD=your-email-password

# File Uploads
UPLOAD_FOLDER=/var/www/researchnest/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## Next Steps

- [Deployment Guide](../deployment/production.md)
- [API Reference](../api/overview.md)