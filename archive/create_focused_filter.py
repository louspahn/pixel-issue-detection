#!/usr/bin/env python3
"""
Create focused Jira filter for specific pixel tickets
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

    if method == 'POST':
        response = requests.post(url, headers=headers, json=data, timeout=30)
    else:
        response = requests.get(url, headers=headers, timeout=30)

    response.raise_for_status()
    return response.json()

def create_focused_filter():
    """Create filter for the specific 8 tickets"""

    # The 8 specific tickets
    tickets = ['PS-9074', 'PS-9155', 'PS-9534', 'PS-9784', 'PS-9814', 'PS-9824', 'PS-9959', 'PS-9970']

    # Create JQL for these specific tickets
    ticket_list = ', '.join(tickets)
    jql = f"key IN ({ticket_list}) ORDER BY key DESC"

    filter_data = {
        'name': '🎯 Focused Pixel Issues',
        'description': f'Specific pixel tickets: {ticket_list}',
        'jql': jql,
        'favourite': True
    }

    print(f"Creating filter with JQL: {jql}")

    # Create the filter
    try:
        result = make_jira_request('/rest/api/3/filter', method='POST', data=filter_data)
        filter_id = result['id']
        filter_url = f"{jira_config['base_url']}/issues/?filter={filter_id}"

        print(f"✅ Created focused filter successfully!")
        print(f"🔗 Filter URL: {filter_url}")
        print(f"📋 Filter ID: {filter_id}")

        return filter_id, filter_url

    except Exception as e:
        print(f"❌ Error creating filter: {e}")
        return None, None

def get_ticket_details():
    """Get details of the 8 tickets for analysis"""

    tickets = ['PS-9074', 'PS-9155', 'PS-9534', 'PS-9784', 'PS-9814', 'PS-9824', 'PS-9959', 'PS-9970']

    # Search for these tickets
    jql = f"key IN ({', '.join(tickets)})"

    search_data = {
        'jql': jql,
        'fields': ['key', 'summary', 'status', 'priority', 'created', 'updated', 'assignee', 'customfield_10610'],
        'maxResults': 10
    }

    try:
        result = make_jira_request('/rest/api/3/search/jql', method='POST', data=search_data)
        issues = result.get('issues', [])

        print(f"\\n📊 FOCUSED PIXEL ISSUES OVERVIEW")
        print("=" * 60)

        for issue in sorted(issues, key=lambda x: x['key']):
            fields = issue['fields']
            key = issue['key']
            summary = fields.get('summary', 'No summary')
            status = fields.get('status', {}).get('name', 'Unknown')
            priority = fields.get('priority', {}).get('name', 'Unknown')
            client = fields.get('customfield_10610', 'Unknown')

            print(f"{key:8s} | {status:12s} | {priority:8s} | {client:15s} | {summary[:40]:40s}")

        return issues

    except Exception as e:
        print(f"❌ Error fetching ticket details: {e}")
        return []

def main():
    print("🎯 Creating Focused Pixel Issues Dashboard View")
    print("=" * 50)

    # Create the focused filter
    filter_id, filter_url = create_focused_filter()

    if filter_id:
        print(f"\\n🎛️ DASHBOARD SETUP INSTRUCTIONS")
        print("=" * 50)
        print(f"1. Go to Jira Dashboard: {jira_config['base_url']}/secure/Dashboard.jspa")
        print(f"2. Create new dashboard: '🎯 Focused Pixel Issues Dashboard'")
        print(f"3. Add Filter Results gadget using filter ID: {filter_id}")
        print(f"4. Configure columns: Key, Summary, Status, Priority, Assignee, Client, Created")
        print(f"\\n🔗 DIRECT LINK TO YOUR 8 TICKETS:")
        print(f"   {filter_url}")

    # Get and display ticket overview
    get_ticket_details()

    print(f"\\n✅ Your focused view is ready!")
    print(f"\\n🎯 This single view contains exactly these 8 tickets:")
    print("   PS-9074, PS-9155, PS-9534, PS-9784, PS-9814, PS-9824, PS-9959, PS-9970")

if __name__ == "__main__":
    main()