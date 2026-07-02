# Personal Journal Application

A secure, encrypted journaling application with AI-powered prompt generation using Claude API.

## Features

- **Encrypted Storage**: All entries are encrypted using Fernet symmetric encryption with PBKDF2 key derivation
- **Password Protection**: Secure your journal with a password/PIN
- **Prompt-Based Journaling**: Random prompts from your custom list guide your writing
- **AI Prompt Generation**: Use Claude API to generate thoughtful, unique prompts
- **Search & Browse**: Search entries by date or text content
- **Entry Management**: View, edit, and delete entries with a clean interface
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up Claude API key:
   - Copy `.env.example` to `.env`
   - Add your Claude API key to `.env`
   - Or enter it when prompted in the application

## Usage

Run the application:
```bash
python main.py
```

### First Time Setup
1. The app will prompt you to create a password
2. This password encrypts all your journal entries
3. **Important**: Remember this password - it cannot be recovered!

### Daily Use
1. Enter your password to access the journal
2. Write your entry based on the random prompt
3. Click "Submit" to save
4. Click "Open" to search and browse previous entries

### AI Prompt Generation
1. Click "Get AI Prompt" button
2. Enter your Claude API key if not configured
3. Review generated prompts and select one to use
4. Optionally save prompts to your library for future use

## Project Structure

```
journal_app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── ui/                    # User interface components
│   ├── main_window.py     # Main journal entry window
│   ├── search_window.py   # Search and browse interface
│   ├── detail_window.py   # Entry detail/edit window
│   ├── auth_dialog.py     # Password authentication
│   └── prompt_selection_dialog.py  # AI prompt selection
├── database/              # Database and encryption
│   ├── db_manager.py      # Database operations
│   └── encryption.py      # Encryption/decryption
├── utils/                 # Utility modules
│   ├── prompts.py         # Prompt management
│   └── claude_api.py      # Claude API integration
└── config/                # Configuration management
    └── settings.py        # Application settings
```

## Security Notes

- Your password is never stored - only a salt for key derivation
- All journal entries are encrypted before being saved to the database
- The encryption key exists only in memory during runtime
- Claude API key is stored in `.env` file (keep it secure)
- Database file (`journal.db`) contains only encrypted data

## Customizing Prompts

Edit the `prompts.txt` file (located in the parent directory) to add your own prompts. Each prompt should be on a new line.

## Troubleshooting

**Forgot Password**: Unfortunately, there's no password recovery. Your entries are encrypted with your password and cannot be accessed without it.

**API Key Issues**: Ensure your Claude API key is valid and has sufficient credits. You can update it through the application interface.

**Database Errors**: If you suspect database corruption, back up your `journal.db` file and contact support.

## License

This is a personal project. Use at your own discretion.
