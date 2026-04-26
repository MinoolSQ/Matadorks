import queue
import threading
import time
from core.logger import Logger
from core.config import (
    QUEUE_MAX_DORK, QUEUE_MAX_URL, 
    QUEUE_MAX_VALID, QUEUE_MAX_VULN
)

class QueueManager:
    """
    Central nervous system for the Matadorks streaming pipeline.
    Manages queues and worker thread lifecycles.
    """
    def __init__(self, stats=None):
        self.queues = {
            'dork_q': queue.Queue(maxsize=QUEUE_MAX_DORK),
            'url_q': queue.Queue(maxsize=QUEUE_MAX_URL),
            'valid_q': queue.Queue(maxsize=QUEUE_MAX_VALID),
            'vuln_q': queue.Queue(maxsize=QUEUE_MAX_VULN)
        }
        self.workers = []
        self.logger = Logger()
        self.stats = stats
        self.running = False
        self._abort_event = threading.Event()

    def start_pipeline(self, app_instance):
        """
        Spawns worker threads for each pipeline stage.
        """
        self.logger.info("Initializing Pipeline Orchestrator (Streaming Mode)...")
        self.running = True
        self._abort_event = app_instance._abort_phase

        # Stages configuration: (Name, In Queue, Out Queue, Module Name, Function Name)
        stages = [
            ("Scanner",   'dork_q',  'url_q',   'modules.scanner',   'run_worker'),
            ("Validator", 'url_q',   'valid_q', 'modules.validator', 'main'),
            ("Injector",  'valid_q', 'vuln_q',  'modules.injector',  'main'),
            ("Exploiter", 'vuln_q',  None,      'modules.exploiter', 'main')
        ]

        for name, in_q_name, out_q_name, mod_name, func_name in stages:
            in_q = self.queues[in_q_name]
            out_q = self.queues[out_q_name] if out_q_name else None
            
            thread = threading.Thread(
                target=self._worker_wrapper,
                args=(name, mod_name, func_name, in_q, out_q, app_instance),
                name=f"{name}Worker",
                daemon=True
            )
            thread.start()
            self.workers.append(thread)
            self.logger.info(f"Worker {name} started.")

        self.logger.success("All pipeline workers are active and streaming.")

    def _worker_wrapper(self, name, mod_name, func_name, in_q, out_q, app):
        """Dynamic importer and executor for workers."""
        try:
            import importlib
            module = importlib.import_module(mod_name)
            worker_func = getattr(module, func_name)
            
            # Common interface: func(in_q, out_q, stats, abort)
            # Some functions might have slightly different signatures, 
            # we adapt based on what we know from Gemini refactors.
            if name == "Scanner":
                worker_func(in_q, out_q, stats=app.stats, abort=self._abort_event)
            elif name == "Validator":
                worker_func(in_q, out_q, stats=app.stats, abort=self._abort_event)
            elif name == "Injector":
                worker_func(in_q, out_q, stats=app.stats) # Injector Gemini version
            elif name == "Exploiter":
                worker_func(in_q, stats=app.stats) # Exploiter Gemini version (no out_q)
                
        except Exception as e:
            self.logger.error(f"Worker {name} critical error: {e}")
            # Propagate None to prevent pipeline hang if a stage dies
            if out_q:
                out_q.put(None)

    def push_dorks(self, dorks):
        """Feeds dorks into the start of the pipeline."""
        for d in dorks:
            self.queues['dork_q'].put(d)
        self.queues['dork_q'].put(None) # End of stream

    def wait_for_completion(self):
        """Wait until all workers finish their tasks."""
        for t in self.workers:
            if t.is_alive():
                t.join()
        self.logger.success("Pipeline finished processing all items.")

    def get_stats(self):
        """Returns the current size of all managed queues."""
        return {name: q.qsize() for name, q in self.queues.items()}
