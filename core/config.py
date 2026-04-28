import os
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
DATA_DIR = "data"
DORKS_DATA_DIR = os.path.join(DATA_DIR, "dorks")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
DORKS_FILE = os.path.join(DATA_DIR, "sqli_dorks.txt")
VALIDATED_FILE = os.path.join(DATA_DIR, "validated_targets.txt")
VULNERABLE_FILE = os.path.join(DATA_DIR, "vulnerable_targets.txt")
PWNED_SUMMARY_FILE = os.path.join(DATA_DIR, "pwned_summary.txt")
EXPLOITATION_LOG_FILE = os.path.join(DATA_DIR, "exploitation.log")

# --- Proxy ---
TCP_TIMEOUT = 1.5
HTTP_TIMEOUT = 6.0
TEST_URLS = ["https://httpbin.org/ip", "https://google.com", "https://bing.com"]
PROXY_MAX_TEST = 5000
PROXY_WORKERS = 200
USE_TOR = False # Set to True if you have Tor running on 127.0.0.1:9050
PRIVATE_PROXIES_FILE = os.path.join(DATA_DIR, "private_proxies.txt")

# --- Scanner ---
SCANNER_THREADS = 20
SCANNER_BATCH_SIZE = 10
SCANNER_AMOUNT = 50
SCANNER_PREFIX = "matadorks"
CONSECUTIVE_FAILURE_THRESHOLD = 20
COOLDOWN_SLEEP = 45
USE_PUBLICWWW = True
USE_STARTPAGE = True

# --- Validator ---
VALIDATOR_THREADS = 20
VALIDATOR_BATCH_SIZE = 10
VALIDATOR_TIMEOUT = 10

# --- Queues ---
QUEUE_MAX_DORK = 1000
QUEUE_MAX_URL = 5000
QUEUE_MAX_VALID = 1000
QUEUE_MAX_VULN = 500
ASYNC_CONCURRENCY_LIMIT = 1000

# --- SQLMap (Injector) ---
SQLMAP_LEVEL = 2
SQLMAP_RISK = 1
SQLMAP_SCAN_TIMEOUT = 300
SQLMAP_CONCURRENT_SCANS = 5
SQLMAP_DBMS = ""
USE_GHAURI_FALLBACK = True

# --- Exploiter ---
SQLMAP_EXPLOIT_TIMEOUT = 600
EXPLOITER_CONCURRENT = 3

# --- Harvester ---
HARVESTER_TARGETS_TLD = ["de", "cz", "pl", "hu", "ro", "sk", "bg", "at", "ch"]
HARVESTER_WAYBACK_LIMIT = 5000
HARVESTER_CRT_FRESHNESS_DAYS = 90
HARVESTER_PROBE_PATHS = [
    "/?id=1", "/index.php?id=1", "/page.php?id=1",
    "/article.php?id=1", "/product.php?id=1",
    "/news.php?id=1", "/item.php?cat=1",
    "/view.php?id=1", "/details.php?id=1",
]

# --- Unified Domain Blacklist ---
DOMAIN_BLACKLIST = [
    "youtube.com", "youtu.be", "reddit.com", "quora.com", "stackoverflow.com",
    "github.com", "github.io", "gitlab.com", "medium.com", "dev.to",
    "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
    "wikipedia.org", "w3schools.com", "geeksforgeeks.org", "microsoft.com",
    "google.com", "bing.com", "duckduckgo.com", "brave.com", "yandex.com",
    "torproject.org", "npmjs.com", "pypi.org", "hackerone.com", "bugcrowd.com",
    "exploit-db.com", "rapid7.com", "packetstormsecurity.com",
    "php.net", "bugs.php.net", "ni.com", "support.microsoft.com", "docs.microsoft.com",
    "amazon.com", "apple.com", "pinterest.com", "adobe.com",
    "oracle.com", "mysql.com", "laracasts.com", "stackexchange.com",
    "serverfault.com", "askubuntu.com", "wordpress.org", "pastebin.com",
    "gist.github.com", "bitbucket.org",
]

# --- AWS API Gateway (IP Rotation) ---
AWS_GATEWAY_GOOGLE = os.getenv("AWS_GATEWAY_GOOGLE", "")
AWS_GATEWAY_BING = os.getenv("AWS_GATEWAY_BING", "")
AWS_GATEWAY_BRAVE = os.getenv("AWS_GATEWAY_BRAVE", "")
AWS_GATEWAY_YANDEX = os.getenv("AWS_GATEWAY_YANDEX", "")
AWS_GATEWAY_DDG = os.getenv("AWS_GATEWAY_DDG", "")
USE_AWS_GATEWAY = any([AWS_GATEWAY_GOOGLE, AWS_GATEWAY_BING, AWS_GATEWAY_BRAVE, AWS_GATEWAY_YANDEX, AWS_GATEWAY_DDG])

# --- Time Range Filter ---
SEARCH_TIME_FILTER = True
SEARCH_AFTER_YEAR = 2020

# --- Harvester ---
USE_HARVESTER = True
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HARVESTER_TARGETS_TLD = ["de", "cz", "pl", "hu", "ro", "sk", "bg", "at", "ch"]
HARVESTER_WAYBACK_LIMIT = 5000
HARVESTER_GITHUB_RATE = 1.0
HARVESTER_CRT_FRESHNESS_DAYS = 90
HARVESTER_PROBE_PATHS = [
    "/?id=1", "/index.php?id=1", "/page.php?id=1",
    "/article.php?id=1", "/product.php?id=1",
    "/news.php?id=1", "/item.php?cat=1",
    "/view.php?id=1", "/details.php?id=1",
]
