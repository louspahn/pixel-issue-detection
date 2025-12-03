#!/usr/bin/env python3
"""
Debug version of enhanced pixel monitor to help troubleshoot issues
"""

import sys
import os
import traceback
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def safe_import(module_name, package=None):
    """Safely import modules and report any issues"""
    try:
        if package:
            module = __import__(f"{package}.{module_name}", fromlist=[module_name])
        else:
            module = __import__(module_name)
        print(f"✅ Successfully imported {module_name}")
        return module
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        traceback.print_exc()
        return None

def main():
    print("🔧 Enhanced Pixel Monitor Debug Mode")
    print("=" * 50)

    # Check current directory
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")

    # Check if we're in the right directory
    expected_files = [
        'enhanced_pixel_monitor.py',
        'learning_system.py',
        'pixel_notification_monitor.py'
    ]

    missing_files = []
    for file in expected_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            missing_files.append(file)

    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        print("Make sure you're running this from the correct directory:")
        print('cd "/Users/l.spahn/Performance Pixel Monitoring System"')
        return

    print("\n🔍 Testing imports...")

    # Test basic imports
    requests = safe_import('requests')
    sqlite3 = safe_import('sqlite3')
    sklearn = safe_import('sklearn')
    numpy = safe_import('numpy')

    # Test our custom modules
    sys.path.append(os.getcwd())

    print("\n🧪 Testing custom modules...")

    # Test learning system
    try:
        from learning_system import PixelDetectionLearningSystem
        print("✅ PixelDetectionLearningSystem imported")

        ls = PixelDetectionLearningSystem()
        print("✅ PixelDetectionLearningSystem initialized")

    except Exception as e:
        print(f"❌ Learning system error: {e}")
        traceback.print_exc()
        return

    # Test original pixel monitor
    try:
        from pixel_notification_monitor import is_pixel_related_ticket, make_jira_request, NOTIFICATION_CONFIG
        print("✅ Original pixel monitor functions imported")
    except Exception as e:
        print(f"❌ Original pixel monitor error: {e}")
        traceback.print_exc()
        return

    # Test enhanced monitor
    try:
        from enhanced_pixel_monitor import EnhancedPixelMonitor
        print("✅ EnhancedPixelMonitor imported")

        monitor = EnhancedPixelMonitor()
        print("✅ EnhancedPixelMonitor initialized")

    except Exception as e:
        print(f"❌ Enhanced monitor error: {e}")
        traceback.print_exc()
        return

    print("\n🎯 Testing detection...")

    # Test detection
    try:
        summary = "Test pixel validation issue"
        description = "Testing the enhanced detection system"

        result, reason, confidence, analysis = monitor.enhanced_is_pixel_related_ticket(summary, description)

        print(f"✅ Detection test successful:")
        print(f"   Result: {result}")
        print(f"   Reason: {reason}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Method: {analysis['method']}")

    except Exception as e:
        print(f"❌ Detection test error: {e}")
        traceback.print_exc()
        return

    print("\n🚀 All tests passed! Starting interactive mode...")

    # Try to start interactive mode
    try:
        import argparse

        # Simulate command line args
        sys.argv = ['enhanced_pixel_monitor.py', 'interactive']

        # Import and run main
        from enhanced_pixel_monitor import main
        main()

    except KeyboardInterrupt:
        print("\n👋 Interactive mode stopped by user")
    except Exception as e:
        print(f"❌ Interactive mode error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()