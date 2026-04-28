import asyncio
import aiohttp
import json
from urllib.parse import urlparse, parse_qs
from core.logger import Logger
from core.config import DOMAIN_BLACKLIST, HARVESTER_TARGETS_TLD
from core.proxy import get_async_session

SQLI_PARAMS = {"id", "cat", "user", "article", "page", "topic", "thread",
               "product", "item", "pid", "sid", "tid", "uid", "gid",
               "news_id", "post_id", "story", "q", "query", "search"}

COLLINFO_URL = "https://index.commoncrawl.org/collinfo.json"

class CommonCrawlHarvester:
    def __init__(self, url_q, proxy_pool, seen_urls, logger, abort=None):
        self.url_q = url_q
        self.proxy_pool = proxy_pool
        self.seen_urls = seen_urls
        self.logger = logger
        self.abort = abort
        self._index_id = None

    async def run(self):
        self.logger.status("[Harvester:CommonCrawl] Starting CommonCrawl CDX harvester...")
        proxy = self.proxy_pool.get_random() if self.proxy_pool else None
        async with get_async_session(proxy, timeout=30) as session:
            # Get latest crawl index
            self._index_id = await self._get_latest_index(session)
            if not self._index_id:
                self.logger.warning("[Harvester:CommonCrawl] Could not fetch index ID — skipping.")
                return
            self.logger.info(f"[Harvester:CommonCrawl] Using index: {self._index_id}")

            # Get seed domains from Wayback harvester logic (reuse Bing search)
            all_domains = []
            for tld in HARVESTER_TARGETS_TLD:
                if self.abort and self.abort.is_set():
                    break
                try:
                    from core.search import bing
                    proxy2 = self.proxy_pool.get_random() if self.proxy_pool else None
                    results = await bing(f"site:.{tld} inurl:?id=", 20, proxy=proxy2)
                    for url in results:
                        domain = urlparse(url).netloc
                        if domain and domain not in all_domains:
                            all_domains.append(domain)
                except Exception:
                    pass

            # Harvest each domain
            for domain in all_domains[:100]:  # cap at 100 domains
                if self.abort and self.abort.is_set():
                    break
                await asyncio.sleep(0.5)
                urls = await self._harvest_domain(session, domain)
                for url in urls:
                    if url not in self.seen_urls:
                        self.seen_urls.add(url)
                        await self.url_q.put(url)

        self.logger.success("[Harvester:CommonCrawl] Done.")

    async def _get_latest_index(self, session):
        """Fetch the most recent CommonCrawl index ID."""
        try:
            async with session.get(COLLINFO_URL, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data and len(data) > 0:
                    # First item is most recent
                    return data[0].get("cdx-api", "").split("/")[-2]
        except Exception:
            pass
        return None

    async def _harvest_domain(self, session, domain):
        """Query CommonCrawl CDX for a domain, return SQLi-candidate URLs."""
        results = []
        try:
            # Use the CDX API endpoint with the index
            cc_url = (
                f"https://index.commoncrawl.org/{self._index_id}-index"
                f"?url=*.{domain}/*"
                f"&output=json"
                f"&filter=status:200"
                f"&filter=url:*?*=*"
                f"&limit=1000"
            )
            async with session.get(cc_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    return results
                text = await resp.text()
                # Response is NDJSON — one JSON object per line
                for line in text.strip().split("\n"):
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        url = obj.get("url", "")
                        if url and self._has_sqli_param(url) and not self._is_blacklisted(url):
                            results.append(url)
                    except Exception:
                        pass
        except Exception:
            pass
        return results

    def _has_sqli_param(self, url):
        try:
            params = parse_qs(urlparse(url).query)
            return any(k.lower() in SQLI_PARAMS for k in params)
        except Exception:
            return False

    def _is_blacklisted(self, url):
        url_lower = url.lower()
        return any(d in url_lower for d in DOMAIN_BLACKLIST)
