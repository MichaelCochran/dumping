# Code Review Tracker Suite

A comprehensive toolkit for tracking and visualizing code review status across SharePoint sites. Designed for team collaboration with individual local tracking and shared dashboard viewing.

---

## � Project Structure

```
Code Review Updater/
├── local/                  # Tools for individual team members
│   ├── code_review_local.py   # Download and track reviews locally
│   ├── dashboard_local.py     # Visual dashboard with integrated refresh
│   └── README.md              # Detailed documentation for local tools
│
├── super/                  # Tools for team coordinators only
│   ├── code_review_updater.py # Upload reviews to shared SharePoint
│   ├── dashboard_app.py       # Basic dashboard viewer
│   └── README.md              # Detailed documentation for coordinator tools
│
├── user_filters.json       # Repository filter configuration
└── README.md               # This file
```

---

## 🚀 Quick Start

### For Individual Team Members (Everyone)

**👉 Go to [`local/`](local/) folder and follow the README**

1. Install dependencies:
   ```bash
   pip install playwright openpyxl
   playwright install chromium
   ```

2. Authenticate once:
   ```bash
   cd local
   python code_review_local.py
   ```

3. Use the dashboard daily:
   ```bash
   python dashboard_local.py
   # Click "↻ Refresh Data" to fetch latest reviews
   ```

**[📖 Full Documentation →](local/README.md)**

---

### For Team Coordinators Only

**⚠️ WARNING: Only the designated coordinator should use these tools**

**👉 Go to [`super/`](super/) folder and follow the README**

1. Install dependencies (same as above)

2. Run the updater periodically:
   ```bash
   cd super
   python code_review_updater.py
   ```

**[📖 Full Documentation →](super/README.md)**

---

## 📋 What's What?

### Local Tools (For Everyone)
- **`code_review_local.py`** - Downloads and processes code reviews, saves locally
- **`dashboard_local.py`** - Visual dashboard with one-click refresh
- **Safe for multi-user** - Everyone can run these independently without conflicts

### Super Tools (Coordinator Only)
- **`code_review_updater.py`** - Uploads new reviews to shared SharePoint tracker
- **`dashboard_app.py`** - Basic dashboard viewer
- **⚠️ Single-user only** - Multiple people running these causes conflicts

---

## 🎨 Features

### Local Dashboard (`dashboard_local.py`)
- 🔄 **Integrated Refresh**: One-click download and update from SharePoint
- 🎨 **Color-Coded Status**: Red (10+), Yellow (6-9), Green (1-5), Blue (0)
- � **Repository Filtering**: Filter by repo name (partial match)
- � **Expandable Cards**: Click to view detailed review information
- 🚫 **Cancelled/Broken Reviews**: Separate view for non-actionable items
- ⚡ **Lazy Loading**: Efficient rendering for large datasets

### Repository Filtering
Edit `user_filters.json` to customize dashboard view:
```json
{
  "repos": ["kv", "msv"]
}
```
- Empty list `[]` shows all repositories
- Supports partial matching (case-insensitive)

---

## 📊 Files Reference

| File | Location | Created By | Purpose |
|------|----------|------------|---------|
| `code_review_local.py` | `local/` | User | Individual local tracker |
| `dashboard_local.py` | `local/` | User | Dashboard with integrated refresh |
| `code_review_updater.py` | `super/` | User | SharePoint uploader (coordinator only) |
| `dashboard_app.py` | `super/` | User | Basic dashboard viewer |
| `user_filters.json` | Root | User | Repository filter configuration |
| `destination_current.xlsx` | Root | Scripts | Local copy of review data (auto-created) |
| `code_review_updater.log` | Root | Scripts | Detailed operation logs (auto-created) |
| `sp_session.json` | Root | Scripts | Source SharePoint session (auto-created) |
| `sp_dest_session.json` | Root | Scripts | Destination SharePoint session (auto-created) |

---

## 🆘 Quick Troubleshooting

### Session Expired
```bash
# Delete session files and re-authenticate
del sp_session.json sp_dest_session.json  # Windows
rm sp_session.json sp_dest_session.json   # Linux/Mac

# Then run again
cd local
python code_review_local.py
```

### Dashboard Shows No Data
```bash
# Option 1: Use integrated refresh button
python dashboard_local.py
# Then click "↻ Refresh Data"

# Option 2: Manual refresh
python code_review_local.py
python dashboard_local.py
```

### More Help
- **Local tools issues**: See [`local/README.md`](local/README.md)
- **Coordinator tools issues**: See [`super/README.md`](super/README.md)
- **Check logs**: Review `code_review_updater.log`

---

## 📚 Documentation

- **[Local Tools (Everyone) →](local/README.md)**
  - `code_review_local.py` - Download and track reviews
  - `dashboard_local.py` - Visual dashboard with refresh

- **[Super Tools (Coordinator Only) →](super/README.md)**
  - `code_review_updater.py` - Upload to SharePoint
  - `dashboard_app.py` - Basic viewer

---

## ⚡ Recommended Workflow

### For Individual Team Members
1. **First Time**: `cd local && python code_review_local.py` to authenticate
2. **Daily/Weekly**: Launch dashboard and click "↻ Refresh Data"
3. **Never**: Run anything in `super/` folder

### For Team Coordinator
1. **For Personal Use**: Use `local/` tools like everyone else
2. **Periodically**: Run `super/code_review_updater.py` to update shared tracker
3. **Monitor**: Check logs and communicate updates to team
