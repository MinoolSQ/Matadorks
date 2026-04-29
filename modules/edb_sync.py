import os
import subprocess
import csv
import logging
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logger import Logger

class EDBSync:
    def __init__(self, base_path="data/exploit-database"):
        self.base_path = base_path
        self.repo_url = "https://gitlab.com/exploit-database/exploitdb.git"
        self.csv_path = os.path.join(self.base_path, "files_exploits.csv")

    def sync(self):
        """Clones or pulls the latest exploit-database from GitLab."""
        if not os.path.exists(self.base_path):
            Logger.info(f"Cloning Exploit-DB repository from GitLab to {self.base_path}...")
            try:
                # GitLab uses 'main' as default branch
                subprocess.run(["git", "clone", "--depth", "1", self.repo_url, self.base_path], check=True)
                Logger.success("Exploit-DB cloned successfully from GitLab.")
            except subprocess.CalledProcessError as e:
                Logger.error(f"Failed to clone Exploit-DB: {e}")
                return False
        else:
            Logger.info("Updating Exploit-DB repository...")
            try:
                subprocess.run(["git", "-C", self.base_path, "pull"], check=True)
                Logger.success("Exploit-DB updated successfully.")
            except subprocess.CalledProcessError as e:
                Logger.warning(f"Failed to update Exploit-DB: {e}. Using existing data.")
        
        return os.path.exists(self.csv_path)

    def search_by_cve(self, cve_id):
        """Searches for exploits related to a specific CVE."""
        results = []
        if not os.path.exists(self.csv_path):
            return results
        
        with open(self.csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if cve_id.lower() in row.get('codes', '').lower():
                    results.append(row)
        return results

    def get_exploit_path(self, edb_id):
        """Returns the local path to the exploit file."""
        if not os.path.exists(self.csv_path):
            return None
        
        with open(self.csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('id') == str(edb_id):
                    relative_path = row.get('file')
                    return os.path.join(self.base_path, relative_path)
        return None

if __name__ == "__main__":
    sync_engine = EDBSync()
    if sync_engine.sync():
        with open(sync_engine.csv_path, mode='r', encoding='utf-8') as f:
            count = sum(1 for line in f) - 1
            Logger.info(f"Total exploits indexed: {count}")
