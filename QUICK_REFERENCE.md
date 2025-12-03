# 🚀 Enhanced Pixel Monitor - Quick Reference

## 🎯 Most Common Commands

### **Start Learning Mode (Recommended First)**
```bash
./start_enhanced_monitor.sh interactive
```
- Opens in new terminal window
- Prompts for feedback on each alert
- Improves accuracy over time

### **Production Monitoring**
```bash
./start_enhanced_monitor.sh monitor
```
- Opens in new terminal window
- Runs continuously with enhanced detection
- No feedback prompts

### **Background Monitoring**
```bash
./start_enhanced_monitor.sh monitor-bg
```
- Runs hidden in background
- Returns control to your terminal immediately
- View logs: `tail -f enhanced_monitor.log`
- Stop: `./start_enhanced_monitor.sh stop`

## 📊 Analysis & Management

### **Check Performance**
```bash
./start_enhanced_monitor.sh analyze
```
Shows:
- Detection accuracy metrics
- False positive patterns
- Suggested improvements

### **Train Model**
```bash
./start_enhanced_monitor.sh train
```
- Retrains ML model with latest feedback
- Improves detection accuracy

### **Test Detection**
```bash
./start_enhanced_monitor.sh test
```
- Tests on PS-9998 case
- Shows hybrid detection results

## 🔧 All Available Options

| Command | Description | Terminal |
|---------|-------------|----------|
| `interactive` | Learning mode with feedback | New window |
| `monitor` | Production monitoring | New window |
| `interactive-here` | Learning mode | Current terminal |
| `monitor-here` | Production monitoring | Current terminal |
| `monitor-bg` | Background monitoring | Background process |
| `stop` | Stop background monitoring | Command only |
| `analyze` | Performance analysis | Command only |
| `train` | Retrain ML model | Command only |
| `test` | Test detection logic | Command only |
| `legacy` | Original monitoring system | Current terminal |

## 🧠 Learning System Workflow

1. **Start**: `./start_enhanced_monitor.sh interactive`
2. **Wait**: System monitors for new tickets every 5 minutes
3. **Alert**: When pixel-related ticket detected, you'll see:
   ```
   🚨 PIXEL ALERT: PS-1234
   Summary: Some ticket summary
   Detected because: tracking + action pattern

   Is this actually pixel-related?
     y = Yes, correct detection
     n = No, false alarm
     s = Skip feedback
   Your feedback (y/n/s):
   ```
4. **Feedback**: Choose y/n/s to train the system
5. **Improve**: System learns and gets better over time

## 🎯 PS-9998 Success Story

**Before**: PS-9998 triggered false positive alerts
**After**:
- ✅ ML model correctly identifies as non-pixel (60% confidence)
- ✅ Hybrid system makes smart decision
- ✅ Future DSP creative tickets avoided automatically

## 💡 Pro Tips

- **Start with interactive mode** for 1-2 weeks to collect feedback
- **Check performance regularly** with `analyze` command
- **Switch to production mode** once accuracy is satisfactory
- **Use background mode** for set-and-forget monitoring
- **The system gets smarter** with every piece of feedback you provide

## 🆘 Need Help?

- **View this reference**: `cat QUICK_REFERENCE.md`
- **Full documentation**: `cat LEARNING_SYSTEM_README.md`
- **Check logs**: `tail -f enhanced_monitor.log` (for background mode)
- **Stop everything**: `./start_enhanced_monitor.sh stop`