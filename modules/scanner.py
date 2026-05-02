import asyncio
import os
import sys
import random
import threading

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from urllib.parse import urlparse, urlunparse, parse_qs
from core.search import duckduckgo, brave, bing, google, publicwww
from core.proxy import get_google_pool
from core.config import (
    DOMAIN_BLACKLIST, SCANNER_THREADS, SCANNER_AMOUNT,
    SCANNER_PREFIX, ASYNC_CONCURRENCY_LIMIT, DORKS_FILE
)
from modules.ghdb_provider import GHDBProvider

seen_urls = set()
seen_lock = threading.Lock() # Still use lock for set deduplication if needed, though async is single-threaded

def normalize_url(url):
    try:
        p = urlparse(url)
        return urlunparse((p.scheme.lower(), p.netloc.lower(), 
                          p.path.rstrip('/'), p.params, p.query, ''))
    except:
        return url

SQLI_PARAMS = {"id", "cat", "user", "article", "page", "topic", "thread", "product", "item", "pid", "sid", "tid", "uid"}

def is_blacklisted(url):
    url_lower = url.lower()
    return any(domain in url_lower for domain in DOMAIN_BLACKLIST)

def is_sqli_candidate(url):
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return any(k.lower() in SQLI_PARAMS for k in params)
    except:
        return False

async def worker(dork, amount, out_all, out_sqli, pool, engines, stats_obj, out_q, app_state=None, dork_map=None):
    # Try 2 random engines in parallel for better coverage and speed
    selected = random.sample(engines, min(len(engines), 2))
    
    tasks = []
    for name, engine_func in selected:
        proxy = pool.get_random()
        tasks.append(engine_func(dork, amount, proxy=proxy))
    
    try:
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = set()
        for i, results in enumerate(results_list):
            engine_name = selected[i][0]
            if isinstance(results, Exception):
                # print(f"[!] {engine_name} error: {results}")
                continue
            
            if not results:
                # If engine returned nothing, maybe proxy is dead
                # but we don't want to be too aggressive in marking dead here
                continue
            
            # print(f"[+] {engine_name} returned {len(results)} results")
            for r in results:
                all_results.add(r)

        if not all_results:
            return

        filtered = []
        for r in all_results:
            if is_blacklisted(r): continue
            
            if app_state and app_state.is_processed(r):
                continue

            norm = normalize_url(r)
            if norm not in seen_urls:
                seen_urls.add(norm)
                filtered.append(r)
        
        if not filtered: return

        sqli_hits = [u for u in filtered if is_sqli_candidate(u)]
        
        # Persistence
        with open(out_all, "a") as f:
            for url in filtered: f.write(url + "\n")
        
        if sqli_hits:
            with open(out_sqli, "a") as f:
                for url in sqli_hits: f.write(url + "\n")
            if stats_obj:
                stats_obj.update(sqli_hits=stats_obj.sqli_hits + len(sqli_hits))
        
        if stats_obj:
            stats_obj.update(urls_scanned=stats_obj.urls_scanned + len(filtered))

        edb_id = dork_map.get(dork) if dork_map else None

        for url in filtered:
            if app_state:
                app_state.mark_processed(url)
            
            url_obj = {"url": url, "dork": dork}
            if edb_id:
                url_obj["edb_id"] = edb_id
            
            await out_q.put(url_obj)

    except Exception as e:
        print(f"[!] Worker overall exception: {e}")

async def run_worker(in_q, out_q, stats=None, abort=None, app_state=None):
    amount = SCANNER_AMOUNT
    prefix = SCANNER_PREFIX
    out_all, out_sqli = f"data/{prefix}_all.txt", f"data/{prefix}_sqli_targets.txt"

    pool = get_google_pool(auto_build=False)
    # Build proxy pool if empty (async)
    if pool.size() < 10:
        await pool.build_async(proto="socks5", max_test=2000, workers=200)

    engines = [
        ("DuckDuckGo", duckduckgo),
        ("Brave", brave),
        ("Bing", bing),
        ("Google", google),
        ("PublicWWW", publicwww)
    ]

    semaphore = asyncio.Semaphore(ASYNC_CONCURRENCY_LIMIT)
    tasks = []
    
    provider = GHDBProvider()
    dork_map = provider.get_dork_map()

    while True:
        if abort and abort.is_set():
            break
        
        dork = await in_q.get()
        if dork is None:
            await asyncio.gather(*tasks, return_exceptions=True)
            await out_q.put(None)
            in_q.task_done()
            break
        
        async def bounded_worker(d):
            async with semaphore:
                await worker(d, amount, out_all, out_sqli, pool, engines, stats, out_q, app_state=app_state, dork_map=dork_map)
        
        task = asyncio.create_task(bounded_worker(dork))
        tasks.append(task)
        
        if len(tasks) > 1000:
            tasks = [t for t in tasks if not t.done()]
        
        in_q.task_done()

async def standalone_main():
    print("\n" + "="*60)
    print("   MATADORKS ASYNC SCANNER - Standalone Mode")
    print("="*60 + "\n")

    if not os.path.exists(DORKS_FILE):
        print(f"[!] {DORKS_FILE} not found!")
        return

    with open(DORKS_FILE, "r") as f:
        all_dorks = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[+] Loaded {len(all_dorks)} dorks.")
    
    in_q = asyncio.Queue()
    out_q = asyncio.Queue()

    for d in all_dorks:
        await in_q.put(d)
    await in_q.put(None)

    await run_worker(in_q, out_q)

if __name__ == "__main__":
    try:
        asyncio.run(standalone_main())
    except KeyboardInterrupt:
        pass
