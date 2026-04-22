# ⚡ apitool-cli

> Modular Python CLI for API testing and interactive learning — REST, SOAR, and Graph APIs.

Built for **cybersecurity students** and **SOC analysts** who want to test, fuzz, and understand APIs — all from the terminal.

---

## 📸 Preview

![apitool CLI preview](./screenshots/preview.png)

> *The tool running in terminal — showing all 4 available subcommands.*

---

## ✨ Features

- 🔧 **Test Mode** — Send HTTP requests (GET, POST, PUT, DELETE, PATCH), measure response time, pretty-print JSON responses
- 🔍 **Fuzz Mode** — Enumerate API endpoints using a wordlist with concurrent threads
- 📚 **Learn Mode** — Interactive lessons for REST, SOAR, and GraphQL with **live API exercises**
- 🗂️ **History Mode** — Save, view, and re-run past requests from a local JSON store
- 🔐 **Security Awareness** — Passive checks on every request: missing auth headers, plain HTTP, leaked stack traces, SQL errors in responses

---

## 📦 Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/apitool-cli.git
cd apitool-cli

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
python apitool.py [COMMAND] [OPTIONS]
```

### Commands

| Command   | Description                                          |
|-----------|------------------------------------------------------|
| `test`    | Send an HTTP request and display the response        |
| `fuzz`    | Fuzz API endpoints using a wordlist                  |
| `learn`   | Interactive learning mode for REST, SOAR, Graph APIs |
| `history` | View, re-run, or clear request history               |

---

## 🔧 test — Send HTTP Requests

```bash
# Simple GET request
python apitool.py test -u https://jsonplaceholder.typicode.com -p /posts/1

# POST with JSON body and custom headers
python apitool.py test \
  --url https://httpbin.org/post \
  --method POST \
  --header "Authorization=Bearer mytoken" \
  --body '{"title":"Hello","body":"World"}' \
  --save
```

**Options:**

| Flag        | Short | Description                          |
|-------------|-------|--------------------------------------|
| `--url`     | `-u`  | Target URL (required)                |
| `--path`    | `-p`  | Endpoint path e.g. `/users/1`        |
| `--method`  | `-m`  | HTTP method (default: GET)           |
| `--header`  | `-H`  | Header as `key=value` (repeatable)   |
| `--body`    | `-b`  | JSON body string                     |
| `--timeout` | `-t`  | Timeout in seconds (default: 10)     |
| `--save`    | `-s`  | Save result to history               |

---

## 🔍 fuzz — Enumerate Endpoints

```bash
python apitool.py fuzz \
  --url https://httpbin.org \
  --wordlist wordlists/common_api_paths.txt \
  --threads 10
```

Shows only **interesting** responses — `200`, `201`, `301`, `403`, `500`. A sample wordlist is included.

---

## 📚 learn — Interactive Learning Mode

```bash
# Show topic menu
python apitool.py learn

# Jump to a specific topic
python apitool.py learn --topic rest
python apitool.py learn --topic soar
python apitool.py learn --topic graph
```

Each module includes theory, diagrams, and **live API calls** you can interact with.

| Topic   | What you learn                                                |
|---------|---------------------------------------------------------------|
| `rest`  | HTTP methods, status codes, statelessness, live GET exercise  |
| `soar`  | What SOAR is, incident lifecycle, simulated API call          |
| `graph` | GraphQL vs REST, schema/query/mutation, live GraphQL query    |

---

## 🗂️ history — Request History

```bash
# List all saved requests
python apitool.py history --list

# Re-run entry #3
python apitool.py history --rerun 3

# Export history to a file
python apitool.py history --export ~/backup.json

# Clear all history
python apitool.py history --clear
```

History is stored at `~/.apitool_history.json`.

---

## 🔐 Security Awareness

Every `test` request is automatically scanned. The tool warns you about:

| Check | Description |
|-------|-------------|
| 🔓 Plain HTTP | Request sent without TLS encryption |
| 🔑 No Auth Header | Missing `Authorization` / `X-API-Key` |
| 💥 500 on Write | Possible unhandled input on POST/PUT/PATCH |
| 🔍 Info Leakage | Stack traces, SQL errors, tokens in response body |
| ✅ Good Headers | Flags presence of HSTS, CSP, X-Frame-Options |

> It warns you. It never exploits.

---

## 🗂️ Project Structure

```
apitool-cli/
├── apitool.py                  ← Entry point
├── requirements.txt
├── README.md
├── screenshots/
│   └── preview.png             ← Add your screenshot here
├── wordlists/
│   └── common_api_paths.txt
└── modules/
    ├── test_mode.py            ← HTTP request engine
    ├── fuzz_mode.py            ← Threaded endpoint fuzzer
    ├── learn_mode.py           ← REST / SOAR / Graph lessons
    ├── history_mode.py         ← JSON persistence layer
    └── security.py             ← Passive security checks
```

---

## 🛠️ Tech Stack

| Library  | Purpose                        |
|----------|--------------------------------|
| `httpx`  | Async-capable HTTP client      |
| `rich`   | Colourised terminal output     |
| `click`  | Subcommand CLI framework       |

**Python 3.10+** recommended.

---

## 📋 Quick Examples

```bash
# Test a public API
python apitool.py test -u https://api.github.com -p /users/octocat

# Learn GraphQL interactively
python apitool.py learn --topic graph

# Fuzz an API
python apitool.py fuzz -u https://httpbin.org -w wordlists/common_api_paths.txt

# Check your history
python apitool.py history --list
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](./LICENSE)

---

<p align="center">Built with ❤️ for cybersecurity students and SOC analysts</p>
