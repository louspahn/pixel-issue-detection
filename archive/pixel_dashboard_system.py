#!/usr/bin/env python3
"""
Jira Dashboard System for Pixel Issues
Aggregates pixel-related tickets and provides classification and analytics
Based on PS-9074 example for GOLO pixel data discrepancy
"""

import json
import requests
import base64
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PixelIssueCategory(Enum):
    """Classification categories for pixel issues"""
    DATA_DISCREPANCY = "data_discrepancy"  # Like PS-9074 - data mismatch between platforms
    IMPLEMENTATION = "implementation"       # Pixel not firing, setup issues
    VALIDATION = "validation"              # Testing and validation requests
    TRACKING_SETUP = "tracking_setup"      # Initial pixel implementation
    TROUBLESHOOTING = "troubleshooting"    # Debugging existing pixels
    CONVERSION_ISSUES = "conversion_issues" # Conversion not tracking properly
    CROSS_DOMAIN = "cross_domain"          # Cross-domain tracking problems
    MOBILE_ISSUES = "mobile_issues"        # Mobile app or responsive issues
    GTM_RELATED = "gtm_related"            # Google Tag Manager issues
    THIRD_PARTY = "third_party"            # Third-party platform integration
    REPORTING = "reporting"                # Reporting and analytics issues

class PixelPriority(Enum):
    """Priority levels for pixel issues"""
    CRITICAL = "critical"     # Revenue-impacting, client-facing
    HIGH = "high"            # Affecting campaign performance
    MEDIUM = "medium"        # Standard implementation requests
    LOW = "low"             # Non-urgent validation/testing

@dataclass
class PixelTicket:
    """Structured pixel ticket data"""
    key: str
    summary: str
    description: str
    status: str
    priority: str
    created: datetime
    updated: datetime
    assignee: Optional[str]
    reporter: str
    client: Optional[str]
    category: Optional[PixelIssueCategory] = None
    pixel_priority: Optional[PixelPriority] = None
    tags: List[str] = None
    resolution_time: Optional[timedelta] = None

class PixelDashboardSystem:
    """Main dashboard system for pixel issue management"""

    def __init__(self, jira_config: Dict):
        self.jira_config = jira_config
        self.db_path = "pixel_dashboard.db"
        self.init_database()

    def init_database(self):
        """Initialize dashboard database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Pixel tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pixel_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_key TEXT UNIQUE NOT NULL,
                summary TEXT NOT NULL,
                description TEXT,
                status TEXT,
                priority TEXT,
                created_date DATETIME,
                updated_date DATETIME,
                assignee TEXT,
                reporter TEXT,
                client TEXT,
                category TEXT,
                pixel_priority TEXT,
                tags TEXT, -- JSON array of tags
                resolution_time_hours REAL,
                raw_data TEXT, -- Full JSON ticket data
                last_sync DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Classification rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                category TEXT NOT NULL,
                keywords TEXT NOT NULL, -- JSON array of keywords
                priority_keywords TEXT, -- JSON array for priority detection
                client_patterns TEXT, -- JSON array of client patterns
                confidence_score REAL DEFAULT 1.0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        ''')

        # Dashboard metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE,
                category TEXT,
                count INTEGER,
                avg_resolution_hours REAL,
                critical_count INTEGER,
                high_count INTEGER,
                medium_count INTEGER,
                low_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Dashboard database initialized")

    def make_jira_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated Jira API request"""
        auth_string = f"{self.jira_config['email']}:{self.jira_config['token']}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()

        headers = {
            'Authorization': f'Basic {auth_bytes}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        url = f"{self.jira_config['base_url']}{endpoint}"

        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Jira API request failed: {e}")
            raise

    def fetch_pixel_tickets(self, days_back: int = 90) -> List[Dict]:
        """Fetch pixel-related tickets from Jira"""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        jql_start = start_date.strftime('%Y-%m-%d')

        # Enhanced JQL query for pixel tickets based on PS-9074 analysis
        jql = f'''
        project = PS AND (
            summary ~ "pixel" OR
            description ~ "pixel" OR
            summary ~ "conversion" OR
            summary ~ "tracking" OR
            summary ~ "tag" OR
            summary ~ "gtm" OR
            summary ~ "validation" OR
            summary ~ "discrepancy" OR
            description ~ "1P and 3P" OR
            description ~ "Samsung pixel" OR
            description ~ "data mismatch" OR
            description ~ "confirmation page" OR
            description ~ "set up issue" OR
            summary ~ "implementation"
        ) AND created >= "{jql_start}"
        ORDER BY created DESC
        '''

        data = {
            'jql': jql,
            'fields': [
                'key', 'summary', 'description', 'status', 'priority',
                'created', 'updated', 'assignee', 'reporter', 'resolutiondate',
                'customfield_10610',  # Client field from PS-9074
                'labels', 'components'
            ],
            'maxResults': 1000
        }

        logger.info(f"Fetching pixel tickets from {jql_start}")
        result = self.make_jira_request('/rest/api/3/search/jql', method='POST', data=data)

        tickets = result.get('issues', [])
        logger.info(f"Found {len(tickets)} potential pixel tickets")

        return tickets

    def extract_client_from_ticket(self, ticket: Dict) -> Optional[str]:
        """Extract client name from ticket data"""
        fields = ticket.get('fields', {})

        # Check custom field (like PS-9074's client field)
        client_field = fields.get('customfield_10610')  # Based on PS-9074
        if client_field:
            return client_field.strip()

        # Extract from summary or description
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '')
        if isinstance(description, dict):
            description = self.extract_text_from_jira_content(description)
        description = description.lower()

        # Common client extraction patterns
        client_patterns = [
            r'client[:\s]+([A-Z][A-Za-z\s&]+)',
            r'([A-Z][A-Za-z\s&]+)\s+pixel',
            r'([A-Z][A-Za-z\s&]+)\s+campaign',
        ]

        import re
        text = f"{summary} {description}"
        for pattern in client_patterns:
            match = re.search(pattern, text)
            if match:
                client = match.group(1).strip()
                if len(client) > 2 and client.lower() not in ['the', 'and', 'for', 'with']:
                    return client

        return None

    def extract_text_from_jira_content(self, content: Dict) -> str:
        """Extract plain text from Jira's rich content format"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            text_parts = []
            if 'content' in content:
                for item in content['content']:
                    text_parts.append(self.extract_text_from_jira_content(item))
            elif 'text' in content:
                text_parts.append(content['text'])
            return ' '.join(text_parts)
        elif isinstance(content, list):
            text_parts = []
            for item in content:
                text_parts.append(self.extract_text_from_jira_content(item))
            return ' '.join(text_parts)
        return str(content)

    def classify_pixel_ticket(self, ticket: Dict) -> Tuple[PixelIssueCategory, PixelPriority]:
        """Classify ticket based on content analysis"""
        fields = ticket.get('fields', {})
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '')
        if isinstance(description, dict):
            description = self.extract_text_from_jira_content(description)
        description = description.lower()

        text = f"{summary} {description}"

        # Category classification based on PS-9074 patterns
        category_rules = {
            PixelIssueCategory.DATA_DISCREPANCY: [
                'similar data between', 'data mismatch', 'discrepancy',
                '1p and 3p', 'user count', 'not seeing similar', 'confirmation page data'
            ],
            PixelIssueCategory.IMPLEMENTATION: [
                'pixel not firing', 'implementation', 'setup', 'install pixel',
                'place pixel', 'add pixel', 'deploy pixel'
            ],
            PixelIssueCategory.VALIDATION: [
                'validation', 'validate', 'test pixel', 'verify pixel',
                'check pixel', 'pixel testing'
            ],
            PixelIssueCategory.TROUBLESHOOTING: [
                'troubleshoot', 'debug', 'investigate', 'pixel issue',
                'not working', 'broken pixel', '0 conversions'
            ],
            PixelIssueCategory.CONVERSION_ISSUES: [
                'conversion', 'conversion tracking', 'purchase tracking',
                'conversion pixel', 'revenue tracking'
            ],
            PixelIssueCategory.GTM_RELATED: [
                'gtm', 'google tag manager', 'tag manager', 'data layer',
                'gtm container', 'tag configuration'
            ],
            PixelIssueCategory.CROSS_DOMAIN: [
                'cross domain', 'cross-domain', 'subdomain', 'multiple domains',
                'domain tracking'
            ],
            PixelIssueCategory.REPORTING: [
                'reporting', 'analytics', 'dashboard', 'report data',
                'metrics', 'performance data'
            ]
        }

        # Determine category
        category = PixelIssueCategory.IMPLEMENTATION  # Default
        max_matches = 0

        for cat, keywords in category_rules.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > max_matches:
                max_matches = matches
                category = cat

        # Priority classification
        priority_high = ['critical', 'urgent', 'high priority', 'revenue impact', 'client escalation']
        priority_medium = ['medium', 'standard', 'normal']
        priority_low = ['low', 'nice to have', 'future', 'enhancement']

        jira_priority = fields.get('priority', {}).get('name', '').lower()

        if any(keyword in text for keyword in priority_high) or jira_priority in ['critical', 'high']:
            pixel_priority = PixelPriority.HIGH
        elif any(keyword in text for keyword in priority_low) or jira_priority == 'low':
            pixel_priority = PixelPriority.LOW
        else:
            pixel_priority = PixelPriority.MEDIUM

        return category, pixel_priority

    def process_and_store_tickets(self, tickets: List[Dict]):
        """Process tickets and store in dashboard database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        processed_count = 0

        for ticket in tickets:
            try:
                fields = ticket.get('fields', {})

                # Extract basic data
                key = ticket.get('key')
                summary = fields.get('summary', '')
                description = fields.get('description', '')
                if isinstance(description, dict):
                    description = self.extract_text_from_jira_content(description)

                status = fields.get('status', {}).get('name', '')
                priority = fields.get('priority', {}).get('name', '')

                # Parse dates
                created = datetime.fromisoformat(fields.get('created', '').replace('Z', '+00:00'))
                updated = datetime.fromisoformat(fields.get('updated', '').replace('Z', '+00:00'))

                # Extract people
                assignee = fields.get('assignee', {})
                assignee_name = assignee.get('displayName') if assignee else None

                reporter = fields.get('reporter', {})
                reporter_name = reporter.get('displayName') if reporter else 'Unknown'

                # Extract client
                client = self.extract_client_from_ticket(ticket)

                # Classify ticket
                category, pixel_priority = self.classify_pixel_ticket(ticket)

                # Calculate resolution time if resolved
                resolution_time_hours = None
                resolution_date = fields.get('resolutiondate')
                if resolution_date:
                    resolved = datetime.fromisoformat(resolution_date.replace('Z', '+00:00'))
                    resolution_time_hours = (resolved - created).total_seconds() / 3600

                # Store in database
                cursor.execute('''
                    INSERT OR REPLACE INTO pixel_tickets
                    (ticket_key, summary, description, status, priority, created_date, updated_date,
                     assignee, reporter, client, category, pixel_priority, resolution_time_hours, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key, summary, description, status, priority, created, updated,
                    assignee_name, reporter_name, client, category.value, pixel_priority.value,
                    resolution_time_hours, json.dumps(ticket)
                ))

                processed_count += 1

            except Exception as e:
                logger.error(f"Error processing ticket {ticket.get('key', 'unknown')}: {e}")
                continue

        conn.commit()
        conn.close()

        logger.info(f"Processed and stored {processed_count} tickets")

    def generate_dashboard_data(self) -> Dict:
        """Generate dashboard analytics data"""
        conn = sqlite3.connect(self.db_path)

        # Get overview metrics
        overview_query = '''
            SELECT
                COUNT(*) as total_tickets,
                COUNT(CASE WHEN status NOT IN ('Done', 'Resolved', 'Closed') THEN 1 END) as open_tickets,
                COUNT(CASE WHEN pixel_priority = 'high' THEN 1 END) as high_priority,
                COUNT(CASE WHEN pixel_priority = 'critical' THEN 1 END) as critical_tickets,
                AVG(resolution_time_hours) as avg_resolution_hours
            FROM pixel_tickets
            WHERE created_date >= date('now', '-30 days')
        '''

        overview = pd.read_sql_query(overview_query, conn).iloc[0].to_dict()

        # Get category breakdown
        category_query = '''
            SELECT
                category,
                COUNT(*) as count,
                COUNT(CASE WHEN status NOT IN ('Done', 'Resolved', 'Closed') THEN 1 END) as open_count,
                AVG(resolution_time_hours) as avg_resolution_hours
            FROM pixel_tickets
            WHERE created_date >= date('now', '-30 days')
            GROUP BY category
            ORDER BY count DESC
        '''

        category_breakdown = pd.read_sql_query(category_query, conn)

        # Get client breakdown
        client_query = '''
            SELECT
                client,
                COUNT(*) as count,
                COUNT(CASE WHEN status NOT IN ('Done', 'Resolved', 'Closed') THEN 1 END) as open_count
            FROM pixel_tickets
            WHERE created_date >= date('now', '-30 days') AND client IS NOT NULL
            GROUP BY client
            ORDER BY count DESC
            LIMIT 10
        '''

        client_breakdown = pd.read_sql_query(client_query, conn)

        # Get recent critical tickets
        critical_query = '''
            SELECT ticket_key, summary, client, created_date, status
            FROM pixel_tickets
            WHERE pixel_priority IN ('critical', 'high')
            AND status NOT IN ('Done', 'Resolved', 'Closed')
            ORDER BY created_date DESC
            LIMIT 10
        '''

        critical_tickets = pd.read_sql_query(critical_query, conn)

        # Get trend data (last 30 days)
        trend_query = '''
            SELECT
                DATE(created_date) as date,
                COUNT(*) as tickets_created,
                COUNT(CASE WHEN pixel_priority = 'high' THEN 1 END) as high_priority_created
            FROM pixel_tickets
            WHERE created_date >= date('now', '-30 days')
            GROUP BY DATE(created_date)
            ORDER BY date
        '''

        trend_data = pd.read_sql_query(trend_query, conn)

        conn.close()

        dashboard_data = {
            'overview': overview,
            'category_breakdown': category_breakdown.to_dict('records'),
            'client_breakdown': client_breakdown.to_dict('records'),
            'critical_tickets': critical_tickets.to_dict('records'),
            'trend_data': trend_data.to_dict('records'),
            'generated_at': datetime.now().isoformat()
        }

        return dashboard_data

    def create_jira_dashboard_filter(self) -> str:
        """Create JQL filter for Jira dashboard"""
        base_jql = '''
        project = PS AND (
            summary ~ "pixel" OR
            description ~ "pixel" OR
            summary ~ "conversion" OR
            summary ~ "tracking" OR
            summary ~ "validation" OR
            summary ~ "discrepancy" OR
            description ~ "1P and 3P" OR
            description ~ "Samsung pixel" OR
            description ~ "data mismatch"
        )
        ORDER BY created DESC, priority DESC
        '''

        return base_jql.strip()

    def export_dashboard_csv(self, filename: str = None):
        """Export dashboard data to CSV"""
        if not filename:
            filename = f"pixel_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        conn = sqlite3.connect(self.db_path)

        query = '''
            SELECT
                ticket_key, summary, description, status, priority,
                created_date, updated_date, assignee, reporter, client,
                category, pixel_priority, resolution_time_hours
            FROM pixel_tickets
            ORDER BY created_date DESC
        '''

        df = pd.read_sql_query(query, conn)
        conn.close()

        df.to_csv(filename, index=False)
        logger.info(f"Dashboard data exported to {filename}")

        return filename

def main():
    """Main function to demonstrate dashboard system"""

    # Jira configuration
    jira_config = {
        'base_url': 'https://adgear.atlassian.net',
        'email': 'l.spahn@samsung.com',
        'token': 'YOUR_JIRA_API_TOKEN_HERE'
    }

    # Create dashboard system
    dashboard = PixelDashboardSystem(jira_config)

    print("🎛️ Pixel Dashboard System")
    print("=" * 40)

    # Fetch and process tickets
    print("📥 Fetching pixel tickets from Jira...")
    tickets = dashboard.fetch_pixel_tickets(days_back=90)

    print("🔄 Processing and classifying tickets...")
    dashboard.process_and_store_tickets(tickets)

    # Generate dashboard
    print("📊 Generating dashboard analytics...")
    dashboard_data = dashboard.generate_dashboard_data()

    # Display results
    print("\n📈 PIXEL DASHBOARD OVERVIEW")
    print("=" * 40)
    overview = dashboard_data['overview']
    print(f"Total Tickets (30 days): {overview['total_tickets']}")
    print(f"Open Tickets: {overview['open_tickets']}")
    print(f"High Priority: {overview['high_priority']}")
    print(f"Critical: {overview['critical_tickets']}")
    if overview['avg_resolution_hours']:
        print(f"Avg Resolution: {overview['avg_resolution_hours']:.1f} hours")

    print(f"\n📂 CATEGORY BREAKDOWN")
    print("=" * 40)
    for category in dashboard_data['category_breakdown']:
        print(f"{category['category']:20s}: {category['count']:3d} total, {category['open_count']:3d} open")

    print(f"\n👥 TOP CLIENTS")
    print("=" * 40)
    for client in dashboard_data['client_breakdown'][:5]:
        print(f"{client['client']:20s}: {client['count']:3d} tickets")

    # Export data
    csv_file = dashboard.export_dashboard_csv()
    print(f"\n💾 Data exported to: {csv_file}")

    # Show JQL for Jira dashboard
    jql = dashboard.create_jira_dashboard_filter()
    print(f"\n🔍 Jira Dashboard JQL:")
    print(jql)

    print(f"\n✅ Dashboard system ready!")

if __name__ == "__main__":
    main()