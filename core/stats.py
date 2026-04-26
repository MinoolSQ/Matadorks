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
        
        # Queue sizes
        self.q_dork_size = 0
        self.q_url_size = 0
        self.q_valid_size = 0
        self.q_vuln_size = 0
        self._warnings_logged = set()
    
    def update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    setattr(self, k, v)

    def update_queues(self, orchestrator):
        """Thread-safe update of queue sizes from the orchestrator."""
        from core.logger import Logger
        with self._lock:
            # Map orchestrator queue attributes to stats attributes and human-readable names
            queues = {
                'q_dork': ('q_dork_size', 'Dorker'),
                'q_url': ('q_url_size', 'Scanner'),
                'q_valid': ('q_valid_size', 'Validator'),
                'q_vuln': ('q_vuln_size', 'Injector')
            }
            
            for q_attr, (size_attr, stage_name) in queues.items():
                if hasattr(orchestrator, q_attr):
                    q = getattr(orchestrator, q_attr)
                    current_size = q.qsize()
                    setattr(self, size_attr, current_size)
                    
                    # Performance Monitoring: log warning if full (with cooldown)
                    if q.maxsize > 0 and current_size >= q.maxsize:
                        if q_attr not in self._warnings_logged:
                            next_stages = {
                                'q_dork': 'Scanner',
                                'q_url': 'Validator',
                                'q_valid': 'Injector',
                                'q_vuln': 'Exploiter'
                            }
                            next_stage = next_stages.get(q_attr, "Next Stage")
                            Logger.warning(f"Bottleneck: {stage_name} is too fast for {next_stage} (Queue '{q_attr}' is FULL)")
                            self._warnings_logged.add(q_attr)
                    else:
                        if q_attr in self._warnings_logged:
                            self._warnings_logged.remove(q_attr)
