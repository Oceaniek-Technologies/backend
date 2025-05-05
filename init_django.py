#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add shorties_api to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'shorties_api'))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shorties_api.settings')

# Initialize Django
django.setup()

# Run migrations
execute_from_command_line(['manage.py', 'makemigrations', 'users', 'videos', 'social'])
execute_from_command_line(['manage.py', 'migrate'])

print("Django application initialized successfully!")
print("Database migrations applied!")