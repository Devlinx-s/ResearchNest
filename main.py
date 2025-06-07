#!/usr/bin/env python3
"""
ResearchNest - Standalone Research Paper Archive System
"""

import os
import sys

# Set environment variables for standalone operation
os.environ.setdefault('SECRET_KEY', 'standalone-secret-key-change-in-production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///researchnest.db')

# Import the Flask app
from app import app
import routes  # Import routes to register them

if __name__ == "__main__":
    print("ResearchNest Research Archive System")
    print("Starting on http://localhost:5000")
    print("Demo admin: admin@researchnest.local")
    print("-" * 40)
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )