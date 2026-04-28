import os
import aiohttp
import asyncio
import threading
from queue import Queue, Empty
from urllib.parse import urlparse
import sys
from core.config import (
    DOMAIN_BLACKLIST, VALIDATED_FILE, VALIDATOR_THREADS, 
    VALIDATOR_TIMEOUT, VALIDATOR_BATCH_SIZE
)
from core.proxy import get_async_session

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
        url_lower = url.lower()
        if not ("?" in url and "=" in url):
            return True
        return any(item in url_lower for item in DOMAIN_BLACKLIST)

    async def validate_url(self, session, url):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.head(url, headers=headers, timeout=self.timeout, allow_redirects=True) as resp:
                return resp.status == 200
        except:
            try:
                async with session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True) as resp:
                    return resp.status == 200
            except:
                return False

    async def process_url(self, session, url):
        if not self.is_blacklisted(url):
            if await self.validate_url(session, url):
                with self.lock:
                    with open(self.output_file, "a") as f:
                        f.write(url + "\n")
                    self.out_q.put_nowait(url)
                    if self.stats:
                        self.stats.update(validated=self.stats.validated + 1)

    async def run(self):
        async with get_async_session() as session:
            while True:
                if self.abort and self.abort.is_set():
                    break
                try:
                    url = await self.in_q.get()
                except:
                    continue
                if url is None:
                    self.out_q.put_nowait(None)
                    break
                await self.process_url(session, url)
                self.in_q.task_done()

async def main(in_q, out_q, stats=None, abort=None):
    validator = Validator(in_q, out_q, stats=stats, abort=abort)
    await validator.run()
