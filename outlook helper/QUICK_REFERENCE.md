# Quick Reference Guide

## 🚀 Getting Started (3 Steps)

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Process your emails:**
   ```powershell
   python email_task_generator.py process --limit 10
   ```

3. **Launch Kanban board:**
   ```powershell
   python kanban_board_qt.py
   ```

---

## 📊 Kanban Board Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  File   Groups   Help                                Kanban Board          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┬────────────┬────────────┬────────────┬────────────┬────────────┐ │
│  │  My Tasks  │  Planning  │  In Work   │   Review   │    Done    │  Hand-off  │ │
│  ├───────────┼────────────┼────────────┼────────────┼────────────┼────────────┤ │
│  │           │            │            │            │            │            │ │
│  │           │ ┌────────┐ │ ┌────────┐ │            │ ┌────────┐ │            │ │
│  │           │ │Task A  │ │ │Task C  │ │            │ │Task F  │ │            │ │
│  │           │ │[Move →]│ │ │[Move →]│ │            │ │[Move →]│ │            │ │
│  │           │ └────────┘ │ └────────┘ │            │ └────────┘ │            │ │
│  │           │            │            │            │            │            │ │
│  └───────────┴────────────┴────────────┴────────────┴────────────┴────────────┘ │
│                                                                              │
│  (Use Groups menu to add/rename/delete/customize groups)                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Task Card Example

```
┌─────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │ ← Priority Color Bar (Red/Orange/Green)
├─────────────────────────────────┤
│                                 │
│ Review: Q4 Budget Proposal      │ ← Task Title (bold)
│                                 │
│ 📌 Review                       │ ← Category Badge
│                                 │
│ From: Sarah Johnson             │ ← Email Sender
│                                 │
│ ⏱ 30 min                        │ ← Estimated Time
│                                 │
└─────────────────────────────────┘
```

**Interactions:**
- **Click "Move →"** → Menu to move to different column
- **Double-Click** → View full details
- **Groups Menu** → Add/rename/delete/customize groups

---

## ⌨️ Common Commands

### Email Processing
```powershell
# Process 10 most recent emails
python email_task_generator.py process

# Process 20 emails
python email_task_generator.py process --limit 20

# Monitor inbox continuously
python email_task_generator.py monitor

# View tasks in terminal
python email_task_generator.py list
```

### Kanban Board
```powershell
# Launch Qt board
python kanban_board_qt.py

# Or use quick start
.\quick_start.ps1

# Or use batch file
launch_kanban.bat
```

---

## 🎨 Customization Quick Links

### Add a New Group
**Via UI:** Groups → Add New Group
1. Enter group name
2. Pick a color
3. Done! Group appears immediately

### Rename/Delete/Change Color
**Via UI:** Groups → Manage Groups
1. Select a group from the list
2. Click Rename, Change Color, or Delete
3. Changes apply immediately

### Add a New Column
**File:** `kanban_board_qt.py`  
**Line:** ~16 (COLUMNS list)

```python
COLUMNS = [
    {"name": "Planning", "color": "#95A5A6"},
    {"name": "Blocked", "color": "#E74C3C"},  # Add this
    {"name": "In Work", "color": "#F39C12"},
    # ... rest of columns
]
```

### Adjust Card/Column Size
**File:** `kanban_board_qt.py`  
**Line:** ~32 (Card sizing)

```python
CARD_WIDTH = 250        # Change this (e.g., 200, 280)
COLUMN_PADDING = 5      # Spacing around cards
```

---

## 📋 Workflow Examples

### Daily Email Review Workflow
1. **Morning:** Run `python email_task_generator.py process --limit 20`
2. **Open Board:** Launch `python kanban_board_qt.py`
3. **Organize:** Use Move button to move tasks to appropriate columns
4. **Work:** Move tasks through workflow as you complete them
5. **Evening:** Review Done column, move completed items to Hand-off

### Continuous Monitoring Workflow
1. **Start Monitor:** Run `python email_task_generator.py monitor` in background
2. **Keep Board Open:** Run `python kanban_board_qt.py`
3. **Load New Emails:** Use File → Load New Emails menu
4. **Organize:** New tasks appear in first group's Planning column automatically

---

## 🎯 Priority Color Guide

| Color  | Priority | When Used |
|--------|----------|-----------|
| 🔴 Red | High | "Urgent", "ASAP", "Important" in subject |
| 🟡 Orange | Medium | Standard emails, default |
| 🟢 Green | Low | FYI, informational emails |

---

## 📁 File Structure

```
outlook helper/
├── email_task_generator.py      # Main email processor
├── kanban_board_qt.py            # Visual Kanban board (PyQt6)
├── config.json                   # Configuration settings
├── requirements.txt              # Python dependencies
├── quick_start.ps1               # Interactive launcher
├── launch_kanban.bat             # Windows batch launcher
├── README.md                     # Full documentation
├── PROJECT_SUMMARY.md            # Project architecture
├── QUICK_REFERENCE.md            # This file
│
└── Generated Files (auto-created):
    ├── generated_tasks.json      # All task data
    ├── processed_emails.json     # Email tracking
    └── kanban_board_state.json   # Board layout + groups config
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Board is empty | Run `python email_task_generator.py process` first |
| Can't connect to Outlook | Make sure Outlook desktop app is running |
| Tasks not moving | Click and drag (not just click) |
| Want to reset board | Delete `kanban_board_state.json` |
| Duplicate tasks | Already tracked in `processed_emails.json` |

---

## 💡 Pro Tips

1. **Use Monitor + Board Together:** Run monitor in one terminal, board in another for real-time updates
2. **Customize Groups by Project:** Edit GROUPS to match your team structure
3. **Add Columns for Your Workflow:** Not using Hand-off? Remove it and add what you need
4. **Keyboard Focus:** While board is focused, use Tab to cycle through clickable elements
5. **File Menu Shortcuts:** Use File → Load New Emails to process without leaving the board
6. **Double-Click for Details:** Full email content and metadata in popup
7. **Color Code Your Way:** Change priority colors to match your preferences

---

## 📞 Need More Help?

- **Full Documentation:** See `README.md`
- **Customization:** See `KANBAN_CUSTOMIZATION_GUIDE.md`
- **Sample Output:** See `sample_output.json` and `sample_console_output.txt`

---

**Last Updated:** Created with Outlook Email Task Generator v1.0
