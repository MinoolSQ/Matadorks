import asyncio
import aiohttp
import random
import re
import contextlib
from bs4 import BeautifulSoup
import urllib.parse
from core.config import (
    ASYNC_CONCURRENCY_LIMIT,
    AWS_GATEWAY_GOOGLE, AWS_GATEWAY_BING,
    AWS_GATEWAY_BRAVE, AWS_GATEWAY_YANDEX, AWS_GATEWAY_DDG,
    SEARCH_TIME_FILTER, SEARCH_AFTER_YEAR,
)
from core.cffi_session import get_cffi_session

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

@contextlib.asynccontextmanager
async def get_async_session(proxy=None, timeout=10):
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        original_get = session.get
        def proxied_get(url, **kwargs):
            if proxy and 'proxy' not in kwargs:
                kwargs['proxy'] = proxy
            return original_get(url, **kwargs)
        session.get = proxied_get
        yield session

async def duckduckgo(dork, amount, proxy=None):
    results = []
    try:
        from duckduckgo_search import AsyncDDGS
        active_proxy = AWS_GATEWAY_DDG if AWS_GATEWAY_DDG else proxy
        async with AsyncDDGS(proxy=active_proxy, timeout=10) as ddgs:
            async for r in ddgs.text(dork, max_results=amount):
                href = r.get('href') or r.get('url', '')
                if href:
                    results.append(href)
    except Exception:
        pass
    return results

async def google(dork, amount, proxy=None):
    results = []
    headers = {
        'User-Agent': get_random_ua(),
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        base = AWS_GATEWAY_GOOGLE if AWS_GATEWAY_GOOGLE else "https://www.google.com"
        active_proxy = None if AWS_GATEWAY_GOOGLE else proxy
        async with get_cffi_session(active_proxy, timeout=12) as session:
            query = urllib.parse.quote_plus(dork)
            tbs_param = f"&tbs=cdr:1,cd_min:1/1/{SEARCH_AFTER_YEAR}" if SEARCH_TIME_FILTER else ""
            url = f"{base}/search?q={query}&num={amount}&hl=en&gl=us{tbs_param}"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
                soup = BeautifulSoup(text, 'html.parser')
                for a in soup.select('a[href]'):
                    href = a.get('href', '')
                    if href.startswith('/url?q='):
                        real = urllib.parse.unquote(href[7:].split('&')[0])
                        if real.startswith('http') and 'google.com' not in real:
                            results.append(real)
    except Exception:
        pass
    return results

async def brave(dork, amount, proxy=None):
    results = []
    headers = {'User-Agent': get_random_ua()}
    try:
        base = AWS_GATEWAY_BRAVE if AWS_GATEWAY_BRAVE else "https://search.brave.com"
        active_proxy = None if AWS_GATEWAY_BRAVE else proxy
        async with get_async_session(active_proxy, timeout=10) as session:
            query = urllib.parse.quote_plus(dork)
            fresh_param = "&tf=y" if SEARCH_TIME_FILTER else ""
            url = f"{base}/search?q={query}&source=web{fresh_param}"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    for a in soup.select('a[href]'):
                        href = a.get('href', '')
                        if href.startswith('http') and 'brave.com' not in href and 'search.brave' not in href:
                            results.append(href)
    except Exception:
        pass
    return results

async def bing(dork, amount, proxy=None):
    results = []
    headers = {'User-Agent': get_random_ua()}
    try:
        base = AWS_GATEWAY_BING if AWS_GATEWAY_BING else "https://www.bing.com"
        active_proxy = None if AWS_GATEWAY_BING else proxy
        async with get_cffi_session(active_proxy, timeout=12) as session:
            query = urllib.parse.quote_plus(dork)
            after_param = f"&filters=ex1:%22ez5_{SEARCH_AFTER_YEAR}%22" if SEARCH_TIME_FILTER else ""
            url = f"{base}/search?q={query}&count={amount}{after_param}"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
                soup = BeautifulSoup(text, 'html.parser')
                for li in soup.select('li.b_algo'):
                    a = li.find('a')
                    if a:
                        href = a.get('href', '')
                        if href.startswith('http') and 'bing.com' not in href:
                            results.append(href)
    except Exception:
        pass
    return results

async def yandex(dork, amount, proxy=None):
    results = []
    headers = {'User-Agent': get_random_ua()}
    try:
        base = AWS_GATEWAY_YANDEX if AWS_GATEWAY_YANDEX else "https://yandex.com"
        active_proxy = None if AWS_GATEWAY_YANDEX else proxy
        async with get_async_session(active_proxy, timeout=12) as session:
            query = urllib.parse.quote_plus(dork)
            url = f"{base}/search/xml?query={query}&results={amount}"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    for a in soup.select('a[href]'):
                        href = a.get('href', '')
                        if href.startswith('http') and 'yandex.' not in href:
                            results.append(href)
    except Exception:
        pass
    return results

async def publicwww(dork, amount, proxy=None):
    results = []
    headers = {'User-Agent': get_random_ua()}
    try:
        async with get_async_session(proxy, timeout=15) as session:
            query = urllib.parse.quote_plus(dork)
            url = f"https://publicwww.com/websites/{query}/"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    for a in soup.select('a.site, td > a[target="_blank"]'):
                        href = a.get('href', '')
                        if href.startswith('http') and 'publicwww.com' not in href:
                            results.append(href)
                        elif '.' in href:
                            results.append(f"http://{href.strip('/')}/")
    except Exception:
        pass
    return results
