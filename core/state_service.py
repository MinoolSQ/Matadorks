import json
import os
import asyncio
from core.config import STATE_FILE
from core.logger import Logger

class StateService:
    """
    Asynchronous state management service.
    Implements periodic batch saving to avoid I/O bottlenecks.
    """
    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.logger = Logger()
        self.data = self._load()
        
        if "processed_urls" not in self.data:
            self.data["processed_urls"] = []
        
        # In-memory set for O(1) lookup
        self._processed_set = set(self.data["processed_urls"])
        self._dirty = False
        self._lock = asyncio.Lock()
        self._running = True

    def _load(self):
        """Synchronous load on initialization."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load state file: {e}")
                return {}
        return {}

    async def start_periodic_save(self, interval=30):
        """Background task to periodically persist dirty state."""
        self.logger.debug(f"Starting periodic state save every {interval}s.")
        while self._running:
            try:
                await asyncio.sleep(interval)
                if self._dirty:
                    await self.save()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic save task: {e}")

    async def save(self):
        """Persist state to disk safely."""
        async with self._lock:
            if not self._dirty:
                return
            
            try:
                os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
                # Atomic-like write using temporary file
                temp_file = self.state_file + ".tmp"
                # Use to_thread for blocking I/O
                await asyncio.to_thread(self._sync_save, temp_file)
                os.replace(temp_file, self.state_file)
                
                self._dirty = False
                self.logger.debug("State persisted successfully.")
            except Exception as e:
                self.logger.error(f"Failed to save state: {e}")

    def _sync_save(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f, indent=4)

    def is_processed(self, url):
        """Check if a URL has already been processed."""
        return url in self._processed_set

    def mark_processed(self, url):
        """Mark a URL as processed and flag state as dirty."""
        if url not in self._processed_set:
            self._processed_set.add(url)
            self.data["processed_urls"].append(url)
            self._dirty = True

    def get(self, key, default=None):
        """Get a generic state value."""
        return self.data.get(key, default)

    def set(self, key, value):
        """Set a generic state value and flag as dirty."""
        self.data[key] = value
        self._dirty = True

    async def shutdown(self):
        """Final save and cleanup."""
        self._running = False
        await self.save()
        self.logger.info("State Service shutdown complete.")
