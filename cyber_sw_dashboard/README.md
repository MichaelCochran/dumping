# Code Review Tracker

A comprehensive toolkit for tracking and visualizing code review status across SharePoint sites. Downloads from production tracker, applies date cutoff filtering, and uploads to staging tracker for review.

---

## Project Structure

```
Code Review Updater/
├── code_review_updater.py    # Main updater script
├── dashboard_app.py           # Visual dashboard viewer
├── user_filters.json          # Repository filter configuration (optional)
├── destination_current.xlsx   # Local review data (auto-generated)
├── staging_current.xlsx       # Staging data (auto-generated)
├── sp_session.json            # SharePoint sessions (auto-generated)
├── sp_dest_session.json       # SharePoint sessions (auto-generated)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Quick Start

### Installation

1. Install dependencies:
   ```bash
   pip install playwright openpyxl
   playwright install chromium
   ```

### First Run - Authenticate

2. Run the updater once to authenticate:
   ```bash
   python code_review_updater.py
   ```
   - Browser will open for SharePoint login
   - Complete MFA and wait for SharePoint to load
   - Press Enter when done

### Daily Use - Dashboard

3. Launch the dashboard:
   ```bash
   python dashboard_app.py
   ```
   - Click "⭮ Refresh Data" to update from SharePoint
   - View outstanding reviews grouped by repository
   - Expandable cards show review details

---

## Features

### Code Review Updater (`code_review_updater.py`)
- **Downloads** from production SharePoint tracker
- **Filters** by configurable date cutoff (only new reviews)
- **Deduplicates** against existing entries
- **Uploads** new reviews to staging SharePoint tracker
- **Saves** local copies for dashboard viewing

### Dashboard (`dashboard_app.py`)
- **Color-coded status**: Red (10+), Yellow (6-9), Green (1-5), Blue (0)
- **Repository filtering** via `user_filters.json` (partial match, case-insensitive)
- **Expandable cards**: Click to view detailed review information
- **Cancelled/Broken reviews**: Separate view for notes containing "cancelled" or "pipeline"
- **Other reviews**: Separate view for reviews with notes
- **Integrated refresh**: One-click update from SharePoint
- **Auto-refresh**: Hourly background checks for updates

### Repository Filtering

Create `user_filters.json` to show only specific repositories:
```json
{
  "repos": ["kv", "msv"]
}
```
- Empty list `[]` or missing file shows all repositories
- Supports partial matching (case-insensitive)

---

## Files Reference

| File | Created By | Purpose |
|------|------------|---------|
| `code_review_updater.py` | You | Main updater - downloads, filters, uploads reviews |
| `dashboard_app.py` | You | Visual dashboard with integrated refresh |
| `user_filters.json` | You (optional) | Repository filter configuration |
| `destination_current.xlsx` | Script | Production tracker data for dashboard |
| `staging_current.xlsx` | Script | Staging tracker data for dashboard |
| `sp_session.json` | Script | Source SharePoint session (auto-created) |
| `sp_dest_session.json` | Script | Destination SharePoint session (auto-created) |
| `requirements.txt` | You | Python dependencies |

---

## Configuration

### Date Cutoff

Edit `code_review_updater.py` to change the date cutoff:
```python
DATE_CUTOFF = "2026-05-01"  # Only process reviews on or after this date
```

### SharePoint URLs

Update these in `code_review_updater.py`:
```python
SOURCE_CONFIG = {
    "site_url": "https://your-source-sharepoint-site",
    "file_path": "/path/to/source/file.xlsx",
}

DEST_READ_CONFIG = {
    "site_url": "https://your-dest-sharepoint-site",
    "file_path": "/path/to/production/tracker.xlsx",
}

DEST_UPLOAD_CONFIG = {
    "site_url": "https://your-dest-sharepoint-site",
    "file_path": "/path/to/staging/tracker.xlsx",
}
```

---

## Troubleshooting

### Session Expired
```bash
# Delete session files and re-authenticate
del sp_session.json sp_dest_session.json  # Windows
rm sp_session.json sp_dest_session.json   # Linux/Mac

# Then run again
python code_review_updater.py
```

### Dashboard Shows No Data
```bash
# Run updater to download data
python code_review_updater.py

# Then launch dashboard
python dashboard_app.py
```

### Upload Fails (File Locked)
- Close the staging tracker Excel file if you have it open
- Ask others to close the file
- Check if file is checked out in SharePoint
- Wait a moment and try again

### More Help
- **Check logs**: Review console output for detailed error messages
- **Specification**: See `SPECIFICATION_SUPER.md` for full architecture details

---

## Workflow

1. **First Time**: Run `python code_review_updater.py` to authenticate
2. **Daily/Weekly**: 
   - Launch dashboard: `python dashboard_app.py`
   - Click "⭮ Refresh Data" to update from SharePoint
3. **Monitor**: Review outstanding reports and track completion
