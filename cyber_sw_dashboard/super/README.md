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
- Downloads from **destination SharePoint** (team's central tracker)
- Processes and categorizes reviews
- Identifies **only new reviews** by comparing Review # against existing entries
- **Uploads** new rows to the **shared destination SharePoint file**

### Features
- 📤 **SharePoint Upload**: Appends new reviews to the central tracker
- 🔄 **Parallel Downloads**: Simultaneous downloads from both sites
- 🚫 **Smart Duplicate Detection**: Compares Review # to avoid re-uploading
- 📂 **Auto-Categorization**: Organizes into Code, Design, Test, and Other sheets
- 🔐 **Session Management**: Persistent authentication
- 📝 **Comprehensive Logging**: All operations logged to `code_review_updater.log`

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
# Full workflow: download → process → deduplicate → upload to SharePoint
python code_review_updater.py

# Skip download if you already have latest files
python code_review_updater.py --skip-download
```

### Workflow Steps
1. **Download**: Parallel download from source and destination SharePoint
2. **Process**: Categorize reviews and extract relevant data
3. **Deduplicate**: Compare Review # to filter out existing entries
4. **Upload**: Append only new rows to destination SharePoint

---

## 2. `dashboard_app.py` - Basic Dashboard (Optional)

Simple dashboard for viewing the shared tracker without refresh capabilities.

### What It Does
- Displays outstanding reviews from `destination_current.xlsx` file
- Groups reviews by repository with expandable cards
- Color-coded status indicators based on workload
- Real-time filtering by repository names

### Features
- 🎨 **Color-Coded Status**: Visual workload indicators
  - 🔴 Red: 10+ outstanding reports
  - 🟡 Yellow: 6-9 reports
  - 🟢 Green: 1-5 reports
  - 🔵 Blue: 0 reports
- 🔍 **Real-time Filtering**: Filter by repository name (partial match, case-insensitive)
- 📊 **Expandable Cards**: Click any repository to see detailed review information
- 🚫 **Cancelled/Broken Reviews**: Separate view for cancelled or broken reviews
- ⚡ **Lazy Loading**: Efficient rendering for large datasets

### Usage
```bash
python dashboard_app.py
```

**Prerequisites:**
- Must run `code_review_updater.py` first to create `destination_current.xlsx`

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

**Destination SharePoint configuration** (team's central tracker):
```python
DEST_CONFIG = {
    "site_url": "https://lmco.sharepoint.us/sites/US-NGI-Cyber-Software",
    "file_path": "/Shared Documents/General/Software Support/Testing New Code Review Tracker.xlsx",
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
