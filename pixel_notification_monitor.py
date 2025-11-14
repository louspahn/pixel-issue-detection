#!/usr/bin/env python3
"""
Web Pixel Jira Notification Monitor
Monitors Jira PS project for new tickets related to web pixels and sends notifications.

Based on research of 16 pixel-related tickets from April-October 2025.
Expected volume: ~3 notifications per month.
"""

import requests
import base64
import json
import time
from datetime import datetime, timedelta
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Back to normal logging
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pixel_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Jira Configuration
JIRA_CONFIG = {
    'base_url': 'https://adgear.atlassian.net',
    'email': os.getenv('JIRA_EMAIL', 'l.spahn@samsung.com'),
    'token': os.getenv('JIRA_TOKEN', ''),  # Set via environment variable
    'project_key': 'PS'
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',  # Adjust for your email provider
        'smtp_port': 587,
        'from_email': 'l.spahn@samsung.com',
        'to_emails': ['l.spahn@samsung.com'],  # Your notification email
        'password': os.getenv('EMAIL_PASSWORD', '')  # Set via environment variable
    },
    'console': {
        'enabled': True
    },
    'check_interval': 300,  # Check every 5 minutes
    'lookback_hours': 6  # Only check tickets created in last 6 hours to avoid duplicates
}

def extract_text_from_rich_format(data):
    """Extract plain text from Jira's rich text format"""
    if isinstance(data, str):
        return data
    elif isinstance(data, dict):
        text_parts = []
        if 'content' in data:
            for item in data['content']:
                text_parts.append(extract_text_from_rich_format(item))
        elif 'text' in data:
            text_parts.append(data['text'])
        return ' '.join(text_parts)
    elif isinstance(data, list):
        text_parts = []
        for item in data:
            text_parts.append(extract_text_from_rich_format(item))
        return ' '.join(text_parts)
    else:
        return str(data)

def make_jira_request(endpoint, method='GET', data=None):
    """Make authenticated request to Jira API"""
    auth_string = f"{JIRA_CONFIG['email']}:{JIRA_CONFIG['token']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    url = f"{JIRA_CONFIG['base_url']}{endpoint}"

    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Jira API request failed: {e}")
        raise

def is_pixel_related_ticket(summary, description=''):
    """
    Detect if a ticket is related to web pixels.

    Based on analysis of 16 real pixel tickets:
    - 14/16 contained 'pixel' keyword
    - Common patterns: pixel validation, pixel firing, conversion pixel
    - Samsung-specific: 'universal tag'
    """
    if not summary:
        return False, 'no_summary'

    # Handle description - could be string or dict (rich text format)
    desc_text = ''
    if description:
        try:
            if isinstance(description, dict):
                # Extract text from Jira's rich text format recursively
                desc_text = extract_text_from_rich_format(description)
            elif isinstance(description, str):
                desc_text = description
            else:
                desc_text = str(description)
        except Exception as e:
            logger.debug(f"Error processing description: {e}")
            desc_text = str(description) if description else ''

    # Combine summary and description for analysis
    text = (summary + ' ' + desc_text).lower()

    # Step 1: Check exclusions first to avoid false positives
    exclusions = [
        'acr',              # TV-related, not web pixels
        'delivery report',   # Reporting, not pixel work
        'access request',    # Access management
        'grant access',      # Access management
        'monitoring alert',  # System monitoring
        'o&o monitoring',    # Operations monitoring
        'user sync',         # Third-party integration, not web pixels
        'sync pixel',        # Third-party integration, not web pixels
        'planning module',   # Planning tools, not web pixels
        'linear ads'         # TV/Linear advertising, not web pixels
    ]

    for exclusion in exclusions:
        if exclusion in text:
            logger.debug(f"Excluded ticket due to: {exclusion}")
            return False, f'excluded:{exclusion}'

    # Step 2: High-confidence keywords and phrases
    high_confidence_keywords = [
        'pixel validation',
        'pixel firing',
        'pixel not firing',
        'conversion pixel',
        'tracking pixel',
        'universal tag',     # Samsung-specific pixel terminology
        'piggyback',         # Pixel implementation method
        'appending a pixel', # Pixel implementation
        'append pixel'       # Pixel implementation variation
    ]

    for keyword in high_confidence_keywords:
        if keyword in text:
            logger.info(f"HIGH confidence match: {keyword}")
            return True, f'high:{keyword}'

    # Step 3: Pixel with context (covers 87.5% of real cases)
    if 'pixel' in text:
        pixel_contexts = [
            'confirmation', 'conversion', 'firing', 'tracking',
            'validation', 'website', 'page', 'code', 'tag',
            'implement', 'install', 'setup', 'not working',
            '0 conversions', 'troubleshoot'
        ]

        for context in pixel_contexts:
            if context in text:
                logger.info(f"Pixel with context match: pixel + {context}")
                return True, f'pixel_context:{context}'

    # Step 4: Medium confidence combination patterns
    tracking_keywords = ['tracking', 'tag', 'javascript', 'js']
    action_keywords = ['implement', 'install', 'setup', 'add', 'place', 'deploy']

    has_tracking = any(keyword in text for keyword in tracking_keywords)
    has_action = any(keyword in text for keyword in action_keywords)

    if has_tracking and has_action:
        logger.info(f"Medium confidence: tracking + action pattern")
        return True, 'medium:tracking_action'

    # Step 5: Web conversion patterns
    if 'conversion' in text and any(web_term in text for web_term in ['web', 'website', 'page', 'tag']):
        logger.info(f"Medium confidence: conversion + web pattern")
        return True, 'medium:conversion_web'

    return False, 'no_match'

def search_recent_tickets():
    """Search for tickets created in the last hour"""
    # Calculate time range
    now = datetime.now()
    lookback = now - timedelta(hours=NOTIFICATION_CONFIG['lookback_hours'])

    # Format for Jira JQL (ISO format)
    created_after = lookback.strftime('%Y-%m-%d %H:%M')

    jql = f"""
    project = "{JIRA_CONFIG['project_key']}"
    AND created >= "{created_after}"
    ORDER BY created DESC
    """

    data = {
        'jql': jql,
        'fields': ['key', 'summary', 'description', 'created', 'priority', 'status', 'creator'],
        'maxResults': 50
    }

    logger.info(f"Searching for tickets created after: {created_after}")
    result = make_jira_request('/rest/api/3/search/jql', method='POST', data=data)

    logger.info(f"Found {len(result['issues'])} recent tickets")
    return result['issues']

def format_notification_message(ticket, confidence_info):
    """Format notification message for pixel-related ticket"""
    # Handle different datetime formats from Jira
    created_str = ticket['fields']['created']
    try:
        if created_str.endswith('Z'):
            created_time = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
        elif '+' in created_str or '-' in created_str[-6:]:
            # Handle timezone offset like -0400 or +0000
            if ':' not in created_str[-6:]:
                # Add colon in timezone offset: -0400 -> -04:00
                created_time = datetime.fromisoformat(created_str[:-2] + ':' + created_str[-2:])
            else:
                created_time = datetime.fromisoformat(created_str)
        else:
            created_time = datetime.fromisoformat(created_str)
    except ValueError:
        # Fallback to current time if parsing fails
        created_time = datetime.now()
        logger.warning(f"Could not parse created time: {created_str}, using current time")

    # Safely handle description field
    description = ticket['fields'].get('description', 'No description provided')
    try:
        if description and description != 'No description provided':
            description_text = extract_text_from_rich_format(description)
        else:
            description_text = 'No description provided'
    except Exception as e:
        logger.debug(f"Error extracting description text: {e}")
        description_text = 'Could not extract description text'

    message = f"""
🔔 NEW PIXEL-RELATED TICKET DETECTED

Ticket: {ticket['key']}
Summary: {ticket['fields']['summary']}
Created: {created_time.strftime('%Y-%m-%d %H:%M:%S')}
Priority: {ticket['fields'].get('priority', {}).get('name', 'Unknown')}
Status: {ticket['fields']['status']['name']}
Reporter: {ticket['fields']['creator']['displayName']}

Detection: {confidence_info}

Direct Link: {JIRA_CONFIG['base_url']}/browse/{ticket['key']}

---
Description:
{description_text}
    """.strip()

    return message

def send_email_notification(subject, message):
    """Send email notification"""
    if not NOTIFICATION_CONFIG['email']['enabled']:
        return

    if not NOTIFICATION_CONFIG['email']['password']:
        logger.info("📧 EMAIL NOTIFICATION (would send - no password configured):")
        logger.info(f"To: {', '.join(NOTIFICATION_CONFIG['email']['to_emails'])}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message preview: {message[:100]}...")
        return

    try:
        import smtplib
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart

        msg = MimeMultipart()
        msg['From'] = NOTIFICATION_CONFIG['email']['from_email']
        msg['To'] = ', '.join(NOTIFICATION_CONFIG['email']['to_emails'])
        msg['Subject'] = subject

        msg.attach(MimeText(message, 'plain'))

        server = smtplib.SMTP(
            NOTIFICATION_CONFIG['email']['smtp_server'],
            NOTIFICATION_CONFIG['email']['smtp_port']
        )
        server.starttls()
        server.login(
            NOTIFICATION_CONFIG['email']['from_email'],
            NOTIFICATION_CONFIG['email']['password']
        )

        text = msg.as_string()
        server.sendmail(
            NOTIFICATION_CONFIG['email']['from_email'],
            NOTIFICATION_CONFIG['email']['to_emails'],
            text
        )
        server.quit()

        logger.info(f"✅ Email notification sent successfully to {', '.join(NOTIFICATION_CONFIG['email']['to_emails'])}")

    except ImportError:
        logger.warning("📧 Email libraries not available - showing preview instead:")
        logger.info(f"To: {', '.join(NOTIFICATION_CONFIG['email']['to_emails'])}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message preview: {message[:100]}...")
    except Exception as e:
        logger.error(f"❌ Failed to send email notification: {e}")
        logger.info("📧 Email preview (failed to send):")
        logger.info(f"To: {', '.join(NOTIFICATION_CONFIG['email']['to_emails'])}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message preview: {message[:100]}...")

def send_console_notification(message):
    """Send console notification"""
    if not NOTIFICATION_CONFIG['console']['enabled']:
        return

    # Create a highly visual alert
    alert_border = "🚨" * 20
    fire_border = "🔥" * 20

    print("\n" * 3)  # Add some space
    print(alert_border)
    print(fire_border)
    print("🚨🔥🚨🔥🚨  PIXEL TICKET ALERT!  🚨🔥🚨🔥🚨")
    print(fire_border)
    print(alert_border)
    print("\n" + "="*60)
    print(message)
    print("="*60)
    print(alert_border)
    print("🔔 ACTION REQUIRED: Check ticket immediately! 🔔")
    print(alert_border)
    print("\n" * 2)  # Add some space after

def notify_pixel_ticket(ticket, confidence_info):
    """Send notifications for pixel-related ticket"""
    message = format_notification_message(ticket, confidence_info)

    # Safely handle summary field - could be string or dict
    summary = ticket['fields']['summary']
    if isinstance(summary, dict):
        summary_text = extract_text_from_rich_format(summary)
    else:
        summary_text = str(summary)

    subject = f"🔥 Pixel Ticket Alert: {ticket['key']} - {summary_text[:50]}..."

    logger.info(f"Sending notification for ticket: {ticket['key']}")

    # Send notifications
    send_console_notification(message)
    send_email_notification(subject, message)

def check_for_pixel_tickets():
    """Main monitoring function - check for new pixel tickets"""
    try:
        logger.info("Starting pixel ticket check...")

        # Get recent tickets
        recent_tickets = search_recent_tickets()

        if not recent_tickets:
            logger.info("No recent tickets found")
            return

        pixel_tickets_found = 0

        # Check each ticket for pixel relevance
        for ticket in recent_tickets:
            try:
                logger.debug(f"Raw ticket data for {ticket.get('key', 'unknown')}: {ticket}")

                summary = ticket['fields'].get('summary', '')
                description = ticket['fields'].get('description', '')

                # Debug logging to see what we're getting
                logger.debug(f"Processing ticket {ticket['key']}: summary='{summary}', description type={type(description)}")

                logger.debug("About to call is_pixel_related_ticket...")
                is_pixel, confidence_info = is_pixel_related_ticket(summary, description)
                logger.debug(f"is_pixel_related_ticket returned: {is_pixel}, {confidence_info}")

                if is_pixel:
                    pixel_tickets_found += 1
                    # Safely handle summary for logging
                    safe_summary = summary if isinstance(summary, str) else str(summary)

                    # Create highly visible log alert
                    print("\n" + "🚨" * 50)
                    print("🔥🔥🔥 PIXEL TICKET DETECTED! 🔥🔥🔥")
                    print("🚨" * 50)
                    logger.warning(f"🚨🔥 PIXEL ALERT: {ticket['key']} - {safe_summary} 🔥🚨")
                    print("🚨" * 50 + "\n")

                    logger.debug("About to call notify_pixel_ticket...")
                    notify_pixel_ticket(ticket, confidence_info)
                    logger.debug("notify_pixel_ticket completed")
                else:
                    logger.debug(f"Not pixel-related: {ticket['key']} - {confidence_info}")

            except Exception as e:
                import traceback
                logger.error(f"Error processing ticket {ticket.get('key', 'unknown')}: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                logger.debug(f"Ticket data: {ticket}")
                # Continue with next ticket instead of failing completely
                continue

        if pixel_tickets_found > 0:
            logger.info(f"Found {pixel_tickets_found} pixel-related tickets in this check")
        else:
            logger.info("No pixel-related tickets found in recent tickets")

    except Exception as e:
        import traceback
        logger.error(f"Error during pixel ticket check: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")

def run_monitor():
    """Run the monitoring loop"""
    logger.info("🚀 Starting Pixel Ticket Notification Monitor")
    logger.info(f"Check interval: {NOTIFICATION_CONFIG['check_interval']} seconds")
    logger.info(f"Lookback period: {NOTIFICATION_CONFIG['lookback_hours']} hours")
    logger.info(f"Email notifications: {'enabled' if NOTIFICATION_CONFIG['email']['enabled'] else 'disabled'}")
    logger.info(f"Console notifications: {'enabled' if NOTIFICATION_CONFIG['console']['enabled'] else 'disabled'}")

    check_count = 0
    try:
        while True:
            check_count += 1
            logger.debug(f"Starting check #{check_count}")

            try:
                check_for_pixel_tickets()
                logger.debug(f"Check #{check_count} completed successfully")
            except Exception as e:
                import traceback
                logger.error(f"Check #{check_count} failed: {e}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Continue monitoring even if one check fails
                pass

            logger.info(f"Sleeping for {NOTIFICATION_CONFIG['check_interval']} seconds...")
            time.sleep(NOTIFICATION_CONFIG['check_interval'])

    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        import traceback
        logger.error(f"Monitor crashed: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

def test_detection():
    """Test the detection logic with known pixel ticket examples"""
    print("🧪 Testing Pixel Detection Logic\n")

    # Test cases based on real tickets from research
    test_cases = [
        # Should detect (True cases) - Web pixel related
        ("Ministry of Supply Pixel Validation Request", True),
        ("Porter Airlines pixel not firing on confirmation page", True),
        ("Pixels not firing in DSP though appearing in Adform", True),
        ("Verification on universal tags", True),
        ("Campaign going live TODAY - needs revenue tracking pixel setup", True),
        ("Website Pixel Conversion Data Not Showing Starting on 6/16/25", True),
        ("U-Variable ingestion in website pixel", True),
        ("Conversion pixel troubleshooting - 0 conversions showing", True),
        ("Web Conversion - Pixel Data Troubleshooting", True),
        ("Appending a pixel for line items", True),

        # Should NOT detect (False cases) - Exclusions and non-web pixel
        ("ACR delivery report for Q3", False),
        ("Grant access to dashboard for new user", False),
        ("O&O monitoring alert - server down", False),
        ("Weekly delivery report schedule change", False),
        ("Xandr GDPR updated macro for user sync pixels", False),  # Third-party integration
        ("FW User Sync Pixels Change scheduled for Monday", False),  # Third-party integration
        ("Planning Module Usage Report enhancement request", False),  # Planning tools
        ("Linear Ads Delivery report with pixel mentioned", False),  # TV/Linear ads
        ("Permission request for advertiser account", False),
    ]

    correct = 0
    total = len(test_cases)

    for summary, expected in test_cases:
        is_pixel, confidence = is_pixel_related_ticket(summary)
        result = "✅ PASS" if is_pixel == expected else "❌ FAIL"

        print(f"{result} | Expected: {expected:5} | Got: {is_pixel:5} | {confidence:15} | {summary}")

        if is_pixel == expected:
            correct += 1

    accuracy = (correct / total) * 100
    print(f"\n📊 Test Results: {correct}/{total} correct ({accuracy:.1f}% accuracy)")

    if accuracy >= 90:
        print("🎉 Detection logic passes quality threshold!")
    else:
        print("⚠️  Detection logic needs improvement")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_detection()
    elif len(sys.argv) > 1 and sys.argv[1] == 'check-once':
        check_for_pixel_tickets()
    else:
        run_monitor()