#!/bin/bash

# Enhanced Pixel Monitor Startup Script
# Provides easy access to the new learning-powered monitoring system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Enhanced Pixel Performance Monitoring System${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if learning system is bootstrapped
if [ ! -f "learning_data.db" ]; then
    echo -e "${YELLOW}⚠️  Learning system not initialized. Bootstrapping...${NC}"
    python3 bootstrap_learning.py
    echo ""
fi

# Show available commands
echo -e "${GREEN}Available Commands:${NC}"
echo ""
echo -e "${BLUE}🖥️  New Terminal Window:${NC}"
echo -e "  ${YELLOW}monitor${NC}        - Production monitoring (new window)"
echo -e "  ${YELLOW}interactive${NC}    - Learning mode with feedback (new window)"
echo ""
echo -e "${BLUE}🔧 Current Terminal:${NC}"
echo -e "  ${YELLOW}monitor-here${NC}   - Production monitoring (current terminal)"
echo -e "  ${YELLOW}interactive-here${NC} - Learning mode (current terminal)"
echo -e "  ${YELLOW}monitor-bg${NC}     - Background monitoring (returns immediately)"
echo -e "  ${YELLOW}stop${NC}           - Stop background monitoring"
echo ""
echo -e "${BLUE}📊 Analysis & Tools:${NC}"
echo -e "  ${YELLOW}analyze${NC}        - Show performance metrics and suggestions"
echo -e "  ${YELLOW}train${NC}          - Retrain ML model with latest feedback"
echo -e "  ${YELLOW}test${NC}           - Test detection on PS-9998 case"
echo -e "  ${YELLOW}legacy${NC}         - Run original monitoring system"
echo ""

# Default to interactive if no argument provided
COMMAND=${1:-"interactive"}

case $COMMAND in
    "monitor")
        echo -e "${GREEN}🔄 Starting Enhanced Monitoring (Production Mode)${NC}"
        echo -e "Opening in new terminal window..."
        echo ""
        # Launch in new Terminal window on macOS
        osascript -e 'tell application "Terminal" to do script "cd \"'"$(pwd)"'\" && python3 enhanced_pixel_monitor.py monitor"'
        echo -e "${GREEN}✅ Enhanced monitoring started in new terminal window${NC}"
        ;;
    "interactive")
        echo -e "${GREEN}🧠 Starting Interactive Learning Mode${NC}"
        echo -e "Opening in new terminal window for feedback collection..."
        echo ""
        # Launch in new Terminal window on macOS
        osascript -e 'tell application "Terminal" to do script "cd \"'"$(pwd)"'\" && python3 enhanced_pixel_monitor.py interactive"'
        echo -e "${GREEN}✅ Interactive learning mode started in new terminal window${NC}"
        echo -e "${YELLOW}💡 Provide feedback on alerts in the new window to improve accuracy${NC}"
        ;;
    "monitor-here")
        echo -e "${GREEN}🔄 Starting Enhanced Monitoring (Production Mode) - Current Terminal${NC}"
        echo -e "Press Ctrl+C to stop"
        echo ""
        python3 enhanced_pixel_monitor.py monitor
        ;;
    "interactive-here")
        echo -e "${GREEN}🧠 Starting Interactive Learning Mode - Current Terminal${NC}"
        echo -e "You'll be prompted for feedback on each alert to improve accuracy"
        echo -e "Press Ctrl+C to stop"
        echo ""
        python3 enhanced_pixel_monitor.py interactive
        ;;
    "monitor-bg")
        echo -e "${GREEN}🔄 Starting Enhanced Monitoring in Background${NC}"
        nohup python3 enhanced_pixel_monitor.py monitor > enhanced_monitor.log 2>&1 &
        MONITOR_PID=$!
        echo -e "${GREEN}✅ Enhanced monitoring started in background (PID: $MONITOR_PID)${NC}"
        echo -e "${YELLOW}💡 View logs: tail -f enhanced_monitor.log${NC}"
        echo -e "${YELLOW}💡 Stop monitoring: kill $MONITOR_PID${NC}"
        echo $MONITOR_PID > enhanced_monitor.pid
        ;;
    "stop")
        echo -e "${GREEN}🛑 Stopping Background Monitoring${NC}"
        if [ -f "enhanced_monitor.pid" ]; then
            MONITOR_PID=$(cat enhanced_monitor.pid)
            if kill $MONITOR_PID 2>/dev/null; then
                echo -e "${GREEN}✅ Stopped monitoring process (PID: $MONITOR_PID)${NC}"
                rm enhanced_monitor.pid
            else
                echo -e "${YELLOW}⚠️  Process $MONITOR_PID not found (may have already stopped)${NC}"
                rm enhanced_monitor.pid
            fi
        else
            echo -e "${YELLOW}⚠️  No background monitoring process found${NC}"
        fi
        ;;
    "analyze")
        echo -e "${GREEN}📊 Running Performance Analysis${NC}"
        echo ""
        python3 enhanced_pixel_monitor.py analyze
        ;;
    "train")
        echo -e "${GREEN}🏋️  Training ML Model${NC}"
        echo ""
        python3 enhanced_pixel_monitor.py train
        ;;
    "test")
        echo -e "${GREEN}🧪 Testing Detection Logic${NC}"
        echo ""
        python3 enhanced_pixel_monitor.py test-learning
        ;;
    "legacy")
        echo -e "${YELLOW}⚙️  Starting Legacy Monitoring System${NC}"
        echo ""
        ./start_pixel_monitor.sh
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo ""
        echo -e "${YELLOW}Usage: $0 [monitor|interactive|analyze|train|test|legacy]${NC}"
        exit 1
        ;;
esac