import asyncio
import aiohttp
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from core.logger import Logger
from core.config import (
    DOMAIN_BLACKLIST, HARVESTER_TARGETS_TLD,
    HARVESTER_WAYBACK_LIMIT
)
from core.proxy import get_async_session

SQLI_PARAMS = {"id", "cat", "user", "article", "page", "topic", "thread",
               "product", "item", "pid", "sid", "tid", "uid", "gid",
               "news_id", "post_id", "story", "q", "query", "search"}

class WaybackHarvester:
    def __init__(self, url_q, proxy_pool, seen_urls, logger, abort=None):
        self.url_q = url_q
        self.proxy_pool = proxy_pool
        self.seen_urls = seen_urls
        self.logger = logger
        self.abort = abort

    async def run(self):
        self.logger.status("[Harvester:Wayback] Starting Wayback Machine CDX harvester...")
        proxy = self.proxy_pool.get_random() if self.proxy_pool else None
        async with get_async_session(proxy, timeout=30) as session:
            for tld in HARVESTER_TARGETS_TLD:
                if self.abort and self.abort.is_set():
                    break
                seed_domains = await self._get_seed_domains(session, tld)
                for domain in seed_domains:
                    if self.abort and self.abort.is_set():
                        break
                    await asyncio.sleep(0.5)  # rate limit
                    urls = await self._harvest_domain(session, domain)
                    for url in urls:
                        if url not in self.seen_urls:
                            self.seen_urls.add(url)
                            await self.url_q.put(url)
        self.logger.success("[Harvester:Wayback] Done.")

    async def _get_seed_domains(self, session, tld):
        """Get seed domains for a TLD via Bing search."""
        domains = []
        try:
            from core.search import bing
            proxy = self.proxy_pool.get_random() if self.proxy_pool else None
            results = await bing(f"site:.{tld} inurl:?id=", 30, proxy=proxy)
            for url in results:
                try:
                    domain = urlparse(url).netloc
                    if domain and domain not in domains:
                        domains.append(domain)
                except Exception:
                    pass
        except Exception:
            pass
        return domains[:20]  # max 20 seed domains per TLD

    async def _harvest_domain(self, session, domain):
        """Query Wayback CDX API for a domain, return SQLi-candidate URLs."""
        results = []
        try:
            cdx_url = (
                f"https://web.archive.org/cdx/search/cdx"
                f"?url=*.{domain}/*"
                f"&output=json"
                f"&fl=original"
                f"&collapse=urlkey"
                f"&filter=statuscode:200"
                f"&filter=original:.*\\?.*=.*"
                f"&limit={HARVESTER_WAYBACK_LIMIT}"
                f"&from=20200101"
            )
            async with session.get(cdx_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    return results
                text = await resp.text()
                rows = json.loads(text)
                # First row is header ["original"], skip it
                for row in rows[1:]:
                    if not row:
                        continue
                    url = row[0] if isinstance(row, list) else row
                    if self._has_sqli_param(url) and not self._is_blacklisted(url):
                        results.append(url)
        except Exception:
            pass
        return results

    def _has_sqli_param(self, url):
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return any(k.lower() in SQLI_PARAMS for k in params)
        except Exception:
            return False

    def _is_blacklisted(self, url):
        url_lower = url.lower()
        return any(d in url_lower for d in DOMAIN_BLACKLIST)
