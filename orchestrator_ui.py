import asyncio
import os
import sys
import warnings
import contextlib
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live

# Suppress annoying warnings that break the TUI
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from core.logger import console, Logger
from core.pipeline_engine import PipelineEngine
from core.state_service import StateService
from core.stats import PipelineStats
from modules.scanner_service import ScannerService
from modules.validator_service import ValidatorService
from modules.injector_service import InjectorService
from modules.exploiter_service import ExploiterService
from modules.dork_service import DorkService

class OrchestratorUI:
    """
    Main TUI for Matadorks Orchestrator.
    Allows running the full pipeline or individual modules with custom inputs.
    """
    def __init__(self):
        self.state = StateService()
        self.stats = PipelineStats()
        self.engine = None

    def generate_stats_table(self):
        """Generates a real-time table of pipeline statistics."""
        table = Table(
            expand=True,
            border_style="blue",
            header_style="bold magenta",
        )
        table.add_column("Stage", style="cyan", no_wrap=True)
        table.add_column("Count", justify="right", style="green")
        table.add_column("Queue", justify="right", style="yellow")

        table.add_row("Scanner (URLs Found)", str(self.stats.urls_scanned), str(self.stats.q_dork_size))
        table.add_row("Validator (Alive)", str(self.stats.validated), str(self.stats.q_url_size))
        table.add_row("Injector (Vuln)", str(self.stats.vulnerable), str(self.stats.q_valid_size))
        table.add_row("Exploiter (Pwned)", str(self.stats.pwned), str(self.stats.q_vuln_size))
        
        return Panel(table, title="[bold blue]Matadorks Pipeline Status[/bold blue]", border_style="cyan")

    async def main_menu(self):
        """Displays the main interactive menu."""
        while True:
            console.clear()
            console.print(Panel.fit(
                "[bold cyan]M A T A D O R K S   O R C H E S T R A T O R[/bold cyan]",
                subtitle="v2.0 [Modular SOA Architecture]",
                border_style="blue"
            ))
            
            console.print("\n[1] [bold green]Full Pipeline[/bold green] (Dorks -> Pwned)")
            console.print("[2] [bold blue]Isolated Module[/bold blue] (Run single stage with custom input)")
            console.print("[3] [bold yellow]View Session Stats[/bold yellow]")
            console.print("[4] [bold magenta]Fetch/Generate Dorks[/bold magenta] (GHDB Sync + Local Gen)")
            console.print("[0] [bold red]Exit[/bold red]")
            
            choice = Prompt.ask("\nSelect operation", choices=["1", "2", "3", "4", "0"], default="1")
            
            if choice == "1":
                await self.start_full_pipeline()
            elif choice == "2":
                await self.start_isolated_module()
            elif choice == "3":
                self.show_stats()
            elif choice == "4":
                await self.run_dork_generation()
            elif choice == "0":
                console.print("[bold yellow]Shutting down services...[/bold yellow]")
                await self.state.shutdown()
                break

    async def run_dork_generation(self):
        """Runs the DorkService to update dork list."""
        console.clear()
        console.print(Panel("[bold magenta]Dork Generation & GHDB Sync[/bold magenta]"))
        
        sync_choice = Prompt.ask("Sync with Exploit-DB (Git)?", choices=["y", "n"], default="y")
        gen_type = Prompt.ask("Generation mode", choices=["all", "light"], default="all")
        
        service = DorkService(config={
            "sync_ghdb": sync_choice == "y",
            "type": gen_type
        })
        
        await service.run_standalone()
        Prompt.ask("\nDorks updated. Press Enter to return")

    async def _run_with_live_stats(self, initial_data):
        """Helper to run engine with live stats display and output redirection."""
        # Redirect stdout/stderr to a log file to avoid TUI pollution from external libs
        log_dir = "data/logs"
        os.makedirs(log_dir, exist_ok=True)
        output_log = os.path.join(log_dir, "output.log")

        with open(output_log, "a") as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            with Live(self.generate_stats_table(), refresh_per_second=4, console=console, screen=False) as live:
                async def update_live():
                    try:
                        while not self.engine.abort_event.is_set():
                            live.update(self.generate_stats_table())
                            await asyncio.sleep(0.25)
                    except asyncio.CancelledError:
                        pass
                
                updater = asyncio.create_task(update_live())
                await self.engine.run(initial_data)
                updater.cancel()
                try:
                    await updater
                except: pass

    async def start_full_pipeline(self):
        """Configures and runs the complete 4-stage pipeline."""
        dorks_file = "data/sqli_dorks.txt"
        if not os.path.exists(dorks_file):
            if os.path.exists("massive_niche_dorks_2026.txt"):
                dorks_file = "massive_niche_dorks_2026.txt"
            else:
                console.print("[red]Error: Dorks file not found![/red]")
                await asyncio.sleep(2)
                return

        with open(dorks_file, "r") as f:
            dorks = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        console.print(f"[green]Loaded {len(dorks)} dorks. Initializing services...[/green]")
        
        self.engine = PipelineEngine(state=self.state, stats=self.stats)
        
        self.engine.add_service(ScannerService(stats=self.stats, app_state=self.state))
        self.engine.add_service(ValidatorService(stats=self.stats))
        self.engine.add_service(InjectorService(stats=self.stats))
        self.engine.add_service(ExploiterService(stats=self.stats))
        
        await self._run_with_live_stats(dorks)
        Prompt.ask("\nPipeline finished. Press Enter to return")

    async def start_isolated_module(self):
        """Runs a single service in isolation with user-provided input file."""
        console.clear()
        console.print(Panel("[bold blue]Isolated Module Execution[/bold blue]"))
        console.print("1. Scanner (Input: Dorks list)")
        console.print("2. Validator (Input: URL list)")
        console.print("3. Injector (Input: URL list)")
        console.print("4. Exploiter (Input: Vulnerable target list)")
        
        mod_choice = Prompt.ask("Select module", choices=["1", "2", "3", "4"], default="1")
        input_file = Prompt.ask("Enter input file path")
        
        if not os.path.exists(input_file):
            console.print(f"[red]Error: {input_file} not found![/red]")
            await asyncio.sleep(2)
            return

        with open(input_file, "r") as f:
            items = [line.strip() for line in f if line.strip()]

        self.engine = PipelineEngine(state=self.state, stats=self.stats)
        
        if mod_choice == "1":
            self.engine.add_service(ScannerService(stats=self.stats, app_state=self.state))
        elif mod_choice == "2":
            self.engine.add_service(ValidatorService(stats=self.stats))
        elif mod_choice == "3":
            self.engine.add_service(InjectorService(stats=self.stats))
        elif mod_choice == "4":
            self.engine.add_service(ExploiterService(stats=self.stats))

        console.print(f"[green]Starting isolated module with {len(items)} items...[/green]")
        await self._run_with_live_stats(items)
        Prompt.ask("\nExecution finished. Press Enter to return")

    def show_stats(self):
        """Displays a static snapshot of the current session stats."""
        console.print(self.generate_stats_table())
        Prompt.ask("\nPress Enter to return")

if __name__ == "__main__":
    ui = OrchestratorUI()
    try:
        asyncio.run(ui.main_menu())
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user. Cleaning up...[/bold red]")
        sys.exit(0)
