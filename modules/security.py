"""
modules/security.py
Passive security checks on outgoing requests and incoming responses.
Warns the analyst — never exploits.
"""

import re

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Headers that indicate good security hygiene
GOOD_HEADERS = {
    "strict-transport-security": "HSTS is set — good.",
    "x-content-type-options":    "X-Content-Type-Options present — prevents MIME sniffing.",
    "x-frame-options":           "X-Frame-Options present — clickjacking protection.",
    "content-security-policy":   "Content-Security-Policy found — strong XSS mitigation.",
    "x-xss-protection":          "X-XSS-Protection header present.",
}

# Response body patterns that suggest information leakage
LEAK_PATTERNS = [
    (r"stack trace",           "Stack trace exposed in response — disclose server internals"),
    (r"traceback",             "Python traceback in response — may leak file paths"),
    (r"at .+\.java:\d+",       "Java exception in response — may reveal code structure"),
    (r"sqlstate",              "SQL error code in response — potential SQL injection indicator"),
    (r"ORA-\d{5}",             "Oracle DB error exposed"),
    (r"syntax error.*sql",     "SQL syntax error in response"),
    (r"password",              "Keyword 'password' found in response body"),
    (r'"token"\s*:\s*"[^"]+"', "Token value visible in response — verify this is intentional"),
]

AUTH_HEADERS = {"authorization", "x-api-key", "api-key", "bearer", "x-auth-token"}


def check_security(request_headers: dict, response: httpx.Response) -> None:
    """
    Run passive security checks on a request/response pair.
    Prints a consolidated warning panel if issues are found.
    """
    warnings = []
    tips     = []

    # ── Check 1: Missing authentication ─────────────────────────────────────
    req_keys = {k.lower() for k in request_headers}
    if not req_keys & AUTH_HEADERS:
        warnings.append("⚠  No authentication header sent  (Authorization / X-API-Key)")

    # ── Check 2: HTTP (not HTTPS) ────────────────────────────────────────────
    if str(response.url).startswith("http://"):
        warnings.append("🔓 Request sent over plain HTTP — credentials/data are unencrypted")

    # ── Check 3: Missing security headers in response ────────────────────────
    resp_keys = {k.lower() for k in response.headers}
    for hdr, msg in GOOD_HEADERS.items():
        if hdr in resp_keys:
            tips.append(f"✅ {msg}")

    # ── Check 4: Verbose error / info leakage in body ───────────────────────
    body_text = response.text.lower()[:5000]
    for pattern, description in LEAK_PATTERNS:
        if re.search(pattern, body_text, re.IGNORECASE):
            warnings.append(f"🔍 {description}")

    # ── Check 5: 500 from a POST/PUT (possible injection surface) ───────────
    if response.status_code == 500 and response.request.method in ("POST", "PUT", "PATCH"):
        warnings.append("💥 500 on a write request — possible unhandled input, review server logs")

    # ── Render panel only if there is something to say ───────────────────────
    if not warnings and not tips:
        return

    content = Text()
    for w in warnings:
        content.append(f"{w}\n", style="bold yellow")
    for t in tips:
        content.append(f"{t}\n", style="dim green")

    console.print(Panel(
        content,
        title="🔐 Security Awareness",
        border_style="yellow" if warnings else "green",
    ))
