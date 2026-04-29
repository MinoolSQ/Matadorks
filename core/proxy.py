import aiohttp
import asyncio
from contextlib import asynccontextmanager
import random
import threading
import re
import os
import json
from datetime import datetime
from urllib.parse import urlparse
from aiohttp_socks import ProxyConnector
from core.config import TCP_TIMEOUT, HTTP_TIMEOUT, TEST_URLS, ASYNC_CONCURRENCY_LIMIT, USE_TOR, PRIVATE_PROXIES_FILE
from core.proxy_sources.github_api import GitHubProxyFetcher, SOURCES as GH_SOURCES

def get_dynamic_sources():
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "socks5": [
            f"https://checkerproxy.net/api/archive/{today}",
            "https://spys.me/socks.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
            "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt"
        ],
        "http": [
            f"https://checkerproxy.net/api/archive/{today}",
            "https://spys.me/proxy.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/Zaeem20/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/andirhm/free-proxy/main/http.txt",
            "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt"
        ],
    }

class ProxyPool:
    def __init__(self):
        self._lock = threading.Lock()
        self._working = []
        self._index = 0
        self.source_stats = {}

        # Add Tor if enabled
        if USE_TOR:
            tor_proxy = "socks5://127.0.0.1:9050"
            self._working.append(tor_proxy)
            self.source_stats[tor_proxy] = {"success": 1, "total": 1, "score": 100.0}

        # Load private proxies if file exists
        if os.path.exists(PRIVATE_PROXIES_FILE):
            try:
                with open(PRIVATE_PROXIES_FILE, "r") as f:
                    for line in f:
                        p = line.strip()
                        if p and not p.startswith("#"):
                            if not p.startswith(("http", "socks4", "socks5")):
                                p = f"socks5://{p}"
                            self._working.append(p)
                            self.source_stats[p] = {"success": 1, "total": 1, "score": 100.0}
            except Exception: pass

        sources = get_dynamic_sources()
        for proto in sources:
            for url in sources[proto]:
                self.source_stats[url] = {"success": 0, "total": 0, "score": 0.0}
        for url in GH_SOURCES:
            self.source_stats[url] = {"success": 0, "total": 0, "score": 0.0}

    async def fetch_raw_async(self, proto="socks5"):
        all_data = []
        sources = get_dynamic_sources()
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_one_async(session, url) for url in sources.get(proto, [])]
            results = await asyncio.gather(*tasks)
            for res in results:
                all_data.extend(res)
        return all_data

    async def _fetch_one_async(self, session, url):
        try:
            async with session.get(url, timeout=12) as resp:
                if resp.status == 200:
                    if "checkerproxy.net" in url:
                        try:
                            data = await resp.json()
                            return [(entry.get('addr'), url) for entry in data if entry.get('addr')]
                        except: pass
                    text = await resp.text()
                    found = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', text)
                    return [(p, url) for p in found]
        except: pass
        return []

    async def _async_tcp_ping(self, host, port):
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=TCP_TIMEOUT
            )
            writer.close()
            await writer.wait_closed()
            return True
        except: return False

    async def _test_http_async(self, ip_port, proto, source_url):
        proxy_url = f"{proto}://{ip_port}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            if proto.startswith("socks"):
                connector = ProxyConnector.from_url(proxy_url)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(TEST_URLS[0], headers=headers, timeout=HTTP_TIMEOUT) as resp:
                        if resp.status == 200: return proxy_url
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(TEST_URLS[0], headers=headers, proxy=proxy_url, timeout=HTTP_TIMEOUT) as resp:
                        if resp.status == 200: return proxy_url
        except: pass
        return None

    async def build_async(self, proto="socks5", max_test=10000, workers=100, verbose=True, abort=None):
        if verbose: print(f"\n[proxy] Započinjem masovni fetch ({proto})...")
        
        passed_tcp = []
        if proto == "http":
            gh_fetcher = GitHubProxyFetcher()
            gh_passed = await gh_fetcher.run_async()
            passed_tcp.extend(gh_passed)

        raw_data = await self.fetch_raw_async(proto)
        unique_map = {p: src for p, src in raw_data}
        candidates = list(unique_map.items())[:max_test]
        
        if verbose: print(f"[proxy] Testiram {len(candidates)} TCP konekcija...")
        
        sem = asyncio.Semaphore(500)
        async def check_tcp(p, src):
            async with sem:
                if abort and abort.is_set(): return
                try:
                    host, port = p.split(':')
                    if await self._async_tcp_ping(host, int(port)):
                        passed_tcp.append((p, src))
                except: pass

        await asyncio.gather(*[check_tcp(p, src) for p, src in candidates])
        
        if verbose: print(f"[proxy] TCP Alive: {len(passed_tcp)}. Validacija HTTP...")
        
        working = []
        sem_http = asyncio.Semaphore(workers)
        async def check_http(p, src):
            async with sem_http:
                if abort and abort.is_set(): return
                res = await self._test_http_async(p, proto, src)
                with self._lock:
                    self.source_stats[src]["total"] += 1
                    if res:
                        self.source_stats[src]["success"] += 1
                        working.append(res)
                        if verbose: print(f"[proxy] + {res} ({len(working)} radnih)", end='\r')
                    s = self.source_stats[src]
                    s["score"] = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0

        await asyncio.gather(*[check_http(p, src) for p, src in passed_tcp])
        
        with self._lock:
            self._working.extend(working)
            self._working = list(set(self._working))
        return len(working)

    def print_source_report(self):
        print("\n" + "-"*50)
        print(f"{'Source Domain':<35} | {'Score':<7} | {'Success'}")
        print("-"*50)
        sorted_stats = sorted(self.source_stats.items(), key=lambda x: x[1]['score'], reverse=True)
        for src, s in sorted_stats:
            if s['total'] > 0:
                domain = urlparse(src).netloc[:34]
                print(f"{domain:<35} | {s['score']:>5.1f}% | {s['success']}/{s['total']}")
        print("-"*50 + "\n")

    def get_random(self):
        with self._lock:
            return random.choice(self._working) if self._working else None

    def mark_dead(self, proxy_url):
        with self._lock:
            if proxy_url in self._working: self._working.remove(proxy_url)

    def size(self):
        return len(self._working)

@asynccontextmanager
async def get_async_session(proxy_url=None, timeout=10):
    connector = None
    if proxy_url and proxy_url.startswith(("socks", "http")):
        from aiohttp_socks import ProxyConnector
        connector = ProxyConnector.from_url(proxy_url)
    
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
        yield session

_pool = ProxyPool()
def get_google_pool(auto_build=False):
    return _pool
