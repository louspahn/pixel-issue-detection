#!/usr/bin/env python3
"""
Working Dashboard Email Generator
Uses the same proven methods as your existing pixel monitoring system.
"""

import sys
import os
sys.path.append('.')

# Import from your existing working monitoring system
from pixel_notification_monitor import search_recent_tickets, make_jira_request, is_pixel_related_ticket

import smtplib
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

EMAIL_CONFIG = {
    'smtp_server': 'smtp.office365.com',
    'smtp_port': 587,
    'from_email': 'l.spahn@samsung.com',
    'to_emails': ['l.spahn@samsung.com'],
    'password': os.getenv('EMAIL_PASSWORD', '')
}

def get_tickets_by_timeframe():
    """Get tickets by different time frames using proven monitoring methods"""

    logger.info("Getting recent tickets using proven monitoring system methods...")

    # Get tickets from different periods
    timeframes = {
        'today': 1,      # Last 24 hours
        'week': 7,       # Last 7 days
        'month': 30      # Last 30 days
    }

    results = {}

    for period, days in timeframes.items():
        logger.info(f"Getting tickets from last {days} days...")

        # Use custom JQL similar to your monitoring system
        jql = f'''project = PS AND created >= -{days}d ORDER BY created DESC'''

        try:
            # Use your proven API method
            data = {
                'jql': jql,
                'maxResults': 100,
                'fields': ['summary', 'status', 'priority', 'assignee', 'created', 'updated', 'reporter', 'description']
            }

            result = make_jira_request('/rest/api/2/search', data=data)  # Try API v2 instead
            if not result:
                result = make_jira_request('/rest/api/3/search', data=data)  # Fallback to v3

            tickets = result.get('issues', []) if result else []

            # Filter for pixel-related tickets using your existing detection logic
            pixel_tickets = []
            for ticket in tickets:
                summary = ticket['fields']['summary']
                description = ticket['fields'].get('description', '')

                # Extract description text if it's in rich format
                desc_text = ""
                if isinstance(description, dict) and 'content' in description:
                    for content in description['content']:
                        if content.get('type') == 'paragraph' and 'content' in content:
                            for text_content in content['content']:
                                if text_content.get('type') == 'text':
                                    desc_text += text_content.get('text', '') + " "
                else:
                    desc_text = str(description) if description else ""

                # Use your existing pixel detection logic
                if is_pixel_related_ticket(summary, desc_text):
                    pixel_tickets.append(ticket)

            results[period] = {
                'all_tickets': tickets,
                'pixel_tickets': pixel_tickets
            }

            logger.info(f"Found {len(tickets)} total tickets, {len(pixel_tickets)} pixel-related in {period}")

        except Exception as e:
            logger.error(f"Error getting {period} tickets: {e}")
            results[period] = {'all_tickets': [], 'pixel_tickets': []}

    return results

def categorize_tickets(tickets):
    """Categorize tickets by priority and status"""
    categories = {
        'critical': [],
        'high_priority': [],
        'open': [],
        'recent': []
    }

    for ticket in tickets:
        priority = ticket['fields'].get('priority')
        status = ticket['fields']['status']['name']
        created = ticket['fields']['created']

        priority_name = priority['name'] if priority else 'None'

        # Categorize
        if priority_name in ['Highest', 'Critical']:
            categories['critical'].append(ticket)
        elif priority_name in ['High']:
            categories['high_priority'].append(ticket)

        if status not in ['Resolved', 'Closed', 'Done']:
            categories['open'].append(ticket)

        # Check if created in last 3 days
        created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
        if (datetime.now(created_date.tzinfo) - created_date).days <= 3:
            categories['recent'].append(ticket)

    return categories

def generate_ticket_table_html(tickets, title, max_show=10):
    """Generate HTML table for tickets"""
    if not tickets:
        return f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #ccc; background: #f9f9f9; border-radius: 4px;">
            <h3 style="margin: 0; color: #666;">📋 {title}</h3>
            <p style="margin: 5px 0; color: #888; font-style: italic;">No tickets found</p>
        </div>
        """

    ticket_rows = ""
    for ticket in tickets[:max_show]:
        key = ticket['key']
        summary = ticket['fields']['summary']
        status = ticket['fields']['status']['name']
        priority = ticket['fields']['priority']['name'] if ticket['fields']['priority'] else 'None'
        created = ticket['fields']['created'][:10]  # Just the date

        # Truncate long summaries
        if len(summary) > 80:
            summary = summary[:77] + "..."

        # Color code by priority
        priority_colors = {
            'Highest': '#d04437',
            'High': '#f79232',
            'Medium': '#f1c40f',
            'Low': '#14892c',
            'Lowest': '#59afe1'
        }
        priority_color = priority_colors.get(priority, '#666')

        ticket_rows += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 10px 8px;">
                <a href="https://adgear.atlassian.net/browse/{key}"
                   style="color: #0052cc; text-decoration: none; font-weight: bold; font-family: monospace;">
                   {key}
                </a>
            </td>
            <td style="padding: 10px 8px; max-width: 350px; line-height: 1.4;">
                {summary}
            </td>
            <td style="padding: 10px 8px; text-align: center;">
                <span style="background: {priority_color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">
                    {priority}
                </span>
            </td>
            <td style="padding: 10px 8px; font-size: 13px;">
                {status}
            </td>
            <td style="padding: 10px 8px; font-size: 12px; color: #666;">
                {created}
            </td>
        </tr>
        """

    return f"""
    <div style="margin-bottom: 30px;">
        <h3 style="color: #0052cc; margin-bottom: 15px; border-bottom: 2px solid #0052cc; padding-bottom: 5px;">
            📋 {title} ({len(tickets)} total)
        </h3>
        <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 6px; overflow: hidden;">
            <thead>
                <tr style="background: linear-gradient(135deg, #f4f5f7, #e9ecef);">
                    <th style="padding: 15px 8px; text-align: left; font-weight: bold; color: #333; border-bottom: 2px solid #0052cc;">Key</th>
                    <th style="padding: 15px 8px; text-align: left; font-weight: bold; color: #333; border-bottom: 2px solid #0052cc;">Summary</th>
                    <th style="padding: 15px 8px; text-align: center; font-weight: bold; color: #333; border-bottom: 2px solid #0052cc;">Priority</th>
                    <th style="padding: 15px 8px; text-align: left; font-weight: bold; color: #333; border-bottom: 2px solid #0052cc;">Status</th>
                    <th style="padding: 15px 8px; text-align: left; font-weight: bold; color: #333; border-bottom: 2px solid #0052cc;">Created</th>
                </tr>
            </thead>
            <tbody>
                {ticket_rows}
            </tbody>
        </table>
        {f'<p style="margin-top: 8px; color: #666; font-size: 12px; font-style: italic;">Showing first {max_show} of {len(tickets)} tickets • <a href="https://adgear.atlassian.net/projects/PS/issues" style="color: #0052cc;">View all</a></p>' if len(tickets) > max_show else ''}
    </div>
    """

def generate_dashboard_email_html(ticket_data):
    """Generate beautiful dashboard email HTML"""
    today = datetime.now().strftime("%B %d, %Y")

    # Extract data
    today_tickets = ticket_data.get('today', {})
    week_tickets = ticket_data.get('week', {})
    month_tickets = ticket_data.get('month', {})

    # Get pixel tickets for different timeframes
    today_pixel = today_tickets.get('pixel_tickets', [])
    week_pixel = week_tickets.get('pixel_tickets', [])
    month_pixel = month_tickets.get('pixel_tickets', [])

    # Categorize all month pixel tickets
    categories = categorize_tickets(month_pixel)

    # Calculate stats
    total_pixel_month = len(month_pixel)
    total_pixel_week = len(week_pixel)
    total_pixel_today = len(today_pixel)
    critical_count = len(categories['critical'])
    open_count = len(categories['open'])
    recent_count = len(categories['recent'])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Pixel Dashboard Report</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">
        <div style="max-width: 1000px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); overflow: hidden;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 32px; font-weight: 300;">🔥 Pixel Dashboard Report</h1>
                <p style="margin: 15px 0 0 0; opacity: 0.9; font-size: 18px;">{today}</p>
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; backdrop-filter: blur(10px);">
                    <p style="margin: 0; font-size: 16px; opacity: 0.95;">Generated by Performance Pixel Monitoring System</p>
                </div>
            </div>

            <!-- Quick Stats -->
            <div style="padding: 40px 30px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
                <h2 style="margin: 0 0 25px 0; color: #495057; font-size: 24px; text-align: center;">📊 Quick Overview</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">

                    <div style="padding: 25px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 12px; text-align: center; border-left: 4px solid #2196f3;">
                        <div style="font-size: 36px; font-weight: bold; color: #1565c0; margin-bottom: 8px;">{total_pixel_month}</div>
                        <div style="font-size: 14px; color: #37474f; font-weight: 500;">Pixel Issues (30 days)</div>
                    </div>

                    <div style="padding: 25px; background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 30%); border-radius: 12px; text-align: center; border-left: 4px solid #ff9800;">
                        <div style="font-size: 36px; font-weight: bold; color: #e65100; margin-bottom: 8px;">{total_pixel_week}</div>
                        <div style="font-size: 14px; color: #37474f; font-weight: 500;">This Week</div>
                    </div>

                    <div style="padding: 25px; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-radius: 12px; text-align: center; border-left: 4px solid #f44336;">
                        <div style="font-size: 36px; font-weight: bold; color: #c62828; margin-bottom: 8px;">{critical_count}</div>
                        <div style="font-size: 14px; color: #37474f; font-weight: 500;">Critical Issues</div>
                    </div>

                    <div style="padding: 25px; background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-radius: 12px; text-align: center; border-left: 4px solid #4caf50;">
                        <div style="font-size: 36px; font-weight: bold; color: #2e7d32; margin-bottom: 8px;">{open_count}</div>
                        <div style="font-size: 14px; color: #37474f; font-weight: 500;">Open Issues</div>
                    </div>

                </div>
            </div>

            <!-- Quick Actions -->
            <div style="padding: 25px 30px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; text-align: center;">
                <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                    <a href="https://adgear.atlassian.net/jira/dashboards/19521"
                       style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; transition: transform 0.2s;">
                        🔗 Full Dashboard
                    </a>
                    <a href="https://adgear.atlassian.net/projects/PS/issues"
                       style="display: inline-block; background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        📋 PS Project
                    </a>
                    <a href="https://adgear.atlassian.net/secure/CreateIssue.jspa?pid=10000&issuetype=10001"
                       style="display: inline-block; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        ➕ Create Issue
                    </a>
                </div>
            </div>

            <!-- Ticket Details -->
            <div style="padding: 40px 30px;">
    """

    # Add sections for different categories
    sections = [
        (categories['critical'], '🚨 Critical Pixel Issues'),
        (categories['recent'], '📅 Recent Pixel Issues (Last 3 days)'),
        (categories['open'], '🔄 Open Pixel Issues'),
        (week_pixel, '📊 All Pixel Issues (Last 7 days)')
    ]

    for tickets, title in sections:
        if tickets or title.startswith('🚨'):  # Always show critical section even if empty
            html += generate_ticket_table_html(tickets, title, max_show=10)

    # Summary and Footer
    html += f"""
            </div>

            <!-- Summary -->
            <div style="padding: 30px; background: linear-gradient(135deg, #f1f3f4 0%, #e8eaf6 100%); border-top: 1px solid #dee2e6;">
                <h3 style="color: #3f51b5; margin-bottom: 15px; text-align: center;">📈 Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; text-align: center;">
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #1565c0;">Today:</strong> {total_pixel_today} pixel issues
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #e65100;">This Week:</strong> {total_pixel_week} pixel issues
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #2e7d32;">Open:</strong> {open_count} requiring attention
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div style="padding: 25px 30px; background: #263238; color: white; text-align: center;">
                <div style="margin-bottom: 15px;">
                    <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="color: #81c784; text-decoration: none; margin: 0 15px;">📊 Dashboard</a>
                    <a href="https://adgear.atlassian.net/projects/PS/issues" style="color: #81c784; text-decoration: none; margin: 0 15px;">📋 All Issues</a>
                    <a href="https://adgear.atlassian.net/secure/RapidBoard.jspa" style="color: #81c784; text-decoration: none; margin: 0 15px;">🏃 Boards</a>
                </div>
                <p style="margin: 0; font-size: 12px; opacity: 0.8;">
                    Automated report generated by Pixel Monitoring System<br>
                    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • Powered by Jira API
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return html

def send_email_or_save_file(html_content):
    """Send email if configured, otherwise save to file"""
    filename = f"pixel_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"

    # Always save to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"📄 Dashboard report saved to: {filename}")

    # Send email if password configured
    if EMAIL_CONFIG['password']:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔥 Pixel Dashboard Report - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = EMAIL_CONFIG['from_email']
            msg['To'] = ', '.join(EMAIL_CONFIG['to_emails'])

            html_part = MIMEText(html_content, 'html', 'utf-8')
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

    logger.info("💡 To enable email delivery, set EMAIL_PASSWORD environment variable")
    logger.info("💡 Example: export EMAIL_PASSWORD='your_app_password'")

    return False

def main():
    """Main function to generate pixel dashboard report"""
    logger.info("🚀 Starting Pixel Dashboard Report Generation...")
    logger.info("Using proven methods from your existing monitoring system")

    # Get ticket data using working methods
    ticket_data = get_tickets_by_timeframe()

    # Generate beautiful HTML report
    html_content = generate_dashboard_email_html(ticket_data)

    # Send or save
    send_email_or_save_file(html_content)

    logger.info("✅ Pixel Dashboard Report completed successfully!")
    logger.info("🎯 Next: Set EMAIL_PASSWORD to enable email delivery")

if __name__ == "__main__":
    main()