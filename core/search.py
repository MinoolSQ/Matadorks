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
    
    # 1. Try AWS Gateway first if configured
    if AWS_GATEWAY_DDG:
        try:
            from duckduckgo_search import DDGS
            def _ddg_aws():
                with DDGS(proxy=None, timeout=10) as ddgs:
                    return [r.get('href') or r.get('url', '') for r in ddgs.text(dork, max_results=amount)]
            
            results = await asyncio.to_thread(_ddg_aws)
            results = [r for r in results if r]
            if results: return results
        except Exception:
            pass

    # 2. Fallback to free proxy pool (or primary if no AWS)
    try:
        from duckduckgo_search import DDGS
        def _ddg_local():
            with DDGS(proxy=proxy, timeout=12) as ddgs:
                return [r.get('href') or r.get('url', '') for r in ddgs.text(dork, max_results=amount)]
        
        results = await asyncio.to_thread(_ddg_local)
        results = [r for r in results if r]
    except Exception:
        pass
    return results

async def _parse_google_results(text):
    results = []
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        if href.startswith('/url?q='):
            real = urllib.parse.unquote(href[7:].split('&')[0])
            if real.startswith('http') and 'google.com' not in real:
                results.append(real)
    return results

async def google(dork, amount, proxy=None):
    headers = {
        'User-Agent': get_random_ua(),
        'Accept-Language': 'en-US,en;q=0.9',
    }
    query = urllib.parse.quote_plus(dork)
    tbs_param = f"&tbs=cdr:1,cd_min:1/1/{SEARCH_AFTER_YEAR}" if SEARCH_TIME_FILTER else ""
    
    # 1. Try AWS Gateway first if configured
    if AWS_GATEWAY_GOOGLE:
        try:
            async with get_cffi_session(None, timeout=12) as session:
                url = f"{AWS_GATEWAY_GOOGLE}/search?q={query}&num={amount}&hl=en&gl=us{tbs_param}"
                resp = await session.get(url, headers=headers)
                status = getattr(resp, 'status_code', getattr(resp, 'status', None))
                if status == 200:
                    try:
                        text = await resp.text()
                    except TypeError:
                        text = resp.text
                    results = await _parse_google_results(text)
                    if results: return results
        except Exception:
            pass
            
    # 2. Fallback to free proxy pool (or primary if no AWS)
    results = []
    try:
        async with get_cffi_session(proxy, timeout=10) as session:
            url = f"https://www.google.com/search?q={query}&num={amount}&hl=en&gl=us{tbs_param}"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
                results = await _parse_google_results(text)
    except Exception:
        pass
    return results

async def _parse_brave_results(text):
    results = []
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        if href.startswith('http') and 'brave.com' not in href and 'search.brave' not in href:
            results.append(href)
    return results

async def brave(dork, amount, proxy=None):
    headers = {'User-Agent': get_random_ua()}
    query = urllib.parse.quote_plus(dork)
    fresh_param = "&tf=y" if SEARCH_TIME_FILTER else ""
    
    # 1. Try AWS Gateway first if configured
    if AWS_GATEWAY_BRAVE:
        try:
            async with get_cffi_session(None, timeout=10) as session:
                url = f"{AWS_GATEWAY_BRAVE}/search?q={query}&source=web{fresh_param}"
                resp = await session.get(url, headers=headers)
                status = getattr(resp, 'status_code', getattr(resp, 'status', None))
                if status == 200:
                    try:
                        text = await resp.text()
                    except TypeError:
                        text = resp.text
                    results = await _parse_brave_results(text)
                    if results: return results
        except Exception:
            pass

    # 2. Fallback to free proxy pool (or primary if no AWS)
    results = []
    try:
        async with get_cffi_session(proxy, timeout=10) as session:
            url = f"https://search.brave.com/search?q={query}&source=web{fresh_param}"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
                results = await _parse_brave_results(text)
    except Exception:
        pass
    return results

async def _parse_bing_results(text):
    results = []
    soup = BeautifulSoup(text, 'html.parser')
    for li in soup.select('li.b_algo'):
        a = li.find('a')
        if a:
            href = a.get('href', '')
            if href.startswith('http') and 'bing.com' not in href:
                results.append(href)
    return results

async def bing(dork, amount, proxy=None):
    headers = {'User-Agent': get_random_ua()}
    query = urllib.parse.quote_plus(dork)
    after_param = f"&filters=ex1:%22ez5_{SEARCH_AFTER_YEAR}%22" if SEARCH_TIME_FILTER else ""
    
    # 1. Try AWS Gateway first if configured
    if AWS_GATEWAY_BING:
        try:
            async with get_cffi_session(None, timeout=12) as session:
                url = f"{AWS_GATEWAY_BING}/search?q={query}&count={amount}{after_param}"
                resp = await session.get(url, headers=headers)
                status = getattr(resp, 'status_code', getattr(resp, 'status', None))
                if status == 200:
                    try:
                        text = await resp.text()
                    except TypeError:
                        text = resp.text
                    results = await _parse_bing_results(text)
                    if results: return results
        except Exception:
            pass

    # 2. Fallback to free proxy pool (or primary if no AWS)
    results = []
    try:
        async with get_cffi_session(proxy, timeout=10) as session:
            url = f"https://www.bing.com/search?q={query}&count={amount}{after_param}"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
                results = await _parse_bing_results(text)
    except Exception:
        pass
    return results

async def _parse_yandex_results(text):
    results = []
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        if href.startswith('http') and 'yandex.' not in href:
            results.append(href)
    return results

async def yandex(dork, amount, proxy=None):
    headers = {'User-Agent': get_random_ua()}
    query = urllib.parse.quote_plus(dork)
    
    # 1. Try AWS Gateway first if configured
    if AWS_GATEWAY_YANDEX:
        try:
            async with get_cffi_session(None, timeout=12) as session:
                url = f"{AWS_GATEWAY_YANDEX}/search/xml?query={query}&results={amount}"
                resp = await session.get(url, headers=headers)
                status = getattr(resp, 'status_code', getattr(resp, 'status', None))
                if status == 200:
                    try:
                        text = await resp.text()
                    except TypeError:
                        text = resp.text
                    results = await _parse_yandex_results(text)
                    if results: return results
        except Exception:
            pass

    # 2. Fallback to free proxy pool (or primary if no AWS)
    results = []
    try:
        async with get_cffi_session(proxy, timeout=10) as session:
            url = f"https://yandex.com/search/xml?query={query}&results={amount}"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
                results = await _parse_yandex_results(text)
    except Exception:
        pass
    return results

async def publicwww(dork, amount, proxy=None):
    results = []
    headers = {'User-Agent': get_random_ua()}
    try:
        async with get_cffi_session(proxy, timeout=10) as session:
            query = urllib.parse.quote_plus(dork)
            url = f"https://publicwww.com/websites/{query}/"
            resp = await session.get(url, headers=headers)
            status = getattr(resp, 'status_code', getattr(resp, 'status', None))
            if status == 200:
                try:
                    text = await resp.text()
                except TypeError:
                    text = resp.text
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
