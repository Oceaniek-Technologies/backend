#!/bin/bash
set -e

# Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Change to the project directory to run migrations
cd shorties_api

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Return to root directory
cd ..

# Start the server
echo "Starting server..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app