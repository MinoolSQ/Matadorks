import asyncio
import aiohttp
import re
import time
from urllib.parse import urlparse, parse_qs
from core.logger import Logger
from core.config import GITHUB_TOKEN, DOMAIN_BLACKLIST, HARVESTER_GITHUB_RATE

GITHUB_DORKS = [
    'filename:deploy.log "Successfully deployed to" "http"',
    'filename:deploy.log "Base URL:" "http"',
    'extension:log "Connected to" "port 3306" "http"',
    'filename:.env "APP_URL=" "http"',
    'filename:.env "BACKEND_URL=" "http"',
    'filename:docker-compose.yml "APP_URL" "http"',
    'filename:docker-compose.yml "VIRTUAL_HOST"',
    'filename:cypress.json "baseUrl" "http"',
    'path:.github/workflows "env:" "url" "http"',
    'filename:pytest.ini "base_url" "http"',
]

URL_REGEX = re.compile(
    r'https?://(?!(?:www\.)?(?:localhost|127\.0\.0\.1|github\.com|'
    r'example\.com|0\.0\.0\.0|test\.com)\b)'
    r'[a-zA-Z0-9][-a-zA-Z0-9._]*\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s"\'>]*)?'
)

SQLI_PARAMS = {"id", "cat", "user", "article", "page", "topic", "thread",
               "product", "item", "pid", "sid", "tid", "uid", "gid",
               "news_id", "post_id", "q", "query"}

class GitHubHarvester:
    def __init__(self, url_q, proxy_pool, seen_urls, logger, abort=None):
        self.url_q = url_q
        self.proxy_pool = proxy_pool
        self.seen_urls = seen_urls
        self.logger = logger
        self.abort = abort
        self._last_request = 0.0

    async def run(self):
        if not GITHUB_TOKEN:
            self.logger.warning("[Harvester:GitHub] No GITHUB_TOKEN — skipping.")
            return
        self.logger.status("[Harvester:GitHub] Starting GitHub Code Search harvester...")
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3.text-match+json",
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            for dork in GITHUB_DORKS:
                if self.abort and self.abort.is_set():
                    break
                await self._search_dork(session, dork)
        self.logger.success("[Harvester:GitHub] Done.")

    async def _rate_limit(self):
        elapsed = time.monotonic() - self._last_request
        wait = HARVESTER_GITHUB_RATE - elapsed
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = time.monotonic()

    async def _search_dork(self, session, dork):
        for page in range(1, 4):  # max 3 pages = 300 results
            if self.abort and self.abort.is_set():
                return
            await self._rate_limit()
            try:
                url = f"https://api.github.com/search/code?q={dork}&per_page=100&page={page}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 422 or resp.status == 403:
                        return
                    if resp.status != 200:
                        return
                    data = await resp.json()
                    items = data.get("items", [])
                    if not items:
                        return
                    for item in items:
                        raw_url = item.get("html_url", "").replace(
                            "github.com", "raw.githubusercontent.com"
                        ).replace("/blob/", "/")
                        if raw_url:
                            await self._extract_from_file(session, raw_url)
                    if len(items) < 100:
                        return
            except Exception:
                return

    async def _extract_from_file(self, session, raw_url):
        await self._rate_limit()
        try:
            async with session.get(raw_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return
                text = await resp.text()
                for match in URL_REGEX.finditer(text):
                    url = match.group(0).rstrip('.,;"\'")')
                    filtered = self._filter_url(url)
                    if filtered and filtered not in self.seen_urls:
                        self.seen_urls.add(filtered)
                        await self.url_q.put(filtered)
        except Exception:
            pass

    def _filter_url(self, url):
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return None
            if any(d in parsed.netloc for d in DOMAIN_BLACKLIST):
                return None
            params = parse_qs(parsed.query)
            if not any(k.lower() in SQLI_PARAMS for k in params):
                return None
            return url
        except Exception:
            return None
