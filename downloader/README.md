# Pixabay Audio Downloader

Two methods to download audio files from Pixabay:

## Method 1: API-Based Downloader (Recommended) ⭐

Uses Pixabay's official API for reliable, legal downloads.

### Requirements
- Python 3.7+
- Pixabay API key (free)

### Setup

1. Install dependencies:
```bash
pip install requests
```

2. Get your API key:
   - Visit https://pixabay.com/api/docs/
   - Sign up or log in
   - Copy your API key from the docs page

3. Set your API key (choose one method):
   - **Option A**: Edit `pixabay_audio_api_downloader.py` line 6:
     ```python
     API_KEY = "your_actual_api_key_here"
     ```
   - **Option B**: Set environment variable:
     ```bash
     $env:PIXABAY_API_KEY="your_actual_api_key_here"
     ```

### Usage

```bash
python pixabay_audio_api_downloader.py
```

### Configuration

Edit these variables in the script:
- `SEARCH_QUERY`: What to search for (default: "8-bit")
- `PER_PAGE`: Results per page (default: 20, max: 200)
- `MAX_PAGES`: Maximum pages to download (default: None for all)

### How it works

1. Searches Pixabay API for music matching your query
2. Downloads all audio files from the current page
3. Waits 30 seconds (respects API rate limits)
4. Fetches the next page
5. Repeats until all results are downloaded

---

## Method 2: Web Scraper (Browser-Based)

Uses Selenium to automate browser interaction.

### Requirements
- Python 3.7+
- Chrome or Edge browser
- ChromeDriver (automatically managed by Selenium 4.x)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

```bash
python pixabay_audio_downloader.py
```

### Notes
- May be blocked by Pixabay's bot detection
- API method is more reliable

---

## General Notes

- Downloaded files are saved to a `downloads` folder
- Press Ctrl+C to stop either script at any time
- Both scripts include 30-second delays between page/API requests
- Files are named with track titles and IDs for easy identification
