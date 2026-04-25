import sys
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

console = Console(theme=custom_theme)

class Logger:
    @staticmethod
    def info(message):
        console.print(f"[info][*][/info] {message}")

    @staticmethod
    def success(message):
        console.print(f"[success][+][/success] {message}")

    @staticmethod
    def warning(message):
        console.print(f"[warning][!][/warning] {message}")

    @staticmethod
    def error(message):
        console.print(f"[error][x][/error] {message}")

    @staticmethod
    def status(message):
        console.print(f"[status]>>>[/status] {message}")

    @staticmethod
    def dork(dork_str):
        console.print(f"[dork]DORK:[/dork] {dork_str}")
