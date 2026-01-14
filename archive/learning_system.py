#!/usr/bin/env python3
"""
Automated Learning System for Pixel Detection
Continuously improves detection accuracy through feedback and machine learning.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

logger = logging.getLogger(__name__)

class PixelDetectionLearningSystem:
    """
    Automated learning system that improves pixel detection through:
    1. Feedback collection from alerts
    2. Pattern analysis and rule optimization
    3. Machine learning model training
    4. Confidence scoring and hybrid detection
    """

    def __init__(self, db_path: str = "learning_data.db"):
        self.db_path = db_path
        self.model_path = "pixel_detection_model.pkl"
        self.vectorizer_path = "text_vectorizer.pkl"
        self.init_database()
        self.load_or_create_model()

    def init_database(self):
        """Initialize SQLite database for storing feedback and training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Feedback table - stores user feedback on alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                description TEXT,
                detection_reason TEXT,
                user_feedback TEXT CHECK(user_feedback IN ('true_positive', 'false_positive', 'false_negative')),
                confidence_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')

        # Training data table - processed examples for ML
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE,
                summary TEXT NOT NULL,
                description TEXT,
                is_pixel_related BOOLEAN NOT NULL,
                features TEXT, -- JSON of extracted features
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Pattern analysis table - tracks detection patterns and performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL, -- 'keyword', 'exclusion', 'context'
                pattern_value TEXT NOT NULL,
                true_positives INTEGER DEFAULT 0,
                false_positives INTEGER DEFAULT 0,
                false_negatives INTEGER DEFAULT 0,
                precision REAL,
                recall REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pattern_type, pattern_value)
            )
        ''')

        # Model performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT NOT NULL,
                training_samples INTEGER,
                precision REAL,
                recall REAL,
                f1_score REAL,
                false_positive_rate REAL,
                training_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Learning database initialized successfully")

    def record_feedback(self, ticket_id: str, summary: str, description: str,
                       detection_reason: str, user_feedback: str, confidence_score: float = None):
        """Record user feedback on detection accuracy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO feedback
            (ticket_id, summary, description, detection_reason, user_feedback, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticket_id, summary, description, detection_reason, user_feedback, confidence_score))

        conn.commit()
        conn.close()
        logger.info(f"Recorded feedback for {ticket_id}: {user_feedback}")

        # Automatically process feedback into training data
        self.process_feedback_to_training_data()

    def process_feedback_to_training_data(self):
        """Convert feedback into structured training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get unprocessed feedback
        cursor.execute('''
            SELECT id, ticket_id, summary, description, user_feedback
            FROM feedback
            WHERE processed = FALSE
        ''')

        unprocessed = cursor.fetchall()

        for feedback_id, ticket_id, summary, description, user_feedback in unprocessed:
            is_pixel_related = user_feedback == 'true_positive'

            # Extract features
            features = self.extract_features(summary, description)

            # Store in training data
            cursor.execute('''
                INSERT OR REPLACE INTO training_data
                (ticket_id, summary, description, is_pixel_related, features)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticket_id, summary, description, is_pixel_related, json.dumps(features)))

            # Mark feedback as processed
            cursor.execute('UPDATE feedback SET processed = TRUE WHERE id = ?', (feedback_id,))

        conn.commit()
        conn.close()

        if unprocessed:
            logger.info(f"Processed {len(unprocessed)} feedback entries into training data")

    def extract_features(self, summary: str, description: str = "") -> Dict:
        """Extract features from ticket text for ML training"""
        text = (summary + " " + (description or "")).lower()

        features = {
            # Basic text features
            'length': len(text),
            'word_count': len(text.split()),

            # Keyword presence
            'has_pixel': 'pixel' in text,
            'has_tracking': any(word in text for word in ['tracking', 'tag', 'javascript', 'js']),
            'has_conversion': 'conversion' in text,
            'has_validation': 'validation' in text,
            'has_firing': 'firing' in text,

            # Context patterns
            'pixel_with_context': self.count_pixel_contexts(text),
            'technical_terms': self.count_technical_terms(text),

            # Exclusion indicators
            'has_exclusions': self.count_exclusion_indicators(text),

            # Action words
            'action_words': self.count_action_words(text),

            # Domain-specific patterns
            'dsp_related': 'dsp' in text or 'creative' in text,
            'web_related': any(word in text for word in ['web', 'website', 'page']),
            'campaign_related': 'campaign' in text
        }

        return features

    def count_pixel_contexts(self, text: str) -> int:
        """Count pixel-related contexts"""
        contexts = ['firing', 'load', 'implement', 'setup', 'troubleshoot', 'validate', 'test']
        if 'pixel' in text:
            return sum(1 for context in contexts if context in text)
        return 0

    def count_technical_terms(self, text: str) -> int:
        """Count technical implementation terms"""
        terms = ['javascript', 'js', 'tag', 'code', 'snippet', 'implementation', 'gtm']
        return sum(1 for term in terms if term in text)

    def count_exclusion_indicators(self, text: str) -> int:
        """Count indicators that suggest non-pixel issues"""
        exclusions = ['acr', 'delivery report', 'access request', 'user sync', 'planning module', 'linear ads']
        return sum(1 for exclusion in exclusions if exclusion in text)

    def count_action_words(self, text: str) -> int:
        """Count action-oriented words"""
        actions = ['implement', 'install', 'setup', 'add', 'place', 'deploy', 'configure']
        return sum(1 for action in actions if action in text)

    def train_ml_model(self, min_samples: int = 20):
        """Train machine learning model with available training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT summary, description, is_pixel_related FROM training_data')
        data = cursor.fetchall()
        conn.close()

        if len(data) < min_samples:
            logger.warning(f"Need at least {min_samples} training samples, have {len(data)}")
            return False

        # Prepare data
        texts = []
        labels = []

        for summary, description, is_pixel in data:
            text = summary + " " + (description or "")
            texts.append(text.lower())
            labels.append(is_pixel)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        # Vectorize text
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Train model
        self.model = LogisticRegression(random_state=42, class_weight='balanced')
        self.model.fit(X_train_vec, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Save model and vectorizer
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)

        # Log performance
        precision = report['weighted avg']['precision']
        recall = report['weighted avg']['recall']
        f1 = report['weighted avg']['f1-score']

        logger.info(f"Model trained with {len(data)} samples")
        logger.info(f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")

        # Store performance metrics
        self.log_model_performance(len(data), precision, recall, f1)

        return True

    def load_or_create_model(self):
        """Load existing model or create placeholder"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info("Loaded existing ML model")
        except FileNotFoundError:
            self.model = None
            self.vectorizer = None
            logger.info("No existing model found, will train when enough data is available")

    def predict_ml(self, summary: str, description: str = "") -> Tuple[bool, float]:
        """Get ML model prediction and confidence"""
        if self.model is None or self.vectorizer is None:
            return False, 0.0

        text = (summary + " " + (description or "")).lower()
        text_vec = self.vectorizer.transform([text])

        prediction = self.model.predict(text_vec)[0]
        confidence = max(self.model.predict_proba(text_vec)[0])

        return bool(prediction), confidence

    def hybrid_detection(self, summary: str, description: str = "",
                        rule_based_result: bool = False, rule_confidence: float = 0.5) -> Tuple[bool, float, Dict]:
        """Combine rule-based and ML predictions for better accuracy"""

        # Get ML prediction
        ml_prediction, ml_confidence = self.predict_ml(summary, description)

        # Extract features for analysis
        features = self.extract_features(summary, description)

        # Weight the predictions
        if self.model is not None:
            # Use weighted combination when ML model is available
            rule_weight = 0.6  # Favor proven rules initially
            ml_weight = 0.4

            # Adjust weights based on confidence
            if ml_confidence > 0.8:
                ml_weight = 0.6
                rule_weight = 0.4

            combined_score = (rule_confidence * rule_weight) + (ml_confidence * ml_weight)

            # Final prediction based on combined score
            final_prediction = combined_score > 0.5

        else:
            # Fall back to rule-based only
            final_prediction = rule_based_result
            combined_score = rule_confidence
            ml_prediction = rule_based_result
            ml_confidence = rule_confidence

        analysis = {
            'rule_based': {'prediction': rule_based_result, 'confidence': rule_confidence},
            'ml_based': {'prediction': ml_prediction, 'confidence': ml_confidence},
            'combined_score': combined_score,
            'features': features,
            'method': 'hybrid' if self.model else 'rule_based_only'
        }

        return final_prediction, combined_score, analysis

    def log_model_performance(self, training_samples: int, precision: float, recall: float, f1: float):
        """Log model performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO model_performance
            (model_version, training_samples, precision, recall, f1_score, false_positive_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y%m%d_%H%M'), training_samples, precision, recall, f1, 1-precision))

        conn.commit()
        conn.close()

    def analyze_patterns(self) -> Dict:
        """Analyze detection patterns and suggest improvements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Analyze false positives
        cursor.execute('''
            SELECT summary, description, detection_reason
            FROM feedback
            WHERE user_feedback = 'false_positive'
        ''')
        false_positives = cursor.fetchall()

        # Analyze false negatives
        cursor.execute('''
            SELECT summary, description
            FROM feedback
            WHERE user_feedback = 'false_negative'
        ''')
        false_negatives = cursor.fetchall()

        conn.close()

        # Extract patterns from false positives
        fp_patterns = []
        for summary, description, reason in false_positives:
            text = (summary + " " + (description or "")).lower()
            fp_patterns.extend(text.split())

        # Extract patterns from false negatives
        fn_patterns = []
        for summary, description in false_negatives:
            text = (summary + " " + (description or "")).lower()
            fn_patterns.extend(text.split())

        # Count pattern frequencies
        fp_counter = Counter(fp_patterns)
        fn_counter = Counter(fn_patterns)

        analysis = {
            'false_positive_count': len(false_positives),
            'false_negative_count': len(false_negatives),
            'common_fp_patterns': fp_counter.most_common(10),
            'common_fn_patterns': fn_counter.most_common(10),
            'suggested_exclusions': [pattern for pattern, count in fp_counter.most_common(5) if count >= 2],
            'suggested_keywords': [pattern for pattern, count in fn_counter.most_common(5) if count >= 2]
        }

        return analysis

    def get_performance_metrics(self) -> Dict:
        """Get overall system performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count feedback types
        cursor.execute('''
            SELECT
                COUNT(CASE WHEN user_feedback = 'true_positive' THEN 1 END) as tp,
                COUNT(CASE WHEN user_feedback = 'false_positive' THEN 1 END) as fp,
                COUNT(CASE WHEN user_feedback = 'false_negative' THEN 1 END) as fn
            FROM feedback
        ''')

        tp, fp, fn = cursor.fetchone()

        # Get latest model performance
        cursor.execute('''
            SELECT precision, recall, f1_score, training_samples
            FROM model_performance
            ORDER BY training_date DESC
            LIMIT 1
        ''')

        model_metrics = cursor.fetchone()
        conn.close()

        # Calculate overall metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        metrics = {
            'feedback_based': {
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score
            },
            'model_based': {
                'precision': model_metrics[0] if model_metrics else None,
                'recall': model_metrics[1] if model_metrics else None,
                'f1_score': model_metrics[2] if model_metrics else None,
                'training_samples': model_metrics[3] if model_metrics else 0
            },
            'total_feedback': tp + fp + fn
        }

        return metrics

def interactive_feedback_prompt(ticket_id: str, summary: str, detection_reason: str) -> str:
    """Interactive prompt for collecting user feedback on detection accuracy"""
    print(f"\n🚨 PIXEL ALERT: {ticket_id}")
    print(f"Summary: {summary}")
    print(f"Detected because: {detection_reason}")
    print("\nIs this actually pixel-related?")
    print("  y = Yes, correct detection (true positive)")
    print("  n = No, false alarm (false positive)")
    print("  m = Missed pixel issue (false negative)")
    print("  s = Skip feedback")

    while True:
        response = input("Your feedback (y/n/m/s): ").lower().strip()
        if response == 'y':
            return 'true_positive'
        elif response == 'n':
            return 'false_positive'
        elif response == 'm':
            return 'false_negative'
        elif response == 's':
            return 'skip'
        else:
            print("Please enter y, n, m, or s")

if __name__ == "__main__":
    # Example usage and testing
    learning_system = PixelDetectionLearningSystem()

    # Test with PS-9998 case
    ticket_summary = "DSP creatives are not moving into Ready state from In-Setup"
    ticket_description = "Hi Team, many of the team members are facing issues in DSP where the newly created creatives are not moving from In-setup stage to ready. This is preventing the QA teams from completing creative QA and also Ad-ops from attaching these creatives to campaigns."

    # Simulate hybrid detection
    rule_result, hybrid_confidence, analysis = learning_system.hybrid_detection(
        ticket_summary,
        ticket_description,
        rule_based_result=True,  # This was flagged by rules
        rule_confidence=0.6
    )

    print(f"Hybrid Detection Result: {rule_result}")
    print(f"Confidence: {hybrid_confidence:.3f}")
    print(f"Analysis: {json.dumps(analysis, indent=2)}")

    # Record feedback (simulating false positive)
    learning_system.record_feedback(
        "PS-9998",
        ticket_summary,
        ticket_description,
        "Medium confidence: tracking + action pattern",
        "false_positive"
    )

    # Show performance metrics
    metrics = learning_system.get_performance_metrics()
    print(f"\nPerformance Metrics: {json.dumps(metrics, indent=2)}")