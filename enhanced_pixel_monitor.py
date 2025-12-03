#!/usr/bin/env python3
"""
Enhanced Pixel Notification Monitor with Learning Integration
Integrates automated learning system for continuous improvement of detection accuracy.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pixel_notification_monitor import *
from learning_system import PixelDetectionLearningSystem, interactive_feedback_prompt
import argparse

class EnhancedPixelMonitor:
    """Enhanced pixel monitor with learning capabilities"""

    def __init__(self):
        self.learning_system = PixelDetectionLearningSystem()
        logger.info("🧠 Enhanced Pixel Monitor with Learning System initialized")

    def enhanced_is_pixel_related_ticket(self, summary, description=''):
        """Enhanced detection using hybrid rule-based + ML approach"""

        # Get original rule-based result
        rule_result, rule_reason = is_pixel_related_ticket(summary, description)

        # Estimate rule confidence based on detection reason
        rule_confidence = self.estimate_rule_confidence(rule_reason)

        # Use hybrid detection
        final_result, combined_confidence, analysis = self.learning_system.hybrid_detection(
            summary, description, rule_result, rule_confidence
        )

        # Log the enhanced detection
        method = analysis['method']
        logger.info(f"🧠 Enhanced detection ({method}): {final_result} (confidence: {combined_confidence:.3f})")

        if analysis['method'] == 'hybrid':
            rule_pred = analysis['rule_based']['prediction']
            ml_pred = analysis['ml_based']['prediction']
            logger.info(f"   Rule-based: {rule_pred} ({analysis['rule_based']['confidence']:.3f})")
            logger.info(f"   ML-based: {ml_pred} ({analysis['ml_based']['confidence']:.3f})")

        return final_result, rule_reason, combined_confidence, analysis

    def estimate_rule_confidence(self, rule_reason: str) -> float:
        """Estimate confidence based on rule detection reason"""
        confidence_map = {
            # High confidence patterns
            'high:pixel_validation': 0.95,
            'high:pixel_not_firing': 0.95,
            'high:conversion_pixel': 0.90,
            'high:tracking_pixel': 0.90,
            'high:universal_tag': 0.90,
            'high:append_pixel': 0.85,

            # Medium confidence patterns (more prone to false positives)
            'medium:tracking_action': 0.60,  # This caught PS-9998
            'medium:conversion_web': 0.70,

            # Context-based patterns
            'pixel_context:firing': 0.85,
            'pixel_context:validation': 0.85,
            'pixel_context:setup': 0.75,
            'pixel_context:conversion': 0.80,

            # Default
            'no_match': 0.0
        }

        return confidence_map.get(rule_reason, 0.5)

    def process_ticket_with_learning(self, ticket):
        """Process a ticket with enhanced detection and optional feedback collection"""

        ticket_key = ticket.get('key', 'UNKNOWN')
        summary = ticket.get('fields', {}).get('summary', '')
        description = ticket.get('fields', {}).get('description', '')

        # Enhanced detection
        is_pixel, reason, confidence, analysis = self.enhanced_is_pixel_related_ticket(summary, description)

        if is_pixel:
            # Log the detection
            logger.warning(f"🚨🔥 ENHANCED PIXEL ALERT: {ticket_key} - {summary[:50]}... 🔥🚨")
            logger.info(f"Detection confidence: {confidence:.3f}")
            logger.info(f"Detection method: {analysis['method']}")

            # Send notification (keeping original functionality)
            if NOTIFICATION_CONFIG['email']['enabled'] or NOTIFICATION_CONFIG['console']['enabled']:
                self.send_enhanced_notification(ticket, reason, confidence, analysis)

            # Collect feedback if in interactive mode
            if hasattr(self, 'interactive_mode') and self.interactive_mode:
                self.collect_feedback(ticket_key, summary, description, reason, confidence)

        return is_pixel, confidence

    def send_enhanced_notification(self, ticket, reason, confidence, analysis):
        """Send enhanced notification with confidence and learning info"""

        ticket_key = ticket.get('key', 'UNKNOWN')
        summary = ticket.get('fields', {}).get('summary', '')

        # Create enhanced message
        confidence_emoji = "🔥" if confidence > 0.8 else "⚠️" if confidence > 0.6 else "💭"
        method_info = f"({analysis['method'].upper()})" if analysis['method'] == 'hybrid' else ""

        subject = f"{confidence_emoji} Pixel Alert {method_info}: {ticket_key} - {summary[:50]}..."

        enhanced_message = f"""🔔 ENHANCED PIXEL DETECTION ALERT

Ticket: {ticket_key}
Summary: {summary}
Detection Confidence: {confidence:.1%}
Detection Method: {analysis['method'].title()}

Detection Details:
- Reason: {reason}
- Rule-based: {analysis['rule_based']['prediction']} ({analysis['rule_based']['confidence']:.3f})
"""

        if analysis['method'] == 'hybrid':
            enhanced_message += f"- ML-based: {analysis['ml_based']['prediction']} ({analysis['ml_based']['confidence']:.3f})\n"

        enhanced_message += f"""
Key Features Detected:
- Pixel keywords: {'✓' if analysis['features']['has_pixel'] else '✗'}
- Tracking terms: {'✓' if analysis['features']['has_tracking'] else '✗'}
- Technical context: {analysis['features']['technical_terms']} terms
- DSP related: {'✓' if analysis['features']['dsp_related'] else '✗'}

🧠 This alert was generated by the Enhanced Pixel Monitor with Learning System.
To improve accuracy, please provide feedback on this detection.

View ticket: https://adgear.atlassian.net/browse/{ticket_key}
"""

        # Send notification using original method but with enhanced message
        if NOTIFICATION_CONFIG['console']['enabled']:
            logger.info("📧 ENHANCED EMAIL NOTIFICATION (would send - no password configured):")
            logger.info(f"To: {NOTIFICATION_CONFIG['email']['to_emails']}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Message preview: {enhanced_message[:200]}...")

        # TODO: Implement actual email sending with enhanced message

    def collect_feedback(self, ticket_key, summary, description, reason, confidence):
        """Collect user feedback on detection accuracy"""

        try:
            feedback = interactive_feedback_prompt(ticket_key, summary, reason)

            if feedback != 'skip':
                self.learning_system.record_feedback(
                    ticket_key, summary, description, reason, feedback, confidence
                )
                logger.info(f"✅ Feedback recorded for {ticket_key}: {feedback}")

                # Try to retrain model if we have enough data
                if feedback in ['true_positive', 'false_positive']:
                    self.learning_system.train_ml_model()

        except KeyboardInterrupt:
            logger.info("Feedback collection interrupted by user")
        except Exception as e:
            logger.error(f"Error collecting feedback: {e}")

    def run_enhanced_monitoring(self, interactive=False):
        """Run the enhanced monitoring loop"""

        self.interactive_mode = interactive

        logger.info("🚀 Starting Enhanced Pixel Ticket Notification Monitor")
        logger.info(f"Check interval: {NOTIFICATION_CONFIG['check_interval']} seconds")
        logger.info(f"Lookback period: {NOTIFICATION_CONFIG['lookback_hours']} hours")
        logger.info(f"Interactive feedback: {'enabled' if interactive else 'disabled'}")
        logger.info(f"Learning system: enabled 🧠")

        # Show current performance metrics
        metrics = self.learning_system.get_performance_metrics()
        total_feedback = metrics['total_feedback']

        if total_feedback > 0:
            logger.info(f"📊 Current Performance: {total_feedback} feedback samples collected")
            fb_metrics = metrics['feedback_based']
            logger.info(f"   Precision: {fb_metrics['precision']:.1%}, Recall: {fb_metrics['recall']:.1%}")

        while True:
            try:
                self.check_for_enhanced_pixel_tickets()
                logger.info(f"Sleeping for {NOTIFICATION_CONFIG['check_interval']} seconds...")
                time.sleep(NOTIFICATION_CONFIG['check_interval'])

            except KeyboardInterrupt:
                logger.info("Enhanced monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in enhanced monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def check_for_enhanced_pixel_tickets(self):
        """Enhanced version of ticket checking"""

        logger.info("Starting enhanced pixel ticket check...")

        # Calculate time window
        now = datetime.now()
        cutoff_time = now - timedelta(hours=NOTIFICATION_CONFIG['lookback_hours'])
        jql_time = cutoff_time.strftime('%Y-%m-%d %H:%M')

        logger.info(f"Searching for tickets created after: {jql_time}")

        try:
            # Search for recent tickets using the new API endpoint
            jql = f'project = {JIRA_CONFIG["project_key"]} AND created >= "{jql_time}" ORDER BY created DESC'

            # Use the new search/jql endpoint with POST method
            data = {
                'jql': jql,
                'fields': ['key', 'summary', 'description', 'created', 'priority', 'status', 'creator'],
                'maxResults': 50
            }
            response = make_jira_request('/rest/api/3/search/jql', method='POST', data=data)

            tickets = response.get('issues', [])
            logger.info(f"Found {len(tickets)} recent tickets")

            if not tickets:
                logger.info("No recent tickets found")
                return

            pixel_tickets_found = 0

            for ticket in tickets:
                is_pixel, confidence = self.process_ticket_with_learning(ticket)

                if is_pixel:
                    pixel_tickets_found += 1

            if pixel_tickets_found > 0:
                logger.info(f"Found {pixel_tickets_found} pixel-related tickets in this check")
            else:
                logger.info("No pixel-related tickets found in recent tickets")

        except Exception as e:
            logger.error(f"Error in enhanced ticket check: {e}")

    def run_learning_analysis(self):
        """Run analysis on learning patterns and performance"""

        logger.info("🧠 Running Learning System Analysis...")

        # Get performance metrics
        metrics = self.learning_system.get_performance_metrics()
        print("\n📊 PERFORMANCE METRICS")
        print("=" * 50)

        fb_metrics = metrics['feedback_based']
        print(f"Feedback-based Performance:")
        print(f"  True Positives: {fb_metrics['true_positives']}")
        print(f"  False Positives: {fb_metrics['false_positives']}")
        print(f"  False Negatives: {fb_metrics['false_negatives']}")
        print(f"  Precision: {fb_metrics['precision']:.1%}")
        print(f"  Recall: {fb_metrics['recall']:.1%}")
        print(f"  F1-Score: {fb_metrics['f1_score']:.3f}")

        model_metrics = metrics['model_based']
        if model_metrics['training_samples']:
            print(f"\nML Model Performance:")
            print(f"  Training Samples: {model_metrics['training_samples']}")
            print(f"  Model Precision: {model_metrics['precision']:.1%}")
            print(f"  Model Recall: {model_metrics['recall']:.1%}")
            print(f"  Model F1-Score: {model_metrics['f1_score']:.3f}")
        else:
            print(f"\nML Model: Not yet trained (need more feedback data)")

        # Analyze patterns
        patterns = self.learning_system.analyze_patterns()

        if patterns['false_positive_count'] > 0:
            print(f"\n🚨 FALSE POSITIVE ANALYSIS")
            print("=" * 50)
            print(f"False Positives Found: {patterns['false_positive_count']}")
            print("Common patterns in false positives:")
            for pattern, count in patterns['common_fp_patterns'][:5]:
                print(f"  '{pattern}': {count} occurrences")

            if patterns['suggested_exclusions']:
                print(f"\n💡 SUGGESTED EXCLUSIONS:")
                for exclusion in patterns['suggested_exclusions']:
                    print(f"  - Add '{exclusion}' to exclusion list")

        if patterns['false_negative_count'] > 0:
            print(f"\n🔍 FALSE NEGATIVE ANALYSIS")
            print("=" * 50)
            print(f"False Negatives Found: {patterns['false_negative_count']}")
            print("Common patterns in missed detections:")
            for pattern, count in patterns['common_fn_patterns'][:5]:
                print(f"  '{pattern}': {count} occurrences")

            if patterns['suggested_keywords']:
                print(f"\n💡 SUGGESTED KEYWORDS:")
                for keyword in patterns['suggested_keywords']:
                    print(f"  - Consider adding '{keyword}' to detection keywords")

def main():
    parser = argparse.ArgumentParser(description='Enhanced Pixel Monitor with Learning System')
    parser.add_argument('command', nargs='?', default='monitor',
                       choices=['monitor', 'interactive', 'analyze', 'train', 'test-learning'],
                       help='Command to run')
    parser.add_argument('--ticket', help='Test detection on specific ticket ID')

    args = parser.parse_args()

    monitor = EnhancedPixelMonitor()

    if args.command == 'monitor':
        monitor.run_enhanced_monitoring(interactive=False)

    elif args.command == 'interactive':
        monitor.run_enhanced_monitoring(interactive=True)

    elif args.command == 'analyze':
        monitor.run_learning_analysis()

    elif args.command == 'train':
        success = monitor.learning_system.train_ml_model()
        if success:
            print("✅ ML model trained successfully")
        else:
            print("❌ Need more training data to train ML model")

    elif args.command == 'test-learning':
        # Test with PS-9998 case
        summary = "DSP creatives are not moving into Ready state from In-Setup"
        description = "Hi Team, many of the team members are facing issues in DSP where the newly created creatives are not moving from In-setup stage to ready."

        is_pixel, reason, confidence, analysis = monitor.enhanced_is_pixel_related_ticket(summary, description)

        print(f"\nTest Results for PS-9998:")
        print(f"Detection Result: {is_pixel}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Detection Reason: {reason}")
        print(f"Method: {analysis['method']}")

        # Record as false positive for learning
        monitor.learning_system.record_feedback(
            "PS-9998", summary, description, reason, "false_positive", confidence
        )
        print("✅ Recorded as false positive for learning")

if __name__ == "__main__":
    main()