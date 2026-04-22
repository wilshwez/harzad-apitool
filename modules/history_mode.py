"""
modules/history_mode.py
Handles the `apitool history` subcommand.
Stores and retrieves requests in a local JSON file.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()

HISTORY_FILE = Path.home() / ".apitool_history.json"


# ── Persistence helpers ────────────────────────────────────────────────────────

def _load() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open() as fh:
            return json.load(fh)
    except Exception:
        return []


def _dump(entries: list) -> None:
    with HISTORY_FILE.open("w") as fh:
        json.dump(entries, fh, indent=2)


def save_to_history(entry: dict) -> None:
    """Append a request entry with a timestamp."""
    entries = _load()
    entry["timestamp"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    entries.append(entry)
    _dump(entries)


# ── Display helpers ────────────────────────────────────────────────────────────

def _status_style(code: int | None) -> str:
    if code is None:    return "dim"
    if code < 300:      return "green"
    if code < 400:      return "yellow"
    return "red"


def _print_list(entries: list) -> None:
    if not entries:
        console.print("[dim]No history entries found.[/]")
        return

    t = Table(header_style="bold cyan", show_lines=True)
    t.add_column("#",          width=4,  justify="right")
    t.add_column("Timestamp",  width=22)
    t.add_column("Method",     width=8)
    t.add_column("Status",     width=7,  justify="center")
    t.add_column("Time (ms)",  width=10, justify="right")
    t.add_column("URL",        overflow="fold")

    for idx, e in enumerate(entries):
        code  = e.get("status_code")
        style = _status_style(code)
        t.add_row(
            str(idx),
            e.get("timestamp", "—"),
            f"[bold]{e.get('method','?')}[/]",
            f"[{style}]{code or '?'}[/]",
            str(e.get("elapsed_ms", "—")),
            e.get("url", "—"),
        )
    console.print(t)


# ── Public entry point ─────────────────────────────────────────────────────────

def run_history(list_entries: bool, rerun: int | None,
                clear: bool, export: str | None) -> None:

    entries = _load()

    # ── Clear ──────────────────────────────────────────────────────────────
    if clear:
        _dump([])
        console.print(f"[green]✔  Cleared {len(entries)} history entries.[/]")
        return

    # ── Export ─────────────────────────────────────────────────────────────
    if export:
        with open(export, "w") as fh:
            json.dump(entries, fh, indent=2)
        console.print(f"[green]✔  Exported {len(entries)} entries to[/] {export}")
        return

    # ── Re-run a specific entry ────────────────────────────────────────────
    if rerun is not None:
        if rerun < 0 or rerun >= len(entries):
            console.print(f"[red]✖  No entry at index {rerun}.[/]")
            return
        e = entries[rerun]
        console.print(Panel(
            Syntax(json.dumps(e, indent=2), "json", theme="monokai"),
            title=f"🔁 Re-running entry #{rerun}", border_style="cyan"
        ))
        # Delegate to test_mode
        from modules.test_mode import run_test
        run_test(
            url=e.get("url", ""),
            path="",
            method=e.get("method", "GET"),
            header=tuple(f"{k}={v}" for k, v in (e.get("headers") or {}).items()),
            body=json.dumps(e["body"]) if e.get("body") else None,
            timeout=10.0,
            save=False,
        )
        return

    # ── Default: list ──────────────────────────────────────────────────────
    console.print(Panel(
        f"[cyan]History file:[/] {HISTORY_FILE}\n"
        f"[cyan]Entries:[/]      {len(entries)}",
        title="🗂  Request History", border_style="cyan"
    ))
    _print_list(entries)
