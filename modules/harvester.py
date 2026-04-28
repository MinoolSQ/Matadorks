import asyncio
import os
from core.logger import Logger
import core.config
from core.proxy import get_google_pool

# Graceful fallback for missing config keys
USE_HARVESTER = getattr(core.config, "USE_HARVESTER", True)
GITHUB_TOKEN = getattr(core.config, "GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))

class HarvesterOrchestrator:
    def __init__(self, url_q, stats=None, abort=None):
        self.url_q = url_q
        self.stats = stats
        self.abort = abort
        self.logger = Logger()
        self.seen_urls = set()

    async def run(self):
        if not USE_HARVESTER:
            self.logger.info("[Harvester] USE_HARVESTER=False — skipping.")
            return

        pool = get_google_pool()

        # Import harvesters — graceful fallback if a module failed to build
        harvesters = []
        try:
            from modules.harvester_wayback import WaybackHarvester
            harvesters.append(WaybackHarvester(self.url_q, pool, self.seen_urls, self.logger, self.abort))
        except ImportError:
            self.logger.warning("[Harvester] harvester_wayback not available.")

        try:
            from modules.harvester_crt import CRTHarvester
            harvesters.append(CRTHarvester(self.url_q, pool, self.seen_urls, self.logger, self.abort))
        except ImportError:
            self.logger.warning("[Harvester] harvester_crt not available.")

        try:
            from modules.harvester_commoncrawl import CommonCrawlHarvester
            harvesters.append(CommonCrawlHarvester(self.url_q, pool, self.seen_urls, self.logger, self.abort))
        except ImportError:
            self.logger.warning("[Harvester] harvester_commoncrawl not available.")

        if GITHUB_TOKEN:
            try:
                from modules.harvester_github import GitHubHarvester
                harvesters.append(GitHubHarvester(self.url_q, pool, self.seen_urls, self.logger, self.abort))
            except ImportError:
                self.logger.warning("[Harvester] harvester_github not available.")
        else:
            self.logger.warning("[Harvester] No GITHUB_TOKEN — GitHub Harvester disabled.")

        if not harvesters:
            self.logger.warning("[Harvester] No harvesters available.")
            return

        self.logger.status(f"[Harvester] Starting {len(harvesters)} harvesters in parallel...")
        results = await asyncio.gather(*[h.run() for h in harvesters], return_exceptions=True)
        
        for r in results:
            if isinstance(r, Exception):
                self.logger.warning(f"[Harvester] A harvester raised: {r}")
        
        self.logger.success(f"[Harvester] All done. Harvested {len(self.seen_urls)} unique URLs.")
