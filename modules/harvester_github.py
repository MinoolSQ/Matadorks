import asyncio
import aiohttp
import re
import time
from urllib.parse import urlparse, parse_qs
from core.logger import Logger
from core.config import GITHUB_TOKEN, DOMAIN_BLACKLIST, HARVESTER_GITHUB_RATE

GITHUB_DORKS = [
    # PHP: old-style mysql_connect with real hosts
    'extension:php "mysql_connect" NOT "localhost" NOT "127.0.0.1"',
    # PHP: PDO with real host
    'extension:php "new PDO" "mysql:host=" NOT "localhost"',
    # WordPress non-default DB host
    'filename:wp-config.php "DB_HOST" NOT "localhost"',
    # Generic PHP config files
    'filename:config.php "$db_host" NOT "localhost"',
    'filename:database.php "password" NOT "localhost"',
    # Joomla
    'filename:configuration.php "public $password" NOT "localhost"',
    # Drupal
    'filename:settings.php "database" "password" NOT "localhost"',
    # .env with real DB hosts
    'filename:.env "DB_HOST" NOT "localhost" NOT "127.0.0.1"',
    'filename:.env "DATABASE_URL" "mysql://"',
    'filename:.env.production "DB_HOST"',
    'filename:.env.live "DB_HOST"',
    # Python/Django
    'filename:settings.py "DATABASES" "HOST" NOT "localhost"',
    'extension:py "mysql+pymysql://" NOT "localhost"',
    # Ruby on Rails
    'filename:database.yml "host:" NOT "localhost"',
    'extension:rb "mysql2://" NOT "localhost"',
    # Java / Spring Boot
    'filename:application.properties "spring.datasource.url" NOT "localhost"',
    'filename:application.yml "spring.datasource" NOT "localhost"',
    # Node.js
    'filename:db.js "host" "password" NOT "localhost"',
    'filename:knexfile.js "host" "password" NOT "localhost"',
    # .NET
    'extension:config "connectionString" "Password=" NOT "localhost"',
    # Docker Compose with exposed MySQL
    'filename:docker-compose.yml "MYSQL_ROOT_PASSWORD" "ports"',
    # CI/CD pipelines with real hosts
    'path:.github/workflows "DB_HOST" NOT "localhost"',
    # Deployment/error logs
    'extension:log "GET /" "HTTP/1" "mysql"',
]

# Direct http/https URLs in file content
URL_REGEX = re.compile(
    r'https?://(?!(?:www\.)?(?:localhost|127\.0\.0\.1|0\.0\.0\.0|'
    r'github\.com|example\.com|test\.com|placeholder)\b)'
    r'[a-zA-Z0-9][-a-zA-Z0-9._]*\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s"\'>]*)?'
)

# Extract hostnames from DB connection strings — second extraction pass
CONN_STRING_PATTERNS = [
    # mysql://user:pass@HOSTNAME/db  or  mysql://HOSTNAME/db
    re.compile(
        r'(?:mysql|postgres(?:ql)?|mariadb)(?:\+\w+)?://'
        r'[^@\s"\']*@([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})'
    ),
    # mysql:host=HOSTNAME;  (PDO)
    re.compile(r'(?:mysql|pgsql|dblib):host=([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})'),
    # mysql_connect("HOSTNAME",
    re.compile(r'mysql_connect\s*\(\s*["\']([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})["\']'),
    # $db_host = "HOSTNAME"  /  'host' => 'HOSTNAME'  /  "host": "HOSTNAME"
    re.compile(
        r'(?:db_host|DB_HOST|["\']host["\'])\s*(?:=>|=|:)\s*'
        r'["\']([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})["\']'
    ),
    # spring.datasource.url=jdbc:mysql://HOSTNAME/
    re.compile(r'datasource\.url\s*=\s*jdbc:\w+://([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})'),
    # Server=HOSTNAME;  (.NET connection strings)
    re.compile(r'(?:Server|Data Source)\s*=\s*([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})\s*;'),
]

SQLI_PARAMS = {"id", "cat", "user", "article", "page", "topic", "thread",
               "product", "item", "pid", "sid", "tid", "uid", "gid",
               "news_id", "post_id", "q", "query", "search"}

# Probe paths to try against discovered DB hosts
PROBE_PATHS = ["/?id=1", "/index.php?id=1", "/product.php?id=1", "/page.php?id=1"]

_IGNORE_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "example.com", "test.com",
    "placeholder.com", "yourdomain.com", "domain.com", "hostname",
    "your-domain.com", "mydomain.com",
}


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
        for page in range(1, 4):  # max 3 pages = 300 results per dork
            if self.abort and self.abort.is_set():
                return
            await self._rate_limit()
            try:
                url = f"https://api.github.com/search/code?q={dork}&per_page=100&page={page}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status in (422, 403):
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

                # Phase 1: direct http/https URLs that already have SQLi params
                for match in URL_REGEX.finditer(text):
                    url = match.group(0).rstrip('.,;"\'")')
                    filtered = self._filter_url(url)
                    if filtered and filtered not in self.seen_urls:
                        self.seen_urls.add(filtered)
                        await self.url_q.put(filtered)

                # Phase 2: DB connection strings → probe the host as web target
                for host in self._extract_db_hosts(text):
                    for path in PROBE_PATHS:
                        for scheme in ("https", "http"):
                            probe = f"{scheme}://{host}{path}"
                            if probe not in self.seen_urls:
                                self.seen_urls.add(probe)
                                await self.url_q.put(probe)
                        break  # one path per host is enough; Validator handles the rest
        except Exception:
            pass

    def _extract_db_hosts(self, text):
        hosts = set()
        for pattern in CONN_STRING_PATTERNS:
            for m in pattern.finditer(text):
                host = m.group(1).lower().strip()
                if not host or host in _IGNORE_HOSTS:
                    continue
                if host.startswith("127.") or host.startswith("10.") or host.startswith("192.168."):
                    continue
                if "example" in host or "test" in host or "placeholder" in host:
                    continue
                if any(d in host for d in DOMAIN_BLACKLIST):
                    continue
                hosts.add(host)
        return hosts

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
