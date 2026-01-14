# 🔥 Pixel Monitoring System

A comprehensive monitoring system for pixel-related issues in Jira, featuring continuous monitoring, machine learning training, automated dashboard generation, and real-time alerting.

## 🚀 Quick Start

### Interactive Menu (Recommended)
```bash
# Start the interactive menu - single entry point for all system operations
python3 interactive_menu.py
```

### Direct Commands
```bash
# 1. Load configuration
source config/config_private.sh

# 2. Check system status
python3 pixel_monitor.py status

# 3. Generate dashboard
python3 pixel_monitor.py dashboard

# 4. Start continuous monitoring (NEW!)
python3 continuous_monitor.py

# 5. Email dashboard (requires email config)
python3 pixel_monitor.py email
```

## 🎯 Key Features

### 🚨 **Continuous Alert Monitoring** (NEW!)
- **Real-time monitoring** that checks for pixel issues every X minutes
- **Sound + visual alerts** when new issues are detected
- **Persistent alert display** that doesn't disappear
- **ML training interface** to improve detection accuracy
- **Alert-only mode** - no dashboard generation during monitoring

### 🤖 **Machine Learning Training** (NEW!)
- Train the system on detected alerts (correct vs false positive)
- Interactive training commands: `y1` (correct), `n1` (false positive)
- Training data saved to `pixel_training_data.json`
- Visual status indicators for trained alerts

### 🖥️ **Interactive Menu System**
- **16 comprehensive options** covering all system operations
- Beautiful terminal interface with color coding
- Organized categories: System Commands, Setup, File Operations, Alert Monitoring

### 📊 **Dashboard & Reporting**
- Advanced pixel detection algorithms
- Beautiful HTML dashboard reports
- Email integration with fallback
- Historical report generation
- Corporate network compatible

## 📁 Directory Structure

```
Performance Pixel Monitoring System/
├── 🎮 interactive_menu.py           # Main interactive interface (16 options)
├── 🚨 continuous_monitor.py         # NEW! Continuous alert monitoring + ML training
├── 🔧 pixel_monitor.py              # Core command interface
├── ⚙️  setup.py                     # Setup and configuration helper
├── 📂 core/                         # Core monitoring system
│   └── pixel_notification_monitor.py  # Main monitoring logic & Jira API
├── 📊 dashboard/                    # Dashboard generation
│   └── email_dashboard.py           # Dashboard emailer
├── 🔐 config/                       # Configuration files
│   └── config_private.sh            # Credentials and settings
├── 📁 archive/                      # Archived/alternative scripts (20+ files)
├── 📈 reports/                      # Generated HTML reports
├── 🚨 pixel_alerts.log              # Alert history log
├── 🤖 pixel_training_data.json      # ML training data
└── 📚 *.md                         # Comprehensive documentation
```

## 🎮 Interactive Menu System

The interactive menu (`python3 interactive_menu.py`) provides 16 organized options:

### 📊 **Main System Commands**
1. System Status Check - Check recent pixel issues
2. Generate Dashboard - Create HTML report
3. Email Dashboard - Generate & email report
4. Test System - Test API connections

### 🔧 **Setup & Configuration**
5. Check Configuration - Verify system setup
6. Test All Functionality - Complete system test
7. Setup Daily Automation - Get cron instructions
8. View Help Guide - Detailed documentation

### 📁 **File Operations**
9. View Generated Reports - List HTML files
10. Open Latest Dashboard - Open in browser
11. View System Configuration - Show config file

### 🚨 **Alert Monitoring** (NEW!)
12. **Start Alert Monitor** - Continuous monitoring with ML training
13. **View Alert Logs** - Show formatted alert history with clearing option

### 🎯 **Special Actions**
14. Complete System Demo - Run full demonstration
15. Direct Dashboard Generation - Bypass main interface
16. System Health Summary - Quick overview

## 🚨 Continuous Monitoring Features

### Real-Time Alert System
```bash
# Start continuous monitoring (option 12 in interactive menu)
python3 continuous_monitor.py
```

**Features:**
- ⏰ **Configurable intervals** (1-60 minutes)
- 🔊 **Sound alerts** (macOS system sounds)
- 📱 **Visual alerts** with persistent display
- 📝 **Alert logging** to `pixel_alerts.log`
- 🎯 **Force check** capability (press Enter)
- 📊 **Live progress bar** and status updates

### Machine Learning Training (NEW!)
When alerts are detected, train the system:

```bash
# In the continuous monitor interface:
y1    # Mark alert #1 as correct
n2    # Mark alert #2 as false positive
```

**Training Interface:**
- 🎯 **Detected Alerts section** shows last 3 alerts
- ✅ **Color-coded status**: ⏳ Awaiting, ✅ Correct, ❌ False positive
- 🤖 **Persistent training data** saved to JSON
- 📈 **Continuous learning** to improve detection

### Controls & Commands
```bash
Enter          # Force check now
interval 10    # Change to 10 minutes
log           # View alert history (paused display)
clear         # Clear displayed alerts
y[#]/n[#]     # Train alert as correct/false positive
Ctrl+C        # Stop monitoring
```

## 🔧 Setup Commands

### System Configuration
```bash
python3 setup.py config    # Verify system setup
python3 setup.py test      # Test functionality
python3 setup.py daily     # Setup automation
python3 setup.py help      # Detailed documentation
```

### Core Monitoring Commands
```bash
python3 pixel_monitor.py status     # System status check
python3 pixel_monitor.py dashboard  # Generate HTML report
python3 pixel_monitor.py email      # Email dashboard
python3 pixel_monitor.py test       # Test connections
```

## 📈 System Architecture

### Core Components
- **`pixel_notification_monitor.py`** - Jira API integration & pixel detection logic
- **`continuous_monitor.py`** - Real-time monitoring with threading & ML training
- **`interactive_menu.py`** - Unified interface with 16 comprehensive options
- **`pixel_monitor.py`** - Command-line interface for core operations

### Key Integrations
- **Jira API** with OAuth2 authentication
- **Corporate SMTP** (Office365) for email reports
- **Threading** for non-blocking UI and background monitoring
- **Signal handling** for graceful shutdown
- **JSON serialization** for ML training data persistence

## 🎯 Optimization Results

### Before Optimization
- 20+ scattered files in root directory
- 5+ duplicate email dashboard scripts
- No unified interface
- No continuous monitoring
- No machine learning capabilities

### After Optimization ✅
- **80% reduction** in root directory clutter
- **Single entry point** via interactive menu
- **Real-time continuous monitoring** with alerts
- **Machine learning training interface**
- **16 comprehensive system operations**
- **Beautiful HTML reports** with working functionality
- **Thread-safe display** with proper synchronization
- **Comprehensive documentation** and setup helpers

## 🚀 Advanced Features

### Alert System Enhancements
- **Persistent display** - alerts stay visible instead of disappearing
- **Thread synchronization** - prevents display conflicts during force checks
- **Atomic pausing** - safe pause/resume for log viewing and force checks
- **Alert training feedback** - interactive ML training during monitoring

### Monitoring Capabilities
- **Configurable check intervals** (1-60 minutes)
- **Progress visualization** with live progress bars
- **Status persistence** across monitoring sessions
- **Graceful shutdown** handling with Ctrl+C
- **Multi-threaded architecture** for responsive UI

### Dashboard Features
- **Corporate network optimization** for Samsung environment
- **Automated email delivery** with app password authentication
- **Historical report archival** in organized reports directory
- **Beautiful HTML formatting** with responsive design

## 📝 Recent Updates (Latest Session)

### New Continuous Monitoring System
- Added `continuous_monitor.py` with real-time pixel issue detection
- Implemented thread-safe display updates and user input handling
- Added configurable monitoring intervals and sound alerts
- Fixed display persistence issues where alerts were disappearing

### Machine Learning Training Interface
- Added interactive training system for detected alerts
- Implemented `y[#]`/`n[#]` commands for correct/false positive feedback
- Added training data persistence to `pixel_training_data.json`
- Created "Detected Alerts" section with color-coded training status

### Enhanced Interactive Menu
- Expanded to 16 comprehensive options with organized categories
- Added alert log viewer (option 13) with formatted display
- Implemented log clearing functionality with user confirmation
- Added system health summary and complete demo capabilities

### Bug Fixes
- Fixed critical tuple unpacking bug in `pixel_monitor.py:88`
- Resolved thread race conditions in continuous monitor display
- Fixed import path issues after directory restructuring
- Corrected menu numbering and option routing

## 🔍 Technical Implementation

### Thread Safety
The continuous monitoring system uses proper threading synchronization:
```python
# Thread-safe pause mechanism
with self.pause_lock:
    self.paused = True
    # Safely pause display for user interactions
```

### Machine Learning Data Format
Training data is stored in JSON format:
```json
{
  "timestamp": "2026-01-14T15:01:55.938411",
  "old_count": 0,
  "new_count": 1,
  "message": "Pixel tickets increased from 0 to 1",
  "is_correct": true,
  "trained_at": "2026-01-14T15:01:55.939115"
}
```

### Signal Handling
Graceful shutdown with signal handling:
```python
signal.signal(signal.SIGINT, self.signal_handler)
signal.signal(signal.SIGTERM, self.signal_handler)
```

## 📚 Documentation

For additional documentation, see:
- `PIXEL_MONITOR_README.md` - Detailed monitoring guide
- `EMAIL_SETUP_GUIDE.md` - Email configuration
- `QUICK_START.md` - Getting started guide
- `LEARNING_SYSTEM_README.md` - ML system documentation
- `detection_keywords_reference.md` - Detection algorithm details

---

**🎉 Ready to monitor pixel issues with continuous alerts and machine learning capabilities!**

Start with: `python3 interactive_menu.py`