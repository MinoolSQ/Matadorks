#!/usr/bin/env python3.10
import os
import subprocess
import threading
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from core.config import (
    VALIDATED_FILE, VULNERABLE_FILE,
    SQLMAP_LEVEL, SQLMAP_RISK, SQLMAP_SCAN_TIMEOUT,
    SQLMAP_CONCURRENT_SCANS, SQLMAP_DBMS,
    USE_GHAURI_FALLBACK
)

def _build_sqlmap_args(url):
    args = [
        "sqlmap", "-u", url,
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
        "ghauri", "-u", url,
        "--batch",
        "--dbs",
        "--current-db",
        "--current-user",
    ]

class SQLMapManager:
    def __init__(self, in_q, out_q, max_scans, stats=None):
        self.in_q = in_q
        self.out_q = out_q
        self.max_scans = max_scans
        self.lock = threading.Lock()
        self.vulnerable_count = 0
        self.stats = stats
        self._ghauri_available = False

    def check_sqlmap_installed(self):
        try:
            subprocess.run(["sqlmap", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def check_ghauri_installed(self):
        try:
            subprocess.run(["ghauri", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def scan_target(self, url):
        print(f"[*] Testing: {url}")
        
        cmd = _build_sqlmap_args(url)
        is_vulnerable = False
        dbms = SQLMAP_DBMS or "Unknown"
        vuln_type = "SQL Injection"

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=SQLMAP_SCAN_TIMEOUT)
                if "is vulnerable" in stdout or "injectable" in stdout or "fetching" in stdout:
                    is_vulnerable = True
                    # Try to extract DBMS from output if it was unknown
                    if not SQLMAP_DBMS:
                        match = re.search(r"back-end DBMS: ([\w\s]+)", stdout)
                        if match:
                            dbms = match.group(1).strip()
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"[!] Timeout for {url}")
                return

            if not is_vulnerable and self._ghauri_available:
                ghauri_cmd = _build_ghauri_args(url)
                try:
                    ghauri_process = subprocess.Popen(
                        ghauri_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    g_stdout, g_stderr = ghauri_process.communicate(timeout=SQLMAP_SCAN_TIMEOUT)
                    g_stdout_lower = g_stdout.lower()
                    if ("is vulnerable" in g_stdout_lower or 
                        ("parameter" in g_stdout_lower and "injectable" in g_stdout_lower) or 
                        "current database" in g_stdout_lower):
                        is_vulnerable = True
                        print(f"[+] Ghauri found vulnerability: {url}")
                except subprocess.TimeoutExpired:
                    ghauri_process.kill()

            if is_vulnerable:
                with self.lock:
                    self.vulnerable_count += 1
                    if self.stats:
                        self.stats.update(vulnerable=self.vulnerable_count)
                
                vuln_data = {
                    "url": url,
                    "dbms": dbms,
                    "type": vuln_type
                }
                self.out_q.put(vuln_data)
                print(f"[+] VULNERABLE: {url} ({dbms})")
            else:
                pass # Silent for non-vulnerable to reduce noise

        except Exception as e:
            print(f"[!] Error scanning {url}: {e}")

    def run(self):
        if not self.check_sqlmap_installed():
            print("[!] SQLMap not found!")
            return

        self._ghauri_available = USE_GHAURI_FALLBACK and self.check_ghauri_installed()

        print(f"[*] Injector started (Threads: {self.max_scans})")
        
        with ThreadPoolExecutor(max_workers=self.max_scans) as executor:
            while True:
                target = self.in_q.get()
                if target is None:
                    break
                executor.submit(self.scan_target, target)

        self.out_q.put(None)
        print(f"[*] Injector finished. Found {self.vulnerable_count} vulnerable targets.")

def main(in_q=None, out_q=None, max_scans=None, stats=None):
    import queue
    # This main is mostly for standalone testing if needed, 
    # but the real app will pass queues.
    if in_q is None:
        return
    
    max_scans = max_scans or SQLMAP_CONCURRENT_SCANS
    manager = SQLMapManager(in_q, out_q, max_scans, stats=stats)
    manager.run()

if __name__ == "__main__":
    main()
