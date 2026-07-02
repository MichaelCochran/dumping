import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, unquote

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_file(url, filename):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def get_audio_links(driver):
    audio_links = []
    try:
        time.sleep(2)
        
        audio_elements = driver.find_elements(By.CSS_SELECTOR, "audio source, audio")
        print(f"Found {len(audio_elements)} audio elements")
        
        for idx, audio in enumerate(audio_elements):
            try:
                audio_url = audio.get_attribute('src')
                if not audio_url:
                    continue
                
                try:
                    parent = audio.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@class, 'container') or contains(@class, 'card')]")
                    title_elem = parent.find_element(By.CSS_SELECTOR, "a[href*='/music/'], h2, h3, [class*='title']")
                    title = title_elem.get_attribute('title') or title_elem.text or f"audio_{idx}"
                except:
                    title = f"audio_{idx}"
                
                audio_id = audio_url.split('/')[-1].split('.')[0] if '/' in audio_url else str(idx)
                safe_title = title.replace('/', '-').replace('\\', '-').replace(':', '-')[:50].strip()
                if not safe_title:
                    safe_title = f"audio_{idx}"
                
                ext = 'mp3'
                if '.' in audio_url:
                    ext = audio_url.split('.')[-1].split('?')[0]
                
                filename = f"{safe_title}_{audio_id}.{ext}"
                
                audio_links.append((audio_url, filename))
                print(f"  [{idx+1}] {safe_title}")
            except Exception as e:
                print(f"Error processing audio {idx}: {e}")
                continue
        
        if not audio_links:
            print("Trying alternative method: looking for download buttons...")
            download_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='ownload'], a[aria-label*='ownload']")
            print(f"Found {len(download_buttons)} download buttons")
            
            for idx, button in enumerate(download_buttons):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.5)
                    button.click()
                    time.sleep(2)
                    
                    new_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='.mp3'], a[download]")
                    for link in new_links:
                        url = link.get_attribute('href')
                        if url and ('.mp3' in url or '.wav' in url):
                            filename = f"audio_{idx}.mp3"
                            audio_links.append((url, filename))
                            break
                except:
                    continue
                    
    except Exception as e:
        print(f"Error finding audio links: {e}")
        import traceback
        traceback.print_exc()
    
    return audio_links

def has_next_button(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
        return next_button.is_displayed() and next_button.is_enabled()
    except NoSuchElementException:
        return False

def click_next_button(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[aria-label='Next']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(1)
        next_button.click()
        return True
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Could not click next button: {e}")
        return False

def main():
    url = "https://pixabay.com/music/search/8-bit/"
    
    driver = None
    
    print("Attempting to start browser...")
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✓ Using Chrome browser")
    except Exception as e:
        print(f"Chrome not available: {e}")
        print("Trying Edge browser...")
        try:
            options = webdriver.EdgeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            driver = webdriver.Edge(options=options)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'})
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✓ Using Edge browser")
        except Exception as e2:
            print(f"Edge not available: {e2}")
            print("\nERROR: No compatible browser found.")
            print("Please ensure Chrome or Edge is installed.")
            return
    
    try:
        print(f"Navigating to: {url}")
        driver.get(url)
        
        print("Waiting for page to load...")
        time.sleep(10)
        
        print("Scrolling to load content...")
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/5 * " + str(i+1) + ");")
            time.sleep(3)
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        print("Saving page source for debugging...")
        with open("downloads/page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to downloads/page_source.html")
        
        page_number = 1
        
        while True:
            print(f"\n{'='*60}")
            print(f"Processing page {page_number}")
            print(f"{'='*60}")
            
            audio_links = get_audio_links(driver)
            
            if not audio_links:
                print("No audio links found on this page")
                break
            
            print(f"Found {len(audio_links)} audio files on page {page_number}")
            
            for i, (download_url, filename) in enumerate(audio_links, 1):
                print(f"[{i}/{len(audio_links)}] Downloading: {filename}")
                download_file(download_url, filename)
                time.sleep(1)
            
            print(f"\nFinished downloading page {page_number}. Waiting 30 seconds...")
            time.sleep(30)
            
            if has_next_button(driver):
                print("Clicking next button...")
                if click_next_button(driver):
                    print("Waiting 30 seconds before processing next page...")
                    time.sleep(30)
                    page_number += 1
                else:
                    print("Failed to click next button. Stopping.")
                    break
            else:
                print("\nNo more pages. Download complete!")
                break
                
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            driver.quit()
        print(f"\nAll downloads saved to: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()
