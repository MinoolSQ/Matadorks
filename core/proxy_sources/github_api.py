import requests
import asyncio
import socket
import json
import os
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.config import TCP_TIMEOUT, DATA_DIR
from core.logger import Logger

SOURCES = [
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/all.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
]

SCORE_FILE = os.path.join(DATA_DIR, "proxy_scores.json")

class GitHubProxyFetcher:
    def __init__(self):
        self.sources = SOURCES
        self.timeout = 1.0  # Mandatory 1s timeout for fast check

    def fetch_all(self):
        all_proxies = []
        for url in self.sources:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    found = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', resp.text)
                    for p in found:
                        all_proxies.append((p, url))
                    Logger.info(f"[GitHubAPI] Fetched {len(found)} proxies from {url}")
            except Exception as e:
                Logger.error(f"[GitHubAPI] Error fetching {url}: {e}")
        return all_proxies

    async def _tcp_check(self, proxy_pair):
        proxy, source = proxy_pair
        try:
            host, port = proxy.split(':')
            conn = asyncio.open_connection(host, int(port))
            reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)
            writer.close()
            await writer.wait_closed()
            return (proxy, source), True
        except:
            return (proxy, source), False

    async def run_async(self):
        Logger.info("[GitHubAPI] Starting ultra-fresh proxy scrape...")
        raw_pairs = self.fetch_all()
        if not raw_pairs:
            return []

        unique_pairs = {}
        for p, src in raw_pairs:
            if p not in unique_pairs:
                unique_pairs[p] = src
        
        raw_list = list(unique_pairs.items())

        tasks = [self._tcp_check(p) for p in raw_list]
        results = await asyncio.gather(*tasks)
        working_pairs = [p for p, ok in results if ok]

        total = len(raw_list)
        working = len(working_pairs)
        workrate = (working / total * 100) if total > 0 else 0

        Logger.info(f"[GitHubAPI] Found {working}/{total} working proxies (Workrate: {workrate:.2f}%)")

        self.save_score(workrate)

        if workrate < 20:
            Logger.warning(f"[GitHubAPI] Workrate low ({workrate:.2f}%). Sources might be stale.")
        
        return working_pairs

    def save_score(self, workrate):
        score_data = {
            "last_update": datetime.now().isoformat(),
            "workrate": workrate,
            "status": "healthy" if workrate >= 20 else "stale"
        }
        try:
            os.makedirs(os.path.dirname(SCORE_FILE), exist_ok=True)
            with open(SCORE_FILE, "w") as f:
                json.dump(score_data, f, indent=4)
        except Exception as e:
            Logger.error(f"[GitHubAPI] Failed to save score: {e}")

if __name__ == "__main__":
    fetcher = GitHubProxyFetcher()
    asyncio.run(fetcher.run_async())
