#!/usr/bin/env python3
"""
Jira Pixel Research Script
Analyzes PS project tickets to understand web pixel-related issues and patterns.
"""

import requests
import base64
import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re

# Jira Configuration
JIRA_CONFIG = {
    'base_url': 'https://adgear.atlassian.net',
    'email': os.getenv('JIRA_EMAIL', 'l.spahn@samsung.com'),
    'token': os.getenv('JIRA_TOKEN', ''),  # Set via environment variable
    'project_key': 'PS'
}

# Pixel-related keywords to search for
PIXEL_KEYWORDS = [
    'pixel',
    'tracking',
    'tag',
    'javascript',
    'web',
    'snippet',
    'code',
    'implementation',
    'script',
    'embed',
    'integration'
]

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

def extract_keywords_from_text(text):
    """Extract relevant keywords from text"""
    if not text:
        return []

    # Convert to lowercase for matching
    text_lower = text.lower()

    # Find all matching keywords
    found_keywords = []
    for keyword in PIXEL_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)

    return found_keywords

def analyze_pixel_tickets():
    """Main analysis function"""
    print("=" * 80)
    print("JIRA PIXEL RESEARCH - PS PROJECT")
    print("=" * 80)
    print()

    # Calculate date 6 months ago
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

    print(f"Searching for tickets created after: {six_months_ago}")
    print()

    # Search for tickets containing pixel-related keywords
    all_pixel_tickets = []
    keyword_search_terms = ' OR '.join([f'text ~ "{keyword}"' for keyword in PIXEL_KEYWORDS])

    jql = f"project={JIRA_CONFIG['project_key']} AND created >= '{six_months_ago}' AND ({keyword_search_terms})"

    print(f"JQL Query: {jql}")
    print()
    print("Fetching tickets from Jira...")

    try:
        result = search_issues(jql, max_results=200)
        all_pixel_tickets = result.get('issues', [])

        print(f"Found {len(all_pixel_tickets)} pixel-related tickets")
        print()
        print("=" * 80)

        if len(all_pixel_tickets) == 0:
            print("No pixel-related tickets found. Trying broader search...")
            # Try a broader search with just "pixel" or "tracking"
            jql = f"project={JIRA_CONFIG['project_key']} AND created >= '{six_months_ago}' AND (text ~ 'pixel' OR text ~ 'tracking')"
            result = search_issues(jql, max_results=200)
            all_pixel_tickets = result.get('issues', [])
            print(f"Broader search found {len(all_pixel_tickets)} tickets")
            print()

        # Analysis data structures
        keyword_counts = Counter()
        priority_counts = Counter()
        issue_type_counts = Counter()
        status_counts = Counter()
        label_counts = Counter()

        # Categorization
        issue_categories = defaultdict(list)

        # Common phrases in summaries and descriptions
        all_summaries = []
        all_descriptions = []

        print("\nANALYZING TICKETS...")
        print("=" * 80)
        print()

        # Analyze each ticket
        for issue in all_pixel_tickets:
            key = issue['key']
            fields = issue['fields']

            summary = fields.get('summary', '')
            description = fields.get('description', '')

            # Handle description structure (Jira API v3 uses ADF format)
            if description and isinstance(description, dict):
                # Extract text from Atlassian Document Format
                description_text = extract_text_from_adf(description)
            else:
                description_text = str(description) if description else ''

            priority = fields.get('priority', {})
            priority_name = priority.get('name', 'None') if priority else 'None'

            issue_type = fields.get('issuetype', {})
            issue_type_name = issue_type.get('name', 'Unknown') if issue_type else 'Unknown'

            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown') if status else 'Unknown'

            labels = fields.get('labels', [])

            # Extract keywords
            summary_keywords = extract_keywords_from_text(summary)
            desc_keywords = extract_keywords_from_text(description_text)
            all_keywords = set(summary_keywords + desc_keywords)

            # Update counts
            for keyword in all_keywords:
                keyword_counts[keyword] += 1

            priority_counts[priority_name] += 1
            issue_type_counts[issue_type_name] += 1
            status_counts[status_name] += 1

            for label in labels:
                label_counts[label] += 1

            # Store summaries and descriptions
            all_summaries.append(summary)
            all_descriptions.append(description_text)

            # Categorize issues
            if any(word in summary.lower() or word in description_text.lower()
                   for word in ['implement', 'install', 'setup', 'deploy', 'add']):
                issue_categories['implementation'].append((key, summary))

            if any(word in summary.lower() or word in description_text.lower()
                   for word in ['not working', 'broken', 'issue', 'problem', 'error', 'fail']):
                issue_categories['troubleshooting'].append((key, summary))

            if any(word in summary.lower() or word in description_text.lower()
                   for word in ['slow', 'performance', 'speed', 'optimize', 'latency']):
                issue_categories['performance'].append((key, summary))

            if any(word in summary.lower() or word in description_text.lower()
                   for word in ['how to', 'question', 'help', 'guidance', 'documentation']):
                issue_categories['guidance'].append((key, summary))

        # Print Analysis Results
        print("\n1. KEYWORD FREQUENCY ANALYSIS")
        print("-" * 80)
        print(f"{'Keyword':<20} {'Count':<10} {'Percentage':<10}")
        print("-" * 80)
        total_tickets = len(all_pixel_tickets)
        for keyword, count in keyword_counts.most_common():
            percentage = (count / total_tickets * 100) if total_tickets > 0 else 0
            print(f"{keyword:<20} {count:<10} {percentage:.1f}%")

        print("\n2. PRIORITY DISTRIBUTION")
        print("-" * 80)
        print(f"{'Priority':<20} {'Count':<10} {'Percentage':<10}")
        print("-" * 80)
        for priority, count in priority_counts.most_common():
            percentage = (count / total_tickets * 100) if total_tickets > 0 else 0
            print(f"{priority:<20} {count:<10} {percentage:.1f}%")

        print("\n3. ISSUE TYPE DISTRIBUTION")
        print("-" * 80)
        print(f"{'Issue Type':<20} {'Count':<10} {'Percentage':<10}")
        print("-" * 80)
        for issue_type, count in issue_type_counts.most_common():
            percentage = (count / total_tickets * 100) if total_tickets > 0 else 0
            print(f"{issue_type:<20} {count:<10} {percentage:.1f}%")

        print("\n4. STATUS DISTRIBUTION")
        print("-" * 80)
        print(f"{'Status':<20} {'Count':<10} {'Percentage':<10}")
        print("-" * 80)
        for status, count in status_counts.most_common():
            percentage = (count / total_tickets * 100) if total_tickets > 0 else 0
            print(f"{status:<20} {count:<10} {percentage:.1f}%")

        print("\n5. LABEL ANALYSIS")
        print("-" * 80)
        if label_counts:
            print(f"{'Label':<30} {'Count':<10}")
            print("-" * 80)
            for label, count in label_counts.most_common(15):
                print(f"{label:<30} {count:<10}")
        else:
            print("No labels found on pixel-related tickets")

        print("\n6. ISSUE CATEGORIZATION")
        print("-" * 80)
        for category, tickets in issue_categories.items():
            print(f"\n{category.upper()} ({len(tickets)} tickets):")
            for key, summary in tickets[:5]:  # Show first 5 examples
                print(f"  - {key}: {summary[:70]}...")
            if len(tickets) > 5:
                print(f"  ... and {len(tickets) - 5} more")

        print("\n7. SAMPLE TICKETS (First 10)")
        print("=" * 80)
        for i, issue in enumerate(all_pixel_tickets[:10], 1):
            fields = issue['fields']
            key = issue['key']
            summary = fields.get('summary', '')
            priority = fields.get('priority', {})
            priority_name = priority.get('name', 'None') if priority else 'None'
            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown') if status else 'Unknown'

            description = fields.get('description', '')
            if description and isinstance(description, dict):
                description_text = extract_text_from_adf(description)
            else:
                description_text = str(description) if description else ''

            print(f"\n{i}. {key} - {summary}")
            print(f"   Priority: {priority_name} | Status: {status_name}")
            print(f"   Description: {description_text[:150]}...")
            print(f"   URL: https://adgear.atlassian.net/browse/{key}")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS FOR DETECTION LOGIC")
        print("=" * 80)

        # Generate recommendations
        print("\nBased on the analysis, here are recommended detection keywords:")
        print("\n1. HIGH-VALUE KEYWORDS (most common in pixel tickets):")
        for keyword, count in keyword_counts.most_common(5):
            print(f"   - '{keyword}' (found in {count} tickets)")

        print("\n2. PHRASE PATTERNS TO DETECT:")
        print("   - 'pixel implementation'")
        print("   - 'tracking code'")
        print("   - 'javascript tag'")
        print("   - 'web pixel'")
        print("   - 'pixel not firing'")
        print("   - 'pixel setup'")
        print("   - 'tag implementation'")

        print("\n3. CONTEXTUAL INDICATORS:")
        print("   - Tickets mentioning 'implement' + 'pixel'")
        print("   - Tickets mentioning 'tracking' + 'issue'")
        print("   - Tickets mentioning 'javascript' + 'code'")

        print("\n4. PRIORITY PATTERNS:")
        print(f"   - Most pixel tickets have priority: {priority_counts.most_common(1)[0][0]}")

        if label_counts:
            print("\n5. RELEVANT LABELS:")
            for label, count in label_counts.most_common(5):
                print(f"   - '{label}' ({count} occurrences)")

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

def extract_text_from_adf(adf_content):
    """Extract plain text from Atlassian Document Format (ADF)"""
    if not adf_content:
        return ''

    text_parts = []

    def extract_recursive(node):
        if isinstance(node, dict):
            # Handle text nodes
            if node.get('type') == 'text':
                text_parts.append(node.get('text', ''))

            # Recursively process content
            if 'content' in node:
                for child in node['content']:
                    extract_recursive(child)

        elif isinstance(node, list):
            for item in node:
                extract_recursive(item)

    extract_recursive(adf_content)
    return ' '.join(text_parts)

if __name__ == '__main__':
    analyze_pixel_tickets()
