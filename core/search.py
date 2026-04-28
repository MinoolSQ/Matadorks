import asyncio
import aiohttp
import random
import re
from bs4 import BeautifulSoup
import urllib.parse
from core.config import ASYNC_CONCURRENCY_LIMIT
from core.proxy import get_async_session

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

def get_random_ua():
    return random.choice(USER_AGENTS)

async def duckduckgo(dork, amount, proxy=None):
    results = []
    try:
        from duckduckgo_search import AsyncDDGS
        async with AsyncDDGS(proxy=proxy, timeout=10) as ddgs:
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
        async with get_async_session(proxy, timeout=12) as session:
            query = urllib.parse.quote_plus(dork)
            url = f"https://www.google.com/search?q={query}&num={amount}&hl=en&gl=us"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
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
        async with get_async_session(proxy, timeout=10) as session:
            query = urllib.parse.quote_plus(dork)
            url = f"https://search.brave.com/search?q={query}&source=web"
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
        async with get_async_session(proxy, timeout=12) as session:
            query = urllib.parse.quote_plus(dork)
            url = f"https://www.bing.com/search?q={query}&count={amount}"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
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
