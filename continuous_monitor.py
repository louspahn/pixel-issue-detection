#!/usr/bin/env python3
"""
Continuous Pixel Monitoring System
Runs continuously, checking for pixel issues every X minutes.
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
import signal
import threading
import json

# Add paths for imports
sys.path.append('core')
sys.path.append('dashboard')

class ContinuousPixelMonitor:
    def __init__(self):
        self.running = True
        self.check_interval = 300  # 5 minutes default
        self.last_check = None
        self.last_ticket_count = 0
        self.alerts_enabled = True
        self.recent_alerts = []  # Store recent alerts for display
        self.paused = False  # Control display loop pausing
        self.pause_lock = threading.Lock()  # Thread synchronization for pausing

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear')

    def print_header(self):
        """Print monitoring header"""
        print("\033[1;36m" + "="*70)
        print("🚨 CONTINUOUS PIXEL ALERT MONITOR")
        print("="*70 + "\033[0m")
        print(f"\033[1;33m📍 Directory:\033[0m {os.getcwd()}")
        print(f"\033[1;33m📅 Started:\033[0m {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\033[1;33m⏰ Check Interval:\033[0m {self.check_interval//60} minutes ({self.check_interval} seconds)")
        print(f"\033[1;33m🚨 Alert Mode:\033[0m {'✅ Sound + Log' if self.alerts_enabled else '❌ Disabled'}")
        print(f"\033[1;33m📝 Log File:\033[0m pixel_alerts.log")

    def print_status_bar(self):
        """Print current status bar"""
        now = datetime.now()
        next_check = self.last_check + timedelta(seconds=self.check_interval) if self.last_check else now
        time_until_next = max(0, (next_check - now).total_seconds())

        # Progress bar for next check
        progress = max(0, min(100, (self.check_interval - time_until_next) / self.check_interval * 100))
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        print(f"\n\033[1;34m📊 STATUS:\033[0m")
        print(f"  ⏰ Next check in: \033[1;33m{int(time_until_next//60):02d}:{int(time_until_next%60):02d}\033[0m")
        print(f"  📊 Progress: [{bar}] {progress:.0f}%")
        print(f"  🎯 Last Count: \033[1;32m{self.last_ticket_count}\033[0m pixel tickets")
        if self.last_check:
            print(f"  🕒 Last Check: {self.last_check.strftime('%H:%M:%S')}")

    def run_pixel_check(self):
        """Run a pixel monitoring check"""
        try:
            print(f"\n\033[1;32m🔍 Running pixel check at {datetime.now().strftime('%H:%M:%S')}...\033[0m")
            print("\033[0;90m" + "─" * 50 + "\033[0m")

            # Run the status check
            result = subprocess.run([
                'bash', '-c',
                'source config/config_private.sh && python3 pixel_monitor.py status'
            ], capture_output=True, text=True, cwd=os.getcwd())

            if result.returncode == 0:
                output = result.stdout
                print(output)

                # Try to extract ticket count from output
                lines = output.split('\n')
                for line in lines:
                    if 'Found' in line and 'pixel-related tickets' in line:
                        try:
                            count = int([word for word in line.split() if word.isdigit()][0])

                            # Check for changes
                            if count != self.last_ticket_count:
                                if count > self.last_ticket_count:
                                    print(f"\033[1;31m🚨 ALERT: Pixel tickets increased from {self.last_ticket_count} to {count}!\033[0m")
                                    if self.alerts_enabled:
                                        self.send_alert(count, self.last_ticket_count)
                                else:
                                    print(f"\033[1;32m✅ GOOD: Pixel tickets decreased from {self.last_ticket_count} to {count}\033[0m")

                                self.last_ticket_count = count
                            break
                        except (IndexError, ValueError):
                            pass

                print("\033[1;32m✅ Check completed successfully\033[0m")
            else:
                print(f"\033[1;31m❌ Check failed: {result.stderr}\033[0m")

            self.last_check = datetime.now()
            print("\033[0;90m" + "─" * 50 + "\033[0m")

        except Exception as e:
            print(f"\033[1;31m❌ Error during check: {e}\033[0m")
            self.last_check = datetime.now()

    def train_alert(self, alert_index, is_correct):
        """Train the model on whether an alert was correct or not"""
        try:
            # Mark the alert as trained
            self.recent_alerts[alert_index]['trained'] = is_correct

            # Get alert details for training data
            alert = self.recent_alerts[alert_index]

            # Save training data to file
            training_entry = {
                'timestamp': alert['time'].isoformat(),
                'old_count': alert['old_count'],
                'new_count': alert['new_count'],
                'message': alert['message'],
                'is_correct': is_correct,
                'trained_at': datetime.now().isoformat()
            }

            # Append to training data file
            with open('pixel_training_data.json', 'a') as f:
                f.write(json.dumps(training_entry) + '\n')

        except Exception as e:
            print(f"\033[1;31m❌ Training failed: {e}\033[0m")

    def send_alert(self, new_count, old_count):
        """Send alert for ticket count increase - NO DASHBOARD GENERATION"""
        try:
            # Sound system alert (macOS)
            os.system('afplay /System/Library/Sounds/Ping.aiff 2>/dev/null &')

            # Store alert for persistent display
            alert_data = {
                'time': datetime.now(),
                'old_count': old_count,
                'new_count': new_count,
                'message': f"Pixel tickets increased from {old_count} to {new_count}"
            }
            self.recent_alerts.append(alert_data)

            # Keep only last 5 alerts
            if len(self.recent_alerts) > 5:
                self.recent_alerts = self.recent_alerts[-5:]

            # Display prominent alert
            print("\n" + "🚨" * 20)
            print(f"\033[1;31m🔥 PIXEL ALERT: New issues detected!\033[0m")
            print(f"\033[1;31m📈 Count increased from {old_count} to {new_count}\033[0m")
            print(f"\033[1;31m⏰ Time: {datetime.now().strftime('%H:%M:%S')}\033[0m")
            print("🚨" * 20 + "\n")

            # Log alert to file
            with open('pixel_alerts.log', 'a') as f:
                f.write(f"{datetime.now().isoformat()} - ALERT: Pixel tickets {old_count} -> {new_count}\n")

            print(f"\033[1;33m📝 Alert logged to: pixel_alerts.log\033[0m")

        except Exception as e:
            print(f"\033[1;31m❌ Alert failed: {e}\033[0m")

    def print_recent_alerts(self):
        """Display recent alerts persistently"""
        if self.recent_alerts:
            print(f"\n\033[1;31m🚨 RECENT ALERTS:\033[0m")
            for i, alert in enumerate(reversed(self.recent_alerts), 1):
                time_str = alert['time'].strftime('%H:%M:%S')
                age_minutes = int((datetime.now() - alert['time']).total_seconds() / 60)
                age_display = f"{age_minutes}m ago" if age_minutes > 0 else "just now"

                print(f"  \033[1;31m#{i}\033[0m \033[0;31m{alert['message']}\033[0m")
                print(f"      \033[0;90m⏰ {time_str} ({age_display})\033[0m")

    def print_detected_alerts(self):
        """Display detected alerts for training feedback"""
        if self.recent_alerts:
            print(f"\n\033[1;33m🎯 DETECTED ALERTS (Training Mode):\033[0m")
            for i, alert in enumerate(reversed(self.recent_alerts[-3:]), 1):  # Show last 3 alerts
                time_str = alert['time'].strftime('%H:%M:%S')
                age_minutes = int((datetime.now() - alert['time']).total_seconds() / 60)
                age_display = f"{age_minutes}m ago" if age_minutes > 0 else "just now"

                # Check if this alert has been trained
                trained_status = alert.get('trained', None)
                if trained_status is None:
                    status_color = "\033[0;33m"
                    status_text = "⏳ Awaiting feedback"
                elif trained_status:
                    status_color = "\033[0;32m"
                    status_text = "✅ Correct"
                else:
                    status_color = "\033[0;31m"
                    status_text = "❌ False positive"

                print(f"  \033[1;31m#{i}\033[0m \033[0;31m{alert['message']}\033[0m")
                print(f"      \033[0;90m⏰ {time_str} ({age_display})\033[0m")
                print(f"      {status_color}{status_text}\033[0m")

                # Show training commands if not yet trained
                if trained_status is None:
                    alert_id = len(self.recent_alerts) - (i-1)  # Calculate alert ID
                    print(f"      \033[0;36my{alert_id}\033[0m=correct  \033[0;36mn{alert_id}\033[0m=false positive")

    def print_controls(self):
        """Print control instructions"""
        print(f"\n\033[1;35m⌨️  CONTROLS:\033[0m")
        print("  \033[0;36mCtrl+C\033[0m - Stop monitoring")
        print("  \033[0;36mEnter\033[0m  - Force check now")
        print("  \033[0;36minterval X\033[0m - Change interval to X minutes")
        print("  \033[0;36mlog\033[0m - View alert history")
        print("  \033[0;36mclear\033[0m - Clear displayed alerts")
        print("  \033[0;36my[#]/n[#]\033[0m - Train alert as correct/false positive")

    def handle_user_input(self):
        """Handle user input in separate thread"""
        while self.running:
            try:
                user_input = input().strip().lower()

                if user_input == '':
                    # Use lock to safely pause display
                    with self.pause_lock:
                        self.paused = True

                        # Give main loop a moment to notice pause
                        time.sleep(0.1)

                        print("\033[2J\033[H")  # Clear screen and go to top
                        print("\033[1;33m🔄 FORCE PIXEL CHECK (Display Paused)\033[0m")
                        print("=" * 60)

                        # Run the check
                        self.run_pixel_check()

                        print("\n" + "=" * 60)
                        print("\033[0;90mPress Enter to resume monitoring...\033[0m")
                        input()

                        # Resume the main display loop
                        self.paused = False

                elif user_input in ['quit', 'exit', 'stop']:
                    self.running = False
                    print("\033[1;36m👋 Stopping monitoring...\033[0m")

                elif user_input.startswith('interval'):
                    try:
                        minutes = int(user_input.split()[1])
                        if 1 <= minutes <= 60:
                            self.check_interval = minutes * 60
                            print(f"\033[1;32m✅ Interval changed to {minutes} minutes\033[0m")
                        else:
                            print("\033[1;31m❌ Interval must be 1-60 minutes\033[0m")
                    except:
                        print("\033[1;31m❌ Usage: interval <minutes>\033[0m")

                elif user_input == 'log':
                    # Use lock to safely pause display
                    with self.pause_lock:
                        self.paused = True

                        # Give main loop a moment to notice pause
                        time.sleep(0.1)

                        print("\033[2J\033[H")  # Clear screen and go to top
                        print("\033[1;33m📝 ALERT HISTORY (Display Paused)\033[0m")
                        print("=" * 50)

                        try:
                            if os.path.exists('pixel_alerts.log'):
                                with open('pixel_alerts.log', 'r') as f:
                                    lines = f.readlines()
                                    if lines:
                                        print(f"\033[1;32mFound {len(lines)} alert(s):\033[0m\n")
                                        for i, line in enumerate(lines[-10:], 1):  # Show last 10 alerts
                                            print(f"\033[1;31m#{i}\033[0m {line.strip()}")
                                    else:
                                        print("  \033[1;33mNo alerts logged yet\033[0m")
                            else:
                                print("  \033[1;33mNo alert log file found\033[0m")
                        except Exception as e:
                            print(f"  \033[1;31mError reading log: {e}\033[0m")

                        print("\n" + "=" * 50)
                        print("\033[0;90mPress Enter to resume monitoring...\033[0m")
                        input()

                        # Resume the main display loop
                        self.paused = False

                elif user_input == 'clear':
                    self.recent_alerts = []
                    print("\033[1;32m✅ Displayed alerts cleared\033[0m")

                elif user_input.startswith('y') and user_input[1:].isdigit():
                    # Mark alert as correct (positive training)
                    alert_id = int(user_input[1:])
                    if 1 <= alert_id <= len(self.recent_alerts):
                        self.train_alert(alert_id - 1, True)  # Convert to 0-based index
                        print(f"\033[1;32m✅ Alert #{alert_id} marked as CORRECT\033[0m")
                    else:
                        print(f"\033[1;31m❌ Invalid alert ID: {alert_id}\033[0m")

                elif user_input.startswith('n') and user_input[1:].isdigit():
                    # Mark alert as false positive (negative training)
                    alert_id = int(user_input[1:])
                    if 1 <= alert_id <= len(self.recent_alerts):
                        self.train_alert(alert_id - 1, False)  # Convert to 0-based index
                        print(f"\033[1;31m❌ Alert #{alert_id} marked as FALSE POSITIVE\033[0m")
                    else:
                        print(f"\033[1;31m❌ Invalid alert ID: {alert_id}\033[0m")

            except EOFError:
                break
            except Exception as e:
                pass

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n\033[1;36m\n👋 Received signal {signum}. Shutting down gracefully...\033[0m")
        self.running = False

    def run(self):
        """Main monitoring loop"""

        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Start input handling thread
        input_thread = threading.Thread(target=self.handle_user_input, daemon=True)
        input_thread.start()

        # Initial setup
        self.clear_screen()
        self.print_header()

        # Run initial check
        print("\n\033[1;33m🚀 Starting continuous monitoring...\033[0m")
        self.run_pixel_check()

        # Main monitoring loop
        while self.running:
            try:
                # Check pause state with lock
                with self.pause_lock:
                    should_display = not self.paused

                # Only update display if not paused
                if should_display:
                    # Update display
                    self.clear_screen()
                    self.print_header()
                    self.print_status_bar()
                    self.print_recent_alerts()
                    self.print_detected_alerts()
                    self.print_controls()

                    # Check if it's time for next check
                    if self.last_check:
                        time_since_check = (datetime.now() - self.last_check).total_seconds()
                        if time_since_check >= self.check_interval:
                            self.run_pixel_check()

                # Sleep for 1 second before updating display
                time.sleep(1)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\033[1;31m❌ Monitoring error: {e}\033[0m")
                time.sleep(5)

        print(f"\n\033[1;36m✅ Continuous monitoring stopped at {datetime.now().strftime('%H:%M:%S')}\033[0m")


def main():
    """Main function with configuration options"""

    # Change to correct directory
    target_dir = "/Users/l.spahn/Performance Pixel Monitoring System"
    if os.path.exists(target_dir):
        os.chdir(target_dir)

    print("\033[1;36m🚨 CONTINUOUS PIXEL ALERT MONITOR SETUP\033[0m")
    print("="*50)
    print("\033[1;33mAlert-Only Mode: No dashboards generated, only notifications\033[0m")
    print()

    # Get configuration from user
    try:
        interval_input = input("⏰ Check interval in minutes (default 5, max 60): ").strip()
        if interval_input:
            interval_minutes = int(interval_input)
            if not (1 <= interval_minutes <= 60):
                print("\033[1;33m⚠️  Using default 5 minutes (invalid range)\033[0m")
                interval_minutes = 5
        else:
            interval_minutes = 5

        alerts_input = input("🚨 Enable alerts for ticket increases? (y/n, default y): ").strip().lower()
        alerts_enabled = alerts_input != 'n'

    except ValueError:
        print("\033[1;33m⚠️  Using default settings\033[0m")
        interval_minutes = 5
        alerts_enabled = True
    except KeyboardInterrupt:
        print("\n\033[1;36m👋 Setup cancelled\033[0m")
        return

    # Create and run monitor
    monitor = ContinuousPixelMonitor()
    monitor.check_interval = interval_minutes * 60
    monitor.alerts_enabled = alerts_enabled

    print(f"\n\033[1;32m🚀 Starting continuous monitoring every {interval_minutes} minutes...\033[0m")
    time.sleep(2)

    try:
        monitor.run()
    except KeyboardInterrupt:
        print(f"\n\033[1;36m👋 Monitoring stopped by user\033[0m")


if __name__ == "__main__":
    main()