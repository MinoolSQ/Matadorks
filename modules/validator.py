import os
import requests
import threading
from queue import Queue
from urllib.parse import urlparse
import sys
from core.config import DOMAIN_BLACKLIST, VALIDATED_FILE, VALIDATOR_THREADS, VALIDATOR_TIMEOUT

class Validator:
    def __init__(self, input_file, output_file, threads, stats=None):
        self.input_file = input_file
        self.output_file = output_file
        self.threads = threads
        self.timeout = VALIDATOR_TIMEOUT
        self.queue = Queue()
        self.valid_urls = []
        self.lock = threading.Lock()
        self.total_processed = 0
        self.total_links = 0
        self.stats = stats

    def is_blacklisted(self, url):
        """Checks if the URL contains any blacklisted keywords or domains."""
        url_lower = url.lower()
        return any(item in url_lower for item in DOMAIN_BLACKLIST)

    def check_url(self):
        """Worker thread to check URL status."""
        while not self.queue.empty():
            if getattr(self, 'abort', None) and self.abort.is_set():
                while not self.queue.empty():
                    self.queue.get()
                    self.queue.task_done()
                return
            url = self.queue.get()
            try:
                # Use a generic User-Agent to avoid simple blocks
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                # Check status but don't download the whole page
                response = requests.head(url, headers=headers, timeout=self.timeout, allow_redirects=True)
                
                # If HEAD fails or is not allowed, try GET
                if response.status_code >= 400:
                    response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True, stream=True)

                if response.status_code == 200:
                    with self.lock:
                        self.valid_urls.append(url)
                        print(f"[+] VALID: {url}")
                        if self.stats:
                            self.stats.update(validated=len(self.valid_urls))
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

def main(input_file=None, output_file=None, threads=None, stats=None, abort=None):
    input_file = input_file or "data/matadorks_sqli_targets.txt"
    output_file = output_file or VALIDATED_FILE
    threads = threads or VALIDATOR_THREADS
    validator = Validator(input_file, output_file, threads, stats=stats)
    validator.abort = abort
    validator.run()

if __name__ == "__main__":
    main()
