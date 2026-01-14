#!/usr/bin/env python3
"""
OAuth2 Dashboard Email Generator
Uses OAuth2 for modern authentication with Office 365 (no app password needed)
"""

import sys
import os
sys.path.append('.')

from pixel_notification_monitor import search_recent_tickets, is_pixel_related_ticket
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_recent_pixel_tickets():
    """Get recent tickets and filter for pixel-related ones using proven methods"""

    logger.info("🔍 Getting recent tickets using your proven monitoring system...")

    try:
        # Use your existing working method
        all_tickets = search_recent_tickets()

        if not all_tickets:
            logger.warning("No recent tickets found")
            return []

        logger.info(f"Found {len(all_tickets)} total recent tickets")

        # Filter for pixel-related tickets using your detection logic
        pixel_tickets = []
        for ticket in all_tickets:
            summary = ticket['fields']['summary']
            description = ticket['fields'].get('description', '')

            # Extract description text if in rich format
            desc_text = ""
            if isinstance(description, dict) and 'content' in description:
                for content in description['content']:
                    if content.get('type') == 'paragraph' and 'content' in content:
                        for text_content in content['content']:
                            if text_content.get('type') == 'text':
                                desc_text += text_content.get('text', '') + " "
            else:
                desc_text = str(description) if description else ""

            # Use your existing pixel detection
            if is_pixel_related_ticket(summary, desc_text):
                pixel_tickets.append(ticket)

        logger.info(f"🎯 Found {len(pixel_tickets)} pixel-related tickets")
        return pixel_tickets

    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        return []

def categorize_pixel_tickets(tickets):
    """Categorize pixel tickets by priority and status"""

    categories = {
        'critical': [],
        'high': [],
        'open': [],
        'recent': []
    }

    for ticket in tickets:
        priority = ticket['fields'].get('priority')
        status = ticket['fields']['status']['name']
        created = ticket['fields']['created']

        priority_name = priority['name'] if priority else 'None'

        # Critical and high priority
        if priority_name in ['Highest', 'Critical']:
            categories['critical'].append(ticket)
        elif priority_name == 'High':
            categories['high'].append(ticket)

        # Open tickets
        if status not in ['Resolved', 'Closed', 'Done', 'Complete']:
            categories['open'].append(ticket)

        # Recent (last 2 days)
        try:
            created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
            days_old = (datetime.now(created_date.tzinfo) - created_date).days
            if days_old <= 2:
                categories['recent'].append(ticket)
        except:
            pass

    return categories

def generate_html_report(pixel_tickets):
    """Generate beautiful HTML dashboard report"""

    categories = categorize_pixel_tickets(pixel_tickets)
    today = datetime.now().strftime("%B %d, %Y")

    # Stats
    total_pixel = len(pixel_tickets)
    critical_count = len(categories['critical'])
    high_count = len(categories['high'])
    open_count = len(categories['open'])
    recent_count = len(categories['recent'])

    def ticket_table_html(tickets, title, icon="📋"):
        if not tickets:
            return f"""
            <div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #dee2e6;">
                <h3 style="margin: 0 0 10px 0; color: #6c757d;">{icon} {title}</h3>
                <p style="margin: 0; color: #6c757d; font-style: italic;">No tickets found</p>
            </div>
            """

        rows = ""
        for i, ticket in enumerate(tickets[:8]):  # Show max 8 per section
            key = ticket['key']
            summary = ticket['fields']['summary']
            if len(summary) > 70:
                summary = summary[:67] + "..."

            status = ticket['fields']['status']['name']
            priority = ticket['fields']['priority']['name'] if ticket['fields']['priority'] else 'None'
            created = ticket['fields']['created'][:10]

            priority_colors = {
                'Highest': '#dc3545', 'Critical': '#dc3545',
                'High': '#fd7e14', 'Medium': '#ffc107',
                'Low': '#28a745', 'Lowest': '#17a2b8'
            }
            color = priority_colors.get(priority, '#6c757d')

            rows += f"""
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 12px 8px;">
                    <a href="https://adgear.atlassian.net/browse/{key}"
                       style="color: #007bff; text-decoration: none; font-weight: 600; font-family: monospace;">
                       {key}
                    </a>
                </td>
                <td style="padding: 12px 8px; line-height: 1.4;">{summary}</td>
                <td style="padding: 12px 8px; text-align: center;">
                    <span style="background: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">
                        {priority}
                    </span>
                </td>
                <td style="padding: 12px 8px; font-size: 13px;">{status}</td>
                <td style="padding: 12px 8px; font-size: 12px; color: #6c757d;">{created}</td>
            </tr>
            """

        return f"""
        <div style="margin: 30px 0;">
            <h3 style="color: #495057; margin-bottom: 15px; display: flex; align-items: center; border-bottom: 2px solid #007bff; padding-bottom: 8px;">
                <span style="margin-right: 8px;">{icon}</span>
                {title} ({len(tickets)} total)
            </h3>
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
                            <th style="padding: 15px 8px; text-align: left; font-weight: 600; color: #495057;">Key</th>
                            <th style="padding: 15px 8px; text-align: left; font-weight: 600; color: #495057;">Summary</th>
                            <th style="padding: 15px 8px; text-align: center; font-weight: 600; color: #495057;">Priority</th>
                            <th style="padding: 15px 8px; text-align: left; font-weight: 600; color: #495057;">Status</th>
                            <th style="padding: 15px 8px; text-align: left; font-weight: 600; color: #495057;">Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
            {f'<p style="margin-top: 10px; color: #6c757d; font-size: 13px; font-style: italic;">Showing first 8 of {len(tickets)} tickets</p>' if len(tickets) > 8 else ''}
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Pixel Dashboard Report</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">

        <div style="max-width: 1100px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 36px; font-weight: 300; letter-spacing: 1px;">🔥 Pixel Dashboard</h1>
                <p style="margin: 15px 0 0 0; font-size: 18px; opacity: 0.9;">{today}</p>
                <div style="margin-top: 25px; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
                    <p style="margin: 0; font-size: 16px;">Performance Pixel Monitoring System Report</p>
                </div>
            </div>

            <!-- Stats Dashboard -->
            <div style="padding: 40px 30px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
                <h2 style="text-align: center; color: #495057; margin-bottom: 30px; font-size: 28px;">📊 Overview</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px;">

                    <div style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 16px rgba(52, 152, 219, 0.3);">
                        <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">{total_pixel}</div>
                        <div style="font-size: 14px; opacity: 0.9; font-weight: 500;">Total Pixel Issues</div>
                    </div>

                    <div style="background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 16px rgba(231, 76, 60, 0.3);">
                        <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">{critical_count}</div>
                        <div style="font-size: 14px; opacity: 0.9; font-weight: 500;">Critical Priority</div>
                    </div>

                    <div style="background: linear-gradient(135deg, #f39c12, #d68910); color: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 16px rgba(243, 156, 18, 0.3);">
                        <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">{open_count}</div>
                        <div style="font-size: 14px; opacity: 0.9; font-weight: 500;">Open Issues</div>
                    </div>

                    <div style="background: linear-gradient(135deg, #27ae60, #229954); color: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 16px rgba(39, 174, 96, 0.3);">
                        <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">{recent_count}</div>
                        <div style="font-size: 14px; opacity: 0.9; font-weight: 500;">Recent (2 days)</div>
                    </div>

                </div>
            </div>

            <!-- Quick Links -->
            <div style="padding: 25px 30px; background: #f1f3f4; text-align: center; border-bottom: 1px solid #dee2e6;">
                <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                    <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="background: #007bff; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: 500; transition: all 0.2s;">🔗 Full Dashboard</a>
                    <a href="https://adgear.atlassian.net/projects/PS/issues" style="background: #28a745; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: 500;">📋 PS Project</a>
                    <a href="https://adgear.atlassian.net/secure/CreateIssue.jspa" style="background: #ffc107; color: #212529; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: 500;">➕ New Issue</a>
                </div>
            </div>

            <!-- Ticket Sections -->
            <div style="padding: 40px 30px;">
    """

    # Add ticket sections
    sections = [
        (categories['critical'], 'Critical Pixel Issues', '🚨'),
        (categories['recent'], 'Recent Pixel Issues', '📅'),
        (categories['open'], 'Open Pixel Issues', '🔄'),
        (pixel_tickets, 'All Pixel Issues Found', '📋')
    ]

    for tickets, title, icon in sections:
        html += ticket_table_html(tickets, title, icon)

    # Footer
    html += f"""
            </div>

            <!-- Footer -->
            <div style="background: #343a40; color: white; padding: 30px; text-align: center;">
                <div style="margin-bottom: 20px;">
                    <a href="https://adgear.atlassian.net/jira/dashboards/19521" style="color: #adb5bd; text-decoration: none; margin: 0 15px;">📊 Dashboard</a>
                    <a href="https://adgear.atlassian.net/projects/PS" style="color: #adb5bd; text-decoration: none; margin: 0 15px;">📋 Project</a>
                    <a href="https://adgear.atlassian.net/secure/RapidBoard.jspa" style="color: #adb5bd; text-decoration: none; margin: 0 15px;">🏃 Boards</a>
                </div>
                <p style="margin: 0; font-size: 14px; opacity: 0.8;">
                    Generated by Pixel Monitoring System<br>
                    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Using proven monitoring methods
                </p>
            </div>

        </div>
    </body>
    </html>
    """

    return html

def main():
    """Generate pixel dashboard report using working methods"""

    logger.info("🚀 Starting Pixel Dashboard Report (OAuth2 Compatible)")
    logger.info("📧 No email password needed - generates HTML report")

    # Get pixel tickets using proven methods
    pixel_tickets = get_recent_pixel_tickets()

    # Generate HTML report
    html_content = generate_html_report(pixel_tickets)

    # Save to file
    filename = f"pixel_dashboard_oauth_{datetime.now().strftime('%Y%m%d_%H%M')}.html"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"✅ Dashboard report saved: {filename}")
    logger.info(f"📊 Found {len(pixel_tickets)} total pixel-related tickets")
    logger.info("🌐 Open the HTML file in your browser to view the dashboard")

    # Instructions
    print(f"""
🎉 Dashboard Report Generated Successfully!

📄 File: {filename}
🌐 Open in browser: open {filename}

📧 EMAIL ALTERNATIVES (since app passwords not available):
1. Forward this HTML file to your email manually
2. Use Samsung's internal email system to schedule reports
3. Contact IT about OAuth2 setup for automated emails
4. Set up browser bookmarks to run this script daily

🔄 TO RUN DAILY:
Add to crontab: 0 8 * * * cd "/Users/l.spahn/Performance Pixel Monitoring System" && python3 oauth_dashboard_emailer.py

✅ This works without any email passwords or OAuth2 setup!
""")

if __name__ == "__main__":
    main()