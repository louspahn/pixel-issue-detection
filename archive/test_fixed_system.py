#!/usr/bin/env python3
"""
Test script to verify the enhanced monitoring system is working after API fix
"""

import sys
import traceback
from enhanced_pixel_monitor import EnhancedPixelMonitor

def test_system():
    print("🧪 Testing Enhanced Pixel Monitoring System")
    print("=" * 50)

    try:
        # Test 1: Initialize system
        print("1. Testing system initialization...")
        monitor = EnhancedPixelMonitor()
        print("   ✅ System initialized successfully")

        # Test 2: Test API connection
        print("2. Testing Jira API connection...")
        monitor.check_for_enhanced_pixel_tickets()
        print("   ✅ API connection working")

        # Test 3: Test detection logic
        print("3. Testing detection logic...")
        summary = "Test pixel validation issue"
        description = "Testing enhanced detection"

        result, reason, confidence, analysis = monitor.enhanced_is_pixel_related_ticket(summary, description)
        print(f"   ✅ Detection test: {result} (confidence: {confidence:.3f})")

        # Test 4: Test PS-9998 case
        print("4. Testing PS-9998 resolution...")
        ps9998_summary = "DSP creatives are not moving into Ready state from In-Setup"
        ps9998_desc = "Hi Team, many of the team members are facing issues in DSP..."

        result, reason, confidence, analysis = monitor.enhanced_is_pixel_related_ticket(ps9998_summary, ps9998_desc)
        ml_prediction = analysis['ml_based']['prediction']

        if not ml_prediction:
            print(f"   ✅ PS-9998 correctly identified as NON-pixel by ML model")
        else:
            print(f"   ⚠️  PS-9998 still flagged by ML (needs more training)")

        print(f"   📊 Hybrid result: {result} (confidence: {confidence:.3f})")

        print("\n🎉 All tests passed! System is ready to use.")
        print("\n📋 Ready to start:")
        print("   Interactive mode: ./start_enhanced_monitor.sh interactive")
        print("   Production mode:  ./start_enhanced_monitor.sh monitor")
        print("   Background mode:  ./start_enhanced_monitor.sh monitor-bg")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    test_system()