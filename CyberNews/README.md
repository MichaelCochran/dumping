# Cyber Dashboard (Python/PyQt6)

A simple personal desktop application for tracking your security work (to‑dos, in‑progress items, blocked work, and done items) and reading cyber news in one place.

This guide is written for **non‑technical users**. You don't need to know anything about programming to follow it.

---

## 1. What this app does

- **Task board (Kanban)**
  - Create tasks with title, description, point of contact (POC), status, and due date.
  - Move tasks between columns: **To Do**, **In Progress**, **Blocked**, **Done**.
  - Attach files (documents, screenshots, etc.) to tasks.
  - View, edit, archive, or delete tasks.
  - **Batch operations**: Select multiple tasks to delete or move them all at once.
  - **Select All / Deselect All** buttons for quick bulk actions.

- **Metrics view**
  - See totals for active / archived tasks.
  - See how many items were completed in the last 7 and 30 days.
  - See average cycle time (days from creation to completion).

- **Cyber news tab**
  - Shows security news from multiple RSS sources (The Hacker News, BleepingComputer, SecurityWeek, CISA, DoD).
  - Filter by source and category (web-app-hacking, vulnerabilities, malware, etc.).
  - Search headlines and summaries.
  - Click any article to open it in an **embedded web browser** with navigation controls.
  - Open articles in your default external browser with one click.

- **Dark theme**
  - Modern dark UI using PyQt6 Fusion style.

All your data (tasks and attachments) is stored locally on your computer in a `data` folder next to this app.

---

## 2. One-time setup (first time only)

You only need to do this once on a given computer.

### 2.1. Install Python

1. Open a web browser and go to: **https://www.python.org/downloads/**
2. Download the latest **Python 3.11+** version for **Windows**.
3. Run the installer.
   - **Important**: Check the box that says **"Add Python to PATH"** at the bottom of the first screen.
   - Click **Install Now**.
4. When done, you may need to restart your computer.

### 2.2. Install required Python packages

1. Open **Command Prompt** or **PowerShell**:
   - Press **Windows Key + R**
   - Type `cmd` and press **Enter**

2. Navigate to the CyberNews folder:
   ```bash
   cd C:\Users\YOURNAME\CyberNews
   ```
   (Replace `YOURNAME` with your actual username)

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install PyQt6 PyQt6-WebEngine feedparser
   ```

This may take a minute or two. You only need to do this **once** on a given computer.

---

## 3. How to start the Cyber Dashboard

Once setup is done, here is what you do **each time** you want to use the dashboard.

### 3.1. Run the application

**Option A: Double-click to run**

1. Navigate to the `CyberNews` folder on your computer.
2. Double-click `main.py`.
3. If prompted, choose to open with **Python**.

**Option B: Run from command line**

1. Open **Command Prompt** or **PowerShell**.
2. Navigate to the CyberNews folder:
   ```bash
   cd C:\Users\YOURNAME\CyberNews
   ```
3. Run:
   ```bash
   python main.py
   ```

The Cyber Dashboard window will open immediately.

### 3.2. Using the dashboard

- **Board tab**: 
  - Add new tasks using the form at the top (title, POC, description, due date).
  - Use the **Move...** dropdown on each task card to change status.
  - Use the **Actions** dropdown to View/Edit/Attach/Archive/Delete individual tasks.
  - Use checkboxes to select multiple tasks, then use **Delete Selected** or **Move Selected** buttons for batch operations.
  - **Select All** and **Deselect All** buttons help manage bulk selections.
- **Metrics tab**: See your overall workload and completion statistics.
- **News tab**: 
  - Click **Refresh** to fetch the latest cyber news.
  - Use source and category filters to narrow down articles.
  - Use the search box to find specific keywords.
  - Click any article card to open it in an embedded browser with back/forward/refresh navigation.
  - Use **Open in Browser** to view articles in your default web browser.

### 3.3. When you are done

- Simply close the application window.
- Your tasks and attachments are saved automatically to the local `data` folder.

---

## 4. Where your data lives

The app creates a `data` folder next to the app files. Typically:

- `C:\Users\YOURNAME\CyberNews\data`

Inside `data`:

- `tasks.json` – all your task information.
- `attachments\` – files you uploaded to tasks.

If you copy this `data` folder to another machine with the app installed, you will bring your tasks and attachments with you.

> **Note**: You can edit `tasks.json` in a text editor if needed, but be careful to maintain valid JSON format.

---

## 5. Troubleshooting

### 5.1. The app won't start

- Make sure Python is installed and added to PATH (see section 2.1).
- Make sure you installed the required packages: `pip install -r requirements.txt`
- Try running from command line to see any error messages.
- If you get an error about `PyQt6.QtWebEngineWidgets`, install: `pip install PyQt6-WebEngine`

### 5.2. News won't load

- Click the **Refresh** button in the News tab.
- Check your internet connection (the app fetches RSS feeds from external sources).
- Some feeds may be temporarily unavailable; try again later.

### 5.3. Tasks aren't appearing on the board

- Check the **Metrics** tab to see if tasks exist.
- If tasks exist but don't show on the board, check that `data/tasks.json` uses the correct status values: `"to do"`, `"in-progress"`, `"blocked"`, `"done"` (with a space in "to do").

---

## 6. Getting help

If you are unsure about any step:

- Take a screenshot of what you see.
- Note what you clicked just before the issue.
- Check the command line output for error messages if you ran the app from terminal.

For technical support, provide:
- Your Python version: `python --version`
- Installed packages: `pip list`
- Any error messages from the console
