#!/bin/bash

# Make the script executable
chmod +x start.sh

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p output

# Run with gunicorn (no space between app and :app)
exec gunicorn wsgi:app --bind 0.0.0.0:$PORT
