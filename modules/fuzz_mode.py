"""
modules/fuzz_mode.py
Handles the `apitool fuzz` subcommand.
Iterates a wordlist, tests each path, shows interesting responses.
Uses a thread pool for concurrency — safe, read-only fuzzing only.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

# Status codes considered "interesting"
INTERESTING = {200, 201, 204, 301, 302, 403, 405, 500}


def _probe(client: httpx.Client, base_url: str,
           path: str, method: str, timeout: float) -> dict:
    """Send a single probe and return a result dict."""
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    try:
        start = time.perf_counter()
        resp  = client.request(method, url, timeout=timeout, follow_redirects=False)
        ms    = round((time.perf_counter() - start) * 1000, 1)
        return {"path": path, "url": url, "status": resp.status_code,
                "size": len(resp.content), "ms": ms, "error": None}
    except httpx.TimeoutException:
        return {"path": path, "url": url, "status": None,
                "size": 0, "ms": None, "error": "timeout"}
    except Exception as exc:
        return {"path": path, "url": url, "status": None,
                "size": 0, "ms": None, "error": str(exc)[:60]}


def _status_style(code: int | None) -> str:
    if code is None:      return "dim red"
    if code < 300:        return "bold green"
    if code < 400:        return "yellow"
    if code == 403:       return "bold yellow"
    if code >= 500:       return "bold red"
    return "white"


def run_fuzz(base_url: str, wordlist_path: str,
             method: str, threads: int, timeout: float) -> None:
    """Core logic for fuzz mode."""

    # Load wordlist
    with open(wordlist_path, "r", errors="replace") as fh:
        paths = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

    console.print(Panel(
        f"[bold cyan]Target:[/] {base_url}\n"
        f"[bold cyan]Wordlist:[/] {wordlist_path}  ([white]{len(paths)}[/] entries)\n"
        f"[bold cyan]Method:[/] {method}   "
        f"[bold cyan]Threads:[/] {threads}   "
        f"[bold cyan]Timeout:[/] {timeout}s",
        title="🔍 Fuzz Mode", border_style="magenta"
    ))

    results = []
    with httpx.Client(follow_redirects=False, timeout=timeout) as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[cyan]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Fuzzing…", total=len(paths))

            with ThreadPoolExecutor(max_workers=threads) as pool:
                futures = {
                    pool.submit(_probe, client, base_url, p, method, timeout): p
                    for p in paths
                }
                for future in as_completed(futures):
                    results.append(future.result())
                    progress.advance(task)

    # ── Build results table (interesting only) ──────────────────────────────
    interesting = [r for r in results if r["status"] in INTERESTING]
    interesting.sort(key=lambda r: (r["status"] or 999, r["path"]))

    table = Table(
        title=f"⚡ Interesting Responses ({len(interesting)} / {len(paths)})",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Status", width=8,  justify="center")
    table.add_column("Path",   width=35)
    table.add_column("Size",   width=8,  justify="right")
    table.add_column("Time",   width=9,  justify="right")
    table.add_column("URL",    overflow="fold")

    for r in interesting:
        style = _status_style(r["status"])
        table.add_row(
            f"[{style}]{r['status']}[/]",
            r["path"],
            f"{r['size']} B",
            f"{r['ms']} ms" if r["ms"] else "-",
            r["url"],
        )

    if interesting:
        console.print(table)
    else:
        console.print("[dim]No interesting responses found.[/]")

    # ── Errors summary ──────────────────────────────────────────────────────
    errors = [r for r in results if r["error"]]
    if errors:
        console.print(f"\n[dim red]⚠  {len(errors)} requests failed (timeouts / network errors).[/]")
