"""
modules/learn_mode.py
Handles the `apitool learn` subcommand.
Provides interactive lessons and live exercises for REST, SOAR, and Graph APIs.
"""

import json
import time

import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table

console = Console()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _section(title: str, color: str = "cyan") -> None:
    console.print()
    console.print(Rule(f"[bold {color}]{title}[/]", style=color))
    console.print()


def _info(md_text: str) -> None:
    console.print(Markdown(md_text))


def _pause() -> None:
    Prompt.ask("\n[dim]Press Enter to continue…[/]", default="")


def _live_get(url: str, label: str = "Live Example") -> None:
    """Perform a GET and show the response inside a panel."""
    console.print(f"\n[cyan]🌐 GET[/] {url}")
    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        try:
            body = json.dumps(resp.json(), indent=2)
            syntax = Syntax(body, "json", theme="monokai", line_numbers=False, word_wrap=True)
            console.print(Panel(syntax,
                                title=f"✅ {label}  —  {resp.status_code}",
                                border_style="green"))
        except Exception:
            console.print(Panel(resp.text[:800],
                                title=f"✅ {label}  —  {resp.status_code}",
                                border_style="green"))
    except Exception as exc:
        console.print(Panel(f"[red]{exc}[/]",
                            title="❌ Request failed", border_style="red"))


# ══════════════════════════════════════════════════════════════════════════════
# REST MODULE
# ══════════════════════════════════════════════════════════════════════════════

REST_METHODS = {
    "GET":    ("Retrieve a resource. No body. Idempotent.",   "green"),
    "POST":   ("Create a new resource. Sends a body.",         "yellow"),
    "PUT":    ("Replace an existing resource entirely.",       "blue"),
    "PATCH":  ("Partially update a resource.",                 "magenta"),
    "DELETE": ("Remove a resource. Idempotent.",              "red"),
}

STATUS_CODES = [
    ("200 OK",                  "Success — response body included.",          "green"),
    ("201 Created",             "Resource successfully created.",              "green"),
    ("204 No Content",          "Success — no response body.",                 "green"),
    ("301 Moved Permanently",   "Redirect to a new URL permanently.",          "yellow"),
    ("400 Bad Request",         "Client sent malformed input.",                "yellow"),
    ("401 Unauthorized",        "Authentication required.",                    "red"),
    ("403 Forbidden",           "Authenticated but not authorised.",           "red"),
    ("404 Not Found",           "Resource does not exist.",                    "red"),
    ("429 Too Many Requests",   "Rate-limited — slow down.",                   "red"),
    ("500 Internal Server Error","Server-side bug — not your fault.",          "bold red"),
]


def _learn_rest() -> None:
    _section("📖 REST APIs — Fundamentals", "cyan")

    _info("""
## What is REST?

**REST** (Representational State Transfer) is an architectural style for building web services.
A RESTful API exposes **resources** (e.g. `/users`, `/posts`) that clients manipulate using
standard **HTTP methods**.

### Key Principles
- **Stateless** — each request carries all the information the server needs; no session stored server-side.
- **Uniform interface** — resources identified by URLs; actions described by HTTP verbs.
- **Client–Server** — frontend and backend are decoupled.
- **Cacheable** — responses may indicate whether they can be cached.
""")

    _pause()

    # HTTP Methods table
    _section("HTTP Methods", "blue")
    t = Table(header_style="bold cyan", show_lines=True)
    t.add_column("Method",  width=10)
    t.add_column("Purpose", width=45)
    t.add_column("Idempotent?", justify="center", width=14)
    idempotent = {"GET": "✅", "POST": "❌", "PUT": "✅", "PATCH": "❌", "DELETE": "✅"}
    for m, (desc, color) in REST_METHODS.items():
        t.add_row(f"[{color}]{m}[/]", desc, idempotent[m])
    console.print(t)

    _pause()

    # Status codes
    _section("HTTP Status Codes", "blue")
    t2 = Table(header_style="bold cyan", show_lines=True)
    t2.add_column("Code",    width=28)
    t2.add_column("Meaning", width=45)
    for code, meaning, color in STATUS_CODES:
        t2.add_row(f"[{color}]{code}[/]", meaning)
    console.print(t2)

    _pause()

    # Live exercise
    _section("🧪 Mini Exercise — Live GET Request", "green")
    _info("Let's call a **public REST API** to see it in action.")
    console.print("[cyan]Public API:[/] https://jsonplaceholder.typicode.com/posts/1")
    _live_get("https://jsonplaceholder.typicode.com/posts/1", "GET /posts/1")

    if Confirm.ask("\n[cyan]Try modifying the endpoint?[/]", default=True):
        path = Prompt.ask("Enter path (e.g. /users/2)", default="/users/2")
        _live_get(f"https://jsonplaceholder.typicode.com{path}", f"GET {path}")

    console.print("\n[green bold]✔  REST module complete![/]")


# ══════════════════════════════════════════════════════════════════════════════
# SOAR MODULE
# ══════════════════════════════════════════════════════════════════════════════

SOAR_PHASES = [
    ("1. Ingest",    "An alert arrives — from SIEM, EDR, email gateway, etc."),
    ("2. Triage",    "Automated enrichment: IP reputation, file hash lookups, user history."),
    ("3. Decision",  "Rule engine decides: close as FP, escalate, or auto-remediate."),
    ("4. Response",  "Actions executed: block IP, isolate host, open ticket, notify analyst."),
    ("5. Close",     "Incident documented, metrics updated, playbook improved."),
]


def _learn_soar() -> None:
    _section("🛡️  SOAR APIs — Security Orchestration", "magenta")

    _info("""
## What is SOAR?

**SOAR** = **S**ecurity **O**rchestration, **A**utomation and **R**esponse.

SOAR platforms (e.g. Splunk SOAR, Palo Alto XSOAR, IBM QRadar SOAR) expose REST APIs
that allow analysts and scripts to:

- Create and update **incidents / cases**
- Run **playbooks** (automated response workflows)
- Query **threat intelligence** enrichment
- Integrate with **ticketing systems** (Jira, ServiceNow)

In a SOC, SOAR glues every tool together so analysts handle only what matters.
""")

    _pause()

    # Lifecycle
    _section("Incident Lifecycle", "magenta")
    for step, desc in SOAR_PHASES:
        console.print(f"  [bold magenta]{step}[/]  —  {desc}")

    _pause()

    # Simulated API calls
    _section("🧪 Simulated SOAR API Calls", "yellow")
    _info("""
Real SOAR APIs look like this. We'll simulate them with a public echo endpoint
so you can see the request/response cycle without needing credentials.
""")

    # Simulate creating an incident
    mock_incident = {
        "title":    "Suspicious PowerShell Execution",
        "severity": "High",
        "source":   "EDR",
        "details":  {
            "host":     "WIN-WORKSTATION-07",
            "user":     "jdoe",
            "command":  "powershell -enc JAB...",
            "mitre":    "T1059.001"
        }
    }

    console.print("\n[cyan]Simulated:[/]  POST /api/v1/incidents")
    syntax = Syntax(json.dumps(mock_incident, indent=2), "json",
                    theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="📤 Incident Payload", border_style="yellow"))

    console.print("\n[dim]Sending to public echo service…[/]")
    try:
        resp = httpx.post(
            "https://httpbin.org/post",
            json=mock_incident,
            timeout=10
        )
        data = resp.json()
        echoed = json.dumps(data.get("json", {}), indent=2)
        console.print(Panel(
            Syntax(echoed, "json", theme="monokai"),
            title=f"📥 Echo Response — {resp.status_code}",
            border_style="green"
        ))
        console.print("\n[green]✔  In a real SOAR platform this would create incident #1234.[/]")
    except Exception as exc:
        console.print(f"[red]Network unavailable: {exc}[/]")

    _pause()

    # Security note
    _section("🔐 Security Note", "red")
    _info("""
SOAR API keys have **high privileges** — they can isolate hosts and block IPs.

Always:
- Store API keys in a secrets manager (not plaintext config files)
- Use least-privilege roles per playbook
- Audit every automated action
- Test playbooks in a **staging** environment first
""")

    console.print("\n[green bold]✔  SOAR module complete![/]")


# ══════════════════════════════════════════════════════════════════════════════
# GRAPH API MODULE
# ══════════════════════════════════════════════════════════════════════════════

GRAPHQL_QUERY = """{
  country(code: "KE") {
    name
    capital
    currency
    continent {
      name
    }
    languages {
      name
    }
  }
}"""


def _learn_graph() -> None:
    _section("🕸️  Graph APIs — GraphQL & Beyond", "yellow")

    _info("""
## REST vs GraphQL

| Aspect            | REST                          | GraphQL                        |
|-------------------|-------------------------------|--------------------------------|
| Endpoints         | One URL per resource          | Single `/graphql` endpoint     |
| Data fetching     | Over-fetch or under-fetch     | Exactly what you ask for       |
| Versioning        | `/v1/`, `/v2/`…               | Evolve schema, no versioning   |
| Learning curve    | Low                           | Medium                         |
| Tooling           | Postman, curl, etc.           | GraphiQL, Apollo Studio, etc.  |

## Key Concepts

- **Schema** — typed contract that describes all available data and operations.
- **Query** — read data (like GET).
- **Mutation** — write / update data (like POST / PATCH).
- **Subscription** — real-time data over WebSocket.
- **Resolver** — server function that returns data for a field.
- **Nodes & Edges** — every entity is a *node*; relationships are *edges*.
""")

    _pause()

    _section("🧪 Live GraphQL Query", "green")
    console.print("[cyan]Endpoint:[/] https://countries.trevorblades.com/")
    console.print("\n[cyan]Query:[/]")
    console.print(Syntax(GRAPHQL_QUERY, "graphql", theme="monokai"))

    console.print("\n[dim]Executing…[/]")
    try:
        resp = httpx.post(
            "https://countries.trevorblades.com/",
            json={"query": GRAPHQL_QUERY},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        data = resp.json()
        pretty = json.dumps(data.get("data", data), indent=2)
        console.print(Panel(
            Syntax(pretty, "json", theme="monokai"),
            title=f"📥 GraphQL Response — {resp.status_code}",
            border_style="green"
        ))
    except Exception as exc:
        console.print(f"[red]Could not reach endpoint: {exc}[/]")
        console.print(Panel(
            '{\n  "data": {\n    "country": {\n'
            '      "name": "Kenya",\n      "capital": "Nairobi",\n'
            '      "currency": "KES"\n    }\n  }\n}',
            title="📦 Expected Response (offline)", border_style="yellow"
        ))

    _pause()

    if Confirm.ask("\n[cyan]Try your own country code?[/]", default=True):
        code = Prompt.ask("Enter ISO 2-letter country code", default="NG").upper()
        custom_q = f'{{\n  country(code: "{code}") {{\n    name\n    capital\n    currency\n  }}\n}}'
        console.print(Syntax(custom_q, "graphql", theme="monokai"))
        try:
            r2 = httpx.post(
                "https://countries.trevorblades.com/",
                json={"query": custom_q},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            console.print(Panel(
                Syntax(json.dumps(r2.json(), indent=2), "json", theme="monokai"),
                title=f"📥 {code} — {r2.status_code}", border_style="green"
            ))
        except Exception as exc:
            console.print(f"[red]{exc}[/]")

    console.print("\n[green bold]✔  Graph API module complete![/]")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

TOPICS = {
    "1": ("rest",  "📡 REST APIs",    _learn_rest),
    "2": ("soar",  "🛡️  SOAR APIs",   _learn_soar),
    "3": ("graph", "🕸️  Graph APIs",  _learn_graph),
}


def run_learn(topic: str) -> None:
    if topic == "menu":
        _section("📚 Learning Mode — Choose a Topic", "cyan")
        for key, (_, label, _) in TOPICS.items():
            console.print(f"  [bold cyan]{key}.[/]  {label}")
        console.print(f"  [bold cyan]q.[/]  Quit\n")

        choice = Prompt.ask("Select", choices=["1", "2", "3", "q"], default="1")
        if choice == "q":
            return
        _, _, fn = TOPICS[choice]
        fn()
    else:
        for _, (t, _, fn) in TOPICS.items():
            if t == topic:
                fn()
                return
        console.print(f"[red]Unknown topic:[/] {topic}")
