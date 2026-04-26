#!/usr/bin/env python3.10
import requests
import random
import time
import threading
import asyncio
import socket
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# HQ Proxy Sources
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

from core.config import TCP_TIMEOUT, HTTP_TIMEOUT, TEST_URLS, PROXY_MAX_TEST, PROXY_WORKERS

class ProxyPool:
    def __init__(self):
        self._lock = threading.Lock()
        self._working = []
        self._index = 0
        self.source_stats = {}
        # Initial stats placeholder
        sources = get_dynamic_sources()
        for proto in sources:
            for url in sources[proto]:
                self.source_stats[url] = {"success": 0, "total": 0, "score": 0.0}

    def fetch_raw(self, proto="socks5"):
        """Paralelno povlacenje listi koristeci threadove za I/O."""
        all_data = []
        sources = get_dynamic_sources()
        
        def fetch_one(url):
            try:
                resp = requests.get(url, timeout=12)
                if resp.status_code == 200:
                    # Checkerproxy.net vraca JSON, ostali TXT
                    if "checkerproxy.net" in url:
                        try:
                            data = resp.json()
                            results = []
                            for entry in data:
                                proxy = entry.get('addr')
                                if proxy: results.append((proxy, url))
                            return results
                        except: pass
                    
                    lines = [l.strip() for l in resp.text.splitlines() if l.strip() and not l.startswith('#')]
                    # Spys.me ima dodatne info u liniji, uzmi samo IP:PORT
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

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(fetch_one, url) for url in sources.get(proto, [])]
            for fut in as_completed(futures):
                all_data.extend(fut.result())
        return all_data

    async def _async_tcp_ping(self, host, port):
        """Ultra-brzi asinhroni port check."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=TCP_TIMEOUT
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

    def _test_http(self, ip_port, proto, source_url):
        """Standardni HTTP test za proksije koji su prosli TCP ping."""
        proxy_url = f"{proto}://{ip_port}"
        proxies = {"http": proxy_url, "https": proxy_url}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            # Pokusaj primarni
            resp = requests.get(TEST_URLS[0], headers=headers, proxies=proxies, timeout=HTTP_TIMEOUT)
            if resp.status_code == 200: return proxy_url
            # Fallback
            resp = requests.get(random.choice(TEST_URLS[1:]), headers=headers, proxies=proxies, timeout=HTTP_TIMEOUT)
            if resp.status_code in [200, 301, 302]: return proxy_url
        except: pass
        return None

    async def build_async(self, proto="socks5", max_test=10000, min_working=100, workers=100, verbose=True):
        if verbose: print(f"\n[proxy] Započinjem masovni fetch (Limit: {max_test})...")
        
        raw_data = self.fetch_raw(proto)
        # Deduplikacija
        unique_map = {}
        for p, src in raw_data:
            if p not in unique_map: unique_map[p] = src
        
        candidates = list(unique_map.items())[:max_test]
        if verbose: print(f"[proxy] Preuzeto {len(raw_data)} | Unikatno {len(unique_map)} | Testiram {len(candidates)}")

        # --- PHASE 1: ASYNC TCP PING ---
        if verbose: print(f"[proxy] Faza 1: TCP Port Knocking (Hiljade paralelnih konekcija)...")
        
        passed_tcp = []
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

        # Procesiraj u grupama od 1000 radi stabilnosti
        for i in range(0, len(candidates), 1000):
            await check_batch_tcp(candidates[i:i+1000])
            if verbose: print(f"[proxy] TCP Alive: {len(passed_tcp)}", end='\r')

        if verbose: print(f"\n[proxy] Faza 2: HTTP Validation na {len(passed_tcp)} proksija sa {workers} workers...")

        # --- PHASE 2: HTTP VALIDATION ---
        working = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self._test_http, p, proto, src): (p, src) for p, src in passed_tcp}
            for fut in as_completed(futures):
                p, src = futures[fut]
                res = fut.result()
                
                with self._lock:
                    self.source_stats[src]["total"] += 1
                    if res:
                        self.source_stats[src]["success"] += 1
                        working.append(res)
                        if verbose: print(f"[proxy] + {res} ({len(working)} radnih)", end='\r')
                    
                    # Update score
                    s = self.source_stats[src]
                    s["score"] = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0
        
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
        """Wrapper da bismo mogli pozvati build() iz sinhronog koda."""
        return asyncio.run(self.build_async(*args, **kwargs))

    def get_random(self):
        with self._lock:
            return random.choice(self._working) if self._working else None

    def mark_dead(self, proxy_url):
        with self._lock:
            if proxy_url in self._working: self._working.remove(proxy_url)

    def size(self):
        return len(self._working)

# Singleton
_pool = ProxyPool()
def get_google_pool(auto_build=True):
    if auto_build and _pool.size() == 0:
        _pool.build(max_test=PROXY_MAX_TEST, min_working=50)
    return _pool

if __name__ == "__main__":
    _pool.build(max_test=10000, min_working=30)
