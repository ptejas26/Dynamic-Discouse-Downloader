#!/usr/bin/env python3
import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ------------------ CONFIG ------------------

# <a class="capitalize active text-sky-700" href="/osho-asambhav_kranti_01#">OSHO-Asambhav_Kranti_01</a>
BASE_URL_TEMPLATE = "https://oshoworld.com/osho-asambhav_kranti_%02d"  # use %02d for page number
DOWNLOAD_PATTERN = r"OSHO-Asambhav_Kranti_(\d+).mp3"  # regex pattern to extract track number
MAX_PAGE = 10 # number of pages to scrape
OUT_DIR = "asambhav_kranti"  # folder to save files download="Kaivalya Upanishad 01.mp3"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15"
}

# ------------------ HELPERS ------------------
os.makedirs(OUT_DIR, exist_ok=True)

def extract_mp3_link(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", download=True)
    for link in links:
        download_name = link.get("download", "")
        href = link.get("href", "")
        match = re.match(DOWNLOAD_PATTERN, download_name)
        if match and href.endswith(".mp3"):
            track_num = int(match.group(1))
            filename = download_name
            full_url = requests.compat.urljoin(base_url, href)
            return full_url, filename
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

# ------------------ MAIN ------------------
def main():
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

        dest_path = os.path.join(OUT_DIR, filename)
        if os.path.exists(dest_path):
            print(f"⏩ Skipping {filename}, already exists")
            continue

        print(f"⬇️  Downloading {filename} from {mp3_url}")
        try:
            download_file(mp3_url, dest_path, filename)
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")

    print(f"🎉 All downloads complete! Files saved in {OUT_DIR}")

if __name__ == "__main__":
    main()
