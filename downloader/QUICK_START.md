# Quick Start Guide - Pixabay Audio Downloader

## Step 1: Get Your API Key

1. Visit: https://pixabay.com/api/docs/
2. Sign up or log in to Pixabay
3. Your API key will be shown on the page
4. Copy the key

## Step 2: Set Your API Key

Open `pixabay_audio_api_downloader.py` and change line 6:

```python
API_KEY = "your_api_key_goes_here"
```

## Step 3: Customize Search (Optional)

Edit these settings in the script:

```python
SEARCH_QUERY = "8-bit"      # Change to search for different music
PER_PAGE = 20               # How many per page (max 200)
MAX_PAGES = None            # Set to a number to limit pages, or None for all
```

## Step 4: Run the Script

```bash
python pixabay_audio_api_downloader.py
```

## What Happens

- Downloads all 8-bit music from Pixabay
- Creates a `downloads` folder with all files
- Waits 30 seconds between pages
- Shows progress for each download
- Files named like: `8-bit-chiptune-music_12345.mp3`

## Stop the Script

Press `Ctrl+C` at any time to stop downloading.

## Troubleshooting

**"ERROR: Please set your Pixabay API key!"**
- You need to edit line 6 of the script with your actual API key

**"Failed to fetch data from API"**
- Check your internet connection
- Verify your API key is correct
- Check if you've exceeded API rate limits (5000 requests/hour for free accounts)

**"No download URL for: [track name]"**
- Some tracks may not have downloadable files
- This is normal, the script will skip them

## API Limits

Free Pixabay API accounts have:
- 5,000 requests per hour
- Each page = 1 request
- With 20 results per page, you can download 100,000 results per hour

That's plenty for most use cases!
