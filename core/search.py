#!/usr/bin/env python3.10
from __future__ import print_function
import site
import sys
import os

# Fix for DDGS and SOCKS in thread context
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    import socks
except ImportError:
    pass

import time
import requests
import random
import json
import base64
import re
from bs4 import BeautifulSoup
import urllib.parse
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for proxy usage
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DDGS = None
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        pass

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

def random_sleep(min_s=0.2, max_s=1.0):
    time.sleep(random.uniform(min_s, max_s))


# ── Standard search engines ──────────────────────────────────────────────────

def duckduckgo(dork, amount, proxy=None):
    results = []
    if DDGS is None:
        print("[DDG] DDGS nije importovan — provjeri instalaciju ddgs/duckduckgo_search", file=sys.stderr)
        return results
    last_error = None
    for backend in ('html', 'lite'):
        try:
            with DDGS(proxy=proxy, timeout=10) as ddgs:
                # Ogranicavamo se na html/lite jer api pokusava druge engine-ove kad je banovan
                for r in ddgs.text(dork, max_results=amount, backend=backend):
                    href = r.get('href') or r.get('url', '')
                    if href:
                        results.append(href)
            if results:
                return results
        except Exception as e:
            err = str(e).lower()
            if 'rate' in err or '202' in err:
                time.sleep(random.uniform(1, 3))
            continue
    if not results and last_error:
        print(f"[DDG] Svi backend-ovi pali za dork: {dork[:50]!r}", file=sys.stderr)
    return results

def google(dork, amount, proxy=None):
    """Google pretrazivanje kroz rotacijski proxy pool (free proxy liste).
    'proxy' parametar se ignorise — koristi interni pool koji podrzava Google."""
    try:
        from core.proxy import get_google_pool
        pool = get_google_pool(auto_build=False)  # pool se gradi u main(), ne ovdje
    except ImportError:
        pool = None

    results = []
    headers = {
        'User-Agent': get_random_ua(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    # Pokusaj do 3 razlicita proxija
    attempts = 3
    for _ in range(attempts):
        proxy_url = pool.get_random() if pool and pool.size() > 0 else None
        proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
        try:
            random_sleep()
            query = urllib.parse.quote_plus(dork)
            url = f"https://www.google.com/search?q={query}&num={amount}&hl=en&gl=us"
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=12, verify=False)
            if resp.status_code == 429 or 'sorry/index' in resp.url:
                if pool and proxy_url:
                    pool.mark_dead(proxy_url)
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.select('a[href]'):
                href = a.get('href', '')
                if href.startswith('/url?q='):
                    real = urllib.parse.unquote(href[7:].split('&')[0])
                    if real.startswith('http') and 'google.com' not in real:
                        results.append(real)
                        if len(results) >= amount:
                            break
            if results:
                break
        except:
            if pool and proxy_url:
                pool.mark_dead(proxy_url)
            continue

    return results

def startpage(dork, amount, proxy=None):
    """Startpage — proxy za Google rezultate, radi kroz Tor.
    Ne podrzava dork operatore, pa ekstrahuje samo keyword dio dorka."""
    results = []
    headers = {
        'User-Agent': get_random_ua(),
        'Accept-Language': 'en-US,en;q=0.9',
    }
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        # Ukloni Google dork operatore — Startpage ih ne podrzava
        keyword = re.sub(r'(inurl|intext|intitle|filetype|site|ext):[^\s"]*', '', dork)
        keyword = re.sub(r'"', '', keyword).strip()
        if not keyword or len(keyword) < 4:
            return results
        random_sleep()
        query = urllib.parse.quote_plus(keyword)
        url = f"https://www.startpage.com/sp/search?q={query}&language=english"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=15, verify=False)
        if resp.status_code != 200:
            print(f"[Startpage] HTTP {resp.status_code}", file=sys.stderr)
            return results
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Pokusaj nekoliko selektora — Startpage mjenja HTML strukturu
        for selector in ('a[data-testid="gl-title-link"]', 'a.result-link', 'h2 > a', 'a[href^="https://"][class*="result"]'):
            for a in soup.select(selector):
                href = a.get('href', '')
                if href.startswith('http') and 'startpage.com' not in href:
                    results.append(href)
                    if len(results) >= amount:
                        break
            if results:
                break
        if not results:
            print(f"[Startpage] Nema rezultata — HTML struktura vjerovatno promijenjena", file=sys.stderr)
    except Exception as e:
        print(f"[Startpage] Greska: {e}", file=sys.stderr)
    return results

def brave(dork, amount, proxy=None):
    results = []
    headers = {
        'User-Agent': get_random_ua(),
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        random_sleep()
        query = urllib.parse.quote_plus(dork)
        url = f"https://search.brave.com/search?q={query}&source=web"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=10, verify=False)
        if resp.status_code == 429:
            raise Exception("RateLimit:429")
        if resp.status_code != 200:
            return results
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.select('a[href]'):
            href = a.get('href', '')
            if href.startswith('http') and 'brave.com' not in href and 'search.brave' not in href:
                results.append(href)
                if len(results) >= amount:
                    break
        if not results:
            print(f"[Brave] HTTP {resp.status_code}, nema rezultata", file=sys.stderr)
    except Exception as e:
        print(f"[Brave] Greska: {e}", file=sys.stderr)
    return results

def yandex(dork, amount, proxy=None):
    results = []
    headers = {'User-Agent': get_random_ua()}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        random_sleep()
        query = urllib.parse.quote_plus(dork)
        url = f"https://yandex.com/search/?text={query}&lang=en"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.select('a.Link_theme_outer, a.organic__url, li.serp-item a'):
            href = a.get('href', '')
            if href.startswith('http') and 'yandex' not in href:
                results.append(href)
                if len(results) >= amount:
                    break
    except:
        pass
    return results

def bing(dork, amount, proxy=None):
    results = []
    headers = {
        'User-Agent': get_random_ua(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.bing.com/'
    }
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        random_sleep()
        query = urllib.parse.quote_plus(dork)
        # Bing pagination: first=1, 11, 21...
        url = f"https://www.bing.com/search?q={query}&count={amount}"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=12, verify=False)
        if resp.status_code != 200:
            return results
        soup = BeautifulSoup(resp.text, 'html.parser')
        for li in soup.select('li.b_algo'):
            a = li.find('a')
            if a:
                href = a.get('href', '')
                if href.startswith('http') and 'bing.com' not in href:
                    results.append(href)
                    if len(results) >= amount:
                        break
    except Exception as e:
        print(f"[Bing] Greska: {e}", file=sys.stderr)
    return results


# ── Shodan ───────────────────────────────────────────────────────────────────
# Postavi: export SHODAN_API_KEY=tvoj_kljuc
# Besplatan plan: ~100 query credita/mjesec
# Shodan vraca IP:port, mi gradimo URL

def _dork_to_shodan_query(dork):
    """Prevedi Google dork u Shodan filter sintaksu."""
    q = dork
    # inurl: → http.html: (aprox)
    q = re.sub(r'inurl:(\S+)', r'http.html:"\1"', q)
    # intitle: → http.title:
    q = re.sub(r'intitle:"([^"]+)"', r'http.title:"\1"', q)
    q = re.sub(r'intitle:(\S+)', r'http.title:"\1"', q)
    # filetype: → Shodan ne podrzava direktno, ali filtriramo
    q = re.sub(r'filetype:\S+', '', q)
    # site:.de → country:DE
    def country_sub(m):
        tld = m.group(1).lstrip('.')
        return f'country:{tld.upper()}'
    q = re.sub(r'site:\.?([a-z]{2})\b', country_sub, q)
    return q.strip()

def shodan(dork, amount, proxy=None):
    """Shodan API — zahtijeva SHODAN_API_KEY env varijablu."""
    api_key = os.environ.get('SHODAN_API_KEY', '')
    if not api_key:
        return []

    results = []
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    query = _dork_to_shodan_query(dork)
    if not query:
        return []

    try:
        params = {
            'key': api_key,
            'query': query,
            'minify': 'true',
        }
        resp = requests.get(
            'https://api.shodan.io/shodan/host/search',
            params=params,
            proxies=proxies,
            timeout=20,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        for match in data.get('matches', [])[:amount]:
            ip = match.get('ip_str', '')
            port = match.get('port', 80)
            transport = match.get('transport', 'tcp')
            if not ip:
                continue
            scheme = 'https' if port in (443, 8443) else 'http'
            url = f"{scheme}://{ip}:{port}/"
            results.append(url)
    except:
        pass
    return results


# ── Censys ───────────────────────────────────────────────────────────────────
# Postavi: export CENSYS_API_ID=id  export CENSYS_API_SECRET=secret
# Registracija: https://search.censys.io/register

def _dork_to_censys_query(dork):
    """Prevedi Google dork u Censys filter sintaksu (v2 API)."""
    q = dork
    q = re.sub(r'inurl:(\S+)', r'services.http.response.body:"\1"', q)
    q = re.sub(r'intitle:"([^"]+)"', r'services.http.response.html_title:"\1"', q)
    q = re.sub(r'intitle:(\S+)', r'services.http.response.html_title:"\1"', q)
    q = re.sub(r'filetype:\S+', '', q)
    def country_sub(m):
        tld = m.group(1).lstrip('.')
        return f'location.country_code:"{tld.upper()}"'
    q = re.sub(r'site:\.?([a-z]{2})\b', country_sub, q)
    return q.strip()

def censys(dork, amount, proxy=None):
    """Censys Search API v2 — zahtijeva CENSYS_API_ID i CENSYS_API_SECRET env varijable."""
    api_id = os.environ.get('CENSYS_API_ID', '')
    api_secret = os.environ.get('CENSYS_API_SECRET', '')
    if not api_id or not api_secret:
        return []

    results = []
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    query = _dork_to_censys_query(dork)
    if not query:
        return []

    try:
        resp = requests.post(
            'https://search.censys.io/api/v2/hosts/search',
            auth=(api_id, api_secret),
            json={'q': query, 'per_page': min(amount, 25)},
            proxies=proxies,
            timeout=20,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        for hit in data.get('result', {}).get('hits', []):
            ip = hit.get('ip', '')
            if not ip:
                continue
            services = hit.get('services', [])
            for svc in services[:1]:
                port = svc.get('port', 80)
                scheme = 'https' if port in (443, 8443) else 'http'
                results.append(f"{scheme}://{ip}:{port}/")
    except:
        pass
    return results


# ── ZoomEye ──────────────────────────────────────────────────────────────────
# Postavi: export ZOOMEYE_API_KEY=tvoj_kljuc
# Registracija: https://www.zoomeye.org/

def zoomeye(dork, amount, proxy=None):
    """ZoomEye API — zahtijeva ZOOMEYE_API_KEY env varijablu."""
    api_key = os.environ.get('ZOOMEYE_API_KEY', '')
    if not api_key:
        return []

    results = []
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    # ZoomEye koristi sličnu sintaksu kao Google dorks za web pretragu
    try:
        headers = {
            'API-KEY': api_key,
            'User-Agent': get_random_ua(),
        }
        params = {
            'query': dork,
            'page': 1,
            'pagesize': min(amount, 20),
            'resource': 'web',
        }
        resp = requests.get(
            'https://api.zoomeye.ai/web/search',
            headers=headers,
            params=params,
            proxies=proxies,
            timeout=20,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        for item in data.get('matches', [])[:amount]:
            url = item.get('url', '')
            if url:
                results.append(url)
    except:
        pass
    return results
