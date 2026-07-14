# Project Manifest
Repository containing multiple Python projects and utilities.

---

## 📁 Projects Overview

### 1. **Pixabay Audio Downloader** (`downloader/`)
Download audio files from Pixabay using API or web scraping methods.

**Main Files:**
- `pixabay_audio_api_downloader.py` - API-based downloader (recommended)
- `pixabay_audio_downloader.py` - Web scraper method

**Prerequisites:**
```bash
# For API method
pip install requests

# For web scraper method
pip install -r downloader/requirements.txt
```

**Run Commands (from root):**
```bash
# API method (requires Pixabay API key)
python downloader/pixabay_audio_api_downloader.py

# Web scraper method
python downloader/pixabay_audio_downloader.py
```

**Documentation:**
- `downloader/README.md` - Full documentation
- `downloader/QUICK_START.md` - Quick start guide

**Notes:**
- API method requires a free Pixabay API key
- Set API key in script or as environment variable: `$env:PIXABAY_API_KEY="your_key"`
- Downloads saved to `downloads/` folder

---

### 2. **Personal Journal App** (`questions/journal_app/`)
Encrypted personal journal with AI-powered prompts using Claude API.

**Main File:**
- `main.py` - Main application entry point

**Prerequisites:**
```bash
# Navigate to app directory
cd questions/journal_app

# Install dependencies
pip install -r requirements.txt
```

**Run Commands (from root):**
```bash
# Run from journal_app directory
cd questions/journal_app && python main.py

# Or using full path
python questions/journal_app/main.py
```

**Documentation:**
- `questions/journal_app/QUICKSTART.md` - Quick start guide
- `questions/journal_app/README.md` - Full documentation

**Features:**
- Password-encrypted journal entries
- Random writing prompts
- AI-generated prompts (requires Claude API key)
- Search and edit past entries
- PyQt5 GUI interface

**Configuration:**
- Optional: Copy `.env.example` to `.env` and add Claude API key
- Prompts file: `questions/prompts.txt`
- Database: `questions/journal_app/journal.db` (auto-created)

---

### 3. **Course Formatter** (`school/`)
Parse and format Georgia Tech course catalog data into various formats.

**Main File:**
- `format_courses.py` - Course formatting utility

**Prerequisites:**
```bash
# No special dependencies required (uses standard library)
```

**Run Commands (from root):**
```bash
# Process courses.txt and generate formatted outputs
python school/format_courses.py
```

**Input:**
- `school/courses.txt` - Raw course data

**Output Files:**
- `school/courses_formatted.md` - Markdown format (best for reading)
- `school/courses_table.txt` - Clean table format
- `school/courses.csv` - CSV format (for spreadsheets/programming)

---

### 4. **Professional Development Self-Assessment** (`self-assessment/`)
Interactive self-assessment tool with radar chart visualization.

**Main Files:**
- `self_assessment_app.py` - Original version
- `self_assessment_app_v2.py` - Enhanced version

**Prerequisites:**
```bash
pip install -r self-assessment/requirements.txt
```

**Run Commands (from root):**
```bash
# Run original version
python self-assessment/self_assessment_app.py

# Run enhanced v2
python self-assessment/self_assessment_app_v2.py
```

**Documentation:**
- `self-assessment/README.md` - Application guide
- `self-assessment/README_v2.md` - Version 2 documentation
- `self-assessment/self-assessment-guide.md` - Assessment guide

**Features:**
- 18 professional development categories
- Interactive questionnaire with 1-10 rating scale
- Radar chart visualization
- PNG export with timestamps
- Progress tracking capabilities

---

### 5. **YTSpecific** (`YTSpecific/`)
iOS app that locks playback to a single YouTube channel at a time — pick a
channel and it queues up an endless stream of just that channel's uploads,
skipping anything already watched. View history and likes are tracked
locally only; likes are never sent to YouTube.

**Main Files:**
- `Sources/YTSpecificApp.swift` - App entry point
- `Sources/Services/YouTubeAPIService.swift` - YouTube Data API v3 client
- `Sources/Services/PlaybackQueueManager.swift` - Per-channel unwatched queue logic
- `Sources/Views/PlayerView.swift` - YouTube IFrame player + like/skip controls

**Prerequisites:**
```bash
# macOS + Xcode required (this is a native iOS app)
brew install xcodegen
```

**Run Commands:**
```bash
cd YTSpecific
xcodegen generate
open YTSpecific.xcodeproj
# Then Run in Xcode on an iOS 17+ simulator or device
```

**Documentation:**
- `YTSpecific/README.md` - Full setup and architecture guide

**Configuration:**
- Requires a free YouTube Data API v3 key (Google Cloud Console), entered
  in-app under Settings and stored in the device Keychain

---

## 🚀 Quick Start - Running All Projects

### From Root Directory Commands

```bash
# 1. Pixabay Audio Downloader (API)
python downloader/pixabay_audio_api_downloader.py

# 2. Journal App
python questions/journal_app/main.py

# 3. Course Formatter
python school/format_courses.py

# 4. Self-Assessment App
python self-assessment/self_assessment_app.py
```

---

## 📦 Global Dependencies Installation

To install all dependencies for all projects:

```bash
# Downloader dependencies
pip install requests selenium

# Journal app dependencies
cd questions/journal_app && pip install -r requirements.txt && cd ../..

# Self-assessment dependencies
pip install -r self-assessment/requirements.txt
```

---

## 📝 Project Status

| Project | Status | Dependencies | GUI | API Required |
|---------|--------|--------------|-----|--------------|
| Pixabay Downloader | ✅ Ready | requests | No | Yes (free) |
| Journal App | ✅ Ready | PyQt5, cryptography, anthropic | Yes | Optional |
| Course Formatter | ✅ Ready | None (stdlib) | No | No |
| Self-Assessment | ✅ Ready | matplotlib, numpy, tkinter | Yes | No |
| YTSpecific | ✅ Ready (needs Xcode to build) | xcodegen (build-time only) | Yes (iOS) | Yes (free) |

---

## 🗂️ Additional Files

- `downloads/` - Download storage directory
- `questions/prompts.txt` - Journal prompt library
- `courses.csv` - Formatted course data (root level)

---

## 💡 Notes

- All projects are self-contained within their respective directories
- Some projects require API keys (Pixabay, Claude) - see individual READMEs
- Journal app creates encrypted database on first run
- Most projects create output files in their own directories
- Virtual environment recommended: Use `.venv/` for isolated dependencies

---

*Last updated: 2026-07-14*
