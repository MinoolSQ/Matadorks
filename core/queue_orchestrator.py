import asyncio
import importlib
from core.logger import Logger
from core.config import (
    QUEUE_MAX_DORK, QUEUE_MAX_URL, 
    QUEUE_MAX_VALID, QUEUE_MAX_VULN
)

class QueueManager:
    """
    Central nervous system for the Matadorks asynchronous streaming pipeline.
    Manages async queues and worker task lifecycles.
    """
    def __init__(self, stats=None):
        self.q_dork = asyncio.Queue(maxsize=QUEUE_MAX_DORK)
        self.q_url = asyncio.Queue(maxsize=QUEUE_MAX_URL)
        self.q_valid = asyncio.Queue(maxsize=QUEUE_MAX_VALID)
        self.q_vuln = asyncio.Queue(maxsize=QUEUE_MAX_VULN)
        
        self.queues = {
            'dork_q': self.q_dork,
            'url_q': self.q_url,
            'valid_q': self.q_valid,
            'vuln_q': self.q_vuln
        }
        self.tasks = []
        self.logger = Logger()
        self.stats = stats
        self.running = False
        self._abort_event = None

    async def start_pipeline(self, app_instance):
        """
        Spawns asynchronous worker tasks for each pipeline stage.
        """
        self.logger.info("Initializing Async Pipeline Orchestrator...")
        self.running = True
        self._abort_event = app_instance._abort_phase # Assuming this becomes an asyncio.Event or similar

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
            
            task = asyncio.create_task(
                self._worker_wrapper(name, mod_name, func_name, in_q, out_q, app_instance),
                name=f"{name}Worker"
            )
            self.tasks.append(task)
            self.logger.info(f"Worker task {name} started.")

        self.logger.success("All async pipeline workers are active.")

    async def _worker_wrapper(self, name, mod_name, func_name, in_q, out_q, app):
        """Dynamic importer and executor for async workers."""
        try:
            module = importlib.import_module(mod_name)
            worker_func = getattr(module, func_name)
            
            # Note: worker_func MUST be an async function (coroutine)
            if name == "Scanner":
                await worker_func(in_q, out_q, stats=app.stats, abort=self._abort_event)
            elif name == "Validator":
                await worker_func(in_q, out_q, stats=app.stats, abort=self._abort_event)
            elif name == "Injector":
                await worker_func(in_q, out_q, stats=app.stats)
            elif name == "Exploiter":
                await worker_func(in_q, stats=app.stats)
                
        except Exception as e:
            self.logger.error(f"Worker {name} critical error: {e}")
            if out_q:
                await out_q.put(None)

    async def push_dorks(self, dorks):
        """Feeds dorks into the start of the pipeline."""
        for d in dorks:
            await self.queues['dork_q'].put(d)
        await self.queues['dork_q'].put(None) # End of stream marker

    async def wait_for_completion(self):
        """Wait until all worker tasks finish their work."""
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        self.logger.success("Async pipeline finished processing all items.")

    def get_stats(self):
        """Returns the current size of all managed queues."""
        return {name: q.qsize() for name, q in self.queues.items()}
