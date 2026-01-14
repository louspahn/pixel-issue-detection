#!/usr/bin/env python3
"""
Email Dashboard Generator
Uses working OAuth2 version and adds email functionality with configured password.
"""

import sys
import os
sys.path.append('.')
sys.path.append('../')
sys.path.append('../core')

from core.pixel_notification_monitor import search_recent_tickets, is_pixel_related_ticket
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_pixel_tickets():
    """Get recent pixel tickets using proven methods"""

    logger.info("🔍 Getting recent tickets using proven monitoring methods...")

    try:
        # Use your existing working method
        all_tickets = search_recent_tickets()

        if not all_tickets:
            logger.warning("No recent tickets found")
            return []

        logger.info(f"Found {len(all_tickets)} total recent tickets")

        # Filter for pixel-related tickets
        pixel_tickets = []
        for ticket in all_tickets:
            summary = ticket['fields']['summary']
            description = ticket['fields'].get('description', '')

            # Extract description text
            desc_text = ""
            if isinstance(description, dict) and 'content' in description:
                for content in description['content']:
                    if content.get('type') == 'paragraph' and 'content' in content:
                        for text_content in content['content']:
                            if text_content.get('type') == 'text':
                                desc_text += text_content.get('text', '') + " "
            else:
                desc_text = str(description) if description else ""

            # Use existing pixel detection
            if is_pixel_related_ticket(summary, desc_text):
                pixel_tickets.append(ticket)

        logger.info(f"🎯 Found {len(pixel_tickets)} pixel-related tickets")
        return pixel_tickets

    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        return []

def generate_email_html(pixel_tickets):
    """Generate HTML email content"""

    today = datetime.now().strftime("%B %d, %Y")
    total_count = len(pixel_tickets)

    # Categorize tickets
    critical = []
    high_priority = []
    open_tickets = []

    for ticket in pixel_tickets:
        priority = ticket['fields'].get('priority')
        status = ticket['fields']['status']['name']

        priority_name = priority['name'] if priority else 'None'

        if priority_name in ['Highest', 'Critical']:
            critical.append(ticket)
        elif priority_name == 'High':
            high_priority.append(ticket)

        if status not in ['Resolved', 'Closed', 'Done']:
            open_tickets.append(ticket)

    def ticket_rows(tickets, max_show=5):
        if not tickets:
            return '<tr><td colspan="4" style="padding: 15px; text-align: center; color: #666; font-style: italic;">No tickets found</td></tr>'

        rows = ""
        for ticket in tickets[:max_show]:
            key = ticket['key']
            summary = ticket['fields']['summary']
            if len(summary) > 60:
                summary = summary[:57] + "..."

            status = ticket['fields']['status']['name']
            priority = ticket['fields']['priority']['name'] if ticket['fields']['priority'] else 'None'

            priority_colors = {
                'Highest': '#dc3545', 'Critical': '#dc3545',
                'High': '#fd7e14', 'Medium': '#ffc107',
                'Low': '#28a745', 'Lowest': '#17a2b8'
            }
            color = priority_colors.get(priority, '#6c757d')

            rows += f'''
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 10px;">
                    <a href="https://adgear.atlassian.net/browse/{key}" style="color: #007bff; text-decoration: none; font-weight: bold;">{key}</a>
                </td>
                <td style="padding: 10px; line-height: 1.4;">{summary}</td>
                <td style="padding: 10px; text-align: center;">
                    <span style="background: {color}; color: white; padding: 3px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;">{priority}</span>
                </td>
                <td style="padding: 10px;">{status}</td>
            </tr>
            '''

        return rows

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Pixel Dashboard Report</title>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f4f5f7;">

        <div style="max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">🔥 Pixel Dashboard Report</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{today}</p>
            </div>

            <!-- Stats -->
            <div style="padding: 30px; background: #f8f9fa; border-bottom: 1px solid #dee2e6;">
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
                    <div style="text-align: center; padding: 20px; background: white; border-radius: 8px; min-width: 120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; font-weight: bold; color: #007bff;">{total_count}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">Total Pixel Issues</div>
                    </div>
                    <div style="text-align: center; padding: 20px; background: white; border-radius: 8px; min-width: 120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; font-weight: bold; color: #dc3545;">{len(critical)}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">Critical</div>
                    </div>
                    <div style="text-align: center; padding: 20px; background: white; border-radius: 8px; min-width: 120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; font-weight: bold; color: #fd7e14;">{len(high_priority)}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">High Priority</div>
                    </div>
                    <div style="text-align: center; padding: 20px; background: white; border-radius: 8px; min-width: 120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; font-weight: bold; color: #28a745;">{len(open_tickets)}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 5px;">Open</div>
                    </div>
                </div>
            </div>

            <!-- Quick Links -->
            <div style="padding: 20px 30px; background: #e9ecef; text-align: center;">
                <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block;">🔗 Full Dashboard</a>
                <a href="https://adgear.atlassian.net/projects/PS/issues" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block;">📋 PS Project</a>
            </div>

            <!-- Critical Issues -->
            <div style="padding: 30px;">
                <h2 style="color: #dc3545; margin-bottom: 15px; border-bottom: 2px solid #dc3545; padding-bottom: 5px;">🚨 Critical Issues ({len(critical)})</h2>
                <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 5px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;">Key</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;">Summary</th>
                            <th style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">Priority</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ticket_rows(critical)}
                    </tbody>
                </table>
            </div>

            <!-- Recent Issues -->
            <div style="padding: 0 30px 30px 30px;">
                <h2 style="color: #007bff; margin-bottom: 15px; border-bottom: 2px solid #007bff; padding-bottom: 5px;">📋 All Recent Pixel Issues ({total_count})</h2>
                <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 5px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;">Key</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;">Summary</th>
                            <th style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">Priority</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ticket_rows(pixel_tickets, max_show=10)}
                    </tbody>
                </table>
                {f'<p style="margin-top: 10px; color: #666; font-size: 13px; font-style: italic;">Showing first 10 of {total_count} tickets</p>' if total_count > 10 else ''}
            </div>

            <!-- Footer -->
            <div style="background: #343a40; color: white; padding: 20px; text-align: center;">
                <p style="margin: 0; font-size: 14px;">
                    Generated by Pixel Monitoring System • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="color: #adb5bd;">View Dashboard</a> |
                    <a href="https://adgear.atlassian.net/projects/PS" style="color: #adb5bd;">PS Project</a>
                </p>
            </div>

        </div>
    </body>
    </html>
    '''

    return html

def send_dashboard_email():
    """Generate and send dashboard email"""

    logger.info("🚀 Starting Email Dashboard Generation...")

    # Get pixel tickets
    pixel_tickets = get_pixel_tickets()

    # Generate HTML
    html_content = generate_email_html(pixel_tickets)

    # Save to file
    filename = f"email_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"📄 Dashboard saved to: {filename}")

    # Email configuration
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'from_email': 'l.spahn@samsung.com',
        'to_emails': ['l.spahn@samsung.com'],
        'password': os.getenv('EMAIL_PASSWORD', '')
    }

    # Send email if password configured
    if EMAIL_CONFIG['password']:
        try:
            logger.info("📧 Sending dashboard email...")

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔥 Pixel Dashboard Report - {datetime.now().strftime('%B %d, %Y')} ({len(pixel_tickets)} issues)"
            msg['From'] = EMAIL_CONFIG['from_email']
            msg['To'] = ', '.join(EMAIL_CONFIG['to_emails'])

            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['password'])
            server.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['to_emails'], msg.as_string())
            server.quit()

            logger.info("✅ EMAIL SENT SUCCESSFULLY!")
            logger.info("📬 Check your inbox for the pixel dashboard report")

            return True

        except Exception as e:
            logger.error(f"❌ Email failed: {e}")
            if '535' in str(e):
                logger.error("💡 Authentication failed - check your email password")
            elif '550' in str(e):
                logger.error("💡 Email blocked - check recipient address")
            return False
    else:
        logger.info("💡 No email password configured")
        logger.info("💡 Report saved to HTML file - you can open it manually")
        return False

def main():
    """Main function"""
    success = send_dashboard_email()

    if success:
        print(f"""
🎉 SUCCESS! Dashboard email sent to your inbox!

📧 Email: l.spahn@samsung.com
📊 Check your email for the pixel dashboard report
🔄 To run daily: Add to cron at 8 AM

✅ Everything is working properly!
""")
    else:
        print(f"""
📄 Dashboard HTML report generated successfully!

🌐 Open the file to view: email_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html
💡 Email not sent - check password configuration
📧 Once email is working, you'll get daily dashboard reports!
""")

if __name__ == "__main__":
    main()