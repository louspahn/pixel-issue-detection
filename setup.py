#!/usr/bin/env python3
"""
Pixel Monitoring System - Setup and Configuration
Helper script to set up your organized pixel monitoring system.
"""

import os
import sys
import subprocess

def main():
    """Setup and configuration helper"""

    if len(sys.argv) < 2:
        print("""
🔧 Pixel Monitoring System - Setup

Usage:
  python3 setup.py [command]

Commands:
  install     - Install/check dependencies
  config      - Check configuration
  test        - Test system setup
  daily       - Setup daily cron job
  help        - Show detailed help

Examples:
  python3 setup.py config
  python3 setup.py test
        """)
        return

    command = sys.argv[1].lower()

    if command == "install":
        install_dependencies()
    elif command == "config":
        check_configuration()
    elif command == "test":
        test_setup()
    elif command == "daily":
        setup_daily_cron()
    elif command == "help":
        show_detailed_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python3 setup.py' for help")

def install_dependencies():
    """Check and install required dependencies"""
    print("📦 Checking Python dependencies...")

    required_packages = ['requests']

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - installed")
        except ImportError:
            print(f"  ❌ {package} - missing")
            print(f"     Install with: pip install {package}")

def check_configuration():
    """Check system configuration"""
    print("🔍 Checking system configuration...\n")

    # Check directory structure
    print("📁 Directory Structure:")
    dirs = ['core', 'dashboard', 'config', 'archive', 'reports']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - missing")

    # Check key files
    print("\n📄 Key Files:")
    files = [
        ('core/pixel_notification_monitor.py', 'Core monitoring system'),
        ('dashboard/email_dashboard.py', 'Dashboard generator'),
        ('config/config_private.sh', 'Configuration file'),
        ('pixel_monitor.py', 'Main interface')
    ]

    for file_path, description in files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} - {description}")
        else:
            print(f"  ❌ {file_path} - {description} (missing)")

    # Check environment variables
    print("\n🔧 Environment Configuration:")

    # Check if config exists
    config_path = 'config/config_private.sh'
    if os.path.exists(config_path):
        print(f"  ✅ Configuration file exists: {config_path}")

        # Read config file to check variables
        with open(config_path, 'r') as f:
            content = f.read()

        if 'JIRA_TOKEN=' in content:
            print("  ✅ JIRA_TOKEN configured")
        else:
            print("  ❌ JIRA_TOKEN not found in config")

        if 'EMAIL_PASSWORD=' in content:
            print("  ✅ EMAIL_PASSWORD configured")
        else:
            print("  ⚠️  EMAIL_PASSWORD not configured (email disabled)")
    else:
        print(f"  ❌ Configuration file missing: {config_path}")
        print("     Copy your credentials to this file")

def test_setup():
    """Test the complete system setup"""
    print("🧪 Testing system setup...\n")

    # Test loading configuration
    print("1. Testing configuration loading...")
    try:
        config_path = 'config/config_private.sh'
        if os.path.exists(config_path):
            result = subprocess.run(['bash', '-c', f'source {config_path} && echo "JIRA_TOKEN: ${{JIRA_TOKEN:+CONFIGURED}}" && echo "EMAIL_PASSWORD: ${{EMAIL_PASSWORD:+CONFIGURED}}"'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Configuration loads successfully")
                print(f"  {result.stdout.strip()}")
            else:
                print("  ❌ Configuration loading failed")
        else:
            print("  ❌ Configuration file not found")
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")

    # Test core system
    print("\n2. Testing core pixel monitoring...")
    try:
        result = subprocess.run([
            'bash', '-c',
            'source config/config_private.sh && python3 pixel_monitor.py test'
        ], capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            print("  ✅ Core system test passed")
            print(f"  {result.stdout.strip()}")
        else:
            print("  ❌ Core system test failed")
            print(f"  Error: {result.stderr.strip()}")

    except Exception as e:
        print(f"  ❌ Core system test error: {e}")

def setup_daily_cron():
    """Help set up daily cron job"""
    current_dir = os.getcwd()

    print("⏰ Setting up daily cron job for pixel dashboard...\n")

    cron_command = f'0 8 * * * cd "{current_dir}" && source config/config_private.sh && python3 pixel_monitor.py email'

    print("Add this line to your crontab (run 'crontab -e'):")
    print(f"\n  {cron_command}\n")

    print("This will:")
    print("  • Run at 8:00 AM daily")
    print("  • Load your configuration")
    print("  • Generate and email the pixel dashboard")

    print("\nTo edit crontab:")
    print("  1. Run: crontab -e")
    print("  2. Add the line above")
    print("  3. Save and exit")

    print("\nTo check cron jobs:")
    print("  Run: crontab -l")

def show_detailed_help():
    """Show detailed help and usage"""
    print("""
📖 Pixel Monitoring System - Detailed Help

DIRECTORY STRUCTURE:
  core/                     - Core monitoring system
  dashboard/                - Dashboard generation
  config/                   - Configuration files
  archive/                  - Archived/backup files
  reports/                  - Generated reports

MAIN COMMANDS:

  python3 pixel_monitor.py status
    - Check system status and recent pixel tickets
    - Shows connection status and recent issues

  python3 pixel_monitor.py dashboard
    - Generate HTML dashboard report
    - Saves to reports/ directory

  python3 pixel_monitor.py email
    - Generate and email dashboard report
    - Requires EMAIL_PASSWORD configuration

SETUP COMMANDS:

  python3 setup.py config
    - Check system configuration
    - Verify files and environment variables

  python3 setup.py test
    - Test complete system functionality
    - Verify Jira API connection and email setup

  python3 setup.py daily
    - Get help setting up daily cron job
    - Shows exact crontab commands to use

CONFIGURATION:

  1. Ensure config/config_private.sh exists with:
     export JIRA_TOKEN="your_jira_token"
     export JIRA_EMAIL="your_email"
     export EMAIL_PASSWORD="your_email_password"  # optional

  2. Load configuration before running:
     source config/config_private.sh

  3. Or run with configuration:
     bash -c 'source config/config_private.sh && python3 pixel_monitor.py status'

DAILY AUTOMATION:

  Set up cron job to run daily dashboard emails:

  crontab -e
  # Add line:
  0 8 * * * cd "/path/to/system" && source config/config_private.sh && python3 pixel_monitor.py email

TROUBLESHOOTING:

  • JIRA API issues: Check token and email in config
  • Email issues: Verify EMAIL_PASSWORD and network access
  • Import errors: Check Python path and file organization
  • Permission errors: Ensure files are executable
    """)

if __name__ == "__main__":
    main()