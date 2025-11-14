#!/bin/bash

# Web Pixel Jira Notification Monitor Startup Script
# This script starts the pixel monitoring system

echo "🚀 Starting Web Pixel Jira Notification Monitor..."
echo "📊 Based on analysis of 16 real pixel tickets (April-October 2025)"
echo "🎯 Expected volume: ~3 notifications per month"
echo ""

# Navigate to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if the monitor script exists
if [ ! -f "pixel_notification_monitor.py" ]; then
    echo "❌ Error: pixel_notification_monitor.py not found!"
    exit 1
fi

echo "✅ Starting monitor in continuous mode..."
echo "⏰ Will check every 5 minutes for new pixel-related tickets"
echo "📧 Email notifications: Configured (placeholder mode)"
echo "💻 Console notifications: Enabled"
echo ""
echo "Press Ctrl+C to stop the monitor"
echo ""

# Start the monitor
python3 pixel_notification_monitor.py