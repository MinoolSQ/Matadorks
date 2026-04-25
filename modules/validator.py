import os
import requests
import threading
from queue import Queue
from urllib.parse import urlparse
import sys

# --- CONFIGURATION ---
INPUT_FILE = "../ugare_sqli_targets.txt"  # Default input file
OUTPUT_FILE = "validated_targets.txt"
THREADS = 20
TIMEOUT = 10

# List of domains or keywords to ignore (garbage/false positives)
BLACK_LIST = [
    "github.com", "stackoverflow.com", "youtube.com", "facebook.com",
    "twitter.com", "linkedin.com", "wikipedia.org", "amazon.com",
    "google.com", "bing.com", "microsoft.com", "apple.com",
    "instagram.com", "reddit.com", "medium.com", "pinterest.com",
    "quora.com", "adobe.com", "oracle.com", "mysql.com", "laracasts.com",
    "stackexchange.com", "serverfault.com", "askubuntu.com", "wordpress.org",
    "forum", "doku.php", "wiki", "community", "support",
    "documentation", "blog", "news", "tutorial", "how-to", "issue", "bugs",
    "pastebin.com", "gist.github.com", "bitbucket.org"
]

class Validator:
    def __init__(self, input_file, output_file, threads):
        self.input_file = input_file
        self.output_file = output_file
        self.threads = threads
        self.queue = Queue()
        self.valid_urls = []
        self.lock = threading.Lock()
        self.total_processed = 0
        self.total_links = 0

    def is_blacklisted(self, url):
        """Checks if the URL contains any blacklisted keywords or domains."""
        url_lower = url.lower()
        for item in BLACK_LIST:
            if item in url_lower:
                return True
        return False

    def check_url(self):
        """Worker thread to check URL status."""
        while not self.queue.empty():
            url = self.queue.get()
            try:
                # Use a generic User-Agent to avoid simple blocks
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                # Check status but don't download the whole page
                response = requests.head(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
                
                # If HEAD fails or is not allowed, try GET
                if response.status_code >= 400:
                    response = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True, stream=True)

                if response.status_code == 200:
                    with self.lock:
                        self.valid_urls.append(url)
                        print(f"[+] VALID: {url}")
                else:
                    print(f"[-] DEAD ({response.status_code}): {url}")
            except Exception as e:
                print(f"[!] ERROR: {url} ({str(e)})")
            
            finally:
                with self.lock:
                    self.total_processed += 1
                self.queue.task_done()

    def run(self):
        if not os.path.exists(self.input_file):
            # Try absolute path or relative to script
            alt_path = os.path.join(os.path.dirname(__file__), self.input_file)
            if not os.path.exists(alt_path):
                print(f"Error: Input file {self.input_file} not found.")
                return

        # Load and deduplicate
        with open(self.input_file, "r") as f:
            links = list(set([line.strip() for line in f if line.strip()]))

        print(f"[*] Loaded {len(links)} unique links from {self.input_file}")

        # Filter blacklisted AND ensure it has a query parameter (?)
        filtered_links = []
        for l in links:
            # SQLi targets must have a '?' and '=' to be attackable by sqlmap
            if not self.is_blacklisted(l) and "?" in l and "=" in l:
                filtered_links.append(l)
        
        print(f"[*] Filtered out {len(links) - len(filtered_links)} blacklisted or invalid (no-param) links")
        
        self.total_links = len(filtered_links)
        for link in filtered_links:
            self.queue.put(link)

        # Start threads
        for _ in range(self.threads):
            t = threading.Thread(target=self.check_url)
            t.daemon = True
            t.start()

        self.queue.join()

        # Save results
        with open(self.output_file, "w") as f:
            for url in self.valid_urls:
                f.write(url + "\n")

        print(f"\n[#] Validation Complete!")
        print(f"[#] Total valid links saved: {len(self.valid_urls)}")
        print(f"[#] Output saved to: {self.output_file}")

def main(input_file=None, output_file=None, threads=20):
    if input_file is None:
        input_file = "data/matadorks_sqli_targets.txt"
    if output_file is None:
        output_file = "data/validated_targets.txt"
    
    validator = Validator(input_file, output_file, threads)
    validator.run()

if __name__ == "__main__":
    main()
