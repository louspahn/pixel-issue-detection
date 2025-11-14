#!/bin/bash

# Environment Setup Script for Pixel Monitoring System
# Run this script to configure your environment variables

echo "🔧 Setting up Pixel Monitoring System Environment"
echo "=================================================="

# Set the Jira API token (replace with your actual token)
export JIRA_TOKEN="YOUR_JIRA_API_TOKEN_HERE"

# Set the Jira email (optional - defaults to l.spahn@samsung.com)
export JIRA_EMAIL="l.spahn@samsung.com"

# Optional: Set email password for notifications
# export EMAIL_PASSWORD="your_email_app_password_here"

echo "✅ Environment variables set for current session"
echo ""
echo "To make these permanent, add to your ~/.bashrc or ~/.zshrc:"
echo "export JIRA_TOKEN=\"\$JIRA_TOKEN\""
echo "export JIRA_EMAIL=\"\$JIRA_EMAIL\""
echo ""
echo "🚀 You can now run: ./start_pixel_monitor.sh"