#!/usr/bin/env python3
"""
Local development runner for ResearchNest
This script sets up the application for local development without Replit dependencies
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for local development
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('SESSION_SECRET', 'local-dev-secret-change-in-production')

# Use SQLite by default for local development
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///researchnest_local.db'

try:
    from local_app import app
    import local_routes  # noqa: F401
    
    if __name__ == "__main__":
        print("Starting ResearchNest in local development mode...")
        print("Database:", os.environ.get('DATABASE_URL'))
        print("Demo user will be created automatically (demo@local.dev)")
        print("Demo user has admin privileges for testing")
        print("Visit: http://localhost:5000")
        print("-" * 50)
        
        app.run(
            host="0.0.0.0", 
            port=5000, 
            debug=True,
            use_reloader=True
        )
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required packages:")
    print("pip install -r local_requirements.txt")
    sys.exit(1)