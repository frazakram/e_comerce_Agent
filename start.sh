#!/bin/bash

# Make the script executable
chmod +x start.sh

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p output

# Explicitly check for required files
echo "Verifying application files..."
ls -la

# Run with gunicorn using our renamed application
exec gunicorn wsgi:app --bind 0.0.0.0:$PORT --log-level debug
