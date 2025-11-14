#!/usr/bin/env python3
"""
Focused Jira Pixel Research Script
Specifically searches for web pixel and tracking implementation tickets.
"""

import requests
import base64
import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Jira Configuration
JIRA_CONFIG = {
    'base_url': 'https://adgear.atlassian.net',
    'email': os.getenv('JIRA_EMAIL', 'l.spahn@samsung.com'),
    'token': os.getenv('JIRA_TOKEN', ''),  # Set via environment variable
    'project_key': 'PS'
}

def make_jira_request(endpoint, method='GET', data=None):
    """Make authenticated request to Jira API"""
    auth_string = f"{JIRA_CONFIG['email']}:{JIRA_CONFIG['token']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    url = f"{JIRA_CONFIG['base_url']}{endpoint}"

    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Jira API request failed: {e}")
        raise

def search_issues(jql, fields=None, max_results=100):
    """Search Jira issues using JQL"""
    if fields is None:
        fields = ['key', 'summary', 'description', 'status', 'priority', 'created',
                 'updated', 'labels', 'issuetype', 'assignee', 'reporter']

    data = {
        'jql': jql,
        'fields': fields,
        'maxResults': max_results
    }

    return make_jira_request('/rest/api/3/search/jql', method='POST', data=data)

def extract_text_from_adf(adf_content):
    """Extract plain text from Atlassian Document Format (ADF)"""
    if not adf_content:
        return ''

    text_parts = []

    def extract_recursive(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                text_parts.append(node.get('text', ''))
            if 'content' in node:
                for child in node['content']:
                    extract_recursive(child)
        elif isinstance(node, list):
            for item in node:
                extract_recursive(item)

    extract_recursive(adf_content)
    return ' '.join(text_parts)

def analyze_focused_pixel_tickets():
    """Focused analysis on specific pixel-related searches"""
    print("=" * 80)
    print("FOCUSED JIRA PIXEL RESEARCH - PS PROJECT")
    print("=" * 80)
    print()

    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

    # Multiple focused searches
    search_queries = [
        {
            'name': 'Pixel-specific tickets',
            'jql': f"project={JIRA_CONFIG['project_key']} AND created >= '{six_months_ago}' AND (summary ~ 'pixel' OR description ~ 'pixel')"
        },
        {
            'name': 'Tracking implementation tickets',
            'jql': f"project={JIRA_CONFIG['project_key']} AND created >= '{six_months_ago}' AND (summary ~ 'tracking' OR description ~ 'tracking') AND (summary ~ 'implement' OR description ~ 'implement' OR summary ~ 'code' OR description ~ 'code')"
        },
        {
            'name': 'Tag/Script implementation tickets',
            'jql': f"project={JIRA_CONFIG['project_key']} AND created >= '{six_months_ago}' AND (summary ~ 'tag' OR summary ~ 'script') AND (summary ~ 'implement' OR summary ~ 'install' OR summary ~ 'setup')"
        },
        {
            'name': 'Web/JavaScript tickets',
            'jql': f"project={JIRA_CONFIG['project_key']} AND created >= '{six_months_ago}' AND (summary ~ 'javascript' OR summary ~ 'js' OR summary ~ 'web') AND (summary ~ 'code' OR summary ~ 'snippet' OR summary ~ 'integration')"
        }
    ]

    all_tickets = {}

    for search in search_queries:
        print(f"\n{'='*80}")
        print(f"Search: {search['name']}")
        print(f"JQL: {search['jql']}")
        print(f"{'='*80}")

        try:
            result = search_issues(search['jql'], max_results=50)
            tickets = result.get('issues', [])
            print(f"Found {len(tickets)} tickets")

            # Store tickets with deduplication
            for ticket in tickets:
                ticket_key = ticket['key']
                if ticket_key not in all_tickets:
                    all_tickets[ticket_key] = {
                        'issue': ticket,
                        'searches': [search['name']]
                    }
                else:
                    all_tickets[ticket_key]['searches'].append(search['name'])

            # Print sample tickets
            if tickets:
                print(f"\nSample tickets from this search:")
                for i, ticket in enumerate(tickets[:5], 1):
                    fields = ticket['fields']
                    summary = fields.get('summary', '')
                    priority = fields.get('priority', {})
                    priority_name = priority.get('name', 'None') if priority else 'None'

                    description = fields.get('description', '')
                    if description and isinstance(description, dict):
                        desc_text = extract_text_from_adf(description)[:100]
                    else:
                        desc_text = str(description)[:100] if description else ''

                    print(f"  {i}. {ticket['key']}: {summary}")
                    print(f"     Priority: {priority_name}")
                    print(f"     Description: {desc_text}...")
                    print()

        except Exception as e:
            print(f"Error in search: {e}")

    print("\n" + "=" * 80)
    print(f"TOTAL UNIQUE TICKETS FOUND: {len(all_tickets)}")
    print("=" * 80)

    # Analyze all unique tickets
    if all_tickets:
        print("\n" + "=" * 80)
        print("DETAILED ANALYSIS OF UNIQUE TICKETS")
        print("=" * 80)

        priority_counts = Counter()
        status_counts = Counter()
        issue_type_counts = Counter()

        # Common words in summaries
        summary_words = Counter()

        # Phrases and patterns
        common_phrases = []

        for ticket_key, ticket_data in all_tickets.items():
            issue = ticket_data['issue']
            fields = issue['fields']

            summary = fields.get('summary', '').lower()
            description = fields.get('description', '')

            if description and isinstance(description, dict):
                desc_text = extract_text_from_adf(description).lower()
            else:
                desc_text = str(description).lower() if description else ''

            priority = fields.get('priority', {})
            priority_name = priority.get('name', 'None') if priority else 'None'
            priority_counts[priority_name] += 1

            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown') if status else 'Unknown'
            status_counts[status_name] += 1

            issue_type = fields.get('issuetype', {})
            issue_type_name = issue_type.get('name', 'Unknown') if issue_type else 'Unknown'
            issue_type_counts[issue_type_name] += 1

            # Extract words from summary
            words = summary.split()
            for word in words:
                if len(word) > 3:  # Only meaningful words
                    summary_words[word] += 1

        print("\n1. PRIORITY DISTRIBUTION")
        print("-" * 80)
        for priority, count in priority_counts.most_common():
            percentage = (count / len(all_tickets) * 100)
            print(f"{priority:<20} {count:<10} {percentage:.1f}%")

        print("\n2. STATUS DISTRIBUTION")
        print("-" * 80)
        for status, count in status_counts.most_common():
            percentage = (count / len(all_tickets) * 100)
            print(f"{status:<20} {count:<10} {percentage:.1f}%")

        print("\n3. ISSUE TYPE DISTRIBUTION")
        print("-" * 80)
        for issue_type, count in issue_type_counts.most_common():
            percentage = (count / len(all_tickets) * 100)
            print(f"{issue_type:<20} {count:<10} {percentage:.1f}%")

        print("\n4. MOST COMMON WORDS IN SUMMARIES")
        print("-" * 80)
        print(f"{'Word':<20} {'Frequency':<10}")
        print("-" * 80)
        for word, count in summary_words.most_common(20):
            print(f"{word:<20} {count:<10}")

        print("\n5. TICKETS APPEARING IN MULTIPLE SEARCHES (High Relevance)")
        print("-" * 80)
        multi_search_tickets = {k: v for k, v in all_tickets.items() if len(v['searches']) > 1}

        if multi_search_tickets:
            for ticket_key, ticket_data in sorted(multi_search_tickets.items(),
                                                   key=lambda x: len(x[1]['searches']),
                                                   reverse=True):
                issue = ticket_data['issue']
                fields = issue['fields']
                summary = fields.get('summary', '')
                searches = ticket_data['searches']

                print(f"\n{ticket_key}: {summary}")
                print(f"  Found in {len(searches)} searches: {', '.join(searches)}")
                print(f"  URL: https://adgear.atlassian.net/browse/{ticket_key}")
        else:
            print("No tickets found in multiple searches")

        print("\n" + "=" * 80)
        print("ALL UNIQUE PIXEL-RELATED TICKETS")
        print("=" * 80)

        for i, (ticket_key, ticket_data) in enumerate(sorted(all_tickets.items()), 1):
            issue = ticket_data['issue']
            fields = issue['fields']

            summary = fields.get('summary', '')
            priority = fields.get('priority', {})
            priority_name = priority.get('name', 'None') if priority else 'None'
            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown') if status else 'Unknown'
            created = fields.get('created', '')

            description = fields.get('description', '')
            if description and isinstance(description, dict):
                desc_text = extract_text_from_adf(description)
            else:
                desc_text = str(description) if description else ''

            print(f"\n{i}. {ticket_key} - {summary}")
            print(f"   Priority: {priority_name} | Status: {status_name}")
            print(f"   Created: {created}")
            print(f"   Description: {desc_text[:200]}...")
            print(f"   Searches: {', '.join(ticket_data['searches'])}")
            print(f"   URL: https://adgear.atlassian.net/browse/{ticket_key}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR WEB PIXEL DETECTION")
    print("=" * 80)

    print("\n1. PRIMARY DETECTION KEYWORDS (Single keyword detection):")
    print("   - 'pixel' (in summary or description)")
    print("   - 'tracking pixel'")
    print("   - 'conversion pixel'")
    print("   - 'tracking tag'")
    print("   - 'pixel implementation'")

    print("\n2. COMBINATION PATTERNS (Multiple keyword detection):")
    print("   - ('tracking' OR 'tag') AND ('implement' OR 'install' OR 'setup')")
    print("   - ('javascript' OR 'js') AND ('code' OR 'snippet')")
    print("   - ('web' OR 'website') AND ('integration' OR 'embed')")

    print("\n3. EXCLUSION PATTERNS (To avoid false positives):")
    print("   - Exclude tickets with 'ACR' (TV-related, not web pixels)")
    print("   - Exclude tickets with 'delivery report' (reporting, not implementation)")
    print("   - Exclude tickets with 'access' or 'permission' (access requests)")

    print("\n4. RECOMMENDED DETECTION LOGIC:")
    print("""
    def is_pixel_related(summary, description):
        text = (summary + ' ' + description).lower()

        # Primary indicators (high confidence)
        primary_keywords = ['pixel', 'tracking pixel', 'conversion pixel']
        for keyword in primary_keywords:
            if keyword in text:
                return True

        # Combination patterns (medium confidence)
        tracking_keywords = ['tracking', 'tag']
        action_keywords = ['implement', 'install', 'setup', 'deploy', 'add']

        has_tracking = any(k in text for k in tracking_keywords)
        has_action = any(k in text for k in action_keywords)

        if has_tracking and has_action:
            # Check for exclusions
            exclusions = ['acr', 'delivery report', 'access request',
                         'permission', 'grant access']
            if not any(ex in text for ex in exclusions):
                return True

        # JavaScript/web integration patterns
        if ('javascript' in text or 'js ' in text) and \
           ('code' in text or 'snippet' in text):
            return True

        return False
    """)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    analyze_focused_pixel_tickets()
