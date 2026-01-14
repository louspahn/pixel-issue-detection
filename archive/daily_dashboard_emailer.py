#!/usr/bin/env python3
"""
Daily Dashboard Email Generator
Creates and sends a custom dashboard email without requiring Jira admin permissions.
Uses existing monitoring system infrastructure.
"""

import requests
import base64
import json
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard_emailer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
JIRA_CONFIG = {
    'base_url': 'https://adgear.atlassian.net',
    'email': os.getenv('JIRA_EMAIL', 'l.spahn@samsung.com'),
    'token': os.getenv('JIRA_TOKEN', ''),
    'project_key': 'PS'
}

EMAIL_CONFIG = {
    'smtp_server': 'smtp.office365.com',
    'smtp_port': 587,
    'from_email': 'l.spahn@samsung.com',
    'to_emails': ['l.spahn@samsung.com'],
    'password': os.getenv('EMAIL_PASSWORD', '')
}

# Dashboard and filter configuration
DASHBOARD_CONFIG = {
    'dashboard_id': '19521',
    'dashboard_url': 'https://adgear.atlassian.net/jira/dashboards/19521',
    'filters': {
        'all_pixel_issues': '26796',
        'validation_issues': '26830',
        'troubleshooting': '26831',
        'implementation': '26832',
        'critical_issues': '26837'
    }
}

def make_jira_request(endpoint, method='GET', data=None):
    """Make authenticated request to Jira API"""
    auth_string = f"{JIRA_CONFIG['email']}:{JIRA_CONFIG['token']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_auth}',
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
    except Exception as e:
        logger.error(f"Jira API error: {e}")
        return None

def get_filter_results(filter_id, max_results=50):
    """Get tickets from a specific filter"""
    try:
        jql_endpoint = f"/rest/api/3/search"

        # Get filter details first
        filter_data = make_jira_request(f"/rest/api/3/filter/{filter_id}")
        if not filter_data:
            return []

        jql = filter_data.get('jql', '')

        data = {
            'jql': jql,
            'maxResults': max_results,
            'fields': ['summary', 'status', 'priority', 'assignee', 'created', 'updated', 'reporter']
        }

        result = make_jira_request(jql_endpoint, method='POST', data=data)
        return result.get('issues', []) if result else []

    except Exception as e:
        logger.error(f"Error fetching filter {filter_id}: {e}")
        return []

def generate_ticket_summary(tickets, filter_name):
    """Generate HTML summary for a set of tickets"""
    if not tickets:
        return f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #ccc; background: #f9f9f9;">
            <h3 style="margin: 0; color: #666;">📋 {filter_name}</h3>
            <p style="margin: 5px 0; color: #888;">No tickets found</p>
        </div>
        """

    ticket_rows = ""
    for ticket in tickets[:10]:  # Limit to 10 tickets per category
        key = ticket['key']
        summary = ticket['fields']['summary']
        status = ticket['fields']['status']['name']
        priority = ticket['fields']['priority']['name'] if ticket['fields']['priority'] else 'None'

        # Color code by priority
        priority_color = {
            'Highest': '#d04437',
            'High': '#f79232',
            'Medium': '#f1c40f',
            'Low': '#14892c',
            'Lowest': '#59afe1'
        }.get(priority, '#666')

        ticket_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                <a href="{JIRA_CONFIG['base_url']}/browse/{key}" style="color: #0052cc; text-decoration: none; font-weight: bold;">{key}</a>
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; max-width: 300px;">{summary}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                <span style="background: {priority_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{priority}</span>
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{status}</td>
        </tr>
        """

    return f"""
    <div style="margin-bottom: 30px;">
        <h3 style="color: #0052cc; margin-bottom: 10px;">📋 {filter_name} ({len(tickets)} total)</h3>
        <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background: #f4f5f7;">
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Key</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Summary</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Priority</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Status</th>
                </tr>
            </thead>
            <tbody>
                {ticket_rows}
            </tbody>
        </table>
        {f'<p style="margin-top: 5px; color: #666; font-size: 12px;">Showing first 10 of {len(tickets)} tickets</p>' if len(tickets) > 10 else ''}
    </div>
    """

def generate_dashboard_email():
    """Generate complete dashboard email HTML"""
    logger.info("Generating daily dashboard email...")

    # Get current date
    today = datetime.now().strftime("%B %d, %Y")

    # Fetch data from all filters
    filter_data = {}
    total_tickets = 0

    for filter_name, filter_id in DASHBOARD_CONFIG['filters'].items():
        logger.info(f"Fetching data for {filter_name} (filter {filter_id})...")
        tickets = get_filter_results(filter_id)
        filter_data[filter_name] = tickets
        if filter_name == 'all_pixel_issues':
            total_tickets = len(tickets)

    # Generate summary stats
    critical_count = len(filter_data.get('critical_issues', []))
    validation_count = len(filter_data.get('validation_issues', []))
    implementation_count = len(filter_data.get('implementation', []))
    troubleshooting_count = len(filter_data.get('troubleshooting', []))

    # Create HTML email
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Daily Pixel Dashboard Report</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: #f4f5f7;">
        <div style="max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0052cc, #0065ff); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🔥 Daily Pixel Dashboard Report</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">{today}</p>
            </div>

            <!-- Quick Stats -->
            <div style="padding: 30px; border-bottom: 1px solid #eee;">
                <h2 style="margin: 0 0 20px 0; color: #0052cc;">📊 Quick Stats</h2>
                <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                    <div style="flex: 1; min-width: 150px; padding: 15px; background: #e8f4fd; border-radius: 6px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #0052cc;">{total_tickets}</div>
                        <div style="font-size: 14px; color: #666;">Total Pixel Issues</div>
                    </div>
                    <div style="flex: 1; min-width: 150px; padding: 15px; background: #ffeaa7; border-radius: 6px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #d63384;">{critical_count}</div>
                        <div style="font-size: 14px; color: #666;">Critical Issues</div>
                    </div>
                    <div style="flex: 1; min-width: 150px; padding: 15px; background: #d1ecf1; border-radius: 6px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #0c5460;">{validation_count}</div>
                        <div style="font-size: 14px; color: #666;">Validation Requests</div>
                    </div>
                </div>
            </div>

            <!-- Dashboard Link -->
            <div style="padding: 20px 30px; background: #f8f9fa; border-bottom: 1px solid #eee;">
                <p style="margin: 0; text-align: center;">
                    <a href="{DASHBOARD_CONFIG['dashboard_url']}" style="display: inline-block; background: #0052cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        🔗 View Full Dashboard
                    </a>
                </p>
            </div>

            <!-- Ticket Details -->
            <div style="padding: 30px;">
    """

    # Add sections for each filter
    section_titles = {
        'critical_issues': '🚨 Critical Issues',
        'validation_issues': '🔍 Validation Requests',
        'implementation': '⚙️ Implementation Issues',
        'troubleshooting': '🔧 Troubleshooting',
        'all_pixel_issues': '📋 All Pixel Issues'
    }

    # Show critical first, then others, all issues last
    priority_order = ['critical_issues', 'validation_issues', 'implementation', 'troubleshooting', 'all_pixel_issues']

    for filter_name in priority_order:
        if filter_name in filter_data:
            tickets = filter_data[filter_name]
            section_title = section_titles.get(filter_name, filter_name.replace('_', ' ').title())
            email_html += generate_ticket_summary(tickets, section_title)

    # Footer
    email_html += f"""
            </div>

            <!-- Footer -->
            <div style="padding: 20px 30px; background: #f4f5f7; border-radius: 0 0 8px 8px; border-top: 1px solid #eee;">
                <h3 style="margin: 0 0 15px 0; color: #0052cc;">🔗 Quick Links</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <a href="{DASHBOARD_CONFIG['dashboard_url']}" style="color: #0052cc; text-decoration: none;">📊 Full Dashboard</a>
                    <span style="color: #ccc;">|</span>
                    <a href="https://adgear.atlassian.net/issues/?filter=26796" style="color: #0052cc; text-decoration: none;">📋 All Issues</a>
                    <span style="color: #ccc;">|</span>
                    <a href="https://adgear.atlassian.net/issues/?filter=26837" style="color: #0052cc; text-decoration: none;">🚨 Critical Only</a>
                </div>
                <p style="margin: 15px 0 0 0; font-size: 12px; color: #666;">
                    Generated automatically by Pixel Monitoring System • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return email_html

def send_dashboard_email():
    """Send the dashboard email"""
    try:
        # Generate email content
        html_content = generate_dashboard_email()

        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔥 Daily Pixel Dashboard Report - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['to_emails'])

        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Send email
        if EMAIL_CONFIG['password']:
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['password'])
            server.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['to_emails'], msg.as_string())
            server.quit()

            logger.info(f"✅ Dashboard email sent successfully to {', '.join(EMAIL_CONFIG['to_emails'])}")
            return True
        else:
            logger.warning("⚠️ Email password not configured - saving email to file instead")
            with open(f"dashboard_report_{datetime.now().strftime('%Y%m%d')}.html", 'w') as f:
                f.write(html_content)
            logger.info("📄 Dashboard report saved to HTML file")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to send dashboard email: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting daily dashboard email generation...")

    # Check configuration
    if not JIRA_CONFIG['token']:
        logger.error("❌ JIRA_TOKEN not configured")
        return

    # Generate and send email
    success = send_dashboard_email()

    if success:
        logger.info("🎉 Daily dashboard email completed successfully!")
    else:
        logger.info("📝 Dashboard report generated (email not sent)")

if __name__ == "__main__":
    main()