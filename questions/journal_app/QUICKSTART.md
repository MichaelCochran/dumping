# Quick Start Guide

## Installation & Setup

### Step 1: Install Dependencies

Navigate to the journal_app directory and install required packages:

```bash
cd journal_app
pip install -r requirements.txt
```

### Step 2: (Optional) Configure Claude API

If you want to use AI-generated prompts:

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your Claude API key:
   ```
   CLAUDE_API_KEY=your_actual_api_key_here
   ```

   Or skip this step and enter it when prompted in the app.

### Step 3: Run the Application

```bash
python main.py
```

## First Time Use

1. **Create Password**: You'll be prompted to create a password. This encrypts all your journal entries.
   - Choose a memorable password (minimum 4 characters)
   - Confirm the password
   - **IMPORTANT**: This password cannot be recovered!

2. **Start Journaling**: 
   - A random prompt will be displayed
   - Write your entry in the text box
   - Click "Submit" to save

## Features Overview

### Writing Entries
- Random prompts are loaded from `../prompts.txt`
- Write as much as you want (no character limit)
- Each entry is automatically encrypted before saving

### AI Prompt Generation
1. Click "Get AI Prompt" button
2. Review AI-generated prompts
3. Select one to use immediately
4. Option to save prompts to your library

### Browsing & Searching
1. Click "Open" to access the search window
2. **Search by Date**: Select a date and click Search
3. **Search by Text**: Enter keywords and click Search
4. Double-click any entry to view details

### Managing Entries
- **View**: See full entry with date and prompt
- **Edit**: Click Edit to modify entry content
- **Delete**: Remove entries (with confirmation)

## Troubleshooting

### "Failed to start application" error
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python 3.8+ is installed

### "Authentication Failed" error
- You entered the wrong password
- Database may be corrupted (restore from backup)

### API Key issues
- Verify your Claude API key is valid
- Check you have API credits available
- Re-enter the key in the app

### Missing prompts.txt
- The app will create a default file with sample prompts
- You can edit `../prompts.txt` to add custom prompts

## Tips

- Back up your `journal.db` file regularly
- Keep your `.env` file secure (contains API key)
- The `.salt` file is critical for decryption - back it up too
- Add custom prompts to `prompts.txt` (one per line)

## File Locations

- **Database**: `journal.db` (encrypted entries)
- **Prompts**: `../prompts.txt` (custom prompts)
- **Salt**: `.salt` (encryption salt)
- **Config**: `.env` (API key)

## Need Help?

Refer to the main README.md for detailed documentation.
