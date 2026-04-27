from contextlib import asynccontextmanager
from core.config import USE_JA3_MIMICRY, JA3_BROWSER

@asynccontextmanager
async def get_cffi_session(proxy_url=None, timeout=10, impersonate=None):
    """Async context manager that mimics browser TLS fingerprint via curl-cffi."""
    if not USE_JA3_MIMICRY:
        # Fallback to aiohttp when JA3 mimicry is disabled
        import aiohttp
        from aiohttp_socks import ProxyConnector
        connector = None
        if proxy_url and proxy_url.startswith(("socks", "http")):
            connector = ProxyConnector.from_url(proxy_url)
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
            yield session
        return

    try:
        from curl_cffi.requests import AsyncSession
        browser = impersonate or JA3_BROWSER
        proxies = {"https": proxy_url, "http": proxy_url} if proxy_url else None
        async with AsyncSession(impersonate=browser, timeout=timeout, proxies=proxies) as session:
            yield session
    except ImportError:
        # curl_cffi not installed — fallback to aiohttp
        import aiohttp
        from aiohttp_socks import ProxyConnector
        connector = None
        if proxy_url and proxy_url.startswith(("socks", "http")):
            connector = ProxyConnector.from_url(proxy_url)
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
            yield session
