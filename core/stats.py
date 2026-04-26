import threading

class PipelineStats:
    def __init__(self):
        self._lock = threading.Lock()
        self.phase = "idle"
        self.proxies_alive = 0
        self.urls_scanned = 0
        self.sqli_hits = 0
        self.validated = 0
        self.vulnerable = 0
        self.pwned = 0
    
    def update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    # Allow dynamic attributes if needed, or just ignore?
                    # For now, let's allow them but maybe log or just set
                    setattr(self, k, v)
