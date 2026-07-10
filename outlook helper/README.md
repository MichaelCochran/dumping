# Outlook Email Task Generator

Automatically generate tasks from your Outlook emails without copying and pasting. Works entirely locally with your installed Outlook client—no cloud permissions needed.

## Features

- **📊 Visual Kanban Board**: Drag-and-drop task management with dynamic, user-customizable groups and columns
- **🔄 Real-time Monitor Mode**: Automatically watches for new emails and generates tasks
- **⚡ On-Demand Processing**: Process recent emails when you want
- **🤖 Smart Task Generation**: 
  - Template-based extraction (works out of the box)
  - Optional AI-powered analysis (OpenAI integration)
- **🎯 Priority Detection**: Automatically assigns priority based on keywords and importance
- **📋 Category Classification**: Groups tasks into Response Required, Review, Action Item, or FYI
- **✅ Tracks Processed Emails**: Won't duplicate tasks for emails you've already processed

## Setup

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `config.json` to customize:

```json
{
  "check_interval_seconds": 60,        // How often to check for new emails (monitor mode)
  "monitor_folders": ["Inbox"],        // Which folders to monitor
  "tasks_output_file": "generated_tasks.json",
  "max_emails_per_run": 10,            // Limit for on-demand processing
  "use_ai": false,                     // Set to true to enable AI task generation
  "ai_api_key": "",                    // Your OpenAI API key (if using AI)
  "ai_model": "gpt-4o-mini"            // AI model to use
}
```

### 3. Outlook Setup

- Make sure Outlook is installed and running on your Windows machine
- No additional permissions or authentication needed

## Usage

### 🎯 Quick Start

Use the interactive launcher:

```powershell
.\quick_start.ps1
```

Choose from:
1. **Kanban Board** - Visual task management (RECOMMENDED)
2. **Monitor Mode** - Real-time background processing
3. **Process Mode** - On-demand email processing
4. **List Mode** - Text-based task list

---

### 📊 Kanban Board (Recommended)

Launch the visual Kanban board for drag-and-drop task management:

```powershell
# Option 1: Direct Python
python kanban_board_qt.py

# Option 2: Windows batch file
launch_kanban.bat

# Option 3: Via email task generator
python email_task_generator.py board
```

**Board Structure:**
- **Dynamic Groups** (rows): Start with 1 default group, add/rename/delete as needed
- **5 Columns** (workflow): Planning → In Work → Review → Done → Hand-off
- New tasks automatically appear in first group's Planning column
- Move cards between any column/group combination

**Features:**
- **Dynamic Groups**: Add, rename, delete, and customize group colors via UI
- **Move Tasks**: Click "Move" button on cards to change columns
- **Priority Colors**: 🔴 High / 🟡 Medium / 🟢 Low color-coded bars
- **Double-click**: View full task details including complete email content
- **Auto-refresh**: Load new emails directly from board menu
- **Persistent**: Saves your board layout and groups between sessions
- **Modern UI**: PyQt6-based professional interface

**Menu Options:**
- File → Refresh Tasks: Reload all tasks from file
- File → Load New Emails: Process new emails without leaving the board
- Groups → Add New Group: Create a new group with custom name and color
- Groups → Manage Groups: Rename, change colors, or delete existing groups
- Help → About: Version information

**Group Management:**
- Start with a single default group "My Tasks"
- Add unlimited groups via Groups menu
- Customize group names to fit your workflow (e.g., "Team A", "Project X", "Personal")
- Pick custom colors for each group
- Delete groups (tasks automatically move to first group)
- All changes persist automatically

---

### 🔄 Monitor Mode (Real-time)

Continuously watches for new emails and generates tasks automatically:

```powershell
python email_task_generator.py monitor
```

Press `Ctrl+C` to stop monitoring.

---

### ⚡ Process Mode (On-demand)

Process recent emails on demand:

```powershell
# Process last 10 emails from Inbox
python email_task_generator.py process

# Process last 20 emails
python email_task_generator.py process --limit 20

# Process emails from a specific folder
python email_task_generator.py process --folder "Projects"
```

---

### 📋 List Generated Tasks

View all generated tasks in terminal:

```powershell
python email_task_generator.py list
```

## Output

Tasks are saved to `generated_tasks.json` with the following information:

```json
{
  "task_title": "Review: Q4 Budget Proposal",
  "task_description": "Review and respond to email from John Smith",
  "priority": "high",
  "estimated_time": "30 min",
  "category": "Review",
  "email_subject": "Q4 Budget Proposal - Needs Review",
  "email_sender": "John Smith",
  "email_received": "2026-07-08 10:15:00",
  "generated_at": "2026-07-08T10:20:00",
  "method": "template"
}
```

## Task Categories

- **Response Required**: Emails with questions or requests
- **Review**: Documents or proposals needing review
- **Action Item**: Urgent tasks with deadlines
- **FYI**: Informational emails

## Priority Levels

- 🔴 **High**: Urgent, ASAP, Important, or high-importance emails
- 🟡 **Medium**: Standard priority
- 🟢 **Low**: FYI or informational

## Optional: AI-Powered Task Generation

For more intelligent task extraction:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Update `config.json`:
   ```json
   {
     "use_ai": true,
     "ai_api_key": "your-api-key-here",
     "ai_model": "gpt-4o-mini"
   }
   ```
3. AI will analyze email content and generate contextual tasks

## Troubleshooting

### "Failed to connect to Outlook"
- Ensure Outlook desktop application is installed
- Make sure Outlook is running
- Try restarting Outlook

### "Could not access folder"
- Check that the folder name in config matches your Outlook folder names exactly
- Default folder is "Inbox" (6 in Outlook API)

### No tasks being generated
- Check that there are unread/recent emails in the folder
- Review `processed_emails.json` to see which emails have been processed
- Delete `processed_emails.json` to reprocess emails

## Files Generated

- `generated_tasks.json`: All generated tasks
- `processed_emails.json`: Tracks which emails have been processed (prevents duplicates)
- `kanban_board_state.json`: Saves your Kanban board layout and task positions

## Additional Documentation

- **`KANBAN_CUSTOMIZATION_GUIDE.md`**: Complete guide to customizing groups, columns, colors, and logic
- **`QUICK_REFERENCE.md`**: Quick reference cheat sheet for common tasks and commands
- **`PROJECT_SUMMARY.md`**: Comprehensive project overview, architecture, and design decisions
- **`sample_output.json`**: Example of generated task data
- **`sample_console_output.txt`**: Example terminal output

## Tips

- **Start with the Kanban board** for the best visual experience
- Start with template-based generation (no API key needed)
- Use monitor mode if you want automatic task generation
- Use process mode for batch processing of recent emails
- Customize keywords in the code for better priority detection
- Adjust `check_interval_seconds` based on your email volume
- Check the customization guide to tailor the board to your workflow
