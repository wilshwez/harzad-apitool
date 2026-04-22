#!/usr/bin/env python3
"""
apitool — A modular CLI for API testing and learning.
Supports: test, fuzz, learn, history subcommands.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def banner():
    title = Text()
    title.append("⚡ ", style="yellow")
    title.append("apitool", style="bold cyan")
    title.append(" v1.0", style="dim white")
    subtitle = Text("API Testing + Learning CLI for Cybersecurity Students", style="dim cyan")
    console.print(Panel.fit(
        f"{title}\n{subtitle}",
        border_style="cyan",
        padding=(0, 2)
    ))


@click.group()
def cli():
    """apitool — Test, fuzz, and learn REST, SOAR, and Graph APIs."""
    pass


# ── Test subcommand ────────────────────────────────────────────────────────────
@cli.command()
@click.option("--url",      "-u", required=True,               help="Full URL or base URL")
@click.option("--path",     "-p", default="",                  help="Endpoint path (e.g. /users)")
@click.option("--method",   "-m", default="GET",
              type=click.Choice(["GET","POST","PUT","DELETE","PATCH"], case_sensitive=False),
              help="HTTP method")
@click.option("--header",   "-H", multiple=True,               help="Header as key=value (repeatable)")
@click.option("--body",     "-b", default=None,                help="JSON body string")
@click.option("--timeout",  "-t", default=10.0,                help="Request timeout in seconds")
@click.option("--save",     "-s", is_flag=True,                help="Save result to history")
def test(url, path, method, header, body, timeout, save):
    """Send an HTTP request and display the response."""
    banner()
    from modules.test_mode import run_test
    run_test(url, path, method, header, body, timeout, save)


# ── Fuzz subcommand ───────────────────────────────────────────────────────────
@cli.command()
@click.option("--url",      "-u", required=True,  help="Base URL to fuzz")
@click.option("--wordlist", "-w", required=True,
              type=click.Path(exists=True),        help="Path to wordlist file")
@click.option("--method",   "-m", default="GET",
              type=click.Choice(["GET","POST","PUT","DELETE","PATCH"], case_sensitive=False))
@click.option("--threads",  "-T", default=5,      help="Concurrent threads")
@click.option("--timeout",  "-t", default=8.0,    help="Per-request timeout")
def fuzz(url, wordlist, method, threads, timeout):
    """Fuzz API endpoints using a wordlist."""
    banner()
    from modules.fuzz_mode import run_fuzz
    run_fuzz(url, wordlist, method, threads, timeout)


# ── Learn subcommand ──────────────────────────────────────────────────────────
@cli.command()
@click.option("--topic", "-t",
              type=click.Choice(["rest","soar","graph","menu"], case_sensitive=False),
              default="menu", help="Topic to learn")
def learn(topic):
    """Interactive learning mode for REST, SOAR, and Graph APIs."""
    banner()
    from modules.learn_mode import run_learn
    run_learn(topic)


# ── History subcommand ────────────────────────────────────────────────────────
@cli.command()
@click.option("--list",   "-l", "list_entries", is_flag=True, help="List saved requests")
@click.option("--rerun",  "-r", default=None,   type=int,     help="Re-run entry by index")
@click.option("--clear",  "-c", is_flag=True,                 help="Clear all history")
@click.option("--export", "-e", default=None,                 help="Export history to a file")
def history(list_entries, rerun, clear, export):
    """View, re-run, or clear request history."""
    banner()
    from modules.history_mode import run_history
    run_history(list_entries, rerun, clear, export)


if __name__ == "__main__":
    cli()
