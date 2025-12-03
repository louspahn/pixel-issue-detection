#!/bin/bash

# Debug startup script for troubleshooting

echo "🔧 Enhanced Pixel Monitor - Debug Mode"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "enhanced_pixel_monitor.py" ]; then
    echo "❌ Error: enhanced_pixel_monitor.py not found"
    echo "Make sure you're in the right directory:"
    echo 'cd "/Users/l.spahn/Performance Pixel Monitoring System"'
    exit 1
fi

echo "✅ Found enhanced_pixel_monitor.py"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

echo "✅ Python3 available"

# Run debug script
echo ""
echo "🧪 Running diagnostic tests..."
python3 debug_enhanced_monitor.py