#!/usr/bin/env python3
"""
Dashboard Integration for Enhanced Pixel Monitor
Automatically categorizes detected pixel issues and updates dashboard
"""

import json
import requests
import base64
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PixelDashboardIntegration:
    """Integration between pixel monitoring and Jira dashboard"""

    def __init__(self, jira_config):
        self.jira_config = jira_config

    def make_jira_request(self, endpoint: str, method: str = 'GET', data: dict = None):
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

            if response.status_code == 204:  # No content response (successful update)
                return {"success": True}

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Jira API request failed: {e}")
            return None

    def categorize_pixel_issue(self, summary: str, description: str) -> tuple:
        """Categorize pixel issue based on content (matches dashboard categories)"""

        text = f"{summary} {description}".lower()

        # Category mapping (matches jira_native_dashboard.py)
        categories = {
            'pixel-data-discrepancy': [
                'similar data between', 'data mismatch', 'discrepancy',
                '1p and 3p', 'user count', 'not seeing similar', 'confirmation page data'
            ],
            'pixel-implementation': [
                'pixel not firing', 'implementation', 'setup', 'install pixel',
                'place pixel', 'add pixel', 'deploy pixel'
            ],
            'pixel-validation': [
                'validation', 'validate', 'test pixel', 'verify pixel',
                'check pixel', 'pixel testing'
            ],
            'pixel-troubleshooting': [
                'troubleshoot', 'debug', 'investigate', 'pixel issue',
                'not working', 'broken pixel', '0 conversions'
            ],
            'pixel-conversion-tracking': [
                'conversion', 'conversion tracking', 'purchase tracking',
                'conversion pixel', 'revenue tracking'
            ],
            'pixel-gtm-related': [
                'gtm', 'google tag manager', 'tag manager', 'data layer',
                'gtm container', 'tag configuration'
            ]
        }

        # Find best matching category
        best_category = 'pixel-implementation'  # default
        max_matches = 0

        for category, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category

        # Determine priority based on keywords
        high_priority_indicators = [
            'critical', 'urgent', 'revenue impact', 'client escalation',
            'not firing', 'broken', '0 conversions', 'data mismatch'
        ]

        priority = 'medium'
        if any(indicator in text for indicator in high_priority_indicators):
            priority = 'high'

        return best_category, priority

    def add_comment_to_ticket(self, ticket_key: str, comment: str) -> bool:
        """Add comment to Jira ticket"""

        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }

        result = self.make_jira_request(f'/rest/api/3/issue/{ticket_key}/comment',
                                      method='POST', data=comment_data)

        if result:
            logger.info(f"✅ Added dashboard comment to {ticket_key}")
            return True
        else:
            logger.error(f"❌ Failed to add comment to {ticket_key}")
            return False

    def update_pixel_monitoring_integration(self, ticket_key: str, summary: str,
                                          description: str, confidence: float,
                                          detection_method: str) -> dict:
        """Update ticket with pixel monitoring information and dashboard categorization"""

        # Categorize the issue
        category, priority = self.categorize_pixel_issue(summary, description)

        # Create dashboard integration comment
        dashboard_comment = f"""🔥 **Pixel Monitoring System Detection**

**Detection Confidence:** {confidence:.1%}
**Detection Method:** {detection_method}
**Dashboard Category:** {category.replace('-', ' ').title()}
**Suggested Priority:** {priority.title()}

**Dashboard Links:**
• [View All Pixel Issues](https://adgear.atlassian.net/issues/?filter=26558)
• [View Critical Issues](https://adgear.atlassian.net/issues/?filter=26562)
• [Pixel Issues Board](https://adgear.atlassian.net/secure/RapidBoard.jspa?rapidView=7539)

**Category-Specific Filters:**"""

        # Add category-specific filter links
        category_filters = {
            'pixel-data-discrepancy': 'https://adgear.atlassian.net/issues/?filter=26559',
            'pixel-implementation': 'https://adgear.atlassian.net/issues/?filter=26560',
            'pixel-validation': 'https://adgear.atlassian.net/issues/?filter=26561',
            'pixel-gtm-related': 'https://adgear.atlassian.net/issues/?filter=26564'
        }

        if category in category_filters:
            dashboard_comment += f"\n• [View {category.replace('-', ' ').title()} Issues]({category_filters[category]})"

        dashboard_comment += f"\n\n*Auto-generated by Enhanced Pixel Monitoring System at {datetime.now().strftime('%Y-%m-%d %H:%M')}*"

        # Add comment to ticket
        success = self.add_comment_to_ticket(ticket_key, dashboard_comment)

        return {
            'ticket_key': ticket_key,
            'category': category,
            'priority': priority,
            'comment_added': success,
            'dashboard_links': {
                'all_issues': 'https://adgear.atlassian.net/issues/?filter=26558',
                'critical_issues': 'https://adgear.atlassian.net/issues/?filter=26562',
                'board': 'https://adgear.atlassian.net/secure/RapidBoard.jspa?rapidView=7539',
                'category_filter': category_filters.get(category)
            }
        }

    def get_dashboard_metrics(self) -> dict:
        """Get current dashboard metrics"""

        # Query each filter for current counts
        filters = {
            'all_pixel_issues': 26558,
            'critical_issues': 26562,
            'data_discrepancy': 26559,
            'implementation': 26560,
            'validation': 26561,
            'recent_issues': 26563,
            'gtm_related': 26564
        }

        metrics = {}

        for filter_name, filter_id in filters.items():
            try:
                result = self.make_jira_request(f'/rest/api/3/search/jql?jql=filter={filter_id}&maxResults=0')
                if result:
                    metrics[filter_name] = result.get('total', 0)
                else:
                    metrics[filter_name] = 0
            except:
                metrics[filter_name] = 0

        metrics['last_updated'] = datetime.now().isoformat()

        return metrics

# Integration with enhanced pixel monitor
def integrate_with_dashboard(ticket_key: str, summary: str, description: str,
                           confidence: float, detection_method: str,
                           jira_config: dict) -> dict:
    """
    Main integration function to call from enhanced pixel monitor
    """

    dashboard_integration = PixelDashboardIntegration(jira_config)

    result = dashboard_integration.update_pixel_monitoring_integration(
        ticket_key, summary, description, confidence, detection_method
    )

    logger.info(f"🎛️ Dashboard integration complete for {ticket_key}")
    logger.info(f"   Category: {result['category']}")
    logger.info(f"   Priority: {result['priority']}")
    logger.info(f"   Board: {result['dashboard_links']['board']}")

    return result

if __name__ == "__main__":
    # Test with PS-9074 example
    jira_config = {
        'base_url': 'https://adgear.atlassian.net',
        'email': 'l.spahn@samsung.com',
        'token': 'YOUR_JIRA_API_TOKEN_HERE'
    }

    # Test categorization
    dashboard_integration = PixelDashboardIntegration(jira_config)

    # Test PS-9074 example
    category, priority = dashboard_integration.categorize_pixel_issue(
        "Samsung pixel vs Golo's user count",
        "Not currently seeing similar confirmation page data between 1P and 3P parties. Want to determine if there is a set up issue."
    )

    print(f"PS-9074 categorized as: {category} (priority: {priority})")

    # Get current dashboard metrics
    metrics = dashboard_integration.get_dashboard_metrics()
    print(f"\nDashboard Metrics:")
    for metric, count in metrics.items():
        if metric != 'last_updated':
            print(f"  {metric}: {count}")