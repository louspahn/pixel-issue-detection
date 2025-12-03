#!/usr/bin/env python3
"""
Create individual category filters for each pixel issue type
"""

import requests
import base64

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

    if method == 'POST':
        response = requests.post(url, headers=headers, json=data, timeout=30)
    else:
        response = requests.get(url, headers=headers, timeout=30)

    response.raise_for_status()
    return response.json()

def create_category_filters():
    """Create filters for each pixel category"""

    # Define category filters
    categories = {
        '🔍 Pixel Validation Issues': {
            'jql': 'project = PS AND labels = pixel-validation ORDER BY created DESC',
            'description': 'Pixel validation and testing requests (like PS-9534, PS-9959)'
        },
        '🛠️ Pixel Troubleshooting': {
            'jql': 'project = PS AND labels = pixel-troubleshooting ORDER BY created DESC',
            'description': 'Debugging and investigation issues (like PS-9074, PS-9784)'
        },
        '⚡ Pixel Implementation': {
            'jql': 'project = PS AND labels = pixel-implementation ORDER BY created DESC',
            'description': 'Setup and firing issues (like PS-9814, PS-9824)'
        },
        '📊 Data Discrepancy Issues': {
            'jql': 'project = PS AND labels = pixel-data-discrepancy ORDER BY created DESC',
            'description': '1P vs 3P data mismatches (like PS-9074 GOLO issue)'
        },
        '🎯 Conversion Tracking': {
            'jql': 'project = PS AND labels = pixel-conversion-tracking ORDER BY created DESC',
            'description': 'Purchase and revenue tracking pixel issues'
        },
        '🏷️ GTM Related Issues': {
            'jql': 'project = PS AND labels = pixel-gtm-related ORDER BY created DESC',
            'description': 'Google Tag Manager configuration and data layer issues'
        },
        '📱 Cross-Domain Issues': {
            'jql': 'project = PS AND labels = pixel-cross-domain ORDER BY created DESC',
            'description': 'Multi-domain and subdomain tracking problems'
        },
        '🚨 Critical Pixel Issues': {
            'jql': 'project = PS AND labels = pixel-critical-revenue AND status NOT IN (Done, Resolved, Closed) ORDER BY priority DESC, created DESC',
            'description': 'Revenue-impacting pixel issues requiring immediate attention'
        }
    }

    created_filters = {}

    print("🎛️ Creating Category-Specific Pixel Filters")
    print("=" * 50)

    for filter_name, config in categories.items():
        try:
            filter_data = {
                'name': filter_name,
                'description': config['description'],
                'jql': config['jql'],
                'favourite': False
            }

            # Create filter
            result = make_jira_request('/rest/api/3/filter', method='POST', data=filter_data)
            filter_id = result['id']
            filter_url = f"{jira_config['base_url']}/issues/?filter={filter_id}"

            created_filters[filter_name] = {
                'id': filter_id,
                'url': filter_url,
                'jql': config['jql']
            }

            print(f"✅ {filter_name}")
            print(f"   {filter_url}")

        except Exception as e:
            print(f"❌ Failed to create {filter_name}: {e}")

    return created_filters

def create_dashboard_summary(filters):
    """Create summary of all created filters"""

    summary = f"""
# 🎯 Pixel Issues Dashboard - Complete Filter Set

## 🔗 Main Dashboard View
**[Labeled Pixel Issues](https://adgear.atlassian.net/issues/?filter=26796)** - Your dynamic view with all categorized tickets

## 📊 Category-Specific Views

"""

    for filter_name, details in filters.items():
        category = filter_name.split(' ', 1)[1]  # Remove emoji
        summary += f"**[{filter_name}]({details['url']})**  \n"
        summary += f"JQL: `{details['jql']}`\n\n"

    summary += f"""
## 🏷️ Label System

The filters use these classification labels:
- `pixel-validation` - Testing and verification requests
- `pixel-troubleshooting` - Debug and investigation issues
- `pixel-implementation` - Setup and firing problems
- `pixel-data-discrepancy` - 1P vs 3P data mismatches
- `pixel-conversion-tracking` - Purchase/revenue tracking
- `pixel-gtm-related` - Google Tag Manager issues
- `pixel-cross-domain` - Multi-domain tracking
- `pixel-critical-revenue` - Revenue-impacting issues

## 🎛️ Dashboard Setup

1. **Go to:** [Jira Dashboard]({jira_config['base_url']}/secure/Dashboard.jspa)
2. **Create Dashboard:** "🎯 Pixel Categories Dashboard"
3. **Add Filter Result gadgets** for each category
4. **Configure columns:** Key, Summary, Status, Priority, Assignee, Labels, Created

## 🔄 Dynamic Features

✅ **Auto-grows** as new tickets get labeled
✅ **Organized by category** for easy management
✅ **Includes original 8 tickets** plus new ones
✅ **Drill-down capability** from overview to specific categories

Your pixel dashboard now has both overview and detailed category views!
"""

    return summary

def main():
    # Create category filters
    filters = create_category_filters()

    if filters:
        print(f"\n✅ Created {len(filters)} category-specific filters!")

        # Create and save summary
        summary = create_dashboard_summary(filters)

        with open('PIXEL_CATEGORY_FILTERS.md', 'w') as f:
            f.write(summary)

        print(f"\n📄 Summary saved to: PIXEL_CATEGORY_FILTERS.md")
        print(f"\n🎯 Your JQL is now label-powered and dynamic!")
        print(f"\n🔗 Main view: https://adgear.atlassian.net/issues/?filter=26796")

if __name__ == "__main__":
    main()