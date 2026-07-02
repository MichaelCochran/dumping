# Super Tools - For Team Coordinators Only

**⚠️ WARNING: COORDINATOR USE ONLY** - These tools modify the shared SharePoint tracker and should only be run by the designated team coordinator.

---

## Why Limit Usage?

If multiple people run these scripts simultaneously, they will:
- Compete for write access to the same SharePoint file
- Potentially create duplicate entries
- Overwrite each other's changes
- Cause data inconsistencies

**👥 For Teams:** Designate ONE person as the coordinator who runs these scripts periodically to update the shared tracker.

**👤 For Everyone Else:** Use the tools in the `local/` folder instead - they provide the same data without conflicts.

---

## Prerequisites

### Install Dependencies
```bash
pip install playwright openpyxl
playwright install chromium
```

---

## 1. `code_review_updater.py` - SharePoint Uploader

Updates the team's central SharePoint tracker with new code reviews.

### What It Does
- Downloads from **source SharePoint** (original review status file)
- Downloads from **production tracker** (team's central live tracker)
- Processes and categorizes reviews
- Identifies **only new reviews** by comparing Review # against existing entries
- Applies a **date cutoff** (configured as `DATE_CUTOFF` in `code_review_updater.py`) so only reviews on or after that date are considered
- Saves a local copy as `super/destination_current.xlsx`
- **Uploads** new rows to the **staging tracker** ("Staging Tracker.xlsx")

### Features
- SharePoint upload: Appends new reviews to the **staging tracker** file
- Parallel downloads: Simultaneous downloads from source and production trackers
- Smart duplicate detection: Compares Review # to avoid re-uploading existing reviews
- Auto-categorization: Organizes into Code, Design, and Other sheets
- Session management: Persistent authentication with session files
- Comprehensive logging: All operations logged to `code_review_updater.log`

### Coordinator Setup
Same authentication process as local tools:
```bash
python code_review_updater.py
```
1. Browser opens for SharePoint login (both source and destination)
2. Complete MFA authentication
3. Press ENTER after successful login
4. Sessions saved for future runs

### Coordinator Usage
```bash
# Full workflow: download → process → deduplicate → upload to staging SharePoint
python code_review_updater.py

# Skip download if you already have latest files
python code_review_updater.py --skip-download
```

### Workflow Steps
1. **Download**: Parallel download from source SharePoint and production tracker
2. **Process**: Categorize reviews and extract relevant data
3. **Deduplicate**: Compare Review # to filter out existing entries
4. **Save Local Copy**: Write updated data to `destination_current.xlsx`
5. **Upload**: Append only new rows to the **staging tracker** on SharePoint

---

## 2. `dashboard_app.py` - Basic Dashboard (Optional)

Simple dashboard for viewing the shared tracker.

### What It Does
- Displays outstanding reviews from `destination_current.xlsx` file
- Groups reviews by repository with expandable cards
- Color-coded status indicators based on workload
- Real-time filtering by repository names using `user_filters.json`

### Features
- Reload button: Reloads data from `super/destination_current.xlsx` (no integrated upload)
- Color-coded status: Visual workload indicators
  - Red: 10+ outstanding reports
  - Yellow: 6-9 reports
  - Green: 1-5 reports
  - Blue: 0 reports
- Real-time filtering: Filter by repository name (partial match, case-insensitive)
- Expandable cards: Click any repository to see detailed review information
- Cancelled/Broken reviews: Separate view for reviews where Notes contain "cancelled" or "pipeline"
- Other reviews: Separate view for reviews with Notes that are not cancelled/pipeline
- Lazy loading and scrollable layout for large datasets

### Usage
```bash
python dashboard_app.py
```

**Prerequisites:**
- Must run `code_review_updater.py` first to create `super/destination_current.xlsx`

**Note:** This is a basic viewer. Team members should use `dashboard_local.py` in the `local/` folder for a better experience with integrated refresh.

---

## Configuration

### SharePoint URLs
Update these in `code_review_updater.py` if URLs change:

**Source SharePoint configuration** (original review status file):
```python
SOURCE_CONFIG = {
    "site_url": "https://space-us.external.lmco.com/sites/ngi",
    "file_path": "/fa/Software/Software/01-Common-Folder/NGI FSW Formal Review Status.xlsx",
    ...
}
```

**Production tracker configuration** (team's central tracker):
```python
DEST_READ_CONFIG = {
    "site_url": "https://lmco.sharepoint.us/sites/US-NGI-Cyber-Software",
    "file_path": "/Shared Documents/General/Software Support/New Code Review Tracker.xlsx",
    ...
}
```

**Staging tracker configuration** ("Staging Tracker.xlsx"):
```python
DEST_UPLOAD_CONFIG = {
    "site_url": "https://lmco.sharepoint.us/sites/US-NGI-Cyber-Software",
    "file_path": "/Shared Documents/General/Software Support/Staging Tracker.xlsx",
    ...
}
```

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
python code_review_updater.py
```

### Upload Failed
**Problem:** "Upload failed" with 403 or 409 errors  
**Solution:** Check permissions and file status
- **403**: Verify you have write permissions to the destination folder
- **409**: File may be locked or checked out by another user
- Wait a few minutes and try again

### No New Data Uploaded
**Problem:** "NO NEW DATA" message in logs  
**Solution:** This is expected behavior - all reviews are already synced. No action needed.

### Check Detailed Logs
Review `code_review_updater.log` for detailed operation history and error messages.

---

## Recommended Workflow for Coordinators

1. **Periodically** (e.g., daily or weekly): Run `code_review_updater.py` to update shared tracker
2. **Monitor**: Check `code_review_updater.log` for any issues
3. **Communicate**: Notify team when central tracker is updated
4. **For Personal Use**: Use tools in `local/` folder like everyone else
