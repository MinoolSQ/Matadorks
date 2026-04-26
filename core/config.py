import os
DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")
TCP_TIMEOUT = 1.5
HTTP_TIMEOUT = 6.0
TEST_URLS = ["https://httpbin.org/ip", "https://google.com", "https://bing.com"]
PROXY_MAX_TEST = 5000
PROXY_WORKERS = 200
