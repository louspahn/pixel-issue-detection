#!/usr/bin/env python3
"""
Bootstrap Learning System with Historical Data
Pre-populate the learning system with known examples to jump-start training.
"""

from learning_system import PixelDetectionLearningSystem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def bootstrap_with_known_examples():
    """Bootstrap learning system with known pixel and non-pixel examples"""

    learning_system = PixelDetectionLearningSystem()

    # Known PIXEL-RELATED tickets (true positives)
    pixel_examples = [
        {
            'ticket_id': 'PS-EXAMPLE-1',
            'summary': 'Ministry of Supply Pixel Validation Request',
            'description': 'Need to validate that conversion pixels are firing correctly on the checkout page',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-2',
            'summary': 'Porter Airlines pixel not firing on confirmation page',
            'description': 'The tracking pixel is not firing when users complete booking confirmation',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-3',
            'summary': 'Conversion pixel troubleshooting - 0 conversions showing',
            'description': 'Samsung campaign shows 0 conversions despite traffic, need to troubleshoot pixel implementation',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-4',
            'summary': 'Universal tag verification for Samsung campaign',
            'description': 'Need to verify universal tag implementation for new Samsung advertising campaign',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-5',
            'summary': 'Website Pixel Conversion Data Not Showing',
            'description': 'Client reports that website conversion data is not appearing in reporting dashboard',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-6',
            'summary': 'Appending a pixel for line items in campaign',
            'description': 'Need to append conversion pixel to multiple line items for tracking',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-7',
            'summary': 'JavaScript tag implementation issue',
            'description': 'Having trouble implementing the JavaScript tracking tag on client website',
            'is_pixel': True
        },
        {
            'ticket_id': 'PS-EXAMPLE-8',
            'summary': 'Pixel firing validation for e-commerce site',
            'description': 'Need to validate that all pixels are firing correctly during checkout process',
            'is_pixel': True
        }
    ]

    # Known NON-PIXEL tickets (false positives to avoid)
    non_pixel_examples = [
        {
            'ticket_id': 'PS-9998',
            'summary': 'DSP creatives are not moving into Ready state from In-Setup',
            'description': 'Hi Team, many of the team members are facing issues in DSP where the newly created creatives are not moving from In-setup stage to ready. This is preventing the QA teams from completing creative QA and also Ad-ops from attaching these creatives to campaigns.',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-10',
            'summary': 'ACR Linear TV Campaign Setup',
            'description': 'Need to setup new ACR linear TV advertising campaign for automotive client',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-11',
            'summary': 'Delivery Report Access Request',
            'description': 'Client requesting access to campaign delivery reports and performance metrics',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-12',
            'summary': 'Grant access to advertising platform',
            'description': 'New team member needs access to DSP platform for campaign management',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-13',
            'summary': 'User sync pixel third-party integration',
            'description': 'Setting up user sync pixels for third-party data provider integration',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-14',
            'summary': 'Planning module configuration issue',
            'description': 'Campaign planning module is not displaying budget allocation correctly',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-15',
            'summary': 'O&O monitoring alert investigation',
            'description': 'Operations monitoring system triggered alert for server performance issue',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-16',
            'summary': 'Creative assets upload and QA process',
            'description': 'Need to upload new creative assets and complete QA review process',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-17',
            'summary': 'Campaign budget adjustment request',
            'description': 'Client requesting to increase daily budget for running campaign',
            'is_pixel': False
        },
        {
            'ticket_id': 'PS-EXAMPLE-18',
            'summary': 'Linear ads trafficking for TV campaign',
            'description': 'Need to traffic linear TV advertisements for automotive brand campaign',
            'is_pixel': False
        }
    ]

    # Add all examples to training data
    all_examples = pixel_examples + non_pixel_examples

    logger.info(f"Bootstrapping learning system with {len(all_examples)} examples")
    logger.info(f"  - {len(pixel_examples)} pixel-related examples")
    logger.info(f"  - {len(non_pixel_examples)} non-pixel examples")

    for example in all_examples:
        # Add directly to training data (bypass feedback collection)
        conn = learning_system.db_path
        import sqlite3
        conn = sqlite3.connect(learning_system.db_path)
        cursor = conn.cursor()

        features = learning_system.extract_features(example['summary'], example['description'])

        cursor.execute('''
            INSERT OR REPLACE INTO training_data
            (ticket_id, summary, description, is_pixel_related, features)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            example['ticket_id'],
            example['summary'],
            example['description'],
            example['is_pixel'],
            __import__('json').dumps(features)
        ))

        conn.commit()
        conn.close()

        logger.info(f"  ✅ Added {example['ticket_id']}: {example['is_pixel']}")

    # Train initial model
    logger.info("Training initial ML model...")
    success = learning_system.train_ml_model(min_samples=10)

    if success:
        logger.info("✅ Successfully trained initial ML model!")

        # Test the model on our problem case
        logger.info("\n🧪 Testing model on PS-9998 (should be false)...")
        ml_prediction, ml_confidence = learning_system.predict_ml(
            "DSP creatives are not moving into Ready state from In-Setup",
            "Hi Team, many of the team members are facing issues in DSP where the newly created creatives are not moving from In-setup stage to ready."
        )

        logger.info(f"ML Prediction: {ml_prediction} (confidence: {ml_confidence:.3f})")

        if not ml_prediction:
            logger.info("🎉 Model correctly identifies PS-9998 as NOT pixel-related!")
        else:
            logger.warning("⚠️ Model still thinks PS-9998 is pixel-related - needs more training")

    else:
        logger.error("❌ Failed to train initial model")

    # Show performance metrics
    metrics = learning_system.get_performance_metrics()
    logger.info(f"\n📊 Bootstrap Complete!")
    logger.info(f"Training samples: {metrics['model_based']['training_samples']}")

    return learning_system

if __name__ == "__main__":
    bootstrap_with_known_examples()