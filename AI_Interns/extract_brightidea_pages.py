"""
Extract content from Brightidea pages using SSO authentication
"""

import logging
import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from html import unescape
import sys

sys.path.insert(0, str(Path(__file__).parent))
from importlib.machinery import SourceFileLoader
sso = SourceFileLoader("sso", str(Path(__file__).parent / "Mike SSO")).load_module()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://lockheedmartin.brightidea.com"
SESSION_FILE = Path(__file__).parent / "brightidea_session.json"
OUTPUT_BASE = Path(__file__).parent

# List of page IDs to extract
PAGE_IDS = [
    "D27101", "D27097", "D27096", "D27093", "D27078", "D27076",
    "D27072", "D27081", "D27080", "D27089", "D27084", "D27083",
    "D27092", "D27091", "D27070", "D27067", "D27066", "D27065",
    "D27063", "D27059", "D27056", "D27053"
]


def extract_attachments(page, page_id):
    """Extract attachment information from the page"""
    attachments = []
    
    # Wait a bit more for attachments section to load
    try:
        page.wait_for_selector("img, a[href*='getfile'], .f-image-block, .f-file-block, [class*='attachment'], [class*='file']", timeout=10000)
    except:
        logging.info("No attachment elements found on page")
    
    try:
        # Look for attachment sections
        attachment_containers = page.query_selector_all(".f-images-horizontal-scroll, .f-image-block, .f-file-block")
        
        # Extract image attachments
        img_blocks = page.query_selector_all(".f-image-block")
        for block in img_blocks:
            try:
                img = block.query_selector("img")
                if img:
                    src = img.get_attribute("src")
                    alt = img.get_attribute("alt") or "image"
                    if src:
                        # Extract filename and size from hover content
                        hover = block.query_selector(".f-image-hover-content")
                        filename = alt
                        filesize = ""
                        if hover:
                            spans = hover.query_selector_all("span")
                            if len(spans) >= 1:
                                filename = spans[0].inner_text().strip() or alt
                            if len(spans) >= 2:
                                filesize = spans[1].inner_text().strip()
                        
                        attachments.append({
                            "type": "image",
                            "url": src,
                            "filename": filename,
                            "size": filesize
                        })
            except Exception as e:
                logging.warning(f"Error extracting image attachment: {e}")
        
        # Extract file attachments
        file_blocks = page.query_selector_all(".f-file-block")
        for block in file_blocks:
            try:
                link = block.query_selector("a")
                if link:
                    href = link.get_attribute("href")
                    if href:
                        spans = link.query_selector_all("span")
                        filename = "file"
                        filesize = ""
                        if len(spans) >= 1:
                            filename = spans[0].inner_text().strip()
                        if len(spans) >= 2:
                            filesize = spans[1].inner_text().strip()
                        
                        attachments.append({
                            "type": "file",
                            "url": href,
                            "filename": filename,
                            "size": filesize
                        })
            except Exception as e:
                logging.warning(f"Error extracting file attachment: {e}")
        
        # Fallback: Search for ANY links to getfile.php (file downloads)
        all_links = page.query_selector_all("a[href*='getfile.php']")
        for link in all_links:
            try:
                href = link.get_attribute("href")
                if href and href not in [a["url"] for a in attachments]:
                    # Try to extract filename from link text or generate one
                    link_text = link.inner_text().strip()
                    # Check if link text looks like a filename
                    if link_text and not link_text.startswith("http") and len(link_text) < 200:
                        filename = link_text.split('\n')[0].strip()
                    else:
                        # Try to guess from URL or use generic name
                        filename = f"file_{len(attachments) + 1}"
                        if ".pptx" in href.lower() or ".ppt" in href.lower():
                            filename += ".pptx"
                        elif ".pdf" in href.lower():
                            filename += ".pdf"
                        elif ".doc" in href.lower():
                            filename += ".docx"
                    
                    attachments.append({
                        "type": "file",
                        "url": href,
                        "filename": filename
                    })
            except Exception as e:
                logging.warning(f"Error processing link: {e}")
        
        # Fallback: Search for ANY images with getfile.php src
        all_images = page.query_selector_all("img[src*='getfile.php']")
        for img in all_images:
            try:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt") or "image"
                if src and src not in [a["url"] for a in attachments]:
                    # Skip small images (likely icons/UI elements)
                    # Try to get dimensions if possible
                    filename = alt if alt and alt != "image" else f"image_{len(attachments) + 1}.png"
                    
                    attachments.append({
                        "type": "image",
                        "url": src,
                        "filename": filename
                    })
            except Exception as e:
                logging.warning(f"Error processing image: {e}")
        
        if attachments:
            logging.info(f"Found {len(attachments)} attachments")
        else:
            logging.info("No attachments found on this page")
        
    except Exception as e:
        logging.warning(f"Error extracting attachments: {e}")
    
    return attachments


def download_attachments(page, attachments, page_folder):
    """Download all attachments to the page folder"""
    if not attachments:
        return
    
    # Create attachments subfolder
    attachments_folder = page_folder / "attachments"
    attachments_folder.mkdir(exist_ok=True)
    
    downloaded = 0
    skipped = 0
    for i, attachment in enumerate(attachments, 1):
        try:
            url = attachment["url"]
            filename = attachment["filename"]
            file_path = attachments_folder / filename
            
            # Check if file already exists
            if file_path.exists():
                existing_size = file_path.stat().st_size
                # If we have size info from metadata, compare it
                expected_size_str = attachment.get("size", "")
                
                # Try to parse size if available (e.g., "1.10MB" -> bytes)
                should_skip = False
                if expected_size_str and existing_size > 0:
                    # If file exists and has content, likely already downloaded
                    should_skip = True
                elif existing_size > 1000:  # If > 1KB, probably valid
                    should_skip = True
                
                if should_skip:
                    logging.info(f"  Skipping [{i}/{len(attachments)}]: {filename} (already exists, {existing_size:,} bytes)")
                    skipped += 1
                    continue
            
            # Make URL absolute if needed
            if not url.startswith("http"):
                url = urljoin(BASE_URL, url)
            
            logging.info(f"  Downloading [{i}/{len(attachments)}]: {filename}")
            
            # Use page context to download with authentication (60 second timeout)
            response = page.request.get(url, timeout=60000)
            
            if response.ok:
                with open(file_path, "wb") as f:
                    f.write(response.body())
                file_size = file_path.stat().st_size
                logging.info(f"    Saved to {file_path} ({file_size:,} bytes)")
                downloaded += 1
            else:
                logging.warning(f"    Failed to download (HTTP {response.status})")
        
        except Exception as e:
            logging.error(f"    Error downloading {attachment.get('filename', 'file')}: {e}")
    
    if skipped > 0:
        logging.info(f"Downloaded {downloaded}/{len(attachments)} attachments (skipped {skipped} already present)")
    else:
        logging.info(f"Downloaded {downloaded}/{len(attachments)} attachments")


def strip_html_to_text(html_content):
    """Strip HTML tags and convert to clean text/markdown"""
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert common HTML elements to markdown-ish format
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n#### \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '\n- ', text, flags=re.IGNORECASE)
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = unescape(text)
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple blank lines to double
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single
    text = text.strip()
    
    return text


def extract_page_content(page, page_id):
    """Extract all relevant content from a Brightidea page"""
    logging.info(f"Extracting content from {page_id}...")
    
    content = {
        "page_id": page_id,
        "url": f"{BASE_URL}/{page_id}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": "",
        "description": "",
        "metadata": {},
        "full_text": "",
        "html_content": "",
        "attachments": []
    }
    
    try:
        # Wait for page to load - React app takes time
        page.wait_for_load_state("networkidle", timeout=45000)
        
        # Wait for the main content container
        try:
            page.wait_for_selector(".fractal-idea-page, #view-idea-3-container", timeout=15000)
        except:
            logging.warning("Main content container not found")
        
        # Additional wait for React to render everything
        time.sleep(5)
        
        # Extract title
        try:
            title = page.title()
            content["title"] = title
        except Exception as e:
            logging.warning(f"Could not extract title: {e}")
        
        # Extract all text content
        try:
            text_content = page.inner_text("body")
            content["full_text"] = text_content
        except Exception as e:
            logging.warning(f"Could not extract text: {e}")
        
        # Extract HTML content
        try:
            html_content = page.content()
            content["html_content"] = html_content
        except Exception as e:
            logging.warning(f"Could not extract HTML: {e}")
        
        # Extract attachments
        try:
            attachments = extract_attachments(page, page_id)
            content["attachments"] = attachments
        except Exception as e:
            logging.warning(f"Could not extract attachments: {e}")
        
        # Extract specific elements if they exist
        selectors = {
            "idea_title": [".idea-title", "h1", ".project-title"],
            "description": [".description", ".idea-description", ".project-description"],
            "author": [".author", ".created-by", ".submitted-by"],
            "date": [".date", ".submitted-date", ".created-date"],
            "status": [".status", ".idea-status"],
            "tags": [".tags", ".tag", ".label"],
            "comments": [".comment", ".comments", ".discussion"],
            "attachments": [".attachment", ".attachments", ".file"],
        }
        
        for key, selector_list in selectors.items():
            for selector in selector_list:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        content["metadata"][key] = [el.inner_text() for el in elements]
                        break
                except Exception:
                    continue
        
        logging.info(f"Successfully extracted content from {page_id}")
        return content
        
    except Exception as e:
        logging.error(f"Error extracting content from {page_id}: {e}")
        return content


def save_page_content(content, page_id):
    """Save extracted content to a dedicated folder"""
    # Create folder for this page
    page_folder = OUTPUT_BASE / page_id
    page_folder.mkdir(exist_ok=True)
    
    # Save JSON data
    json_file = page_folder / "content.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved JSON to {json_file}")
    
    # Save full text
    text_file = page_folder / "full_text.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(content.get("full_text", ""))
    logging.info(f"Saved text to {text_file}")
    
    # Save stripped/cleaned text as markdown
    if content.get("html_content"):
        clean_text = strip_html_to_text(content["html_content"])
        md_file = page_folder / "content.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# {content.get('title', page_id)}\n\n")
            f.write(f"**URL:** {content.get('url', '')}\n\n")
            f.write(f"**Extracted:** {content.get('timestamp', '')}\n\n")
            f.write("---\n\n")
            f.write(clean_text)
        logging.info(f"Saved cleaned text to {md_file}")
    
    # Save HTML
    html_file = page_folder / "page.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content.get("html_content", ""))
    logging.info(f"Saved HTML to {html_file}")
    
    # Save metadata
    if content.get("metadata"):
        metadata_file = page_folder / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(content["metadata"], f, indent=2, ensure_ascii=False)
        logging.info(f"Saved metadata to {metadata_file}")
    
    return page_folder


def main():
    """Main extraction workflow"""
    logging.info("Starting Brightidea content extraction")
    logging.info(f"Will extract {len(PAGE_IDS)} pages")
    
    with sync_playwright() as p:
        # Check if we have a valid session
        test_url = f"{BASE_URL}/{PAGE_IDS[0]}"
        
        if not sso.check_session_valid(p, SESSION_FILE, test_url):
            logging.info("No valid session found. Authentication required.")
            if not sso.authenticate(p, SESSION_FILE, test_url):
                logging.error("Authentication failed. Exiting.")
                return
        
        # Launch browser with saved session
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            ignore_https_errors=True  # Handle self-signed certificates
        )
        page = context.new_page()
        
        # Extract content from each page
        successful = 0
        failed = 0
        
        for i, page_id in enumerate(PAGE_IDS, 1):
            logging.info(f"\n[{i}/{len(PAGE_IDS)}] Processing {page_id}...")
            
            try:
                url = f"{BASE_URL}/{page_id}"
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Check if we got redirected to login
                if sso.is_login_page(page.url):
                    logging.error("Session expired during extraction. Please re-run the script.")
                    break
                
                # Extract and save content
                content = extract_page_content(page, page_id)
                page_folder = save_page_content(content, page_id)
                
                # Download attachments
                if content.get("attachments"):
                    download_attachments(page, content["attachments"], page_folder)
                
                successful += 1
                
                # Brief pause between requests
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Failed to process {page_id}: {e}")
                failed += 1
                continue
        
        browser.close()
        
        # Summary
        logging.info("\n" + "="*70)
        logging.info(f"Extraction complete!")
        logging.info(f"Successful: {successful}/{len(PAGE_IDS)}")
        logging.info(f"Failed: {failed}/{len(PAGE_IDS)}")
        logging.info(f"Output location: {OUTPUT_BASE}")
        logging.info("="*70)


if __name__ == "__main__":
    main()
