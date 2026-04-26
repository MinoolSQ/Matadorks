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
from urllib.parse import urlparse, parse_qs
socket.setdefaulttimeout(10)

from concurrent.futures import ThreadPoolExecutor, as_completed
from core.search import (duckduckgo, startpage, brave, yandex, bing, google)
from core.proxy import get_google_pool
from core.config import (
    DOMAIN_BLACKLIST, DORKS_FILE, SCANNER_THREADS, SCANNER_AMOUNT,
    SCANNER_PREFIX, CONSECUTIVE_FAILURE_THRESHOLD, COOLDOWN_SLEEP
)

# --- CONFIG & BLACKLIST ---

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

def worker(dork, amount, output_file, sqli_file, leak_file, pool, engines, lock, stats, stats_obj=None):
    proxy = pool.get_random()
    fail_reasons = []
    
    for name, engine_func in engines:
        try:
            results = engine_func(dork, amount, proxy=proxy)
            if not results:
                if proxy: pool.mark_dead(proxy)
                proxy = pool.get_random()
                continue

            filtered = [r for r in results if not is_blacklisted(r)]
            
            sqli_hits = []
            leak_hits = []
            for url in filtered:
                kind = classify_result(url, dork)
                if kind == "sqli":
                    sqli_hits.append(url)
                elif kind == "leak":
                    leak_hits.append(url)

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

def main(threads=None, amount=None, prefix=None, stats=None):
    threads = threads or SCANNER_THREADS
    amount = amount or SCANNER_AMOUNT
    prefix = prefix or SCANNER_PREFIX

    print("\n" + "="*60)
    print("   MATADORKS BULK SCANNER v1.1 - No Tor, Just Speed")
    print("="*60 + "\n")

    dork_path = DORKS_FILE
    if not os.path.exists(dork_path):
        print(f"[!] {dork_path} not found!")
        return

    with open(dork_path, "r") as f:
        all_dorks = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[+] Loaded {len(all_dorks)} dorks.")
    
    out_all, out_sqli, out_leak = f"data/{prefix}_all.txt", f"data/{prefix}_sqli_targets.txt", f"data/{prefix}_leaks.txt"

    print("[!] Gradim masivni proxy pool...")
    pool = get_google_pool(auto_build=False)
    # Masivno testiranje na pocetku
    pool.build(proto="socks5", max_test=5000, workers=400)
    pool.build(proto="http", max_test=3000, workers=400)
    
    if stats:
        stats.update(proxies_alive=pool.size())

    if pool.size() < 5:
        print("[!] Premalo radnih proksija.")
        return

    engines = [
        ("DuckDuckGo", duckduckgo),
        ("Brave", brave),
        ("Yandex", yandex),
        ("Bing", bing),
        ("Google", google)
    ]
    lock, internal_stats = threading.Lock(), {"total": 0, "sqli": 0, "leaks": 0}
    consecutive_failures = 0

    print(f"\n[!] Skeniranje pocinje sa {pool.size()} proksija...\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(worker, d, amount, out_all, out_sqli, out_leak, pool, engines, lock, internal_stats, stats) for d in all_dorks]
        for i, future in enumerate(as_completed(futures)):
            result_str = future.result()
            print(f"[{i+1:>4}/{len(all_dorks)}] {result_str}")
            
            if "(failed)" in result_str:
                consecutive_failures += 1
            else:
                consecutive_failures = 0

            # Povecan prag na 20 gresaka i dodat cool-down
            if consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                print(f"\n\033[91m[!] {CONSECUTIVE_FAILURE_THRESHOLD} gresaka zaredom! Pool je spržen. Hlađenje {COOLDOWN_SLEEP}s i refetch...\033[0m")
                time.sleep(COOLDOWN_SLEEP)
                # Agresivniji refetch
                pool.build(proto="socks5", max_test=5000, workers=400)
                pool.build(proto="http", max_test=4000, workers=400)
                if stats:
                    stats.update(proxies_alive=pool.size())
                consecutive_failures = 0
                print(f"\n[!] Novi pool spreman: {pool.size()} proksija. Nastavljam...\n")

            if i % threads == 0:
                time.sleep(0.3)

    print(f"\n[!] Gotovo! SQLi: {internal_stats['sqli']} | Leaks: {internal_stats['leaks']}")

if __name__ == "__main__":
    main()
