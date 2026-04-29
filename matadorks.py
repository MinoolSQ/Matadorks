import os
import sys
import warnings
warnings.filterwarnings("ignore")
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import threading
import asyncio
import time
import signal
import subprocess
import argparse

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from core.logger import Logger, console
from core.state import State
from core.git_handler import GitHandler
from core.stats import PipelineStats
from core.queue_orchestrator import QueueManager
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.console import Group

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
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1).lower()
                    if char == 'q':
                        self.app.logger.warning("Quit requested...")
                        self.app._quit_requested = True
                        break
                    elif char == 's':
                        self.app.logger.warning("Skip phase requested — aborting current phase...")
                        self.app._skip_requested = True
                        if isinstance(self.app._abort_phase, asyncio.Event):
                            self.app.loop.call_soon_threadsafe(self.app._abort_phase.set)
                        else:
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
        self.version = "1.1.0-async"
        self.stats = PipelineStats()
        self.queue_manager = QueueManager(stats=self.stats)
        self.no_tui = no_tui
        self._quit_requested = False
        self._skip_requested = False
        self._paused = False
        self._abort_phase = asyncio.Event()
        self.loop = None

    def sync_dependencies(self):
        self.logger.status("Synchronizing dependencies with uv...")
        try:
            subprocess.run(["uv", "sync"], check=True)
            self.logger.success("Dependencies synchronized successfully.")
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")

    def show_banner(self):
        banner_path = os.path.join(os.path.dirname(__file__), "assets", "banner.txt")
        try:
            with open(banner_path, "r", encoding="utf-8") as f:
                banner_text = f.read()
        except FileNotFoundError:
            banner_text = "MATADORKS"
        banner_text += f"\n[dim]Asynchronous SQLi Pipeline v{self.version}[/dim]"
        console.print(Panel(banner_text, border_style="red", padding=(1, 2)))

    def build_dashboard(self):
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right", ratio=1)
        
        phase_color = "bold cyan"
        if self._paused:
            phase_color = "bold yellow"
        
        status_text = f"Status: [{phase_color}]ASYNC STREAMING[/{phase_color}]"
        if self._paused:
            status_text += " [blink yellow](PAUSED)[/blink yellow]"
        
        table.add_row(
            status_text,
            f"Proxiji: [bold green]{self.stats.proxies_alive}[/bold green] alive"
        )
        
        q_table = Table.grid(expand=True)
        q_table.add_column(ratio=1)
        q_table.add_column(ratio=1)
        q_table.add_column(ratio=1)
        q_table.add_column(ratio=1)
        q_table.add_row(
            f"Dorks: [bold yellow]{self.stats.q_dork_size}[/bold yellow]",
            f"URLs: [bold yellow]{self.stats.q_url_size}[/bold yellow]",
            f"Valid: [bold blue]{self.stats.q_valid_size}[/bold blue]",
            f"Vuln: [bold red]{self.stats.q_vuln_size}[/bold red]"
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
        
        footer = "[dim][Q] Quit  [S] Skip phase  [P] Pause[/dim]"

        return Panel(
            Group(table, Panel(q_table, title="Queue Status", border_style="yellow"), Panel(stats_table, border_style="dim"), footer),
            title="[bold red]MATADORKS ASYNC[/bold red]",
            border_style="red"
        )

    def _dashboard_refresher(self):
        while not self._stop_refresh.is_set():
            self.stats.update_queues(self.queue_manager)
            self._live.update(self.build_dashboard())
            time.sleep(0.5)

    async def run_pipeline(self):
        self.loop = asyncio.get_running_loop()
        self.show_banner()
        self.logger.info("Starting Async Matadorks Pipeline...")

        if not self.no_tui:
            # Silence high-volume logs when TUI is active
            self.logger.set_quiet(True)
            listener = KeyboardListener(self)
            listener.start()

            self._stop_refresh = threading.Event()
            with Live(self.build_dashboard(), refresh_per_second=4, console=console) as live:
                self._live = live
                refresher = threading.Thread(target=self._dashboard_refresher, daemon=True)
                refresher.start()
                await self._execute_phases()
                self._stop_refresh.set()

            listener.stop()
        else:
            await self._execute_phases()

    async def _execute_phases(self):
        # Phase 1: Dorking
        self.stats.update(phase="Dorking")
        self.logger.status("Generating dorks...")
        from modules.dorker import generate_all
        dorks = await asyncio.to_thread(generate_all) # Dorker is still sync
        output_path = "data/sqli_dorks.txt"
        with open(output_path, "w") as f:
            for d in dorks: f.write(d + "\n")
        self.logger.info(f"Generated {len(dorks)} dorks.")

        # Phase 2: Proxy Building
        await self.run_phase("Proxy Building", self.proxy_phase)

        # Start the Streaming Pipeline
        self.logger.status("Starting Real-time Async Pipeline...")
        await self.queue_manager.start_pipeline(self)
        
        # Feed dorks
        await self.queue_manager.push_dorks(dorks)

        # Start Harvester in background (runs parallel to scanner)
        from modules.harvester import HarvesterOrchestrator
        harvester = HarvesterOrchestrator(
            url_q=self.queue_manager.q_url,
            stats=self.stats,
            abort=self._abort_phase
        )
        harvester_task = asyncio.create_task(harvester.run(), name="HarvesterTask")

        # Wait for both Scanner AND Harvester to finish their seeding work
        self.logger.info("Waiting for Scanner and Harvester to finish seeding...")
        await asyncio.gather(self.queue_manager.tasks['Scanner'], harvester_task, return_exceptions=True)
        
        # Now that both seeding sources are done, we can signal the Validator (and beyond) to finish
        self.logger.info("Seeding complete. Draining pipeline...")
        await self.queue_manager.q_url.put(None)

        # Wait for the rest of the pipeline to process remaining items
        await self.queue_manager.wait_for_completion()
        
        if not self._quit_requested:
            self.logger.success("Async Pipeline finished!")
            self.git.commit("Matadorks: Completed async pipeline execution.")

    async def run_phase(self, name, func):
        if self._quit_requested:
            return

        self.stats.update(phase=name)

        if self.state.get(f"phase_{name.lower()}") == "completed":
            self.logger.info(f"Phase {name} already completed. Skipping.")
            return

        self.logger.status(f"Running Phase: {name}")
        try:
            if self._skip_requested:
                self._skip_requested = False
                self.logger.warning(f"Phase {name} SKIPPED by user.")
                self.state.set(f"phase_{name.lower()}", "skipped")
                return

            while self._paused:
                await asyncio.sleep(0.5)
                if self._quit_requested:
                    return

            if asyncio.iscoroutinefunction(func):
                await func()
            else:
                await asyncio.to_thread(func)
            
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

    async def proxy_phase(self):
        from core.proxy import get_google_pool
        pool = get_google_pool(auto_build=False)
        self.logger.info("Building proxy pool...")
        await pool.build_async(max_test=5000, workers=200, abort=self._abort_phase)
        self.stats.update(proxies_alive=pool.size())
        self.logger.info(f"Proxy pool built with {pool.size()} working proxies.")

def main():
    parser = argparse.ArgumentParser(description="Matadorks Unified Async SQLi Pipeline")
    parser.add_argument("--sync", action="store_true", help="Sync dependencies using uv")
    parser.add_argument("--no-tui", action="store_true", help="Disable Live TUI dashboard")
    args = parser.parse_args()

    app = MatadorksApp(no_tui=args.no_tui)
    
    if args.sync:
        app.sync_dependencies()
    else:
        try:
            asyncio.run(app.run_pipeline())
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
