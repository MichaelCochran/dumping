# Local Tools - For Individual Team Members

**⭐ RECOMMENDED FOR EVERYONE** - These tools let you track and view code reviews locally without affecting shared resources.

---

## Quick Start

### Install Dependencies
```bash
pip install playwright openpyxl
playwright install chromium
```

### First Time Setup
```bash
# Authenticate and download initial data
python code_review_local.py
```

### Daily Use
```bash
# Launch dashboard with integrated refresh
python dashboard_local.py
```

---

## 1. `code_review_local.py` - Individual Tracker

Maintains your own local copy of code review data without conflicts.

### What It Does
- Downloads from **source SharePoint** (original review status file)
- Downloads from **comparison tracker** (team's central tracker)
- Processes and categorizes reviews into Code, Design, Test, and Other sheets
- Identifies **only new reviews** by comparing Review # against the tracker
- Saves results **locally** to `destination_current.xlsx` on your machine
- **No conflicts** - everyone can run this independently

### Features
- ✅ **Parallel Downloads**: Fast simultaneous downloads from both SharePoint sites
- ✅ **Smart Duplicate Detection**: Only saves reviews with numbers higher than current max
- ✅ **Auto-Categorization**: Organizes by review type
- ✅ **Session Management**: Saves login credentials for future runs
- ✅ **Safe for Multi-User**: No shared file modifications

### First Run - Authentication
```bash
python code_review_local.py
```
On first run:
1. Browser opens for SharePoint login
2. Complete MFA authentication
3. Press ENTER after successful login
4. Sessions saved to `sp_session.json` and `sp_dest_session.json`

### Regular Usage
```bash
# Full workflow: download → process → save locally
python code_review_local.py

# Skip download if you already have latest files
python code_review_local.py --skip-download
```

### Output Files
- `destination_current.xlsx` - Your local copy with latest reviews
- `code_review_updater.log` - Detailed operation logs
- `sp_session.json` - Saved source SharePoint login session (auto-created)
- `sp_dest_session.json` - Saved comparison tracker session (auto-created)

---

## 2. `dashboard_local.py` - Visual Dashboard

Displays outstanding reviews with integrated refresh functionality.

### What It Does
- Displays outstanding reviews from your `destination_current.xlsx` file
- Groups reviews by repository with expandable cards
- Color-coded status indicators based on workload
- **Integrated refresh button** - automatically runs `code_review_local.py` to download and process latest data
- Real-time filtering by repository names using `user_filters.json`

### Features
- One-click refresh: Automatically runs `code_review_local.py` in the background (non-blocking UI)
  - Shows status updates during refresh
  - Displays detailed error dialogs if the updater fails
- Color-coded status: Visual workload indicators
  - Red: 10+ outstanding reports
  - Yellow: 6-9 reports
  - Green: 1-5 reports
  - Blue: 0 reports
- Repository filtering: Filter by repository name (partial match, case-insensitive) via `user_filters.json`
- Expandable cards: Click any repository to see detailed review information
- Cancelled/Broken reviews: Separate view for reviews where Notes contain "cancelled" or "pipeline"
- Other reviews: Separate view for reviews with Notes that are not cancelled/pipeline
- Lazy loading and scrollable layout for large datasets

### Usage
```bash
python dashboard_local.py
```

**First-time setup:**
- Run `code_review_local.py` once manually to authenticate and create initial data file
- After that, use the dashboard's built-in "Refresh Data" button

### Workflow
1. Launch dashboard: `python dashboard_local.py`
2. Click "↻ Refresh Data" button when you want to fetch latest reviews
3. Dashboard automatically downloads, processes, and updates display
4. Filter repositories using `user_filters.json` (optional)

### Filtering Repositories
Edit `user_filters.json` to customize which repositories you see:
```json
{
  "repos": ["kv", "msv"]
}
```
- Empty list `[]` = show all repositories
- Supports partial matching (e.g., "kv" matches "kv-repo", "my-kv-project")
- Case-insensitive
- Dashboard automatically applies filters on load and refresh

---

## Troubleshooting

### Session Expired
**Problem:** "Session expired" or browser opens unexpectedly  
**Solution:** Delete session files and re-authenticate
```bash
# Delete session files
rm sp_session.json sp_dest_session.json  # Linux/Mac
del sp_session.json sp_dest_session.json  # Windows

# Run script again to re-authenticate
python code_review_local.py
```

### Dashboard Shows No Data
**Problem:** "File not found" or empty dashboard  
**Solution:** Run local tracker first, or use the built-in refresh button
```bash
# Option 1: Manual refresh
python code_review_local.py
python dashboard_local.py

# Option 2: Use dashboard's built-in refresh button
python dashboard_local.py
# Then click "↻ Refresh Data" button
```

### No New Data Saved
**Problem:** "NO NEW DATA" message in logs  
**Solution:** This is expected behavior - all reviews are already synced. No action needed.

### Check Detailed Logs
Review `code_review_updater.log` for detailed operation history and error messages.

---

## Recommended Workflow

1. **First Time**: Run `code_review_local.py` once to authenticate
2. **Daily/Weekly**: Launch `dashboard_local.py` and click "↻ Refresh Data" button
3. **Anytime**: Use dashboard to view and filter reviews
4. **Never**: Run tools in the `super/` folder (let coordinator handle those)
