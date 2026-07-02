# Code Review Tracker – Super Tools Specification

**Scope**

This specification defines the behavior and architecture for the **Coordinator (“super”) tools**:

- `super/code_review_updater.py`
- `super/dashboard_app.py`
- `user_filters.json` (shared config format)

The goal is to support a complete rewrite without needing to reference the existing code.

---

## 1. High‑Level Workflow

### 1.1 Actors

- **Users**: run the updater and dashboard, have permissions to read and write the SharePoint trackers.

### 1.2 Data Flow Overview

1. **Input**: A “source” SharePoint workbook with raw code review status.
2. **Processing**:
   - Download source workbook to local temp file.
   - Transform rows into a normalized structure with:
     - Repo name
     - Review number
     - Date (date‑only)
     - Description
   - Classify into sheets: `Code`, `Design`, `Other`.
   - Compare against an existing “destination” tracker workbook (production) to find new rows (based on a date cutoff and duplicate detection).
3. **Outputs**:
   - Write a local Excel file `destination_current.xlsx` in `super/` with the new data **only** (sliced for dashboard usage).
   - Upload a “staging” tracker workbook to a *staging* SharePoint location, containing all new entries appended to existing tables.
4. **Dashboard**:
   - `dashboard_app.py` reads `destination_current.xlsx` and displays outstanding reviews grouped by repository.
   - Supports a “Refresh” action that runs `code_review_updater.py` and reloads data.
5. **Filters**:
   - An optional JSON file (`user_filters.json`) in the script directory defines repo filters used by the dashboard.

---

## 2. Shared Concepts and Data Model

### 2.1 Repository Identifier

- Repositories are identified by **canonical strings** such as:
  - `MSV-EM`, `MSV-FSW`, `MSV-NGC`, `MSV-PTS`
  - `KV-EM`, `KV-FSW`, `KV-NGC`, `KV-PTS`
  - `COMMON-ALGO`, `COMMON-FSW`
  - `NGICON`, `HSP`, `HS`
- Mapping logic must be configurable but by default:
  - Derived from a free‑text description field (from source workbook).
  - Uses substring matching rules (e.g., presence of “MSV” and “EM” → `MSV-EM`).
- If mapping fails, the value **must** be `ENTER REPO NAME` to signal manual cleanup.

### 2.2 Normalized Row Schema

The updater and dashboards should agree on an internal row schema (Python data class or dict):

```python
ReviewRow = {
    "review_number": str,
    "date": "YYYY-MM-DD" or "M/D/YYYY" as string,
    "repo": str,             # canonical repo name
    "description": str,
    "report_uploaded": str | None,  # dest workbook field
    "notes": str | None,     # free-text notes from dest workbook
}
```

Dashboard will only need a subset:

```python
DashboardRow = {
    "reviewNum": str,
    "date": "YYYY-MM-DD" or "N/A",
    "repo": str,
    "description": str,
    "notes": str | None,
}
```

### 2.3 Date Handling

- Acceptable input:
  - `datetime` or `date` objects.
  - Strings in formats:
    - `YYYY-MM-DD`
    - `M/D/YYYY`
    - `D-Mon-YYYY` (e.g., `5-May-2026`)
    - Strings containing a time component (e.g., `2026-05-06 00:00:00`).
- **Normalize** to a date‑only string:
  - Return `YYYY-MM-DD` when starting from a true date/datetime.
  - When given strings, strip time and return only the date portion; if no date is detected, return the original string.
- **Cutoff rule**:
  - Configurable `DATE_CUTOFF` (ISO string) – ignore any *source* row whose processed date is **strictly before** this cutoff when computing “new entries”.

### 2.4 User Filters (`user_filters.json`)

File location:

- Root: `user_filters.json` in the script directory.

Schema:

```json
{
  "repos": [
    "KV",
    "MSV-EM"
  ]
}
```

Rules:

- Empty or missing `repos` → show **all** repositories.
- Matching is **partial**, **case‑insensitive**:
  - repo is included if `filter_term.lower() in repo.lower()` for any term.
- Invalid JSON or IO errors → treat as “no filter” (log a warning).

---

## 3. `code_review_updater.py` – Updater Specification

### 3.1 Responsibility

- Authenticate to SharePoint (source + destination).
- Download a production tracker from source SharePoint.
- Process/transform rows into normalized structure and per‑sheet output.
- Detect and prepare **new entries** based on date cutoff and duplicates.
- Append new rows to tables in a *staging* tracker workbook on SharePoint (via REST).
- Write `destination_current.xlsx` and `staging_current.xlsx` used by dashboard.
- Provide robust logging and clearly surfaced errors.

### 3.2 Configuration

**Source configuration**

- `SOURCE_SITE_URL`: SharePoint site.
- `SOURCE_FILE_PATH`: server‑relative path to the “raw status” workbook.
- `SOURCE_SESSION_FILE`: path to JSON session storage (Playwright storage state).

**Destination configuration**

- `DEST_READ_SITE_URL`: site containing the **production tracker** (for reading baseline).
- `DEST_READ_FILE_PATH`: server‑relative path to production tracker workbook.
- `DEST_UPLOAD_SITE_URL`: same site or another; this is where the **staging tracker** lives.
- `DEST_UPLOAD_FILE_PATH`: server‑relative path to staging tracker workbook (overwritten or updated).
- `DEST_SESSION_FILE`: JSON session for destination site.

**Runtime configuration**

- `TARGET_SHEETS`: list of sheet names in the destination tracker used for categories:
  - Must include `"Code"`, `"Design"`, `"Other"`.
- `DATE_CUTOFF`: string; used to ignore old rows when computing new entries.
- `SESSION_MAX_AGE`: max file age before session is auto‑expired and re‑login is forced.
- Environment variable:
  - `CODE_REVIEW_DASHBOARD_MODE="1"` → login flow must be coordinated via flag files (see 3.5.3).

### 3.3 Authentication and Session Management

Implementation must use **Playwright** with storage‑state files.

#### 3.3.1 Session Validation

- Function: `check_session_valid(session_path, site_url) -> bool`
- Behavior:
  - If session file missing → invalid.
  - Launch headless browser, create context with `storage_state=session_path`, navigate to `site_url`.
  - If the resulting URL is a Microsoft login/auth URL (list of domains), session is invalid.
  - Network/timeout errors → log and treat as invalid but do **not** crash.

#### 3.3.2 Session Age and Auto‑expire

- On startup, for each known session file (source, dest‑read, dest‑upload):
  - If file exists and `now - mtime > SESSION_MAX_AGE`, delete it and log info.

#### 3.3.3 Interactive Authentication

- Function: `authenticate(session_path, site_url) -> bool`
- Must:
  - Launch browser (non‑headless).
  - Navigate to `site_url` (if this fails, instruct user to navigate manually).
  - Provide user instructions in terminal OR via dashboard flags (see below).
  - After login, verify final page is *not* a login page.
  - Save Playwright storage state to `session_path`.
- If any fatal error occurs (user cancels, still on login page, cannot save session) → return False; caller will exit program with message.

#### 3.3.4 Dashboard‑Mode Login Coordination

When `CODE_REVIEW_DASHBOARD_MODE="1"`:

- Use flag files in script directory:
  - `dashboard_mode_login_needed.flag`
  - `dashboard_mode_continue.flag`
- Flow:
  - Updater, before requiring login confirmation:
    - Delete any stale flags.
    - Create `dashboard_mode_login_needed.flag` to signal UI to show login dialog.
  - Updater then waits (up to a configurable timeout, e.g., 15 minutes) for `dashboard_mode_continue.flag` to appear.
  - Dashboard app is responsible for:
    - Watching `dashboard_mode_login_needed.flag`.
    - Displaying a modal with instructions.
    - On “Login Complete”, delete `dashboard_mode_login_needed.flag`, create `dashboard_mode_continue.flag`.
- If timeout occurs, or any unexpected login failure, updater exits with a non‑zero code.

When `CODE_REVIEW_DASHBOARD_MODE` is **not** set:

- Use terminal prompt `input("Press ENTER after successful login...")`.

### 3.4 SharePoint File Operations

#### 3.4.1 Downloading Files

- Function signature: `download_file(site_url, file_path, session_path, output_path) -> bool`.
- Behavior:
  - Compose download URL: `site_url.rstrip('/') + file_path + '?download=1'`.
  - Use Playwright context with `storage_state` and `accept_downloads=True`.
  - Handle navigation interrupted by download; treat timeouts as “check if download triggered” rather than fatal.
  - Save to temporary file first, validate file size non‑zero, then copy/overwrite `output_path`.
  - Log meaningful errors:
    - 404 → file not found.
    - 403 → access denied.
    - 5xx → server error.
    - Page title indicates login or error.

#### 3.4.2 Uploading to Test Tracker

- Function signature: `upload_file(site_url, file_path, session_path, local_file) -> bool`
- Behavior:
  - Read `local_file` fully into memory; ensure non‑empty.
  - Use REST API:
    - Get form digest via `POST {site_url}/_api/contextinfo`.
    - Then upload file via `POST` to:
      - `"{site_url}/_api/web/GetFolderByServerRelativeUrl('{folder_relative}')/Files/add(url='{file_name}',overwrite=true)"`
  - Interpret status codes:
    - 200/201 → success.
    - 401, 403, 404, 409, >=500 → log specific, human‑readable errors.
  - Must handle network and JSON parsing failures gracefully and return False.

### 3.5 Data Processing & Transformation

#### 3.5.1 Source Workbook Reading

- Use `openpyxl` in read‑only mode.
- Assumptions (but keep configurable):
  - Single active sheet with raw review rows.
  - First row may be header; logic:
    - If first cell is numeric (int/float) → treat as data row.
    - Otherwise → treat as header and skip.
- Skip entirely empty rows.

#### 3.5.2 Classification into Target Sheets

- Function: `classify(source_row) -> 'Code' | 'Design' | 'Other' | None`
- Default rules:
  - If column C contains `"test"` (case‑insensitive) → ignore row (`None`).
  - Else, check column D:
    - contains `"code"` → `Code`
    - contains `"design"` → `Design`
    - otherwise → `Other`.
- An additional ignore rule:
  - If column E (0‑based index 4) contains `"test"` → ignore row (`None`).
- These rules must be centralized and easy to change.

#### 3.5.3 Repository Mapping

- Function: `map_repo(description_field) -> str`.
- Must implement the canonical mapping rules from section 2.1.
- Return `ENTER REPO NAME` when no mapping matches.

#### 3.5.4 Destination Workbook Construction

Two output artifacts:

1. **Destination tracker workbook (for SharePoint – staging file)**:
   - The updater must:
     - Load the current staging (or baseline) workbook from SharePoint, **or** create a new one if not present.
     - For each target sheet (`Code`, `Design`, `Other`):
       - Identify existing Excel table (by name or first table).
       - Append new rows to the table’s data body range **after** existing rows (preserving existing data/formatting).
   - Table range must be extended to include all new rows.

2. **`destination_current.xlsx` and `staging_current.xlsx` (local dashboard files)**:
   - This file is the coordinator’s view of **outstanding** or **new** reviews.
   - Minimal requirements:
     - Must contain a sheet named `"Code"` with columns:
       - Column B → Review Number (`reviewNum`)
       - Column C → Date (`date`, date‑only string)
       - Column D → Repository (`repo`)
       - Column E → Description (`description`)
       - Column F → Report Uploaded status (may be blank)
       - Column I → Notes
   - Content:
     - Recommended: For simplicity, write **only new entries** generated in this run, but preserve the column structure used by the dashboards.
     - Alternatively, the spec can require the full set of relevant rows from the staging tracker; the dashboard logic is already robust to older rows.

### 3.6 Duplicate Detection & Date Cutoff

- **Date cutoff**:
  - For each source row, compute normalized date string.
  - If date is missing or cannot be parsed:
    - Option 1 (preferred): treat as **new** but log a warning; subject to duplicate check.
    - Option 2: ignore; this decision should be explicit in code comments.
  - If date is strictly less than `DATE_CUTOFF` → ignore row.
- **Duplicate detection**:
  - A row is considered already processed if a matching review number + repo combination is already present in the staging or production tracker.
  - Implementation detail:
    - On startup, read the destination’s `Code`, `Design`, `Other` sheets and construct a set of keys:
      - e.g., `(repo, review_number, date)` or `(repo, review_number)`.
    - For each candidate source row, skip if key is in that set.
- **Result**:
  - Only rows passing **both**:
    - `date >= DATE_CUTOFF`
    - Not already in destination
  - Are appended to staging tracker and written into `destination_current.xlsx`.

---

## 4. `dashboard_app.py` – Dashboard Specification

### 4.1 Responsibility

- Provide a Tkinter GUI to visualize outstanding / categorized reviews from `destination_current.xlsx`.
- Allow users to:
  - Refresh data by running `code_review_updater.py`.
  - View grouped lists:
    - Outstanding reviews per repo.
    - Cancelled/broken reviews.
    - Other reviews with notes.

### 4.2 Data Source

- Path: `destination_current.xlsx` in script directory.
- Sheet: `"Code Reviews"`.
- Assumed layout (0‑based indices in code):

| Column | Excel | Meaning           |
|--------|--------|-------------------|
| 1      | B      | review_number     |
| 2      | C      | date              |
| 3      | D      | repo              |
| 4      | E      | description       |
| 5      | F      | report_uploaded   |
| 9      | J      | notes             |

- Skip first 3 rows as headers (configurable).
- Treat rows where all cells are `None` as empty.

### 4.3 Categorization Logic

For each row:

- Compute:
  - `is_uploaded`:
    - `True` if `report_uploaded` is non‑empty and not equal to `"none"` (case‑insensitive).
    - If `report_uploaded` contains substring `"no"` (case‑insensitive), force `is_uploaded=False`.
  - `has_notes`: `bool(str(notes).strip())`.

Category:

- Ignore rows with no `repo`.
- Apply filters (see 4.4).
- If `is_uploaded` is `True` → row is **not** actionable; ignore for all categories.
- Else (not uploaded):
  - If `has_notes`:
    - `notes_lower = notes_str.lower()`
    - If `"cancelled"` in notes_lower or `"pipeline"` in notes_lower:
      - Add to `cancelled_data[repo]`.
    - Else:
      - Add to `other_data[repo]`.
  - Else:
    - Add to `repo_data[repo]` (outstanding).

Track counts:

- `total_outstanding = sum(len(v) for v in repo_data.values())`.
- `total_cancelled`, `total_other` similarly.

### 4.4 Repo Filtering

- Load filters from `FILTER_CONFIG = SCRIPT_DIR / "user_filters.json"`.
- Apply the same partial, case‑insensitive logic as section 2.4.
- If filter list is non‑empty:
  - Include row only if any filter term matches the repo.
- UI should display current filter in summary (`"Filter: <terms>"` or `"Filter: All repos"`).

### 4.5 UI Layout

- **Main window**:
  - Title: `"Code Review Dashboard - Super"` or `"Code Review Dashboard"` (configurable).
  - Size: default `400x600`, resizable.
- **Sections**:
  1. **Summary card**:
     - Displays:
       - `"Total Outstanding Reports"`.
       - Large count number.
       - “Data Updated: MM-DD HH:MM” (local time).
       - Current filter info.
     - Color‑coding based on `total_outstanding`:
       - `>= 10`: red theme.
       - `6–9`: yellow theme.
       - `1–5`: green theme.
       - `0`: blue theme.
  2. **Toolbar**:
     - `Refresh Data` button:
       - Disabled and text changed to `"Updating from SharePoint..."` during refresh.
     - `Cancelled/Broken` button:
       - Enabled only if `total_cancelled > 0`.
       - Text `"🚫 Cancelled/Broken (N)"` when enabled, `"🚫 Cancelled/Broken"` when disabled.
     - `Other` button:
       - Enabled only if `total_other > 0`.
       - Text `"📋 Other (N)"` when enabled, `"📋 Other"` when disabled.
  3. **Scrollable repo list**:
     - Scrollable canvas with a frame of **repo cards**.
     - Each repo card:
       - Header:
         - Icon (e.g., 📦 or similar).
         - Repo name.
         - Subtext `<count> outstanding report(s)`.
         - A badge with count and badge color based on count:
           - `>=5`: red.
           - `3–4`: yellow.
           - `1–2`: green.
           - `0`: blue/grey.
         - Expand/collapse arrow (▶ / ▼).
       - Expanded content:
         - List of outstanding reviews for that repo:
           - Show review number, date, description, notes (if any).
     - Only outstanding (`repo_data`) are shown in main list.
  4. **Cancelled/Broken popup**:
     - Toplevel window listing repos with cancelled/broken reviews, in cards similar to main view.
  5. **Other popup**:
     - Toplevel window listing “other” reviews (notes present but not cancelled/pipeline).

### 4.6 Refresh Behavior

- `Refresh` button:
  - Spawns a **background thread** that:
    - Runs `code_review_updater.py` via `subprocess.run` in script directory.
    - Sets `CODE_REVIEW_DASHBOARD_MODE=1` in environment.
  - Meanwhile, the main thread:
    - Updates label: “Updating data from SharePoint…”.
    - Starts a polling loop checking for `dashboard_mode_login_needed.flag`:
      - When flag exists → shows login dialog (see 4.7).
  - After updater finishes:
    - If exit code non‑zero → show error dialog with stderr.
    - In all cases → call `load_data()` to refresh UI from disk.
    - Re‑enable Refresh button and reset text.
    - Clean up any login flag files.

### 4.7 Login Coordination UI

- When `dashboard_mode_login_needed.flag` exists:
  - Show a modal Toplevel window with:
    - Instructions to complete SharePoint login in the browser, then click “Login Complete”.
  - On “Login Complete”:
    - Delete `dashboard_mode_login_needed.flag`.
    - Create `dashboard_mode_continue.flag`.
    - Close window.
  - A “Cancel” button should allow closing dialog without signalling login; updater will eventually time out.

---

## 5. Error Handling & Logging

### 5.1 Updater

- Must log:
  - Start/finish of major phases:
    - Session cleanup.
    - Authentication.
    - Downloads/uploads.
    - Data processing/categorization.
  - Any non‑fatal issues (timeouts, retries, small file sizes).
- Logs should be written to console (with optional ANSI colors).

### 5.2 Dashboard

- File not found (`destination_current.xlsx` missing):
  - Show error dialog instructing to run updater.
  - Set Refresh button text to “Reload Data”.
- Data loading errors:
  - Show error dialog with exception text, but do not crash the UI.
- Invalid filter config:
  - Print warning to console; fall back to no filters.

---

## 6. Non‑Functional Requirements

- **Dependencies**:
  - Python 3.9+ (configurable).
  - `playwright`, `openpyxl`, `tkinter` (standard on Windows), `requests` (optional if not using Playwright’s request API).
- **Performance**:
  - Updater must handle thousands of rows in reasonable time (< 1–2 minutes, dominated mainly by network & SharePoint).
  - Dashboard should remain responsive during refresh by using a background thread.
