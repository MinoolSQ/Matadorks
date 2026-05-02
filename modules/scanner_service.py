import asyncio
import random
from urllib.parse import urlparse, urlunparse, parse_qs
from core.base_service import BaseService
from core.search import duckduckgo, brave, bing, google, publicwww
from core.proxy import get_google_pool
from core.config import (
    DOMAIN_BLACKLIST, SCANNER_AMOUNT, ASYNC_CONCURRENCY_LIMIT
)
from modules.ghdb_provider import GHDBProvider

SQLI_PARAMS = {"id", "cat", "user", "article", "page", "topic", "thread", "product", "item", "pid", "sid", "tid", "uid"}

class ScannerService(BaseService):
    """
    Independent service for dork scanning and URL discovery.
    Refactored from modules/scanner.py following the BaseService interface.
    """
    def __init__(self, name="Scanner", config=None, stats=None, app_state=None):
        super().__init__(name, config, stats)
        self.app_state = app_state
        self.amount = self.config.get("amount", SCANNER_AMOUNT)
        self.concurrency = self.config.get("concurrency", ASYNC_CONCURRENCY_LIMIT)
        self.semaphore = asyncio.Semaphore(self.concurrency)
        self.pool = None
        self.engines = [
            ("DuckDuckGo", duckduckgo),
            ("Brave", brave),
            ("Bing", bing),
            ("Google", google),
            ("PublicWWW", publicwww)
        ]
        self.dork_map = {}
        self.seen_urls = set()

    async def initialize(self):
        """Build proxy pool and load GHDB dork mappings."""
        self.pool = get_google_pool(auto_build=False)
        if self.pool.size() < 10:
            self.logger.info("Proxy pool low, rebuilding...")
            await self.pool.build_async(proto="socks5", max_test=2000, workers=200)
        
        provider = GHDBProvider()
        self.dork_map = provider.get_dork_map()
        self.logger.success(f"Scanner initialized. Engines: {[e[0] for e in self.engines]}. GHDB Mappings: {len(self.dork_map)}")

    def _normalize_url(self, url):
        try:
            p = urlparse(url)
            return urlunparse((p.scheme.lower(), p.netloc.lower(), 
                              p.path.rstrip('/'), p.params, p.query, ''))
        except:
            return url

    def _is_blacklisted(self, url):
        url_lower = url.lower()
        return any(domain in url_lower for domain in DOMAIN_BLACKLIST)

    def _is_sqli_candidate(self, url):
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return any(k.lower() in SQLI_PARAMS for k in params)
        except:
            return False

    async def process_item(self, dork):
        """
        Processes a single dork by querying a random search engine.
        Returns a list of discovered and filtered URL objects.
        """
        async with self.semaphore:
            proxy = self.pool.get_random()
            engine_name, engine_func = random.choice(self.engines)

            try:
                self.logger.debug(f"Scanning dork: {dork} via {engine_name}")
                results = await engine_func(dork, self.amount, proxy=proxy)
                
                if not results:
                    self.logger.debug(f"{engine_name} returned no results for {dork}")
                    # Only mark dead if we are sure it's a proxy issue, but for now we follow old logic
                    # if proxy: self.pool.mark_dead(proxy) 
                    return None

                output_items = []
                edb_id = self.dork_map.get(dork)

                for r in results:
                    if self._is_blacklisted(r): continue
                    if self.app_state and self.app_state.is_processed(r): continue
                    
                    norm = self._normalize_url(r)
                    if norm in self.seen_urls: continue
                    
                    self.seen_urls.add(norm)
                    
                    if self.app_state:
                        self.app_state.mark_processed(r)
                    
                    item = {"url": r, "dork": dork}
                    if edb_id:
                        item["edb_id"] = edb_id
                    
                    # Update shared stats if present
                    if self.stats:
                        self.stats.update(urls_scanned=self.stats.urls_scanned + 1)
                        if self._is_sqli_candidate(r):
                            self.stats.update(sqli_hits=self.stats.sqli_hits + 1)
                    
                    output_items.append(item)
                
                self.logger.debug(f"{engine_name} found {len(output_items)} valid URLs for {dork}")
                return output_items

            except Exception as e:
                self.logger.error(f"Scanner error for {engine_name} with dork '{dork}': {e}")
                if proxy: self.pool.mark_dead(proxy)
                return None

    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Scanner Service shutting down.")
        self.seen_urls.clear()
