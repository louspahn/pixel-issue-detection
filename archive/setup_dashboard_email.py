#!/usr/bin/env python3
"""
Setup email delivery for Pixel Dashboard
Creates subscriptions for dashboard and filters
"""

import requests
import base64
import json

# Jira config
jira_config = {
    'base_url': 'https://adgear.atlassian.net',
    'email': 'l.spahn@samsung.com',
    'token': 'YOUR_JIRA_API_TOKEN_HERE'
}

def make_jira_request(endpoint, method='GET', data=None):
    auth_string = f"{jira_config['email']}:{jira_config['token']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    url = f"{jira_config['base_url']}{endpoint}"

    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def setup_filter_subscription():
    """Setup email subscription for the main pixel filter"""

    filter_id = '26796'  # Your main pixel filter

    print("📧 Setting up Filter Email Subscription")
    print("=" * 40)

    # Filter subscription data
    subscription_data = {
        "subject": "🔥 Daily Pixel Issues Report",
        "emailFormat": "html",
        "schedule": {
            "type": "daily",
            "timeZone": "America/New_York",
            "time": "08:00"
        },
        "groups": [],
        "users": [
            {
                "name": jira_config['email'],
                "displayName": "Louis Spahn"
            }
        ]
    }

    try:
        # Create filter subscription
        result = make_jira_request(
            f'/rest/api/3/filter/{filter_id}/subscription',
            method='POST',
            data=subscription_data
        )

        if result:
            print(f"✅ Filter subscription created!")
            print(f"📊 Filter: https://adgear.atlassian.net/issues/?filter={filter_id}")
            print(f"📧 Daily email at 8:00 AM EST to: {jira_config['email']}")
            print(f"📋 Subscription ID: {result.get('id', 'Unknown')}")
            return result
        else:
            print("❌ Failed to create filter subscription")
            return None

    except Exception as e:
        print(f"❌ Error creating subscription: {e}")
        return None

def create_automation_rule():
    """Create automation rule for dashboard email (if permissions allow)"""

    print("\n🤖 Automation Rule Setup")
    print("=" * 40)

    # This typically requires project admin permissions
    # Providing the configuration for manual setup

    automation_config = {
        "name": "Daily Pixel Dashboard Email",
        "description": "Send daily email with pixel issues summary",
        "trigger": {
            "type": "scheduled",
            "configuration": {
                "intervalType": "DAILY",
                "time": "08:00",
                "timezone": "America/New_York"
            }
        },
        "conditions": [],
        "actions": [
            {
                "type": "SEND_EMAIL",
                "configuration": {
                    "to": jira_config['email'],
                    "subject": "🔥 Daily Pixel Issues Dashboard Report",
                    "body": """
Daily Pixel Issues Summary:

🔗 Dashboard: https://adgear.atlassian.net/jira/dashboards/19521
🎯 All Issues: https://adgear.atlassian.net/issues/?filter=26796

Key Filters:
• Validation: https://adgear.atlassian.net/issues/?filter=26830
• Troubleshooting: https://adgear.atlassian.net/issues/?filter=26831
• Implementation: https://adgear.atlassian.net/issues/?filter=26832
• Critical: https://adgear.atlassian.net/issues/?filter=26837

Generated automatically by Jira Automation
                    """
                }
            }
        ]
    }

    print("📋 Automation Rule Configuration:")
    print(json.dumps(automation_config, indent=2))
    print("\n💡 To create this rule:")
    print("1. Go to Project Settings → Automation")
    print("2. Click 'Create Rule'")
    print("3. Use the configuration above")

    return automation_config

def manual_setup_instructions():
    """Provide manual setup instructions"""

    instructions = f"""
# 📧 Manual Dashboard Email Setup

## Option 1: Dashboard Subscription (Recommended)

1. **Go to your dashboard**: https://adgear.atlassian.net/jira/dashboards/19521
2. **Click "Actions" (⚙️) menu** in top right
3. **Select "Subscribe"**
4. **Configure settings:**
   - Frequency: Daily
   - Time: 8:00 AM
   - Time Zone: America/New_York
   - Format: HTML (shows full dashboard)
   - Recipients: {jira_config['email']}
5. **Click "Subscribe"**

## Option 2: Filter Email (Alternative)

1. **Go to main filter**: https://adgear.atlassian.net/issues/?filter=26796
2. **Click "Export" → "Subscribe"**
3. **Configure:**
   - Schedule: Daily at 8:00 AM EST
   - Format: Excel or HTML
   - Email: {jira_config['email']}
4. **Save subscription**

## Option 3: Multiple Filter Subscriptions

Subscribe to category-specific filters:
- **Validation**: https://adgear.atlassian.net/issues/?filter=26830
- **Troubleshooting**: https://adgear.atlassian.net/issues/?filter=26831
- **Implementation**: https://adgear.atlassian.net/issues/?filter=26832
- **Critical**: https://adgear.atlassian.net/issues/?filter=26837

## 📧 Email Content

Your daily email will contain:
✅ **Dashboard snapshot** (if using dashboard subscription)
✅ **Ticket list** with Key, Summary, Status, Priority
✅ **Direct links** to each ticket
✅ **Filter links** for drill-down analysis
✅ **Automatic updates** - no manual work needed

## 🎯 Benefits

- **Daily visibility** into pixel issues
- **Proactive monitoring** - catch issues early
- **Team awareness** - share with stakeholders
- **Trend tracking** - see patterns over time
- **No manual work** - fully automated

## ⚙️ Advanced Options

**Custom Email Format:**
- HTML: Full dashboard visual
- Excel: Spreadsheet for analysis
- PDF: Professional report format

**Multiple Recipients:**
- Add team members
- Include managers for visibility
- CC clients for transparency

**Filtering Options:**
- Only open tickets
- Only high priority
- Specific clients only
- Recent changes only
"""

    return instructions

def main():
    print("📧 Pixel Dashboard Email Setup")
    print("=" * 40)

    # Try to setup filter subscription
    subscription = setup_filter_subscription()

    # Show automation rule config
    automation = create_automation_rule()

    # Generate manual instructions
    instructions = manual_setup_instructions()

    # Save instructions to file
    with open('DASHBOARD_EMAIL_SETUP.md', 'w') as f:
        f.write(instructions)

    print(f"\n📄 Instructions saved to: DASHBOARD_EMAIL_SETUP.md")
    print(f"\n🎯 Recommended: Use Dashboard Subscription for full visual report")
    print(f"🔗 Your dashboard: https://adgear.atlassian.net/jira/dashboards/19521")

if __name__ == "__main__":
    main()