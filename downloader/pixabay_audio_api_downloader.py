import os
import time
import requests
from urllib.parse import urlparse

API_KEY = "56514438-161014f2f8318de3b8a332a34"
SEARCH_QUERY = "8-bit"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

PER_PAGE = 20
MAX_PAGES = None

def download_file(url, filename):
    try:
        print(f"  Downloading: {filename}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath) / 1024 / 1024
        print(f"  ✓ Downloaded: {filename} ({file_size:.2f} MB)")
        return True
    except Exception as e:
        print(f"  ✗ Failed to download {filename}: {e}")
        return False

def search_music(query, page=1, per_page=20):
    url = "https://pixabay.com/api/"
    
    params = {
        'key': API_KEY,
        'q': query,
        'media_type': 'music',
        'page': page,
        'per_page': per_page
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error searching Pixabay API: {e}")
        return None

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '-')
    return filename[:200]

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("=" * 60)
        print("ERROR: Please set your Pixabay API key!")
        print("=" * 60)
        print("\nTo get your API key:")
        print("1. Go to: https://pixabay.com/api/docs/")
        print("2. Sign up or log in to your Pixabay account")
        print("3. Your API key will be displayed on the docs page")
        print("4. Copy the API key and paste it in this script")
        print(f"5. Edit line 6 of this file: API_KEY = 'your_key_here'")
        print("\nAlternatively, set it as an environment variable: PIXABAY_API_KEY")
        return
    
    print(f"Searching Pixabay for: {SEARCH_QUERY}")
    print(f"Results per page: {PER_PAGE}")
    print("=" * 60)
    
    page = 1
    total_downloaded = 0
    
    while True:
        print(f"\n{'='*60}")
        print(f"Page {page}")
        print(f"{'='*60}")
        
        data = search_music(SEARCH_QUERY, page=page, per_page=PER_PAGE)
        
        if not data:
            print("Failed to fetch data from API")
            break
        
        total_hits = data.get('total', 0)
        hits = data.get('hits', [])
        
        print(f"Total results available: {total_hits}")
        print(f"Results on this page: {len(hits)}")
        
        if not hits:
            print("\nNo more results. Download complete!")
            break
        
        for idx, track in enumerate(hits, 1):
            track_id = track.get('id', 'unknown')
            track_name = track.get('tags', f'track_{track_id}')
            duration = track.get('duration', 0)
            
            download_url = track.get('audio', {}).get('url')
            if not download_url:
                print(f"[{idx}/{len(hits)}] No download URL for: {track_name}")
                continue
            
            ext = 'mp3'
            parsed_url = urlparse(download_url)
            if parsed_url.path:
                file_ext = os.path.splitext(parsed_url.path)[1]
                if file_ext:
                    ext = file_ext.lstrip('.')
            
            safe_name = sanitize_filename(track_name)
            filename = f"{safe_name}_{track_id}.{ext}"
            
            print(f"\n[{idx}/{len(hits)}] {track_name} (ID: {track_id}, {duration}s)")
            
            if download_file(download_url, filename):
                total_downloaded += 1
            
            time.sleep(1)
        
        print(f"\n✓ Finished page {page}")
        print(f"Total tracks downloaded so far: {total_downloaded}")
        
        if MAX_PAGES and page >= MAX_PAGES:
            print(f"\nReached maximum page limit ({MAX_PAGES})")
            break
        
        if len(hits) < PER_PAGE:
            print("\nNo more pages available. Download complete!")
            break
        
        print("\nWaiting 30 seconds before fetching next page...")
        time.sleep(30)
        
        page += 1
    
    print("\n" + "=" * 60)
    print(f"Download Complete!")
    print(f"Total tracks downloaded: {total_downloaded}")
    print(f"Files saved to: {DOWNLOAD_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    api_key_env = os.environ.get('PIXABAY_API_KEY')
    if api_key_env:
        API_KEY = api_key_env
        print("Using API key from environment variable")
    
    main()
