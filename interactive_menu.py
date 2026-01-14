#!/usr/bin/env python3
"""
Interactive Pixel Monitoring System Menu
Beautiful terminal interface for all system operations.
"""

import os
import sys
import subprocess
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear')

def print_header():
    """Print colorful header"""
    print("\033[1;36m" + "="*60)
    print("🔥 PIXEL MONITORING SYSTEM - INTERACTIVE MENU")
    print("="*60 + "\033[0m")
    print(f"\033[1;33m📍 Directory:\033[0m {os.getcwd()}")
    print(f"\033[1;33m📅 Time:\033[0m {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\033[1;33m👤 User:\033[0m {os.getenv('USER', 'Unknown')}")
    print()

def print_menu():
    """Print the main menu options"""
    print("\033[1;32m📊 MAIN SYSTEM COMMANDS:\033[0m")
    print("  \033[0;36m1)\033[0m System Status Check         \033[0;90m(Check recent pixel issues)\033[0m")
    print("  \033[0;36m2)\033[0m Generate Dashboard          \033[0;90m(Create HTML report)\033[0m")
    print("  \033[0;36m3)\033[0m Email Dashboard             \033[0;90m(Generate & email report)\033[0m")
    print("  \033[0;36m4)\033[0m Test System                 \033[0;90m(Test API connections)\033[0m")
    print()
    print("\033[1;32m🔧 SETUP & CONFIGURATION:\033[0m")
    print("  \033[0;36m5)\033[0m Check Configuration         \033[0;90m(Verify system setup)\033[0m")
    print("  \033[0;36m6)\033[0m Test All Functionality      \033[0;90m(Complete system test)\033[0m")
    print("  \033[0;36m7)\033[0m Setup Daily Automation      \033[0;90m(Get cron instructions)\033[0m")
    print("  \033[0;36m8)\033[0m View Help Guide             \033[0;90m(Detailed documentation)\033[0m")
    print()
    print("\033[1;32m📁 FILE OPERATIONS:\033[0m")
    print("  \033[0;36m9)\033[0m View Generated Reports       \033[0;90m(List HTML files)\033[0m")
    print("  \033[0;36m10)\033[0m Open Latest Dashboard       \033[0;90m(Open in browser)\033[0m")
    print("  \033[0;36m11)\033[0m View System Configuration   \033[0;90m(Show config file)\033[0m")
    print()
    print("\033[1;32m🚨 ALERT MONITORING:\033[0m")
    print("  \033[0;36m12)\033[0m Start Alert Monitor          \033[0;90m(Alert-only, no dashboards)\033[0m")
    print("  \033[0;36m13)\033[0m View Alert Logs              \033[0;90m(Show alert history)\033[0m")
    print()
    print("\033[1;32m🎯 SPECIAL ACTIONS:\033[0m")
    print("  \033[0;36m14)\033[0m Complete System Demo        \033[0;90m(Run full demonstration)\033[0m")
    print("  \033[0;36m15)\033[0m Direct Dashboard Generation  \033[0;90m(Bypass main interface)\033[0m")
    print("  \033[0;36m16)\033[0m System Health Summary       \033[0;90m(Quick overview)\033[0m")
    print()
    print("  \033[0;36m0)\033[0m Exit")
    print()

def run_command(command, description="Running command"):
    """Run a system command and display results"""
    print(f"\033[1;33m🔄 {description}...\033[0m")
    print("\033[0;90m" + "─" * 50 + "\033[0m")

    try:
        # Change to the correct directory and run command
        result = subprocess.run(
            f'cd "/Users/l.spahn/Performance Pixel Monitoring System" && source config/config_private.sh && {command}',
            shell=True,
            capture_output=True,
            text=True,
            executable='/bin/bash'
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"\033[1;31mError:\033[0m {result.stderr}")

        print("\033[0;90m" + "─" * 50 + "\033[0m")

        if result.returncode == 0:
            print("\033[1;32m✅ Command completed successfully!\033[0m")
        else:
            print(f"\033[1;31m❌ Command failed with exit code {result.returncode}\033[0m")

    except Exception as e:
        print(f"\033[1;31m❌ Error executing command: {e}\033[0m")

def wait_for_continue():
    """Wait for user to press enter"""
    print()
    input("\033[1;34mPress Enter to continue...\033[0m")

def main():
    """Main interactive loop"""

    # Ensure we're in the right directory
    target_dir = "/Users/l.spahn/Performance Pixel Monitoring System"
    if not os.path.exists(target_dir):
        print(f"\033[1;31m❌ Error: Directory not found: {target_dir}\033[0m")
        sys.exit(1)

    os.chdir(target_dir)

    while True:
        clear_screen()
        print_header()
        print_menu()

        try:
            choice = input("\033[1;35mEnter your choice (0-16): \033[0m").strip()

            if choice == "0":
                print("\033[1;36m👋 Thanks for using Pixel Monitoring System!\033[0m")
                break

            elif choice == "1":
                clear_screen()
                print_header()
                run_command("python3 pixel_monitor.py status", "Checking system status")
                wait_for_continue()

            elif choice == "2":
                clear_screen()
                print_header()
                run_command("python3 pixel_monitor.py dashboard", "Generating HTML dashboard")
                wait_for_continue()

            elif choice == "3":
                clear_screen()
                print_header()
                run_command("python3 pixel_monitor.py email", "Generating and emailing dashboard")
                wait_for_continue()

            elif choice == "4":
                clear_screen()
                print_header()
                run_command("python3 pixel_monitor.py test", "Testing system connections")
                wait_for_continue()

            elif choice == "5":
                clear_screen()
                print_header()
                run_command("python3 setup.py config", "Checking system configuration")
                wait_for_continue()

            elif choice == "6":
                clear_screen()
                print_header()
                run_command("python3 setup.py test", "Testing complete functionality")
                wait_for_continue()

            elif choice == "7":
                clear_screen()
                print_header()
                run_command("python3 setup.py daily", "Getting daily automation setup")
                wait_for_continue()

            elif choice == "8":
                clear_screen()
                print_header()
                run_command("python3 setup.py help", "Displaying detailed help")
                wait_for_continue()

            elif choice == "9":
                clear_screen()
                print_header()
                run_command("ls -la reports/", "Listing generated reports")
                wait_for_continue()

            elif choice == "10":
                clear_screen()
                print_header()
                run_command("ls -la reports/*.html | tail -3 && open reports/email_dashboard_*.html 2>/dev/null || echo 'No HTML reports found'", "Opening latest dashboard")
                wait_for_continue()

            elif choice == "11":
                clear_screen()
                print_header()
                run_command("echo '📄 Configuration File Contents:' && cat config/config_private.sh", "Displaying configuration")
                wait_for_continue()

            elif choice == "12":
                clear_screen()
                print_header()
                print("\033[1;33m🚨 Starting Pixel Alert Monitor...\033[0m")
                print("This will start alert-only monitoring - NO dashboards generated.")
                print("You'll get sound + visual alerts when new pixel issues are detected.")
                print("Press Ctrl+C to stop the alert monitor when you're done.")
                print()
                input("Press Enter to continue or Ctrl+C to cancel...")

                # Execute continuous monitor
                try:
                    subprocess.run([sys.executable, 'continuous_monitor.py'], cwd=os.getcwd())
                except KeyboardInterrupt:
                    print("\n\033[1;36m👋 Continuous monitoring cancelled\033[0m")
                except Exception as e:
                    print(f"\033[1;31m❌ Failed to start continuous monitoring: {e}\033[0m")

                wait_for_continue()

            elif choice == "13":
                clear_screen()
                print_header()
                print("\033[1;33m📝 Pixel Alert Log Viewer\033[0m")
                print("\033[0;90m" + "─" * 50 + "\033[0m")

                try:
                    if os.path.exists('pixel_alerts.log'):
                        with open('pixel_alerts.log', 'r') as f:
                            lines = f.readlines()

                        if lines:
                            print(f"\033[1;32m📋 Found {len(lines)} alert(s) in log file:\033[0m\n")

                            # Show all alerts with formatting
                            for i, line in enumerate(lines, 1):
                                line = line.strip()
                                if line:
                                    # Parse the alert line
                                    parts = line.split(' - ALERT: ')
                                    if len(parts) == 2:
                                        timestamp = parts[0]
                                        alert_msg = parts[1]

                                        # Format timestamp
                                        try:
                                            from datetime import datetime
                                            dt = datetime.fromisoformat(timestamp)
                                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                                        except:
                                            formatted_time = timestamp

                                        print(f"\033[1;31m🚨 Alert #{i}\033[0m")
                                        print(f"   \033[1;33m⏰ Time:\033[0m {formatted_time}")
                                        print(f"   \033[1;33m📈 Change:\033[0m {alert_msg}")
                                        print()
                                    else:
                                        print(f"\033[0;90m{i}. {line}\033[0m")

                            # Show summary
                            print("\033[0;90m" + "─" * 50 + "\033[0m")
                            print(f"\033[1;32m📊 Summary: {len(lines)} total alerts logged\033[0m")

                            # Offer to clear logs
                            print()
                            clear_logs = input("\033[1;35mClear all logs? (y/n): \033[0m").strip().lower()
                            if clear_logs == 'y':
                                os.remove('pixel_alerts.log')
                                print("\033[1;32m✅ Alert logs cleared\033[0m")

                        else:
                            print("\033[1;33m📝 Alert log file exists but is empty\033[0m")
                            print("No alerts have been logged yet.")
                    else:
                        print("\033[1;33m📝 No alert log file found\033[0m")
                        print("No alerts have been logged yet.")
                        print("Start the Alert Monitor (option 12) to begin logging alerts.")

                except Exception as e:
                    print(f"\033[1;31m❌ Error reading alert log: {e}\033[0m")

                print("\033[0;90m" + "─" * 50 + "\033[0m")
                wait_for_continue()

            elif choice == "14":
                clear_screen()
                print_header()
                print("\033[1;33m🚀 Running Complete System Demo...\033[0m")
                print()
                run_command("python3 setup.py config", "1/4: Checking configuration")
                print()
                run_command("python3 pixel_monitor.py status", "2/4: Checking status")
                print()
                run_command("python3 pixel_monitor.py dashboard", "3/4: Generating dashboard")
                print()
                run_command("ls -la reports/ | tail -3", "4/4: Showing results")
                print("\033[1;32m🎉 Complete system demo finished!\033[0m")
                wait_for_continue()

            elif choice == "14":
                clear_screen()
                print_header()
                run_command("python3 dashboard/email_dashboard.py", "Running direct dashboard generation")
                wait_for_continue()

            elif choice == "15":
                clear_screen()
                print_header()
                print("\033[1;33m📊 System Health Summary\033[0m")
                print("\033[0;90m" + "─" * 30 + "\033[0m")

                # Quick health checks
                checks = [
                    ("📁 Directory Structure", "ls -d core dashboard config archive reports 2>/dev/null | wc -l | xargs test 5 -eq && echo '✅ Complete' || echo '❌ Missing dirs'"),
                    ("🔧 Configuration", "test -f config/config_private.sh && echo '✅ Found' || echo '❌ Missing'"),
                    ("🧠 Core System", "test -f core/pixel_notification_monitor.py && echo '✅ Found' || echo '❌ Missing'"),
                    ("📊 Dashboard", "test -f dashboard/email_dashboard.py && echo '✅ Found' || echo '❌ Missing'"),
                    ("📈 Recent Reports", "ls reports/*.html 2>/dev/null | wc -l | sed 's/^/📄 /' || echo '📄 0 reports'")
                ]

                for check_name, check_cmd in checks:
                    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                    print(f"{check_name}: {result.stdout.strip()}")

                print("\033[0;90m" + "─" * 30 + "\033[0m")
                wait_for_continue()

            else:
                print(f"\033[1;31m❌ Invalid choice: {choice}\033[0m")
                print("Please enter a number between 0-15")
                wait_for_continue()

        except KeyboardInterrupt:
            print("\n\033[1;36m👋 Goodbye!\033[0m")
            break
        except Exception as e:
            print(f"\033[1;31m❌ An error occurred: {e}\033[0m")
            wait_for_continue()

if __name__ == "__main__":
    main()