import os

# --- Paths ---
DATA_DIR = "data"
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

# --- Scanner ---
SCANNER_THREADS = 20
SCANNER_AMOUNT = 50
SCANNER_PREFIX = "matadorks"
CONSECUTIVE_FAILURE_THRESHOLD = 20
COOLDOWN_SLEEP = 45

# --- Validator ---
VALIDATOR_THREADS = 20
VALIDATOR_TIMEOUT = 10

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
