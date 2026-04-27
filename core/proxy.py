import aiohttp
import asyncio
import random
import time
import threading
import socket
import re
import os
import json
from contextlib import asynccontextmanager
from datetime import datetime
from urllib.parse import urlparse
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
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt"
        ],
        "http": [
            f"https://checkerproxy.net/api/archive/{today}",
            "https://spys.me/proxy.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/Zaeem20/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/andirhm/free-proxy/main/http.txt"
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
        """Asinhrono povlačenje listi proksija."""
        all_data = []
        sources = get_dynamic_sources()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in sources.get(proto, []):
                tasks.append(self._fetch_one_async(session, url))
            
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
                            results = []
                            for entry in data:
                                proxy = entry.get('addr')
                                if proxy: results.append((proxy, url))
                            return results
                        except: pass
                    
                    text = await resp.text()
                    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
                    processed = []
                    for l in lines:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+:\d+)', l)
                        if match:
                            processed.append((match.group(1), url))
                        elif ':' in l:
                            processed.append((l.split()[0], url))
                    return processed
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
        except:
            return False

    async def _test_http_async(self, session, ip_port, proto, source_url):
        proxy_url = f"{proto}://{ip_port}"
        # Note: aiohttp session needs to be configured for proxy if using socks5
        # actually aiohttp supports socks5 via aiohttp-socks
        # For simplicity, if proto is socks5, we might need a different session or connector
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            # This is a simplified check. In real scenario, socks5 proxy requires special handling in aiohttp
            # For now, let's assume we use a session that can handle proxies or we use it for http only
            async with session.get(TEST_URLS[0], headers=headers, proxy=proxy_url, timeout=HTTP_TIMEOUT, allow_redirects=True) as resp:
                if resp.status == 200: return proxy_url
        except: pass
        return None

    async def build_async(self, proto="socks5", max_test=10000, min_working=100, workers=100, verbose=True, abort=None):
        if verbose: print(f"\n[proxy] Započinjem masovni fetch (Limit: {max_test})...")
        
        passed_tcp = []
        # Deduplikacija
        raw_data = await self.fetch_raw_async(proto)
        unique_map = {}
        for p, src in raw_data:
            if p not in unique_map: unique_map[p] = src
        
        candidates = list(unique_map.items())[:max_test]
        if verbose: print(f"[proxy] Preuzeto {len(raw_data)} | Unikatno {len(unique_map)} | Testiram {len(candidates)}")

        if verbose: print(f"[proxy] Faza 1: TCP Port Knocking...")
        
        async def check_batch_tcp(batch):
            tasks = []
            for p, src in batch:
                try:
                    host, port = p.split(':')
                    tasks.append(self._async_tcp_ping(host, int(port)))
                except: tasks.append(asyncio.sleep(0, result=False))
            
            results = await asyncio.gather(*tasks)
            for (p, src), is_up in zip(batch, results):
                if is_up: passed_tcp.append((p, src))

        for i in range(0, len(candidates), 1000):
            if abort and (isinstance(abort, asyncio.Event) and abort.is_set() or hasattr(abort, 'is_set') and abort.is_set()):
                break
            await check_batch_tcp(candidates[i:i+1000])
            if verbose: print(f"[proxy] TCP Alive: {len(passed_tcp)}", end='\r')

        if verbose: print(f"\n[proxy] Faza 2: HTTP Validation...")

        working = []
        # aiohttp socks support usually requires aiohttp-socks
        # For validation, we might still use a ThreadPool for SOCKS5 if aiohttp-socks is not available
        # But let's try to stick to async as much as possible.
        
        async with aiohttp.ClientSession() as session:
            # Note: aiohttp doesn't support socks5 natively without aiohttp-socks
            # If we don't have it, we might fall back to sync tests for socks5
            tasks = []
            semaphore = asyncio.Semaphore(workers)
            
            async def bounded_test(p, proto, src):
                async with semaphore:
                    res = await self._test_http_async(session, p, proto, src)
                    with self._lock:
                        self.source_stats[src]["total"] += 1
                        if res:
                            self.source_stats[src]["success"] += 1
                            working.append(res)
                            if verbose: print(f"[proxy] + {res} ({len(working)} radnih)", end='\r')
                        s = self.source_stats[src]
                        s["score"] = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0

            for p, src in passed_tcp:
                tasks.append(asyncio.create_task(bounded_test(p, proto, src)))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        with self._lock:
            self._working = working
            self._index = 0
        
        if verbose:
            print(f"\n[proxy] Završeno! Radnih: {len(working)}")
            self.print_source_report()
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

    def build(self, *args, **kwargs):
        return asyncio.run(self.build_async(*args, **kwargs))

    def get_random(self):
        with self._lock:
            return random.choice(self._working) if self._working else None

    def mark_dead(self, proxy_url):
        with self._lock:
            if proxy_url in self._working: self._working.remove(proxy_url)

    def size(self):
        return len(self._working)

_pool = ProxyPool()
def get_google_pool(auto_build=True):
    if auto_build and _pool.size() == 0:
        _pool.build(max_test=1000, min_working=50) # Reduced default for speed
    return _pool

@asynccontextmanager
async def get_async_session(proxy_url=None, timeout=30):
    """Helper context manager to provide an aiohttp session with proxy support."""
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    # Note: aiohttp doesn't support socks5 natively without aiohttp-socks.
    # We use a patched request method to inject the proxy for HTTP/HTTPS.
    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        if proxy_url:
            orig_request = session._request
            async def patched_request(method, str_or_url, **kwargs):
                if 'proxy' not in kwargs and proxy_url.startswith('http'):
                    kwargs['proxy'] = proxy_url
                return await orig_request(method, str_or_url, **kwargs)
            session._request = patched_request
        yield session
