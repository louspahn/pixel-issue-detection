#!/usr/bin/env python3
"""
Simple Dashboard Email Generator
Uses direct JQL queries instead of filter IDs to avoid permission issues.
"""

import requests
import base64
import json
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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

def search_tickets_by_jql(jql, max_results=50):
    """Search tickets using JQL"""
    try:
        data = {
            'jql': jql,
            'maxResults': max_results,
            'fields': ['summary', 'status', 'priority', 'assignee', 'created', 'updated', 'reporter', 'description']
        }

        result = make_jira_request('/rest/api/3/search', method='POST', data=data)
        return result.get('issues', []) if result else []

    except Exception as e:
        logger.error(f"Error searching tickets: {e}")
        return []

def get_pixel_tickets():
    """Get various categories of pixel tickets using JQL"""

    # Define JQL queries for different categories
    queries = {
        'all_pixel': f'''project = PS AND (
            summary ~ "pixel" OR
            summary ~ "tracking" OR
            summary ~ "conversion" OR
            summary ~ "tag" OR
            summary ~ "gtm" OR
            description ~ "pixel"
        ) ORDER BY created DESC''',

        'recent_pixel': f'''project = PS AND (
            summary ~ "pixel" OR
            summary ~ "tracking" OR
            summary ~ "conversion"
        ) AND created >= -7d ORDER BY created DESC''',

        'high_priority': f'''project = PS AND (
            summary ~ "pixel" OR
            summary ~ "tracking" OR
            summary ~ "conversion"
        ) AND priority in (Highest, High) ORDER BY priority DESC''',

        'open_pixel': f'''project = PS AND (
            summary ~ "pixel" OR
            summary ~ "tracking" OR
            summary ~ "conversion"
        ) AND status not in (Resolved, Closed, Done) ORDER BY created DESC'''
    }

    results = {}
    for category, jql in queries.items():
        logger.info(f"Searching for {category} tickets...")
        tickets = search_tickets_by_jql(jql, max_results=20)
        results[category] = tickets
        logger.info(f"Found {len(tickets)} {category} tickets")

    return results

def generate_ticket_table(tickets, title, max_show=10):
    """Generate HTML table for tickets"""
    if not tickets:
        return f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #ccc; background: #f9f9f9;">
            <h3 style="margin: 0; color: #666;">📋 {title}</h3>
            <p style="margin: 5px 0; color: #888;">No tickets found</p>
        </div>
        """

    ticket_rows = ""
    for i, ticket in enumerate(tickets[:max_show]):
        key = ticket['key']
        summary = ticket['fields']['summary']
        status = ticket['fields']['status']['name']
        priority = ticket['fields']['priority']['name'] if ticket['fields']['priority'] else 'None'
        created = ticket['fields']['created'][:10]  # Just the date

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
            <td style="padding: 8px; border-bottom: 1px solid #eee; font-size: 12px; color: #666;">{created}</td>
        </tr>
        """

    return f"""
    <div style="margin-bottom: 30px;">
        <h3 style="color: #0052cc; margin-bottom: 10px;">📋 {title} ({len(tickets)} total)</h3>
        <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background: #f4f5f7;">
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Key</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Summary</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Priority</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Status</th>
                    <th style="padding: 12px 8px; text-align: left; font-weight: bold;">Created</th>
                </tr>
            </thead>
            <tbody>
                {ticket_rows}
            </tbody>
        </table>
        {f'<p style="margin-top: 5px; color: #666; font-size: 12px;">Showing first {max_show} of {len(tickets)} tickets</p>' if len(tickets) > max_show else ''}
    </div>
    """

def generate_dashboard_html(ticket_data):
    """Generate complete dashboard email HTML"""
    today = datetime.now().strftime("%B %d, %Y")

    # Calculate stats
    total_pixel = len(ticket_data.get('all_pixel', []))
    recent_pixel = len(ticket_data.get('recent_pixel', []))
    high_priority = len(ticket_data.get('high_priority', []))
    open_tickets = len(ticket_data.get('open_pixel', []))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Daily Pixel Dashboard Report</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: #f4f5f7;">
        <div style="max-width: 900px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0052cc, #0065ff); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🔥 Pixel Dashboard Report</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">{today}</p>
            </div>

            <!-- Quick Stats -->
            <div style="padding: 30px; border-bottom: 1px solid #eee;">
                <h2 style="margin: 0 0 20px 0; color: #0052cc;">📊 Quick Stats</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="padding: 20px; background: #e8f4fd; border-radius: 8px; text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #0052cc;">{total_pixel}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">Total Pixel Issues</div>
                    </div>
                    <div style="padding: 20px; background: #fff3cd; border-radius: 8px; text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #856404;">{recent_pixel}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">Recent (7 days)</div>
                    </div>
                    <div style="padding: 20px; background: #f8d7da; border-radius: 8px; text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #721c24;">{high_priority}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">High Priority</div>
                    </div>
                    <div style="padding: 20px; background: #d1ecf1; border-radius: 8px; text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #0c5460;">{open_tickets}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">Open Issues</div>
                    </div>
                </div>
            </div>

            <!-- Dashboard Link -->
            <div style="padding: 20px 30px; background: #f8f9fa; border-bottom: 1px solid #eee; text-align: center;">
                <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="display: inline-block; background: #0052cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 0 10px;">
                    🔗 View Full Dashboard
                </a>
                <a href="https://adgear.atlassian.net/projects/PS" style="display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 0 10px;">
                    📋 PS Project
                </a>
            </div>

            <!-- Ticket Details -->
            <div style="padding: 30px;">
    """

    # Add ticket sections
    sections = [
        ('high_priority', '🚨 High Priority Issues'),
        ('recent_pixel', '📅 Recent Pixel Issues (Last 7 Days)'),
        ('open_pixel', '🔄 Open Pixel Issues'),
        ('all_pixel', '📋 All Pixel Issues')
    ]

    for key, title in sections:
        tickets = ticket_data.get(key, [])
        html += generate_ticket_table(tickets, title, max_show=8)

    # Footer
    html += f"""
            </div>

            <!-- Footer -->
            <div style="padding: 20px 30px; background: #f4f5f7; border-radius: 0 0 8px 8px; border-top: 1px solid #eee;">
                <div style="text-align: center; margin-bottom: 15px;">
                    <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="color: #0052cc; text-decoration: none; margin: 0 15px;">📊 Dashboard</a>
                    <a href="https://adgear.atlassian.net/projects/PS/issues" style="color: #0052cc; text-decoration: none; margin: 0 15px;">📋 All Issues</a>
                    <a href="https://adgear.atlassian.net/secure/CreateIssue.jspa?pid=10000&issuetype=10001" style="color: #0052cc; text-decoration: none; margin: 0 15px;">➕ Create Issue</a>
                </div>
                <p style="margin: 0; font-size: 12px; color: #666; text-align: center;">
                    Generated by Pixel Monitoring System • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return html

def send_email_or_save(html_content):
    """Send email if configured, otherwise save to file"""
    filename = f"pixel_dashboard_{datetime.now().strftime('%Y%m%d')}.html"

    # Always save to file first
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"📄 Dashboard saved to {filename}")

    # Try to send email if password is configured
    if EMAIL_CONFIG['password']:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔥 Pixel Dashboard Report - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = EMAIL_CONFIG['from_email']
            msg['To'] = ', '.join(EMAIL_CONFIG['to_emails'])

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['password'])
            server.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['to_emails'], msg.as_string())
            server.quit()

            logger.info(f"✅ Email sent successfully to {', '.join(EMAIL_CONFIG['to_emails'])}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            logger.info("💡 Email saved to file instead")

    else:
        logger.info("💡 No email password configured - report saved to file")
        logger.info("💡 To enable email: export EMAIL_PASSWORD='your_password'")

    return False

def main():
    """Main function"""
    logger.info("🚀 Starting Pixel Dashboard Report generation...")

    # Check Jira configuration
    if not JIRA_CONFIG['token']:
        logger.error("❌ JIRA_TOKEN not configured")
        return

    # Get ticket data
    ticket_data = get_pixel_tickets()

    # Generate HTML report
    html_content = generate_dashboard_html(ticket_data)

    # Send or save
    send_email_or_save(html_content)

    logger.info("✅ Pixel Dashboard Report completed!")

if __name__ == "__main__":
    main()