"""
modules/test_mode.py
Handles the `apitool test` subcommand.
Sends HTTP requests, measures response time, displays colorised output,
detects security issues, and optionally saves to history.
"""

import json
import time

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from modules.history_mode import save_to_history
from modules.security import check_security

console = Console()


def parse_headers(header_tuples: tuple) -> dict:
    """Convert ('Key=Value', ...) tuples into a dict."""
    headers = {}
    for h in header_tuples:
        if "=" in h:
            k, _, v = h.partition("=")
            headers[k.strip()] = v.strip()
        else:
            console.print(f"[yellow]⚠  Ignoring malformed header:[/] {h!r}  (expected key=value)")
    return headers


def parse_body(body_str: str | None) -> dict | None:
    """Parse a JSON body string, returning None on failure."""
    if not body_str:
        return None
    try:
        return json.loads(body_str)
    except json.JSONDecodeError as exc:
        console.print(f"[red]✖  Invalid JSON body:[/] {exc}")
        return None


def run_test(url: str, path: str, method: str,
             header: tuple, body: str | None,
             timeout: float, save: bool) -> None:
    """Core logic for test mode."""

    full_url = url.rstrip("/") + ("/" + path.lstrip("/") if path else "")
    headers  = parse_headers(header)
    payload  = parse_body(body)
    method   = method.upper()

    # ── Print request summary ───────────────────────────────────────────────
    req_table = Table(show_header=False, box=None, padding=(0, 1))
    req_table.add_column(style="bold cyan",  width=10)
    req_table.add_column(style="white")
    req_table.add_row("Method",  f"[bold magenta]{method}[/]")
    req_table.add_row("URL",     full_url)
    if headers:
        req_table.add_row("Headers", str(headers))
    if payload:
        req_table.add_row("Body",    json.dumps(payload, indent=2))
    console.print(Panel(req_table, title="📤 Request", border_style="blue"))

    # ── Execute request ─────────────────────────────────────────────────────
    try:
        start = time.perf_counter()
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.request(
                method,
                full_url,
                headers=headers,
                json=payload,
            )
        elapsed_ms = (time.perf_counter() - start) * 1000

    except httpx.TimeoutException:
        console.print(Panel(
            f"[red]Request timed out after {timeout}s[/]",
            title="⏱  Timeout", border_style="red"
        ))
        return
    except httpx.InvalidURL:
        console.print(Panel(
            f"[red]Invalid URL:[/] {full_url}",
            title="✖  URL Error", border_style="red"
        ))
        return
    except httpx.RequestError as exc:
        console.print(Panel(
            f"[red]{exc}[/]",
            title="✖  Network Error", border_style="red"
        ))
        return

    # ── Status line ─────────────────────────────────────────────────────────
    code        = resp.status_code
    code_style  = ("green" if code < 300
                   else "yellow" if code < 400
                   else "red")
    speed_style = "green" if elapsed_ms < 500 else "yellow" if elapsed_ms < 1500 else "red"

    status_text = Text()
    status_text.append(f"  {code} {resp.reason_phrase}", style=f"bold {code_style}")
    status_text.append(f"   ⏱ {elapsed_ms:.1f} ms", style=speed_style)
    console.print(Panel(status_text, title="📥 Response", border_style=code_style))

    # ── Response headers ────────────────────────────────────────────────────
    hdr_table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    hdr_table.add_column("Header")
    hdr_table.add_column("Value", style="dim white")
    for k, v in resp.headers.items():
        hdr_table.add_row(k, v)
    console.print(Panel(hdr_table, title="🗂  Response Headers", border_style="dim blue"))

    # ── Response body ───────────────────────────────────────────────────────
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type or resp.text.lstrip().startswith(("{", "[")):
        try:
            pretty = json.dumps(resp.json(), indent=2)
            syntax = Syntax(pretty, "json", theme="monokai", line_numbers=False)
            console.print(Panel(syntax, title="📦 Response Body (JSON)", border_style="green"))
        except Exception:
            console.print(Panel(resp.text[:4000], title="📦 Response Body", border_style="green"))
    else:
        console.print(Panel(resp.text[:4000], title="📦 Response Body", border_style="green"))

    # ── Security checks ─────────────────────────────────────────────────────
    check_security(headers, resp)

    # ── Save to history ─────────────────────────────────────────────────────
    if save:
        entry = {
            "method":      method,
            "url":         full_url,
            "headers":     headers,
            "body":        payload,
            "status_code": code,
            "elapsed_ms":  round(elapsed_ms, 2),
        }
        save_to_history(entry)
        console.print("[dim green]✔  Saved to history.[/]")
