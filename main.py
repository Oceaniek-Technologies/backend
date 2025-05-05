#!/usr/bin/env python
"""
WSGI config for Shorties API.
"""

import os
import sys
import django
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent

# Add the project directory to the Python path
sys.path.insert(0, str(BASE_DIR))

# Add the shorties_api directory to Python path
sys.path.insert(0, str(BASE_DIR / 'shorties_api'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shorties_api.settings')

try:
    # Initialize Django
    django.setup()
    
    # Import and create WSGI application
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    
    print("Django WSGI application initialized successfully!")
except Exception as e:
    print(f"Error initializing Django application: {str(e)}")
    
    # Fallback to a simple Flask app for debugging
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({
            "error": "Django initialization failed",
            "message": str(e),
            "python_path": sys.path,
            "base_dir": str(BASE_DIR),
            "django_settings_module": os.environ.get('DJANGO_SETTINGS_MODULE')
        })
        
    print("Fallback Flask application initialized for debugging!")