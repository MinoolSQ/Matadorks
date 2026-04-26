import os
import sys
import warnings
warnings.filterwarnings("ignore")
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import threading
import time
import signal
from core.logger import Logger, console
from core.state import State
from core.git_handler import GitHandler
from core.stats import PipelineStats
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.console import Group

import subprocess
import argparse

class KeyboardListener(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.running = True

    def run(self):
        if os.name == 'nt' or not sys.stdin.isatty():
            return 
        
        import tty
        import termios
        import select
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while self.running:
                # Use select to wait for input with a timeout so we can check self.running
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1).lower()
                    if char == 'q':
                        self.app.logger.warning("Quit requested...")
                        self.app._quit_requested = True
                        break
                    elif char == 's':
                        self.app.logger.warning("Skip phase requested — aborting current phase...")
                        self.app._skip_requested = True
                        self.app._abort_phase.set()
                    elif char == 'p':
                        self.app._paused = not self.app._paused
                        status = "PAUSED" if self.app._paused else "RESUMED"
                        self.app.logger.info(f"Execution {status}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def stop(self):
        self.running = False

class MatadorksApp:
    def __init__(self, no_tui=False):
        self.state = State()
        self.logger = Logger()
        self.git = GitHandler()
        self.version = "1.0.0"
        self.stats = PipelineStats()
        self.no_tui = no_tui
        self._quit_requested = False
        self._skip_requested = False
        self._paused = False
        self._abort_phase = threading.Event()

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
        from rich.panel import Panel
        banner_path = os.path.join(os.path.dirname(__file__), "assets", "banner.txt")
        try:
            with open(banner_path, "r", encoding="utf-8") as f:
                banner_text = f.read()
        except FileNotFoundError:
            banner_text = "MATADORKS"
        banner_text += f"\n[dim]Unified SQLi Pipeline v{self.version}[/dim]"
        console.print(Panel(banner_text, border_style="red", padding=(1, 2)))

    def build_dashboard(self):
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right", ratio=1)
        
        phase_color = "bold cyan"
        if self._paused:
            phase_color = "bold yellow"
        
        status_text = f"Faza: [{phase_color}]{self.stats.phase.upper()}[/{phase_color}]"
        if self._paused:
            status_text += " [blink yellow](PAUSED)[/blink yellow]"
        
        table.add_row(
            status_text,
            f"Proxiji: [bold green]{self.stats.proxies_alive}[/bold green] alive"
        )
        
        stats_table = Table.grid(expand=True)
        stats_table.add_column(ratio=1)
        stats_table.add_column(ratio=1)
        stats_table.add_row(
            f"URL-ovi: [bold white]{self.stats.urls_scanned:,}[/bold white] scanned",
            f"SQLi hits: [bold yellow]{self.stats.sqli_hits}[/bold yellow]"
        )
        stats_table.add_row(
            f"Valid: [bold blue]{self.stats.validated}[/bold blue]",
            f"Vulnerable: [bold red]{self.stats.vulnerable}[/bold red]"
        )
        stats_table.add_row(
            f"Pwned: [bold magenta]{self.stats.pwned}[/bold magenta] databases",
            ""
        )
        
        footer = "[dim][Q] Quit  [S] Skip fazu  [P] Pauziraj[/dim]"

        return Panel(
            Group(table, Panel(stats_table, border_style="dim"), footer),
            title="[bold red]MATADORKS LIVE[/bold red]",
            border_style="red"
        )

    def _dashboard_refresher(self):
        while not self._stop_refresh.is_set():
            self._live.update(self.build_dashboard())
            self._stop_refresh.wait(0.5)

    def run_pipeline(self):
        self.show_banner()
        self.logger.info("Starting Matadorks Pipeline...")

        if not self.no_tui:
            listener = KeyboardListener(self)
            listener.start()

            self._stop_refresh = threading.Event()
            with Live(self.build_dashboard(), refresh_per_second=4, console=console) as live:
                self._live = live
                refresher = threading.Thread(target=self._dashboard_refresher, daemon=True)
                refresher.start()
                self._execute_phases()
                self._stop_refresh.set()

            listener.stop()
        else:
            self._execute_phases()

    def _execute_phases(self):
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

        if not self._quit_requested:
            self.logger.success("All phases completed successfully!")
            self.git.commit("Matadorks: Full pipeline execution completed.")

    def run_phase(self, name, func):
        if self._quit_requested:
            return

        self.stats.update(phase=name)

        if self.state.get(f"phase_{name.lower()}") == "completed":
            self.logger.info(f"Phase {name} already completed. Skipping.")
            return

        self.logger.status(f"Running Phase: {name}")
        try:
            # Check for skip before starting
            if self._skip_requested:
                self._skip_requested = False
                self.logger.warning(f"Phase {name} SKIPPED by user.")
                self.state.set(f"phase_{name.lower()}", "skipped")
                return

            # Pause check
            while self._paused:
                time.sleep(0.5)
                if self._quit_requested:
                    return

            func()
            self._abort_phase.clear()

            if self._skip_requested:
                self._skip_requested = False
                self.logger.warning(f"Phase {name} SKIPPED by user during execution.")
                self.state.set(f"phase_{name.lower()}", "skipped")
            else:
                self.state.set(f"phase_{name.lower()}", "completed")
                self.logger.success(f"Phase {name} finished.")
                self.git.commit(f"Matadorks: Completed {name} phase.")
                
        except Exception as e:
            self.logger.error(f"Phase {name} failed: {e}")
            sys.exit(1)

    def dorking_phase(self):
        from modules.dorker import generate_all
        dorks = generate_all()
        output_path = "data/sqli_dorks.txt"
        with open(output_path, "w") as f:
            for d in dorks: f.write(d + "\n")
        self.logger.info(f"Generated {len(dorks)} dorks in {output_path}")
        self.stats.update(urls_scanned=len(dorks)) # Just as an example

    def proxy_phase(self):
        from core.proxy import get_google_pool
        pool = get_google_pool(auto_build=False)
        self.logger.info("Building proxy pool...")
        # In a real scenario, we would pass stats to pool.build
        pool.build(max_test=5000, workers=200)
        self.stats.update(proxies_alive=pool.size())
        self.logger.info(f"Proxy pool built with {pool.size()} working proxies.")

    def scanning_phase(self):
        from modules.scanner import main as scanner_main
        self.logger.info("Starting bulk scanning...")
        scanner_main(threads=20, amount=50, prefix="matadorks", stats=self.stats, abort=self._abort_phase)
        self.logger.success("Scanning completed.")

    def validating_phase(self):
        from modules.validator import main as validator_main
        self.logger.info("Starting target validation...")
        validator_main(input_file="data/matadorks_sqli_targets.txt", output_file="data/validated_targets.txt", stats=self.stats, abort=self._abort_phase)
        self.logger.success("Validation completed.")

    def injecting_phase(self):
        from modules.injector import main as injector_main
        self.logger.info("Starting SQLMap injection phase...")
        injector_main(input_file="data/validated_targets.txt", output_file="data/vulnerable_targets.txt", stats=self.stats, abort=self._abort_phase)
        self.logger.success("Injection phase completed.")

    def exploiting_phase(self):
        from modules.exploiter import main as exploiter_main
        self.logger.info("Starting exploitation phase...")
        exploiter_main(input_file="data/vulnerable_targets.txt", summary_file="data/pwned_summary.txt", log_file="data/exploitation.log", stats=self.stats)
        self.logger.success("Exploitation phase completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matadorks Unified SQLi Pipeline")
    parser.add_argument("--sync", action="store_true", help="Sync dependencies using uv")
    parser.add_argument("--no-tui", action="store_true", help="Disable Live TUI dashboard")
    args = parser.parse_args()

    app = MatadorksApp(no_tui=args.no_tui)
    
    if args.sync:
        app.sync_dependencies()
    else:
        app.run_pipeline()
