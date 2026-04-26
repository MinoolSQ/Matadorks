#!/usr/bin/env python3.10
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from core.config import (
    VALIDATED_FILE, VULNERABLE_FILE,
    SQLMAP_LEVEL, SQLMAP_RISK, SQLMAP_SCAN_TIMEOUT,
    SQLMAP_CONCURRENT_SCANS, SQLMAP_DBMS
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

class SQLMapManager:
    def __init__(self, input_file, output_file, max_scans, stats=None):
        self.input_file = input_file
        self.output_file = output_file
        self.max_scans = max_scans
        self.lock = threading.Lock()
        self.vulnerable_count = 0
        self.stats = stats

    def check_sqlmap_installed(self):
        try:
            subprocess.run(["sqlmap", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def scan_target(self, url):
        print(f"[*] Pokrećem SQLMap na: {url}")
        
        # Formatiranje komande
        cmd = _build_sqlmap_args(url)
        
        try:
            # Pokretanje procesa
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Pratimo output u realnom vremenu za kljucne reci
            is_vulnerable = False
            try:
                # Cekamo do timeout-a
                stdout, stderr = process.communicate(timeout=SQLMAP_SCAN_TIMEOUT)
                
                # Provera da li je sqlmap nasao ranjivost
                # SQLMap obicno ispisuje "is vulnerable" ili "injectable"
                if "is vulnerable" in stdout or "injectable" in stdout or "fetching" in stdout:
                    is_vulnerable = True
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"[!] Timeout za {url} - prekidam.")
                return None

            if is_vulnerable:
                with self.lock:
                    self.vulnerable_count += 1
                    if self.stats:
                        self.stats.update(vulnerable=self.vulnerable_count)
                    with open(self.output_file, "a") as f:
                        f.write(f"[VULNERABLE] {url}\n")
                return f"[+] RAGNJIV: {url}"
            else:
                return f"[-] Nije ranjiv: {url}"

        except Exception as e:
            return f"[!] Greška kod {url}: {str(e)}"

    def run(self):
        if not self.check_sqlmap_installed():
            print("[!] SQLMap nije instaliran ili nije u PATH-u!")
            print("[!] Instaliraj ga sa: sudo apt install sqlmap")
            return

        if not os.path.exists(self.input_file):
            print(f"[!] Ulazni fajl {self.input_file} nije pronađen.")
            return

        with open(self.input_file, "r") as f:
            targets = [line.strip() for line in f if line.strip()]

        if not targets:
            print("[!] Nema linkova za skeniranje.")
            return

        print(f"\n[!] Započinjem SQLMap fazu na {len(targets)} meta...")
        print(f"[!] Paralelnih skenova: {self.max_scans}\n")

        with ThreadPoolExecutor(max_workers=self.max_scans) as executor:
            futures = [executor.submit(self.scan_target, url) for url in targets]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    print(res)

        print(f"\n[#] SQLMap faza završena!")
        print(f"[#] Pronađeno ranjivih meta: {self.vulnerable_count}")
        print(f"[#] Rezultati sačuvani u: {self.output_file}")

def main(input_file=None, output_file=None, max_scans=None, stats=None):
    input_file = input_file or VALIDATED_FILE
    output_file = output_file or VULNERABLE_FILE
    max_scans = max_scans or SQLMAP_CONCURRENT_SCANS
    manager = SQLMapManager(input_file, output_file, max_scans, stats=stats)
    manager.run()

if __name__ == "__main__":
    main()
