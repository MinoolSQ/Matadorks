import sys
import threading
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "status": "magenta",
    "dork": "blue",
})

# Use sys.__stdout__ to ensure logs are visible even if sys.stdout is redirected
console = Console(theme=custom_theme, file=sys.__stdout__)

class Logger:
    _lock = threading.Lock()
    _quiet_mode = False

    @classmethod
    def set_quiet(cls, quiet: bool):
        cls._quiet_mode = quiet

    @classmethod
    def _print(cls, prefix_style, prefix_char, message, level="info"):
        if cls._quiet_mode and level not in ["error", "success", "status"]:
            return
        
        with cls._lock:
            console.print(f"[{prefix_style}][{prefix_char}][/{prefix_style}] {message}")

    @classmethod
    def info(cls, message):
        cls._print("info", "*", message, level="info")

    @classmethod
    def success(cls, message):
        cls._print("success", "+", message, level="success")

    @classmethod
    def warning(cls, message):
        cls._print("warning", "!", message, level="warning")

    @classmethod
    def error(cls, message):
        cls._print("error", "x", message, level="error")

    @classmethod
    def debug(cls, message):
        cls._print("info", "D", message, level="info")

    @classmethod
    def critical(cls, message):
        cls._print("error", "!!!", message, level="error")

    @classmethod
    def status(cls, message):
        with cls._lock:
            console.print(f"[status]>>>[/status] {message}")

    @classmethod
    def dork(cls, dork_str):
        if not cls._quiet_mode:
            with cls._lock:
                console.print(f"[dork]DORK:[/dork] {dork_str}")
