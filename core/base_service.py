from abc import ABC, abstractmethod
import asyncio
from core.logger import Logger

class BaseService(ABC):
    """
    Base class for all Matadorks services.
    Provides a standardized interface for independent execution and pipeline integration.
    """
    def __init__(self, name, config=None, stats=None):
        self.name = name
        self.config = config or {}
        self.stats = stats
        self.logger = Logger()
        self.running = False
        self._processed_count = 0
        self._error_count = 0

    @abstractmethod
    async def initialize(self):
        """Perform async initialization (e.g., opening sessions, loading data)."""
        pass

    @abstractmethod
    async def process_item(self, item):
        """
        Process a single item from the input queue.
        Must return the result to be passed to the next stage, or None to drop.
        Can return a list of items to push multiple results.
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """Cleanup resources (e.g., closing sessions, flushing buffers)."""
        pass

    async def run(self, in_q: asyncio.Queue, out_q: asyncio.Queue = None, abort_event: asyncio.Event = None):
        """
        Standardized execution loop for the service.
        Consumes from in_q and optionally produces to out_q.
        """
        self.running = True
        self.logger.info(f"Service {self.name} started.")
        await self.initialize()

        try:
            while self.running:
                if abort_event and abort_event.is_set():
                    self.logger.warning(f"Service {self.name} received abort signal.")
                    break

                try:
                    # Short timeout to allow checking abort_event and loop condition
                    item = await asyncio.wait_for(in_q.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                if item is None:
                    # End of stream signal
                    self.logger.debug(f"Service {self.name} received End-of-Stream.")
                    if out_q:
                        await out_q.put(None)
                    in_q.task_done()
                    break

                try:
                    result = await self.process_item(item)
                    if out_q and result is not None:
                        if isinstance(result, list):
                            for r in result:
                                await out_q.put(r)
                        else:
                            await out_q.put(result)
                    
                    self._processed_count += 1
                except Exception as e:
                    self._error_count += 1
                    self.logger.error(f"Service {self.name} error processing item '{item}': {e}")
                finally:
                    in_q.task_done()
        
        except Exception as e:
            self.logger.critical(f"Service {self.name} loop encountered a fatal error: {e}")
        finally:
            await self.shutdown()
            self.running = False
            self.logger.info(f"Service {self.name} shutdown. Processed: {self._processed_count}, Errors: {self._error_count}")

    def get_stats(self):
        """Return basic metrics for the service."""
        return {
            "name": self.name,
            "processed": self._processed_count,
            "errors": self._error_count,
            "running": self.running
        }
