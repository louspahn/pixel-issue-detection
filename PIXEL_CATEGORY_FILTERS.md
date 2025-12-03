
# 🎯 Pixel Issues Dashboard - Complete Filter Set

## 🔗 Main Dashboard View
**[Labeled Pixel Issues](https://adgear.atlassian.net/issues/?filter=26796)** - Your dynamic view with all categorized tickets

## 📊 Category-Specific Views

**[🔍 Pixel Validation Issues](https://adgear.atlassian.net/issues/?filter=26830)**  
JQL: `project = PS AND labels = pixel-validation ORDER BY created DESC`

**[🛠️ Pixel Troubleshooting](https://adgear.atlassian.net/issues/?filter=26831)**  
JQL: `project = PS AND labels = pixel-troubleshooting ORDER BY created DESC`

**[⚡ Pixel Implementation](https://adgear.atlassian.net/issues/?filter=26832)**  
JQL: `project = PS AND labels = pixel-implementation ORDER BY created DESC`

**[📊 Data Discrepancy Issues](https://adgear.atlassian.net/issues/?filter=26833)**  
JQL: `project = PS AND labels = pixel-data-discrepancy ORDER BY created DESC`

**[🎯 Conversion Tracking](https://adgear.atlassian.net/issues/?filter=26834)**  
JQL: `project = PS AND labels = pixel-conversion-tracking ORDER BY created DESC`

**[🏷️ GTM Related Issues](https://adgear.atlassian.net/issues/?filter=26835)**  
JQL: `project = PS AND labels = pixel-gtm-related ORDER BY created DESC`

**[📱 Cross-Domain Issues](https://adgear.atlassian.net/issues/?filter=26836)**  
JQL: `project = PS AND labels = pixel-cross-domain ORDER BY created DESC`

**[🚨 Critical Pixel Issues](https://adgear.atlassian.net/issues/?filter=26837)**  
JQL: `project = PS AND labels = pixel-critical-revenue AND status NOT IN (Done, Resolved, Closed) ORDER BY priority DESC, created DESC`


## 🏷️ Label System

The filters use these classification labels:
- `pixel-validation` - Testing and verification requests
- `pixel-troubleshooting` - Debug and investigation issues
- `pixel-implementation` - Setup and firing problems
- `pixel-data-discrepancy` - 1P vs 3P data mismatches
- `pixel-conversion-tracking` - Purchase/revenue tracking
- `pixel-gtm-related` - Google Tag Manager issues
- `pixel-cross-domain` - Multi-domain tracking
- `pixel-critical-revenue` - Revenue-impacting issues

## 🎛️ Dashboard Setup

1. **Go to:** [Jira Dashboard](https://adgear.atlassian.net/secure/Dashboard.jspa)
2. **Create Dashboard:** "🎯 Pixel Categories Dashboard"
3. **Add Filter Result gadgets** for each category
4. **Configure columns:** Key, Summary, Status, Priority, Assignee, Labels, Created

## 🔄 Dynamic Features

✅ **Auto-grows** as new tickets get labeled
✅ **Organized by category** for easy management
✅ **Includes original 8 tickets** plus new ones
✅ **Drill-down capability** from overview to specific categories

Your pixel dashboard now has both overview and detailed category views!
