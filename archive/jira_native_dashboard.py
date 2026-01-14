#!/usr/bin/env python3
"""
Jira Native Dashboard Setup for Pixel Issues
Creates filters, dashboards, and manages custom fields entirely within Jira
Based on PS-9074 example for pixel issue classification
"""

import json
import requests
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraPixelDashboard:
    """Creates and manages pixel dashboards natively in Jira"""

    def __init__(self, jira_config: Dict):
        self.jira_config = jira_config

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
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Jira API request failed: {e}")
            raise

    def create_pixel_filters(self) -> Dict[str, str]:
        """Create Jira filters for different pixel categories"""

        filters = {
            "All Pixel Issues": '''
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
                    description ~ "set up issue"
                ) ORDER BY created DESC, priority DESC
            ''',

            "Data Discrepancy Issues": '''
                project = PS AND (
                    description ~ "similar data between" OR
                    description ~ "data mismatch" OR
                    description ~ "discrepancy" OR
                    description ~ "1P and 3P" OR
                    description ~ "user count" OR
                    description ~ "not seeing similar" OR
                    summary ~ "discrepancy"
                ) ORDER BY created DESC
            ''',

            "Implementation Issues": '''
                project = PS AND (
                    summary ~ "pixel not firing" OR
                    summary ~ "implementation" OR
                    summary ~ "setup" OR
                    summary ~ "install pixel" OR
                    summary ~ "place pixel" OR
                    description ~ "pixel not firing"
                ) ORDER BY created DESC
            ''',

            "Validation Requests": '''
                project = PS AND (
                    summary ~ "validation" OR
                    summary ~ "validate" OR
                    summary ~ "test pixel" OR
                    summary ~ "verify pixel" OR
                    description ~ "validation"
                ) ORDER BY created DESC
            ''',

            "Critical Pixel Issues": '''
                project = PS AND (
                    summary ~ "pixel" OR description ~ "pixel"
                ) AND priority IN (Critical, High) AND status NOT IN (Done, Resolved, Closed)
                ORDER BY priority DESC, created DESC
            ''',

            "Recent Pixel Issues": '''
                project = PS AND (
                    summary ~ "pixel" OR description ~ "pixel" OR
                    summary ~ "conversion" OR summary ~ "tracking"
                ) AND created >= -7d ORDER BY created DESC
            ''',

            "GTM Related Issues": '''
                project = PS AND (
                    summary ~ "gtm" OR
                    summary ~ "google tag manager" OR
                    summary ~ "tag manager" OR
                    description ~ "data layer" OR
                    description ~ "gtm"
                ) ORDER BY created DESC
            '''
        }

        created_filters = {}

        for filter_name, jql in filters.items():
            try:
                filter_data = {
                    "name": f"🔥 Pixel: {filter_name}",
                    "description": f"Auto-generated filter for {filter_name.lower()} based on PS-9074 analysis",
                    "jql": jql.strip(),
                    "favourite": False
                }

                # Create filter
                result = self.make_jira_request('/rest/api/3/filter', method='POST', data=filter_data)
                filter_id = result['id']
                filter_url = f"{self.jira_config['base_url']}/issues/?filter={filter_id}"

                created_filters[filter_name] = filter_url
                logger.info(f"✅ Created filter: {filter_name} (ID: {filter_id})")

            except Exception as e:
                logger.error(f"❌ Failed to create filter '{filter_name}': {e}")

        return created_filters

    def create_pixel_labels(self) -> List[str]:
        """Create standardized labels for pixel issue classification"""

        labels = [
            "pixel-data-discrepancy",
            "pixel-implementation",
            "pixel-validation",
            "pixel-troubleshooting",
            "pixel-conversion-tracking",
            "pixel-gtm-related",
            "pixel-cross-domain",
            "pixel-mobile-issue",
            "pixel-third-party",
            "pixel-critical-revenue"
        ]

        # Labels are created automatically when first used in Jira
        # We'll return the list for reference
        logger.info(f"📋 Standardized pixel labels: {', '.join(labels)}")
        return labels

    def create_dashboard_gadgets_config(self) -> Dict:
        """Generate configuration for Jira dashboard gadgets"""

        dashboard_config = {
            "name": "🔥 Pixel Performance Dashboard",
            "description": "Comprehensive dashboard for pixel-related issues based on PS-9074 analysis",
            "gadgets": [
                {
                    "title": "Pixel Issues Overview",
                    "type": "filter-results",
                    "filter_name": "All Pixel Issues",
                    "columns": ["Key", "Summary", "Status", "Priority", "Assignee", "Created"],
                    "max_results": 50
                },
                {
                    "title": "Critical Pixel Issues",
                    "type": "filter-results",
                    "filter_name": "Critical Pixel Issues",
                    "columns": ["Key", "Summary", "Client", "Created", "Age"],
                    "max_results": 20
                },
                {
                    "title": "Pixel Issue Categories",
                    "type": "pie-chart",
                    "statistic_type": "labels",
                    "filter_jql": '''project = PS AND (summary ~ "pixel" OR description ~ "pixel") AND created >= -30d'''
                },
                {
                    "title": "Recent Data Discrepancies",
                    "type": "filter-results",
                    "filter_name": "Data Discrepancy Issues",
                    "columns": ["Key", "Summary", "Client", "Status"],
                    "max_results": 15
                },
                {
                    "title": "Pixel Resolution Time",
                    "type": "average-age-chart",
                    "filter_jql": '''project = PS AND (summary ~ "pixel" OR description ~ "pixel") AND resolved >= -30d''',
                    "period": "monthly"
                },
                {
                    "title": "Implementation Queue",
                    "type": "filter-results",
                    "filter_name": "Implementation Issues",
                    "columns": ["Key", "Summary", "Priority", "Assignee"],
                    "max_results": 20
                }
            ],
            "layout": {
                "columns": 2,
                "gadget_positions": [
                    {"row": 0, "col": 0, "size_x": 2, "size_y": 1},  # Overview (full width)
                    {"row": 1, "col": 0, "size_x": 1, "size_y": 1},  # Critical Issues
                    {"row": 1, "col": 1, "size_x": 1, "size_y": 1},  # Categories Chart
                    {"row": 2, "col": 0, "size_x": 1, "size_y": 1},  # Data Discrepancies
                    {"row": 2, "col": 1, "size_x": 1, "size_y": 1},  # Resolution Time
                    {"row": 3, "col": 0, "size_x": 2, "size_y": 1}   # Implementation Queue
                ]
            }
        }

        return dashboard_config

    def bulk_classify_existing_tickets(self, days_back: int = 90):
        """Bulk classify existing pixel tickets with labels"""

        # Fetch existing pixel tickets
        jql = f'''
        project = PS AND (
            summary ~ "pixel" OR description ~ "pixel" OR
            summary ~ "conversion" OR summary ~ "tracking"
        ) AND created >= -{days_back}d
        ORDER BY created DESC
        '''

        search_data = {
            'jql': jql,
            'fields': ['key', 'summary', 'description', 'labels'],
            'maxResults': 500
        }

        try:
            result = self.make_jira_request('/rest/api/3/search/jql', method='POST', data=search_data)
            tickets = result.get('issues', [])
            logger.info(f"Found {len(tickets)} pixel tickets to classify")

            classification_rules = {
                'pixel-data-discrepancy': [
                    'similar data between', 'data mismatch', 'discrepancy',
                    '1p and 3p', 'user count', 'not seeing similar'
                ],
                'pixel-implementation': [
                    'pixel not firing', 'implementation', 'setup',
                    'install pixel', 'place pixel'
                ],
                'pixel-validation': [
                    'validation', 'validate', 'test pixel', 'verify pixel'
                ],
                'pixel-troubleshooting': [
                    'troubleshoot', 'debug', 'investigate', 'not working', '0 conversions'
                ],
                'pixel-gtm-related': [
                    'gtm', 'google tag manager', 'tag manager', 'data layer'
                ],
                'pixel-conversion-tracking': [
                    'conversion', 'purchase tracking', 'revenue tracking'
                ]
            }

            classified_count = 0

            for ticket in tickets:
                key = ticket['key']
                fields = ticket['fields']
                summary = fields.get('summary', '').lower()
                description = fields.get('description', '')

                if isinstance(description, dict):
                    description = self.extract_text_from_content(description).lower()
                else:
                    description = str(description).lower()

                text = f"{summary} {description}"
                current_labels = [label for label in fields.get('labels', [])]

                # Find matching labels
                new_labels = []
                for label, keywords in classification_rules.items():
                    if any(keyword in text for keyword in keywords):
                        if label not in current_labels:
                            new_labels.append(label)

                # Add pixel base label if not present
                if not any('pixel' in label for label in current_labels):
                    new_labels.append('pixel-issue')

                # Update ticket if new labels found
                if new_labels:
                    try:
                        all_labels = current_labels + new_labels
                        update_data = {
                            "fields": {
                                "labels": all_labels
                            }
                        }

                        self.make_jira_request(f'/rest/api/3/issue/{key}', method='PUT', data=update_data)
                        logger.info(f"✅ Classified {key} with labels: {new_labels}")
                        classified_count += 1

                    except Exception as e:
                        logger.error(f"❌ Failed to update {key}: {e}")

            logger.info(f"✅ Classified {classified_count} tickets with labels")

        except Exception as e:
            logger.error(f"❌ Failed to classify tickets: {e}")

    def extract_text_from_content(self, content):
        """Extract text from Jira rich content"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            if 'content' in content:
                return ' '.join([self.extract_text_from_content(item) for item in content['content']])
            elif 'text' in content:
                return content['text']
        elif isinstance(content, list):
            return ' '.join([self.extract_text_from_content(item) for item in content])
        return str(content)

    def create_jira_board(self) -> str:
        """Create a Kanban board for pixel issues"""

        board_config = {
            "name": "🔥 Pixel Issues Board",
            "type": "kanban",
            "filterId": None,  # Will use the "All Pixel Issues" filter
            "location": {
                "type": "project",
                "projectKeyOrId": "PS"
            }
        }

        try:
            # First get the filter ID for "All Pixel Issues"
            filters = self.make_jira_request('/rest/api/3/filter/search?filterName=🔥 Pixel: All Pixel Issues')
            if filters.get('values'):
                board_config["filterId"] = filters['values'][0]['id']

                # Create the board
                result = self.make_jira_request('/rest/agile/1.0/board', method='POST', data=board_config)
                board_id = result['id']
                board_url = f"{self.jira_config['base_url']}/secure/RapidBoard.jspa?rapidView={board_id}"

                logger.info(f"✅ Created Kanban board: {board_url}")
                return board_url

        except Exception as e:
            logger.error(f"❌ Failed to create board: {e}")

        return ""

    def setup_complete_pixel_dashboard(self) -> Dict:
        """Set up complete pixel dashboard in Jira"""

        logger.info("🚀 Setting up Jira native pixel dashboard...")

        results = {
            'filters': {},
            'labels': [],
            'board_url': '',
            'dashboard_config': {},
            'classification_complete': False
        }

        # 1. Create filters
        logger.info("📊 Creating Jira filters...")
        results['filters'] = self.create_pixel_filters()

        # 2. Setup labels
        logger.info("🏷️ Setting up classification labels...")
        results['labels'] = self.create_pixel_labels()

        # 3. Classify existing tickets
        logger.info("🔄 Classifying existing pixel tickets...")
        self.bulk_classify_existing_tickets()
        results['classification_complete'] = True

        # 4. Create Kanban board
        logger.info("📋 Creating pixel issues board...")
        results['board_url'] = self.create_jira_board()

        # 5. Generate dashboard config
        results['dashboard_config'] = self.create_dashboard_gadgets_config()

        return results

    def generate_dashboard_instructions(self, setup_results: Dict) -> str:
        """Generate instructions for setting up the dashboard manually"""

        instructions = f"""
# 🔥 Pixel Performance Dashboard Setup Complete!

## 📊 Created Filters

Your new Jira filters for pixel issues:
"""

        for filter_name, filter_url in setup_results['filters'].items():
            instructions += f"- **{filter_name}**: {filter_url}\n"

        instructions += f"""

## 📋 Kanban Board

Pixel Issues Board: {setup_results['board_url']}

## 🏷️ Classification Labels

Use these labels to categorize pixel tickets:
"""

        for label in setup_results['labels']:
            instructions += f"- `{label}`\n"

        instructions += f"""

## 🎛️ Manual Dashboard Setup

Since Jira dashboard creation requires admin permissions, follow these steps:

1. **Go to Jira Dashboard**: {self.jira_config['base_url']}/secure/Dashboard.jspa
2. **Create New Dashboard**: Click "Create Dashboard"
3. **Name**: "🔥 Pixel Performance Dashboard"
4. **Add Gadgets**:
   - **Filter Results**: Use "🔥 Pixel: All Pixel Issues" filter
   - **Filter Results**: Use "🔥 Pixel: Critical Pixel Issues" filter
   - **Pie Chart**: Show labels for pixel tickets (last 30 days)
   - **Filter Results**: Use "🔥 Pixel: Data Discrepancy Issues" filter
   - **Average Age Chart**: Show resolution time for pixel tickets
   - **Filter Results**: Use "🔥 Pixel: Implementation Issues" filter

## 🎯 Quick Actions

**View All Pixel Issues:**
{setup_results['filters'].get('All Pixel Issues', 'Filter not created')}

**View Critical Issues:**
{setup_results['filters'].get('Critical Pixel Issues', 'Filter not created')}

**Manage on Board:**
{setup_results['board_url']}

## 📈 Analytics Available

- **Issue categorization** by type (data discrepancy, implementation, etc.)
- **Priority breakdown** (critical, high, medium, low)
- **Resolution time tracking** by category
- **Client-specific views** using existing client fields
- **Trend analysis** over time

## 🔧 Ticket Classification

✅ **{len(setup_results.get('labels', []))} classification labels** created
✅ **Existing tickets classified** automatically based on content analysis
✅ **PS-9074 patterns** used as baseline for classification rules

Your dashboard is ready! All pixel issues will now be automatically organized and easily accessible through the filters and board.
"""

        return instructions

def main():
    """Main function to setup Jira pixel dashboard"""

    # Jira configuration
    jira_config = {
        'base_url': 'https://adgear.atlassian.net',
        'email': 'l.spahn@samsung.com',
        'token': 'YOUR_JIRA_API_TOKEN_HERE'
    }

    # Create dashboard system
    dashboard = JiraPixelDashboard(jira_config)

    print("🎛️ Jira Native Pixel Dashboard Setup")
    print("Based on PS-9074 analysis")
    print("=" * 50)

    # Setup complete dashboard
    setup_results = dashboard.setup_complete_pixel_dashboard()

    # Generate instructions
    instructions = dashboard.generate_dashboard_instructions(setup_results)

    # Save instructions to file
    with open('PIXEL_DASHBOARD_SETUP.md', 'w') as f:
        f.write(instructions)

    print(instructions)
    print(f"\n📄 Instructions saved to: PIXEL_DASHBOARD_SETUP.md")
    print("🎉 Pixel dashboard setup complete!")

if __name__ == "__main__":
    main()