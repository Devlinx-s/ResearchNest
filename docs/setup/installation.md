# Installation Guide

This guide will walk you through setting up the ResearchNest application on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js 14.x or higher (for frontend assets)
- PostgreSQL 12 or higher
- Redis (for task queue)

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ResearchNest.git
cd ResearchNest
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd static
npm install
cd ..
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root with the following content:

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/researchnest
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
```

### 6. Initialize the Database

```bash
flask db upgrade
```

### 7. Run the Application

Start the development server:

```bash
flask run
```

Start the Celery worker (in a new terminal):

```bash
celery -A app.celery worker --loglevel=info
```

### 8. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## Next Steps

- [Configure the application](./configuration.md)
- [Get started with the quickstart guide](../usage/quickstart.md)

## Troubleshooting

If you encounter any issues during installation, please check the [troubleshooting guide](../../troubleshooting/common_issues.md) or open an issue on GitHub.