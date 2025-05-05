#!/bin/bash
set -e

# Change to the project directory
cd shorties_api

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create a superuser if one doesn't exist (optional)
# Use environment variables to provide credentials
# DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@example.com DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput

# Return to the root directory
cd ..

# Start the application using gunicorn
echo "Starting application..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app