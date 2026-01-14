#!/usr/bin/env python3
"""
Pixel Monitoring System - Main Interface
Simplified interface to your proven pixel monitoring system.
"""

import sys
import os
sys.path.append('core')
sys.path.append('dashboard')

def main():
    """Main interface for pixel monitoring system"""

    if len(sys.argv) < 2:
        print("""
🔥 Pixel Monitoring System

Usage:
  python3 pixel_monitor.py [command]

Commands:
  status      - Check system status and recent alerts
  dashboard   - Generate HTML dashboard report
  email       - Generate and email dashboard report
  test        - Test system connectivity

Configuration:
  source config/config_private.sh  # Load credentials

Examples:
  python3 pixel_monitor.py status
  python3 pixel_monitor.py dashboard
  python3 pixel_monitor.py email
        """)
        return

    command = sys.argv[1].lower()

    if command == "status":
        run_status_check()
    elif command == "dashboard":
        generate_dashboard()
    elif command == "email":
        email_dashboard()
    elif command == "test":
        test_system()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python3 pixel_monitor.py' for help")

def run_status_check():
    """Run system status check"""
    try:
        from core.pixel_notification_monitor import search_recent_tickets, is_pixel_related_ticket
        import logging

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        logger = logging.getLogger(__name__)

        print("🔍 Running pixel monitoring status check...")

        # Get recent tickets
        recent_tickets = search_recent_tickets()
        if recent_tickets is None:
            print("❌ Failed to connect to Jira API")
            return

        print(f"✅ Connected to Jira API - Found {len(recent_tickets)} recent tickets")

        # Filter for pixel tickets
        pixel_tickets = []
        for ticket in recent_tickets:
            summary = ticket['fields']['summary']
            description = ticket['fields'].get('description', '')

            # Handle rich text description
            desc_text = ""
            if isinstance(description, dict) and 'content' in description:
                for content in description['content']:
                    if content.get('type') == 'paragraph' and 'content' in content:
                        for text_content in content['content']:
                            if text_content.get('type') == 'text':
                                desc_text += text_content.get('text', '') + " "
            else:
                desc_text = str(description) if description else ""

            is_pixel_related, reason = is_pixel_related_ticket(summary, desc_text)
            if is_pixel_related:
                pixel_tickets.append(ticket)

        print(f"🎯 Found {len(pixel_tickets)} pixel-related tickets")

        # Show recent pixel tickets
        if pixel_tickets:
            print("\n📋 Recent Pixel Issues:")
            for ticket in pixel_tickets[:5]:  # Show first 5
                key = ticket['key']
                summary = ticket['fields']['summary']
                status = ticket['fields']['status']['name']
                print(f"  • {key}: {summary[:60]}{'...' if len(summary) > 60 else ''} [{status}]")

        print("\n✅ Status check completed successfully!")

    except Exception as e:
        print(f"❌ Status check failed: {e}")

def generate_dashboard():
    """Generate HTML dashboard report"""
    try:
        # Import from the organized dashboard directory
        import subprocess
        result = subprocess.run([
            sys.executable, 'dashboard/email_dashboard.py'
        ], cwd=os.getcwd(), capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Dashboard generated successfully!")
            print(result.stdout)
        else:
            print("❌ Dashboard generation failed:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")

def email_dashboard():
    """Generate and email dashboard report"""
    try:
        print("📧 Generating and sending dashboard email...")
        generate_dashboard()  # This also handles emailing

    except Exception as e:
        print(f"❌ Email dashboard failed: {e}")

def test_system():
    """Test system connectivity"""
    try:
        from core.pixel_notification_monitor import search_recent_tickets

        print("🧪 Testing system connectivity...")

        # Test Jira connection
        tickets = search_recent_tickets()
        if tickets is not None:
            print(f"✅ Jira API connection: Working ({len(tickets)} tickets)")
        else:
            print("❌ Jira API connection: Failed")
            return

        # Test email configuration
        password = os.getenv('EMAIL_PASSWORD', '')
        if password:
            print("✅ Email configuration: Configured")
        else:
            print("⚠️  Email configuration: Not configured")
            print("   Set EMAIL_PASSWORD environment variable to enable email")

        print("\n🎉 System test completed!")

    except Exception as e:
        print(f"❌ System test failed: {e}")

if __name__ == "__main__":
    main()