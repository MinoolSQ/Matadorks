import os
import sys
from core.logger import Logger
from core.state import State
from core.git_handler import GitHandler
from core import config
from rich.panel import Panel
from rich.console import Console

import subprocess
import argparse

console = Console()

class MatadorksApp:
    def __init__(self):
        self.state = State()
        self.logger = Logger()
        self.git = GitHandler()
        try:
            from importlib.metadata import version
            self.version = version("matadorks")
        except Exception:
            self.version = "1.0.0"

    def sync_dependencies(self):
        self.logger.status("Synchronizing dependencies with uv...")
        try:
            subprocess.run(["uv", "sync"], check=True)
            self.logger.success("Dependencies synchronized successfully.")
        except FileNotFoundError:
            self.logger.error("uv not found. Please install uv (https://github.com/astral-sh/uv).")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"uv sync failed: {e}")

    def show_banner(self):
        banner = rf"""
[bold red]
  __  __         _             _             _        
 |  \/  |  __ _ | |_  __ _  __| | ___  _ __ | | __ ___
 | |\/| | / _` || __|/ _` |/ _` |/ _ \| '__|| |/ // __|
 | |  | || (_| || |_| (_| | (_| | (_) | |   |   < \__ \\
 |_|  |_| \__,_| \__|\__,_|\__,_|\___/|_|   |_|\_\|___/
[/bold red]
[yellow]              Unified SQLi Pipeline v{self.version}[/yellow]
        """
        console.print(Panel(banner, border_style="magenta"))

    def run_pipeline(self):
        self.show_banner()
        self.logger.info("Starting Matadorks Pipeline...")

        # Phase 1: Dorking
        self.run_phase("Dorking", self.dorking_phase)
        
        # Phase 2: Proxy Building
        self.run_phase("Proxy Building", self.proxy_phase)

        # Phase 3: Scanning
        self.run_phase("Scanning", self.scanning_phase)

        # Phase 4: Validating
        self.run_phase("Validating", self.validating_phase)

        # Phase 5: Injecting
        self.run_phase("Injecting", self.injecting_phase)

        # Phase 6: Exploiting
        self.run_phase("Exploiting", self.exploiting_phase)

        self.logger.success("All phases completed successfully!")
        self.git.commit("Matadorks: Full pipeline execution completed.")

    def run_phase(self, name, func):
        if self.state.get(f"phase_{name.lower()}") == "completed":
            self.logger.info(f"Phase {name} already completed. Skipping.")
            return

        self.logger.status(f"Running Phase: {name}")
        try:
            func()
            self.state.set(f"phase_{name.lower()}", "completed")
            self.logger.success(f"Phase {name} finished.")
            self.git.commit(f"Matadorks: Completed {name} phase.")
        except Exception as e:
            self.logger.error(f"Phase {name} failed: {e}")
            sys.exit(1)

    def dorking_phase(self):
        from modules.dorker import generate_all
        dorks = generate_all()
        output_path = config.DORKS_FILE
        with open(output_path, "w") as f:
            for d in dorks: f.write(d + "\n")
        self.logger.info(f"Generated {len(dorks)} dorks in {output_path}")

    def proxy_phase(self):
        from core.proxy import get_google_pool
        pool = get_google_pool(auto_build=False)
        self.logger.info("Building proxy pool...")
        pool.build(max_test=config.PROXY_MAX_TEST, workers=config.PROXY_WORKERS)
        self.logger.info(f"Proxy pool built with {pool.size()} working proxies.")

    def scanning_phase(self):
        from modules.scanner import main as scanner_main
        self.logger.info("Starting bulk scanning...")
        scanner_main(
            threads=config.SCANNER_THREADS,
            amount=config.SCANNER_AMOUNT,
            prefix=config.SCANNER_PREFIX
        )
        self.logger.success("Scanning completed.")

    def validating_phase(self):
        from modules.validator import main as validator_main
        self.logger.info("Starting target validation...")
        validator_main(
            input_file=config.DORKS_FILE.replace("sqli_dorks", f"{config.SCANNER_PREFIX}_sqli_targets"),
            output_file=config.VALIDATED_FILE
        )
        self.logger.success("Validation completed.")

    def injecting_phase(self):
        from modules.injector import main as injector_main
        self.logger.info("Starting SQLMap injection phase...")
        injector_main(input_file=config.VALIDATED_FILE, output_file=config.VULNERABLE_FILE)
        self.logger.success("Injection phase completed.")

    def exploiting_phase(self):
        from modules.exploiter import main as exploiter_main
        self.logger.info("Starting exploitation phase...")
        exploiter_main(
            input_file=config.VULNERABLE_FILE,
            summary_file=config.PWNED_SUMMARY_FILE,
            log_file=config.EXPLOITATION_LOG_FILE
        )
        self.logger.success("Exploitation phase completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matadorks Unified SQLi Pipeline")
    parser.add_argument("--sync", action="store_true", help="Sync dependencies using uv")
    args = parser.parse_args()

    app = MatadorksApp()
    
    if args.sync:
        app.sync_dependencies()
    else:
        app.run_pipeline()
