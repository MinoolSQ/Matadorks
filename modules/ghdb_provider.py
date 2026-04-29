import os
import xml.etree.ElementTree as ET
import logging
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logger import Logger

class GHDBProvider:
    def __init__(self, xml_path="data/exploit-database/ghdb.xml"):
        self.xml_path = xml_path

    def get_dork_map(self, categories=None):
        """Returns a dict mapping dork query to EDB-ID."""
        dork_map = {}
        if not os.path.exists(self.xml_path):
            return dork_map

        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()

            for entry in root.findall('entry'):
                category = entry.find('category').text if entry.find('category') is not None else ""
                query = entry.find('query').text if entry.find('query') is not None else ""
                edb_url = entry.find('edb').text if entry.find('edb') is not None else ""

                if not query:
                    continue

                if categories and category not in categories:
                    continue

                # Extract ID from edb url https://www.exploit-db.com/exploits/5616
                edb_id = edb_url.split('/')[-1] if edb_url else ""
                if edb_id:
                    dork_map[query] = edb_id
                
        except Exception as e:
            Logger.error(f"Failed to map GHDB: {e}")

        return dork_map

    def get_dorks(self, categories=None):
        """Parses ghdb.xml and returns a list of dorks."""
        dork_map = self.get_dork_map(categories)
        dorks = list(dork_map.keys())
        Logger.success(f"Loaded {len(dorks)} dorks from GHDB.")
        return dorks

if __name__ == "__main__":
    provider = GHDBProvider()
    # Example: only "Advisories and Vulnerabilities"
    vuln_dorks = provider.get_dorks(categories=["Advisories and Vulnerabilities"])
    for d in vuln_dorks[:10]:
        print(f"GHDB: {d}")
