import os
DATA_DIR = "data"
VALIDATED_FILE = os.path.join(DATA_DIR, "validated_targets.txt")
VULNERABLE_FILE = os.path.join(DATA_DIR, "vulnerable_targets.txt")
DORKS_FILE = os.path.join(DATA_DIR, "sqli_dorks.txt")
PWNED_SUMMARY_FILE = os.path.join(DATA_DIR, "pwned_summary.txt")
EXPLOITATION_LOG_FILE = os.path.join(DATA_DIR, "exploitation.log")
SQLMAP_LEVEL = 2
SQLMAP_RISK = 1
SQLMAP_SCAN_TIMEOUT = 300
SQLMAP_CONCURRENT_SCANS = 5
SQLMAP_DBMS = "mysql"
SQLMAP_EXPLOIT_TIMEOUT = 600
PROXY_MAX_TEST = 5000
PROXY_WORKERS = 200
SCANNER_THREADS = 20
SCANNER_AMOUNT = 50
SCANNER_PREFIX = "matadorks"
