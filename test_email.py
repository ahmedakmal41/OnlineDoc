#!/usr/bin/env python3
"""
Test script to verify email configuration
Run this to check if your Gmail setup is working correctly
"""

import os
import sys
from flask import Flask
from flask_mail import Mail, Message

# Check environment variables
mail_username = os.environ.get('MAIL_USERNAME')
mail_password = os.environ.get('MAIL_PASSWORD')

print("=" * 50)
print("Email Configuration Test")
print("=" * 50)
print()

if not mail_username or mail_username == 'your-email@gmail.com':
    print("❌ ERROR: MAIL_USERNAME not set!")
    print("   Please run: export MAIL_USERNAME='xmun41@gmail.com'")
    sys.exit(1)

if not mail_password or mail_password == 'your-app-password':
    print("❌ ERROR: MAIL_PASSWORD not set!")
    print("   Please run: export MAIL_PASSWORD='guknimymqmnewlaa'")
    sys.exit(1)

print(f"✅ MAIL_USERNAME: {mail_username}")
print(f"✅ MAIL_PASSWORD: {'*' * len(mail_password)} (hidden)")
print()

# Create Flask app for testing
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_DEFAULT_SENDER'] = mail_username

mail = Mail(app)

# Test email - use command line argument or default to Gmail account
test_email = sys.argv[1] if len(sys.argv) > 1 else mail_username
print(f"Will send test email to: {test_email}")
print()

print()
print(f"Attempting to send test email to: {test_email}")
print("Connecting to Gmail SMTP server...")
print()

try:
    with app.app_context():
        msg = Message(
            subject='MediBook Email Test',
            recipients=[test_email],
            body='This is a test email from MediBook. If you receive this, your email configuration is working correctly!',
            html='<h2>MediBook Email Test</h2><p>This is a test email from MediBook. If you receive this, your email configuration is working correctly!</p>'
        )
        
        mail.send(msg)
        print("=" * 50)
        print("✅ SUCCESS! Email sent successfully!")
        print("=" * 50)
        print(f"Please check the inbox of: {test_email}")
        print("(Also check spam/junk folder if not in inbox)")
        
except Exception as e:
    print("=" * 50)
    print("❌ ERROR: Failed to send email")
    print("=" * 50)
    print(f"Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    print()
    print("Common issues:")
    print("1. App Password incorrect - verify it's correct (no spaces)")
    print("2. 2-Step Verification not enabled on Gmail account")
    print("3. Firewall blocking SMTP connection")
    print("4. Gmail account security settings blocking the connection")
    import traceback
    traceback.print_exc()
    sys.exit(1)

