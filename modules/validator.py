import asyncio
import aiohttp
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from urllib.parse import urlparse
from core.config import (
    DOMAIN_BLACKLIST, VALIDATED_FILE, VALIDATOR_TIMEOUT, 
    ASYNC_CONCURRENCY_LIMIT
)

class AsyncValidator:
    def __init__(self, in_q, out_q, stats=None, abort=None):
        self.in_q = in_q
        self.out_q = out_q
        self.stats = stats
        self.abort = abort
        self.timeout = VALIDATOR_TIMEOUT
        self.output_file = VALIDATED_FILE
        self.semaphore = asyncio.Semaphore(ASYNC_CONCURRENCY_LIMIT)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def is_blacklisted(self, url):
        """Checks if the URL contains any blacklisted keywords or domains."""
        url_lower = url.lower()
        if not ("?" in url and "=" in url):
            return True
        return any(item in url_lower for item in DOMAIN_BLACKLIST)

    async def validate_url(self, session, url):
        """Performs non-blocking HTTP check to see if the URL is alive."""
        async with self.semaphore:
            try:
                # Some servers are picky, we try to be as minimal as possible
                async with session.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True) as response:
                    return response.status == 200
            except Exception:
                return False

    async def process_url(self, session, url):
        """Validates a single URL and handles persistence/queuing."""
        if not self.is_blacklisted(url):
            if await self.validate_url(session, url):
                # Persistence: Append to file (async file I/O could be used but for logs it's fine)
                with open(self.output_file, "a") as f:
                    f.write(url + "\n")
                
                # Push to next stage (valid_q)
                await self.out_q.put(url)
                
                if self.stats:
                    self.stats.update(validated=self.stats.validated + 1)
                
                # We don't want to spam console too much if running thousands
                # print(f"[+] VALID: {url}")
        self.in_q.task_done()

    async def run(self):
        """Main loop for the continuous async worker."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            while True:
                if self.abort and self.abort.is_set():
                    break
                
                url = await self.in_q.get()
                
                if url is None:
                    # End of stream marker
                    await asyncio.gather(*tasks, return_exceptions=True)
                    if self.out_q:
                        await self.out_q.put(None)
                    self.in_q.task_done()
                    break
                
                task = asyncio.create_task(self.process_url(session, url))
                tasks.append(task)
                
                # Periodic cleanup of completed tasks to save memory
                if len(tasks) > 1000:
                    tasks = [t for t in tasks if not t.done()]

async def main(in_q, out_q, stats=None, abort=None):
    validator = AsyncValidator(in_q, out_q, stats=stats, abort=abort)
    await validator.run()

if __name__ == "__main__":
    print("Async Validator module loaded.")
