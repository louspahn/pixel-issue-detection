# Reports Directory

This directory contains generated HTML dashboard reports.

## Files Generated Here:
- `email_dashboard_YYYYMMDD_HHMM.html` - Email dashboard reports
- `pixel_dashboard_YYYYMMDD_HHMM.html` - Standard dashboard reports
- `dashboard_report_YYYYMMDD.html` - General dashboard reports

## Note:
HTML files in this directory are automatically excluded from Git via `.gitignore` as they are generated locally and contain potentially sensitive data.

To generate reports, use:
```bash
python3 pixel_monitor.py dashboard
python3 pixel_monitor.py email
```

Or via the interactive menu:
```bash
python3 interactive_menu.py
# Select option 2 (Generate Dashboard) or 3 (Email Dashboard)
```