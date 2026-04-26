#!/usr/bin/env python3.10
import site
import sys
import os

# Fix for imports
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import time
import random
import threading
import socket
from queue import Queue, Empty
from urllib.parse import urlparse, urlunparse, parse_qs
socket.setdefaulttimeout(10)

from concurrent.futures import ThreadPoolExecutor, as_completed
from core.search import (duckduckgo, startpage, brave, yandex, bing, google, publicwww)
from core.proxy import get_google_pool
from core.config import (
    DOMAIN_BLACKLIST, DORKS_FILE, SCANNER_THREADS, SCANNER_BATCH_SIZE, SCANNER_AMOUNT,
    SCANNER_PREFIX, CONSECUTIVE_FAILURE_THRESHOLD, COOLDOWN_SLEEP,
    USE_PUBLICWWW, USE_STARTPAGE
)

# --- CONFIG & BLACKLIST ---

seen_urls = set()
seen_lock = threading.Lock()

def normalize_url(url):
    try:
        p = urlparse(url)
        # Lowercase scheme and host, remove fragment, rstrip / from path
        return urlunparse((p.scheme.lower(), p.netloc.lower(), 
                          p.path.rstrip('/'), p.params, p.query, ''))
    except:
        return url

SQLI_PARAMS = {
    "id", "cat", "user", "article", "page", "topic", "thread", "product",
    "item", "news_id", "post_id", "profile_id", "artikel", "produkt",
    "benutzer", "kategorie", "articolo", "prodotto", "utente", "notizia",
    "articulo", "producto", "usuario", "tema", "artykul", "uzytkownik",
    "kategoria", "temat", "clanek", "uzivatel", "cikk", "termek",
    "felhasznalo", "sujet", "produit", "utilisateur", "pid", "sid", "tid", "uid"
}

SQL_ERROR_MARKERS = [
    "microsoft ole db", "warning: mysql_fetch", "warning: mysqli",
    "warning: mysql_num", "you have an error in your sql syntax",
    "ora-01756", "unclosed quotation mark", "odbc microsoft access",
    "supplied argument is not a valid mysql", "pg_query():",
]

def is_blacklisted(url):
    url_lower = url.lower()
    return any(domain in url_lower for domain in DOMAIN_BLACKLIST)

def is_sqli_candidate(url, dork=""):
    dork_lower = dork.lower()
    if any(m in dork_lower for m in SQL_ERROR_MARKERS):
        return True
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return any(k.lower() in SQLI_PARAMS for k in params)
    except:
        return False

def classify_result(url, dork):
    if is_sqli_candidate(url, dork):
        return "sqli"
    dork_lower = dork.lower()
    if any(x in dork_lower for x in ["filetype:env", "ext:sql", ".git/config", "wp-config"]):
        return "leak"
    return "general"

def worker(dork, amount, output_file, sqli_file, leak_file, pool, engines, lock, stats, out_q=None, stats_obj=None):
    proxy = pool.get_random()
    
    results_found = []
    for name, engine_func in engines:
        try:
            results = engine_func(dork, amount, proxy=proxy)
            if not results:
                if proxy: pool.mark_dead(proxy)
                proxy = pool.get_random()
                continue

            filtered = [r for r in results if not is_blacklisted(r)]
            
            # Normalization & De-duplication
            normalized = [normalize_url(u) for u in filtered]
            with seen_lock:
                new_urls = []
                for i, u in enumerate(normalized):
                    if u not in seen_urls:
                        seen_urls.add(u)
                        new_urls.append(filtered[i])
                filtered = new_urls

            if not filtered:
                continue

            sqli_hits = []
            leak_hits = []
            for url in filtered:
                if out_q:
                    out_q.put(url)
                kind = classify_result(url, dork)
                if kind == "sqli":
                    sqli_hits.append(url)
                elif kind == "leak":
                    leak_hits.append(url)
            
            results_found.extend(filtered)

            with lock:
                with open(output_file, "a") as f:
                    f.write(f"\n# [{name}] {dork}\n")
                    for url in filtered: f.write(url + "\n")
                
                if sqli_hits:
                    with open(sqli_file, "a") as f:
                        for url in sqli_hits: f.write(url + "\n")
                    stats["sqli"] += len(sqli_hits)
                    if stats_obj:
                        stats_obj.update(sqli_hits=stats["sqli"])
                
                if leak_hits:
                    with open(leak_file, "a") as f:
                        for url in leak_hits: f.write(url + "\n")
                    stats["leaks"] += len(leak_hits)
                
                stats["total"] += len(filtered)
                if stats_obj:
                    stats_obj.update(urls_scanned=stats["total"])

            tag = f" [{len(filtered)} url]"
            if sqli_hits: tag += f" [SQLi:{len(sqli_hits)}]"
            return f"[+] {dork[:40]:<40} {name:<10}{tag}"

        except Exception:
            if proxy: pool.mark_dead(proxy)
            proxy = pool.get_random()
            continue

    return f"[-] {dork[:40]:<40} (failed)"

def run_worker(in_q, out_q, threads=None, amount=None, prefix=None, stats=None, abort=None):
    threads = threads or SCANNER_THREADS
    amount = amount or SCANNER_AMOUNT
    prefix = prefix or SCANNER_PREFIX
    batch_size = SCANNER_BATCH_SIZE

    out_all, out_sqli, out_leak = f"data/{prefix}_all.txt", f"data/{prefix}_sqli_targets.txt", f"data/{prefix}_leaks.txt"

    pool = get_google_pool(auto_build=False)
    pool.build(proto="socks5", max_test=5000, workers=400)
    pool.build(proto="http", max_test=3000, workers=400)
    
    if stats:
        stats.update(proxies_alive=pool.size())

    if pool.size() < 5:
        print("[!] Premalo radnih proksija za skeniranje.")
        out_q.put(None)
        return

    engines = [
        ("DuckDuckGo", duckduckgo),
        ("Brave", brave),
        ("Yandex", yandex),
        ("Bing", bing),
        ("Google", google)
    ]
    if USE_STARTPAGE:
        engines.insert(1, ("Startpage", startpage))
    if USE_PUBLICWWW:
        engines.append(("PublicWWW", publicwww))

    lock, internal_stats = threading.Lock(), {"total": 0, "sqli": 0, "leaks": 0}
    consecutive_failures = 0
    total_processed = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        active_futures = set()
        while True:
            if abort and abort.is_set():
                break
            
            # Refill futures up to batch_size OR threads limit
            refilled = 0
            while len(active_futures) < threads and refilled < batch_size:
                try:
                    dork = in_q.get_nowait()
                    refilled += 1
                    if dork is None:
                        in_q.task_done()
                        goto_cleanup = True
                        break
                    
                    future = executor.submit(worker, dork, amount, out_all, out_sqli, out_leak, pool, engines, lock, internal_stats, out_q, stats)
                    # Add a callback to call task_done when future is finished
                    future.add_done_callback(lambda f: in_q.task_done())
                    active_futures.add(future)
                    total_processed += 1
                except Empty:
                    break
            else:
                goto_cleanup = False

            if not active_futures:
                if 'goto_cleanup' in locals() and goto_cleanup:
                    break
                time.sleep(0.1)
                continue

            # Check for completed futures
            done, active_futures = wait_for_some(active_futures, timeout=0.1)
            for future in done:
                result_str = future.result()
                
                # Prikazuj samo ako je nesto pronadjeno ili ako je greska kriticna
                if "[0 url]" not in result_str:
                    print(f"[{total_processed - len(active_futures):>4}] {result_str}")

                if "(failed)" in result_str:
                    consecutive_failures += 1
                else:
                    consecutive_failures = 0

                if consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                    print(f"\n\033[91m[!] {CONSECUTIVE_FAILURE_THRESHOLD} gresaka zaredom! Hlađenje {COOLDOWN_SLEEP}s...\033[0m")
                    time.sleep(COOLDOWN_SLEEP)
                    pool.build(proto="socks5", max_test=2000, workers=200)
                    if stats: stats.update(proxies_alive=pool.size())
                    consecutive_failures = 0

    out_q.put(None)
    print(f"\n[!] Scanner worker finished. Total processed: {total_processed}")

def wait_for_some(futures, timeout=None):
    """Helper to wait for some futures to complete."""
    done = set()
    not_done = set(futures)
    if not futures:
        return done, not_done
    
    # as_completed is an iterator, we want non-blocking check if possible
    # but concurrent.futures doesn't have a great "check all" without blocking
    # we use a small timeout and check which are done
    for f in futures:
        if f.done():
            done.add(f)
            not_done.remove(f)
    
    if not done and timeout:
        # Wait a bit if nothing is done
        time.sleep(timeout)
        for f in list(not_done):
            if f.done():
                done.add(f)
                not_done.remove(f)
                
    return done, not_done

def main(threads=None, amount=None, prefix=None, stats=None, abort=None):
    seen_urls.clear()

    print("\n" + "="*60)
    print("   MATADORKS BULK SCANNER v1.2 - Queue Enabled")
    print("="*60 + "\n")

    dork_path = DORKS_FILE
    if not os.path.exists(dork_path):
        print(f"[!] {dork_path} not found!")
        return

    with open(dork_path, "r") as f:
        all_dorks = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[+] Loaded {len(all_dorks)} dorks.")
    
    in_q = Queue()
    out_q = Queue()

    for d in all_dorks:
        in_q.put(d)
    in_q.put(None) # Sentinel

    # Start run_worker in a way that we can monitor out_q if we want, 
    # but for compatibility we can just call it.
    run_worker(in_q, out_q, threads=threads, amount=amount, prefix=prefix, stats=stats, abort=abort)

    # Optional: drain out_q if needed, though run_worker already put things there.
    # In this standalone main, we don't really use out_q yet.

if __name__ == "__main__":
    main()
