#!/usr/bin/env python3
import os
import json
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from pathlib import Path
from urllib.parse import urlparse

# ------------------ CONFIG ------------------
BASE_URL_TEMPLATE = "https://oshoworld.com/osho-asambhav_kranti_%02d"  # %02d for zero-padded page numbers
MAX_PAGE = 10 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ------------------ HELPERS ------------------

def extract_mp3_link(html, base_url):
    """
    Parses the Next.js __NEXT_DATA__ script block to reliably extract the audio file URL.
    """
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    
    if script_tag and script_tag.string:
        try:
            data = json.loads(script_tag.string)
            # Drill down into the specific Next.js JSON path to locate the audio file
            audio_file = data["props"]["pageProps"]["data"]["pageData"]["audioData"]["audioFile"]
            
            if audio_file:
                # Construct the full download URL
                full_url = requests.compat.urljoin(base_url, audio_file)
                # Decode the URL (e.g., %20 to space) and extract the exact filename
                filename = os.path.basename(urllib.parse.unquote(audio_file))
                return full_url, filename
        except (KeyError, TypeError, json.JSONDecodeError):
            pass # Fails gracefully if the expected JSON schema is altered or missing

    return None, None

def download_file(url, dest_path, filename):
    resp = requests.get(url, headers=HEADERS, stream=True, verify=False)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))

    with open(dest_path, "wb") as file, tqdm(
        desc=filename,
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            size = file.write(chunk)
            bar.update(size)

def create_folder_from_url():
    # 1. Ensure a URL was passed as a CLI argument
    if len(sys.argv) < 2:
        print("Error: Please provide a URL as a command-line argument.")
        sys.exit(1)

    url = sys.argv[1]

    try:
        # 2. Parse the URL
        parsed_url = urlparse(url)

        # 3. Extract and clean the path
        # .strip('/') removes leading/trailing slashes so we only get 'ajhun-chet-ganwar'
        folder_name = parsed_url.path.strip("/")

        # Check if the path actually contained a folder name
        if not folder_name:
            print("Error: Could not extract a valid folder name from the URL.")
            sys.exit(1)

        # 4. Create the folder
        # parents=True creates any missing parent directories
        # exist_ok=True prevents an error if the folder already exists
        folder_path = Path(folder_name)
        folder_path.mkdir(parents=True, exist_ok=True)

        print(f"Success: Folder '{folder_path.resolve()}' created.")
        return (folder_name, folder_path)

    except Exception as e:
        print(f"An error occurred: {e}")

# ------------------ MAIN ------------------
def main():
    # Suppress insecure request warnings if verify=False is necessary for your environment
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    if len(sys.argv) < 2:
        print("Error: Please provide a URL.")
        print("Usage: python script.py <URL>")
        sys.exit(1)
        
    # sys.argv[0] is the script name, sys.argv[1] is the first argument
    BASE_URL_TEMPLATE = sys.argv[1][:-2] + "%02d"  # Remove the last two characters (e.g., "01") and add the page placeholder
    MAX_PAGE = int(sys.argv[2]) 
    folder_name, folder_path = create_folder_from_url()
    
    for page in range(1, MAX_PAGE + 1):
        page_url = BASE_URL_TEMPLATE % page
        print(f"🌐 Fetching page {page_url}")

        try:
            resp = requests.get(page_url, headers=HEADERS, verify=False)
            resp.raise_for_status()
        except Exception as e:
            print(f"⚠️ Failed to load {page_url}: {e}")
            continue

        mp3_url, filename = extract_mp3_link(resp.text, page_url)
        if not mp3_url:
            print(f"⚠️ No matching MP3 found on page {page}")
            continue

        dest_path = os.path.join(folder_name[:-2], filename)
        if os.path.exists(dest_path):
            print(f"⏩ Skipping {filename}, already exists")
            continue

        print(f"⬇️  Downloading {filename} from {mp3_url}")
        try:
            download_file(mp3_url, dest_path, filename)
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")

    print(f"🎉 All downloads complete! Files saved in {folder_name}/")

if __name__ == "__main__":
    main()
