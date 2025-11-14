# Email Notification Setup Guide

## Quick Setup for Samsung Email

### Option 1: Using Samsung/Outlook Email (Recommended)
If you're using Samsung's corporate email (likely Outlook/Exchange):

1. **Generate App Password**:
   - Go to your Samsung/Microsoft account security settings
   - Generate an "App Password" for email applications

2. **Configure Environment Variable**:
   ```bash
   export EMAIL_PASSWORD="your_generated_app_password"
   ```

3. **Update SMTP Settings** (if needed):
   ```python
   # For Samsung/Outlook, update in pixel_notification_monitor.py:
   'smtp_server': 'smtp-mail.outlook.com',  # Samsung corporate email
   'smtp_port': 587,
   ```

### Option 2: Using Gmail (Alternative)
If you want to use a personal Gmail for notifications:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Google Account → Security → App passwords
   - Create password for "Mail"
3. **Set Environment Variable**:
   ```bash
   export EMAIL_PASSWORD="your_gmail_app_password"
   ```

### Option 3: Disable Email (Console Only)
If you prefer console-only notifications for now:

```python
# In pixel_notification_monitor.py, change:
'email': {
    'enabled': False,  # Disable email notifications
    # ... rest of config
}
```

## Testing Email Setup

Once configured, test with:
```bash
python3 pixel_notification_monitor.py check-once
```

If a pixel ticket is found, you should receive an email like:

```
Subject: 🔥 Pixel Ticket Alert: PS-XXXX - Ministry of Supply Pixel...

🔔 NEW PIXEL-RELATED TICKET DETECTED

Ticket: PS-XXXX
Summary: Ministry of Supply Pixel Validation Request
Created: 2025-10-22 16:05:00
Priority: Medium
Status: Open

Detection: high:pixel validation

Direct Link: https://adgear.atlassian.net/browse/PS-XXXX
```

## Troubleshooting

**Authentication Errors**:
- Verify app password is correct
- Check SMTP server settings for your email provider

**No Emails Received**:
- Check spam folder
- Verify email address is correct: l.spahn@samsung.com
- Test with personal Gmail first

**Corporate Email Issues**:
- Samsung IT may block external SMTP
- Use console notifications as backup
- Consider internal email relay if available

## Current Configuration

- **From**: l.spahn@samsung.com
- **To**: l.spahn@samsung.com
- **SMTP**: smtp.gmail.com:587 (adjust for Samsung email)
- **Security**: App password required (no plain passwords)