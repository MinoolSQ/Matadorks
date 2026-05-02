import asyncio
import re
from core.base_service import BaseService
from core.config import (
    SQLMAP_LEVEL, SQLMAP_RISK, SQLMAP_SCAN_TIMEOUT,
    SQLMAP_CONCURRENT_SCANS, SQLMAP_DBMS,
    USE_GHAURI_FALLBACK
)

class InjectorService(BaseService):
    """
    Independent service for SQL injection detection using SQLMap and Ghauri.
    Refactored from modules/injector.py following the BaseService interface.
    """
    def __init__(self, name="Injector", config=None, stats=None):
        super().__init__(name, config, stats)
        self.semaphore = asyncio.Semaphore(self.config.get("concurrent_scans", SQLMAP_CONCURRENT_SCANS))
        self.timeout = self.config.get("timeout", SQLMAP_SCAN_TIMEOUT)
        self.use_ghauri = self.config.get("use_ghauri_fallback", USE_GHAURI_FALLBACK)

    async def initialize(self):
        self.logger.success("Injector initialized.")

    def _build_sqlmap_args(self, url):
        args = [
            "-u", url,
            "--batch",
            "--random-agent",
            f"--level={SQLMAP_LEVEL}",
            f"--risk={SQLMAP_RISK}",
            "--timeout=10",
            "--threads=3",
            "--technique=BEUSTQ",
            "--fresh-queries",
        ]
        if SQLMAP_DBMS:
            args.append(f"--dbms={SQLMAP_DBMS}")
        return args

    def _build_ghauri_args(self, url):
        return ["-u", url, "--batch", "--dbs"]

    async def process_item(self, target_obj):
        """
        Tests a target for SQL injection vulnerability.
        Returns vulnerability data if confirmed, otherwise None.
        """
        async with self.semaphore:
            url = target_obj["url"] if isinstance(target_obj, dict) else target_obj
            is_vulnerable = False
            dbms = SQLMAP_DBMS or "Unknown"

            try:
                self.logger.debug(f"Testing for SQLi: {url}")
                
                # Try SQLMap first
                process = await asyncio.create_subprocess_exec(
                    "sqlmap", *self._build_sqlmap_args(url),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
                    stdout_str = stdout.decode('utf-8', errors='ignore')
                    
                    if any(x in stdout_str.lower() for x in ["is vulnerable", "injectable", "fetching back-end dbms"]):
                        is_vulnerable = True
                        if not SQLMAP_DBMS:
                            match = re.search(r"back-end DBMS: ([\w\s]+?)(?=\n|\[|$)", stdout_str)
                            if match: dbms = match.group(1).strip()
                except asyncio.TimeoutError:
                    try:
                        process.kill()
                    except: pass
                    self.logger.warning(f"SQLMap timeout for {url}")
                    return None

                # Fallback to Ghauri if SQLMap is not conclusive
                if not is_vulnerable and self.use_ghauri:
                    self.logger.debug(f"Falling back to Ghauri for {url}")
                    g_process = await asyncio.create_subprocess_exec(
                        "ghauri", *self._build_ghauri_args(url),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    try:
                        g_stdout, g_stderr = await asyncio.wait_for(g_process.communicate(), timeout=self.timeout)
                        g_stdout_str = g_stdout.decode('utf-8', errors='ignore').lower()
                        if any(x in g_stdout_str for x in ["is vulnerable", "injectable", "fetching current database"]):
                            is_vulnerable = True
                            dbms = "Unknown (Ghauri)"
                    except asyncio.TimeoutError:
                        try:
                            g_process.kill()
                        except: pass
                        self.logger.warning(f"Ghauri timeout for {url}")

                if is_vulnerable:
                    vuln_data = {"url": url, "dbms": dbms}
                    if isinstance(target_obj, dict):
                        vuln_data.update(target_obj)
                    vuln_data["dbms"] = dbms

                    if self.stats:
                        self.stats.update(vulnerable=self.stats.vulnerable + 1)
                    
                    self.logger.success(f"VULNERABLE confirmed: {url} ({dbms})")
                    return vuln_data

            except Exception as e:
                self.logger.error(f"Injector exception for {url}: {e}")
            
            return None

    async def shutdown(self):
        self.logger.info("Injector Service shutting down.")
