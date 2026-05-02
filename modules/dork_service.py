import asyncio
import os
import random
from core.base_service import BaseService
from core.config import DORKS_DATA_DIR
from modules.dork_gen import generate_all, generate_light_dorks
from modules.edb_sync import EDBSync
from modules.ghdb_provider import GHDBProvider

class DorkService(BaseService):
    """
    Independent service for fetching and generating search dorks.
    Integrates GHDB syncing and local generation logic.
    """
    def __init__(self, name="Dorker", config=None, stats=None):
        super().__init__(name, config, stats)
        self.output_file = self.config.get("output_file", "massive_niche_dorks_2026.txt")
        self.sync_ghdb = self.config.get("sync_ghdb", True)
        self.generator_type = self.config.get("type", "all") # all, light

    async def initialize(self):
        """Sync with Exploit-DB if requested."""
        if self.sync_ghdb:
            self.logger.info("Checking for Exploit-DB/GHDB updates...")
            sync_engine = EDBSync()
            # Run blocking git sync in thread
            success = await asyncio.to_thread(sync_engine.sync)
            if success:
                self.logger.success("GHDB data is up to date.")
            else:
                self.logger.warning("GHDB sync failed or skipped. Using local data if available.")

    async def process_item(self, item=None):
        """
        Generates dorks based on the selected generator type.
        Returns a list of generated dork strings.
        """
        self.logger.info(f"Generating dorks (type: {self.generator_type})...")
        
        # Generation logic is synchronous, run in thread to keep loop responsive
        if self.generator_type == "light":
            dorks = await asyncio.to_thread(generate_light_dorks)
        else:
            dorks = await asyncio.to_thread(generate_all)

        random.shuffle(dorks)
        
        # Save to file
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(f"# Generated {len(dorks)} Dorks\n")
                for d in dorks:
                    f.write(d + "\n")
            self.logger.success(f"Generated {len(dorks)} dorks and saved to {self.output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save dorks to {self.output_file}: {e}")

        return dorks

    async def shutdown(self):
        self.logger.info("Dork Service shutting down.")

    async def run_standalone(self):
        """Standard execution for dork generation."""
        await self.initialize()
        results = await self.process_item()
        await self.shutdown()
        return results
