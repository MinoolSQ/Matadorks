import os
import requests
import threading
from queue import Queue, Empty
from urllib.parse import urlparse
import sys
from concurrent.futures import ThreadPoolExecutor
from core.config import (
    DOMAIN_BLACKLIST, VALIDATED_FILE, VALIDATOR_THREADS, 
    VALIDATOR_TIMEOUT, VALIDATOR_BATCH_SIZE
)

class Validator:
    def __init__(self, in_q, out_q, stats=None, abort=None):
        self.in_q = in_q
        self.out_q = out_q
        self.stats = stats
        self.abort = abort
        self.threads = VALIDATOR_THREADS
        self.timeout = VALIDATOR_TIMEOUT
        self.output_file = VALIDATED_FILE
        self.batch_size = VALIDATOR_BATCH_SIZE
        self.lock = threading.Lock()

    def is_blacklisted(self, url):
        """Checks if the URL contains any blacklisted keywords or domains."""
        url_lower = url.lower()
        # SQLi targets must have a '?' and '=' to be attackable
        if not ("?" in url and "=" in url):
            return True
        return any(item in url_lower for item in DOMAIN_BLACKLIST)

    def validate_url(self, url):
        """Performs HTTP check to see if the URL is alive."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            # Try HEAD first for speed
            response = requests.head(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            # If HEAD fails, try GET (some servers block HEAD)
            if response.status_code >= 400:
                response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True, stream=True)

            return response.status_code == 200
        except Exception:
            return False

    def process_url(self, url):
        """Validates a single URL and handles persistence/queuing."""
        if not self.is_blacklisted(url):
            if self.validate_url(url):
                with self.lock:
                    # Persistence: Append to file
                    with open(self.output_file, "a") as f:
                        f.write(url + "\n")
                    
                    # Push to next stage (valid_q)
                    self.out_q.put(url)
                    
                    if self.stats:
                        self.stats.update(validated=self.stats.validated + 1)
                
                print(f"[+] VALID: {url}")
            else:
                # print(f"[-] DEAD: {url}")
                pass
        self.in_q.task_done()

    def run(self):
        """Main loop for the continuous worker."""
        # print(f"[*] Validator worker started. Threads: {self.threads}")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while True:
                if self.abort and self.abort.is_set():
                    break
                
                try:
                    # Use a timeout to allow checking for abort/None
                    url = self.in_q.get(timeout=1)
                except Empty:
                    continue

                if url is None:
                    # Wait for all submitted tasks to complete before signaling next stage
                    executor.shutdown(wait=True)
                    self.out_q.put(None)
                    self.in_q.task_done()
                    break
                
                executor.submit(self.process_url, url)

def main(in_q, out_q, stats=None, abort=None):
    """
    Entry point for the continuous validator worker.
    :param in_q: Input queue (url_q)
    :param out_q: Output queue (valid_q)
    :param stats: PipelineStats object for tracking
    :param abort: threading.Event to signal abortion
    """
    validator = Validator(in_q, out_q, stats=stats, abort=abort)
    validator.run()

if __name__ == "__main__":
    # Example usage (not intended for standalone run without queues)
    print("Validator module refactored for queue-based pipeline.")
