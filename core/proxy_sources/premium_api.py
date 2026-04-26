import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.logger import Logger

class PremiumProxyScraper:
    def __init__(self):
        self.sources = {
            "proxyscrape": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=anonymous,elite",
            "geonode": "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc&protocols=http,https&anonymityLevel=elite&anonymityLevel=anonymous",
            "proxy_download": "https://www.proxy-list.download/api/v1/get?type=https&anon=elite"
        }
        self.scores_path = "data/proxy_scores.json"
        self.test_url = "https://www.google.com"
        self.timeout = 3

    def fetch_proxyscrape(self):
        try:
            resp = requests.get(self.sources["proxyscrape"], timeout=10)
            if resp.status_code == 200:
                proxies = [line.strip() for line in resp.text.splitlines() if line.strip()]
                return proxies
        except Exception as e:
            Logger.error(f"Error fetching ProxyScrape: {e}")
        return []

    def fetch_geonode(self):
        try:
            # GeoNode requires anonymityLevel filtering in URL if possible, or manual filter
            url = self.sources["geonode"] + "&anonymityLevel=elite&anonymityLevel=anonymous"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                proxies = []
                for entry in data.get("data", []):
                    ip = entry.get("ip")
                    port = entry.get("port")
                    if ip and port:
                        proxies.append(f"{ip}:{port}")
                return proxies
        except Exception as e:
            Logger.error(f"Error fetching GeoNode: {e}")
        return []

    def fetch_proxy_download(self):
        try:
            resp = requests.get(self.sources["proxy_download"], timeout=10)
            if resp.status_code == 200:
                proxies = [line.strip() for line in resp.text.splitlines() if line.strip()]
                return proxies
        except Exception as e:
            Logger.error(f"Error fetching Proxy-List.download: {e}")
        return []

    def validate_proxy(self, proxy_addr):
        proxy_url = f"http://{proxy_addr}"
        proxies = {"http": proxy_url, "https": proxy_url}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        try:
            start_time = time.time()
            # Mandatory Validation: Perform a full HTTP GET check against https://google.com (timeout 3s)
            resp = requests.get(self.test_url, proxies=proxies, timeout=self.timeout, headers=headers)
            if resp.status_code == 200:
                return True, time.time() - start_time
        except:
            pass
        return False, 0

    def run(self):
        Logger.info("Starting Premium Proxy Scraper...")
        all_proxies = []
        
        all_proxies.extend(self.fetch_proxyscrape())
        all_proxies.extend(self.fetch_geonode())
        all_proxies.extend(self.fetch_proxy_download())
        
        # Deduplicate
        unique_proxies = list(set(all_proxies))
        total_fetched = len(unique_proxies)
        Logger.info(f"Fetched {total_fetched} unique proxies. Starting validation...")

        working_proxies = []
        results = []

        with ThreadPoolExecutor(max_workers=50) as executor:
            future_to_proxy = {executor.submit(self.validate_proxy, p): p for p in unique_proxies}
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                is_working, latency = future.result()
                if is_working:
                    working_proxies.append(proxy)
                    results.append({"proxy": proxy, "latency": latency})

        working_count = len(working_proxies)
        workrate = (working_count / total_fetched * 100) if total_fetched > 0 else 0
        
        Logger.success(f"Validation finished. Working: {working_count}/{total_fetched} ({workrate:.2f}%)")

        self.save_scores(workrate, working_count, total_fetched)
        return working_proxies

    def save_scores(self, workrate, working_count, total_fetched):
        score_data = {
            "timestamp": time.time(),
            "workrate": workrate,
            "working_count": working_count,
            "total_fetched": total_fetched,
            "provider": "premium_api_rotation"
        }
        
        history = []
        if os.path.exists(self.scores_path):
            try:
                with open(self.scores_path, "r") as f:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = [history]
            except:
                history = []
        
        history.append(score_data)
        history = history[-50:] # Keep only last 50 entries
        
        os.makedirs(os.path.dirname(self.scores_path), exist_ok=True)
        with open(self.scores_path, "w") as f:
            json.dump(history, f, indent=4)
        Logger.info(f"Scores saved to {self.scores_path}")

if __name__ == "__main__":
    scraper = PremiumProxyScraper()
    scraper.run()
