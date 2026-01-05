# Email Setup Guide for MediBook

This guide will help you configure Gmail to send appointment confirmation emails.

## Prerequisites

1. A Gmail account
2. Flask-Mail installed (already in requirements.txt)

## Step 1: Install Flask-Mail

If you haven't already, install the required package:

```bash
pip install Flask-Mail
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step 2: Enable 2-Factor Authentication on Gmail

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

## Step 3: Generate an App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", click **2-Step Verification**
4. Scroll down and click **App passwords**
5. Select **Mail** as the app and **Other (Custom name)** as the device
6. Enter "MediBook" as the custom name
7. Click **Generate**
8. **Copy the 16-character password** (you'll need this in the next step)

## Step 4: Configure Environment Variables

You have two options:

### Option A: Environment Variables (Recommended for Production)

Set these environment variables before running your Flask app:

**On macOS/Linux:**
```bash
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-16-character-app-password"
```

**On Windows (Command Prompt):**
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-16-character-app-password
```

**On Windows (PowerShell):**
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-16-character-app-password"
```

### Option B: Direct Configuration (For Testing Only)

You can temporarily modify `app.py` and replace the default values:

```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-16-character-app-password'
```

⚠️ **Warning:** Never commit your actual credentials to version control!

## Step 5: Test the Email Service

1. Start your Flask application
2. Log in as an admin
3. Go to the admin appointments page
4. Confirm a pending appointment
5. Check the patient's email inbox for the confirmation email

## Troubleshooting

### Email not sending?

1. **Check your credentials:**
   - Make sure you're using the App Password, not your regular Gmail password
   - Verify the email address is correct

2. **Check Gmail security:**
   - Ensure 2-Step Verification is enabled
   - Make sure "Less secure app access" is not required (App Passwords should work)

3. **Check Flask logs:**
   - Look for error messages in your terminal/console
   - The error will be printed if email sending fails

4. **Test SMTP connection:**
   - Verify you can connect to smtp.gmail.com on port 587
   - Check if your firewall is blocking the connection

### Common Errors

- **"Authentication failed"**: Check that you're using an App Password, not your regular password
- **"Connection refused"**: Check your internet connection and firewall settings
- **"SMTP server not found"**: Verify the SMTP server settings in app.py

## Security Best Practices

1. **Never commit credentials to Git:**
   - Use environment variables
   - Add `.env` to `.gitignore` if using a .env file

2. **Use App Passwords:**
   - Never use your main Gmail password
   - App Passwords are more secure and can be revoked easily

3. **Rotate passwords regularly:**
   - Generate new App Passwords periodically
   - Revoke old App Passwords that are no longer in use

## Email Template

The email template is located at:
`templates/emails/appointment_confirmation.html`

You can customize this template to match your branding and preferences.

