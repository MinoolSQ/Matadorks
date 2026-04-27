import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
from core.logger import Logger
from core.config import (
    DOMAIN_BLACKLIST, HARVESTER_TARGETS_TLD,
    HARVESTER_CRT_FRESHNESS_DAYS, HARVESTER_PROBE_PATHS
)
from core.proxy import get_async_session

class CRTHarvester:
    def __init__(self, url_q, proxy_pool, seen_urls, logger, abort=None):
        self.url_q = url_q
        self.proxy_pool = proxy_pool
        self.seen_urls = seen_urls
        self.logger = logger
        self.abort = abort
        self.cutoff = datetime.now() - timedelta(days=HARVESTER_CRT_FRESHNESS_DAYS)

    async def run(self):
        self.logger.status("[Harvester:CRT] Starting Certificate Transparency harvester...")
        proxy = self.proxy_pool.get_random() if self.proxy_pool else None
        async with get_async_session(proxy, timeout=30) as session:
            for tld in HARVESTER_TARGETS_TLD:
                if self.abort and self.abort.is_set():
                    break
                await asyncio.sleep(1.0)  # rate limit crt.sh
                domains = await self._fetch_certs(session, tld)
                self.logger.info(f"[Harvester:CRT] .{tld}: {len(domains)} fresh domains")
                
                # Probe in batches of 20
                sem = asyncio.Semaphore(20)
                async def probe(domain):
                    async with sem:
                        await self._probe_domain(session, domain)
                
                await asyncio.gather(*[probe(d) for d in domains], return_exceptions=True)
        self.logger.success("[Harvester:CRT] Done.")

    async def _fetch_certs(self, session, tld):
        """Fetch recent domain names from crt.sh for a TLD."""
        domains = []
        try:
            url = f"https://crt.sh/?q=%.{tld}&output=json&exclude=expired&deduplicate=Y"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    return domains
                text = await resp.text()
                certs = json.loads(text)
                for cert in certs:
                    if not self._is_fresh(cert):
                        continue
                    name = cert.get("name_value", "") or cert.get("common_name", "")
                    for line in name.split("\n"):
                        line = line.strip().lstrip("*.")
                        if line and "." in line and not self._is_blacklisted(line):
                            if line not in domains:
                                domains.append(line)
        except Exception:
            pass
        return domains[:500]  # cap at 500 domains per TLD

    async def _probe_domain(self, session, domain):
        """Probe domain with SQLi paths, add live URLs to queue."""
        for path in HARVESTER_PROBE_PATHS:
            if self.abort and self.abort.is_set():
                return
            for scheme in ["https", "http"]:
                url = f"{scheme}://{domain}{path}"
                if url in self.seen_urls:
                    continue
                try:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=8),
                        allow_redirects=True
                    ) as resp:
                        if resp.status in (200, 301, 302, 403):
                            self.seen_urls.add(url)
                            await self.url_q.put(url)
                            return  # found alive, no need to try more paths
                except Exception:
                    pass

    def _is_fresh(self, cert):
        try:
            not_before_str = cert.get("not_before", "")
            if not not_before_str:
                return False
            # Format: "2024-01-15T12:34:56"
            not_before = datetime.fromisoformat(not_before_str.replace("Z", ""))
            return not_before >= self.cutoff
        except Exception:
            return False

    def _is_blacklisted(self, domain):
        domain_lower = domain.lower()
        return any(d in domain_lower for d in DOMAIN_BLACKLIST)
