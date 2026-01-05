#!/bin/bash
# Startup script for MediBook Flask app with email support

# Set email environment variables
export MAIL_USERNAME="xmun41@gmail.com"
export MAIL_PASSWORD="guknimymqmnewlaa"

echo "🚀 Starting MediBook Flask Application..."
echo "📧 Email configured: $MAIL_USERNAME"
echo ""

# Check if Flask-Mail is installed
python3 -c "import flask_mail" 2>/dev/null || {
    echo "❌ Flask-Mail not installed. Installing..."
    pip3 install Flask-Mail
}

# Start Flask app
python3 app.py

