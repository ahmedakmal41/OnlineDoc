#!/bin/bash
# Email Configuration Script for MediBook
# Run this script before starting your Flask app to set email credentials

export MAIL_USERNAME="xmun41@gmail.com"
export MAIL_PASSWORD="guknimymqmnewlaa"

echo "✅ Email environment variables configured!"
echo "   Gmail: $MAIL_USERNAME"
echo ""
echo "To start your Flask app with email support, run:"
echo "   source setup_email.sh && python3 app.py"
echo ""
echo "Or manually set the variables each time:"
echo "   export MAIL_USERNAME='xmun41@gmail.com'"
echo "   export MAIL_PASSWORD='guknimymqmnewlaa'"

