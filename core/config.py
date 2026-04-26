import os
DATA_DIR = "data"
VALIDATED_FILE = os.path.join(DATA_DIR, "validated_targets.txt")
VALIDATOR_THREADS = 20
VALIDATOR_TIMEOUT = 10
DOMAIN_BLACKLIST = [
    "youtube.com", "youtu.be", "reddit.com", "quora.com", "stackoverflow.com",
    "github.com", "github.io", "gitlab.com", "medium.com", "dev.to",
    "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
    "wikipedia.org", "w3schools.com", "geeksforgeeks.org", "microsoft.com",
    "google.com", "bing.com", "duckduckgo.com", "brave.com", "yandex.com",
    "torproject.org", "npmjs.com", "pypi.org", "hackerone.com", "bugcrowd.com",
    "exploit-db.com", "rapid7.com", "packetstormsecurity.com",
    "php.net", "bugs.php.net", "amazon.com", "apple.com", "pinterest.com",
    "oracle.com", "mysql.com", "laracasts.com", "stackexchange.com",
    "serverfault.com", "askubuntu.com", "wordpress.org", "pastebin.com",
    "gist.github.com", "bitbucket.org",
]
