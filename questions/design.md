# Journal GUI Application - Design Document

## Overview
A personal journaling application with encrypted storage, prompt-based journaling, and search/retrieval capabilities. The application runs locally on Windows, Linux, or macOS.

## Tech Stack
- **GUI Framework**: PyQt5/PyQt6
- **Database**: SQLite with encryption (SQLCipher or custom encryption layer)
- **Language**: Python 3.8+
- **Encryption**: cryptography library (Fernet symmetric encryption)
- **Password Protection**: PBKDF2 key derivation from user PIN/password

## Core Features

### 1. Main Window (Journal Entry)
- Text input field (multi-line QTextEdit)
- Random prompt display from `prompts.txt`
- "Get AI Prompt" button to query Claude for new prompts
- Submit button to save entry
- Open button to access search/view interface

### 2. Search Window
- Search by date (QDateEdit calendar widget)
- Search by text/prompt (QLineEdit search field)
- Results displayed in list view (QListWidget)
- Double-click or select entry to open in detail window

### 3. Entry Detail Window
- Display full entry content
- Show date and prompt
- Edit button (enables editing mode)
- Delete button (with confirmation dialog)
- Save button (visible in edit mode)
- Close button

### 4. Authentication
- PIN/password entry on application startup
- First-time setup creates new encrypted database
- Failed authentication prevents access to database

### 5. AI Prompt Generation
- Button to request new prompts from Claude API
- Generated prompts can be added to `prompts.txt`
- User can choose to use generated prompt immediately or save for later
- Optional: Batch generate multiple prompts at once

## Architecture

### Application Structure
```
journal_app/
├── main.py                 # Application entry point
├── ui/
│   ├── main_window.py     # Main journal entry window
│   ├── search_window.py   # Search and browse window
│   ├── detail_window.py   # Entry detail/edit window
│   └── auth_dialog.py     # Password/PIN authentication
├── database/
│   ├── db_manager.py      # Database operations
│   └── encryption.py      # Encryption/decryption logic
├── utils/
│   ├── prompts.py         # Prompt loading and selection
│   └── claude_api.py      # Claude API integration
├── config/
│   └── settings.py        # Configuration and API key management
├── journal.db             # Encrypted SQLite database (created at runtime)
├── prompts.txt            # User-defined prompts
└── .env                   # API keys (gitignored)
```

### Database Schema

#### Table: entries
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique entry identifier |
| date | DATETIME | Entry creation timestamp |
| prompt | TEXT | The prompt shown to user |
| content | TEXT | User's journal entry |
| created_at | DATETIME | Record creation time |
| updated_at | DATETIME | Last modification time |

### Encryption Approach
1. **Password Derivation**: Use PBKDF2 to derive encryption key from user PIN/password
2. **Database Encryption**: 
   - Option A: Use SQLCipher for full database encryption
   - Option B: Use standard SQLite with encrypted BLOB storage for content
3. **Key Storage**: Encryption key exists only in memory during runtime
4. **Salt Storage**: Store salt in application config file for key derivation

## User Interface Design

### Main Window Layout
```
┌─────────────────────────────────────────┐
│  Journal Entry                     [×]  │
├─────────────────────────────────────────┤
│                                         │
│  Today's Prompt:        [Get AI Prompt] │
│  [Random prompt displayed here...]      │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │  [Text Entry Area]                │  │
│  │                                   │  │
│  │                                   │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│         [Submit]        [Open]          │
└─────────────────────────────────────────┘
```

### Search Window Layout
```
┌─────────────────────────────────────────┐
│  Browse Entries                    [×]  │
├─────────────────────────────────────────┤
│  Search by Date: [📅]  [Search]         │
│  Search by Text: [________]  [Search]   │
├─────────────────────────────────────────┤
│  Results:                               │
│  ┌───────────────────────────────────┐  │
│  │ • 2026-07-01 - Prompt: What...    │  │
│  │ • 2026-06-30 - Prompt: Describe...│  │
│  │ • 2026-06-29 - Prompt: How did... │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                        [Close]          │
└─────────────────────────────────────────┘
```

### Entry Detail Window Layout
```
┌─────────────────────────────────────────┐
│  Entry Details                     [×]  │
├─────────────────────────────────────────┤
│  Date: July 1, 2026, 8:00 AM            │
│  Prompt: What are you grateful for?     │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │  [Entry content displayed here]   │  │
│  │  [Read-only by default]           │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [Edit]  [Delete]           [Close]     │
└─────────────────────────────────────────┘
```

## Implementation Details

### Startup Flow
1. Application launches
2. Check if database exists
   - If no: Show setup dialog (create PIN/password)
   - If yes: Show authentication dialog
3. Derive encryption key from PIN/password
4. Attempt to open/decrypt database
5. If successful: Show main window
6. If failed: Show error and retry authentication

### Journal Entry Flow
1. On window load, randomly select prompt from `prompts.txt`
2. User writes entry in text field
3. On Submit:
   - Capture current timestamp
   - Save entry with prompt, content, and timestamp
   - Encrypt and store in database
   - Clear text field and load new random prompt
   - Show success notification

### Search Flow
1. User opens search window
2. **Date Search**:
   - User selects date from calendar
   - Query all entries matching that date
   - Display in list view
3. **Text Search**:
   - User enters search terms
   - Query entries where content OR prompt contains search terms
   - Display in list view
4. User selects entry → Opens detail window

### Entry Management
- **View**: Display in read-only mode
- **Edit**: 
  - Enable text editing
  - Update `updated_at` timestamp on save
  - Re-encrypt and update database
- **Delete**:
  - Show confirmation dialog
  - Remove from database if confirmed
  - Close detail window and refresh search results

### AI Prompt Generation Flow
1. User clicks "Get AI Prompt" button
2. Check if Claude API key is configured
   - If no: Prompt user to enter API key in settings
   - If yes: Proceed to API call
3. Load existing prompts from `prompts.txt` into memory
4. Make API request to Claude with prompt engineering:
   - Request: "Generate thoughtful journaling prompts for personal reflection and deep introspection"
   - Receive multiple prompts from Claude
5. Filter generated prompts for uniqueness:
   - Compare against existing prompts (case-insensitive, trimmed)
   - Only keep prompts that don't already exist
   - If all generated prompts are duplicates, request new batch from Claude
6. Display unique prompts in selection dialog
7. User can:
   - Select a prompt to use immediately (replaces current prompt)
   - Add selected prompts to `prompts.txt` for future use (automatically appended)
   - Cancel and keep current prompt

## Security Considerations
- Encryption key never written to disk
- Application locks/closes on inactivity (optional feature)
- Secure memory clearing of password variables
- No plaintext storage of entries
- Database file permissions restricted to owner
- Claude API key stored in `.env` file (not committed to version control)
- API key encrypted at rest using same encryption as database (optional enhancement)

## Text Input Constraints
- No artificial character limit on text input
- SQLite TEXT type supports up to ~2GB per field
- Practical limit: Warn if entry exceeds 1MB (optional)

## Dependencies
```
PyQt5>=5.15.0 or PyQt6>=6.0.0
cryptography>=41.0.0
anthropic>=0.21.0
python-dotenv>=1.0.0
```

## Future Enhancements (Optional)
- Export entries to PDF/text
- Backup/restore functionality
- Entry tagging system
- Mood tracking
- Statistics dashboard
- Dark mode theme
- Multi-language support
