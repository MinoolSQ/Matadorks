import json
import os
from core.config import STATE_FILE

class State:
    def __init__(self):
        self.data = self._load()
        if "processed_urls" not in self.data:
            self.data["processed_urls"] = []
        # Koristimo set u memoriji za O(1) proveru, ali čuvamo kao listu u JSON-u
        self._processed_set = set(self.data["processed_urls"])

    def is_processed(self, url):
        return url in self._processed_set

    def mark_processed(self, url):
        if url not in self._processed_set:
            self._processed_set.add(url)
            self.data["processed_urls"].append(url)
            self.save()

    def _load(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save(self):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def update_phase(self, phase_name, status="completed"):
        if "phases" not in self.data:
            self.data["phases"] = {}
        self.data["phases"][phase_name] = status
        self.save()
