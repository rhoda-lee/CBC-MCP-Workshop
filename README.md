# 🤖 CBC MCP Workshop

**Claude Builder Club · University of Ghana**

A hands-on workshop introducing the **Model Context Protocol (MCP)** using Claude. You will progress from building your first MCP server to connecting it to a fully working client — both in the terminal and in a browser.

> *"AI is for all, not for techies."* — CBC Philosophy

---

## What is MCP?

The **Model Context Protocol** is an open standard that lets you connect Claude (and other AI models) to external tools, APIs, and data sources. Instead of Claude only knowing what was in its training data, MCP lets it take real actions — like doing math, managing a calendar, reading files, or calling APIs.

```
Your App / Client
      │
      ▼
 MCP Client  ──────────►  Claude (via Anthropic API)
      │                         │
      ▼                         │  tool calls
 MCP Server  ◄──────────────────┘
  (your tools)
```

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | >= 3.10 | [python.org](https://www.python.org/downloads/) |
| uv | latest | See below |

Install `uv` (a fast Python package manager):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternatives
pip install uv          # via pip
brew install uv         # via Homebrew (macOS)
winget install astral-sh.uv  # via winget (Windows)
```

---

## Quick Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/CBC-MCP-Workshop.git
cd CBC-MCP-Workshop

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Open .env and paste your key from https://console.anthropic.com/
```

> **Using uv?** Replace steps 2–3 with:
> ```bash
> uv venv && source .venv/bin/activate
> uv sync
> ```

---

## Project Structure

```
CBC-MCP-Workshop/
├── 1-mcp-server/
│   ├── my_calculator.py     # Module 1a — Calculator MCP server
│   └── my_calendar.py       # Module 1b — Calendar MCP server
│
├── 2-mcp-client/
│   ├── client_cli.py        # Module 2a — Terminal chat client
│   ├── client_gui.py        # Module 2b — Browser chat client
│   └── templates/
│       └── index.html       # Web UI for the GUI client
│
├── 3-real-world-mcp/
│   └── GUIDE.md             # Module 3 — Live demo: Asana + Notion
│
├── pyproject.toml           # Dependencies (managed by uv)
├── requirements.txt         # Dependencies (managed by pip)
├── .env.example             # API key template
└── README.md
```

---

## Workshop Modules

### Module 1a — Calculator MCP Server

**File:** `1-mcp-server/my_calculator.py`

Your first MCP server. It exposes six math operations to Claude as callable tools.

**Tools exposed:**

| Tool | Description |
|------|-------------|
| `add(a, b)` | Add two numbers |
| `subtract(a, b)` | Subtract b from a |
| `multiply(a, b)` | Multiply two numbers |
| `divide(a, b)` | Divide a by b |
| `power(base, exp)` | Raise base to a power |
| `square_root(n)` | Square root of a number |

**Key concepts introduced:**
- `FastMCP` — the quickest way to create an MCP server
- `@mcp.tool()` — decorator that exposes a Python function as an MCP tool
- `@mcp.prompt()` — decorator for reusable prompt templates
- Tool documentation via Python docstrings

**Run standalone to test:**
```bash
uv run 1-mcp-server/my_calculator.py
```

**Add to Claude Desktop** (Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": [
        "--directory", "/ABSOLUTE/PATH/TO/CBC-MCP-Workshop/1-mcp-server",
        "run", "my_calculator.py"
      ]
    }
  }
}
```

> 💡 **Get the absolute path:** In VS Code, right-click the folder → *Copy Path*. On macOS/Linux run `pwd`. On Windows run `cd`.

Restart Claude Desktop, then ask: *"What is 15 × 23?"*

---

### Module 1b — Calendar MCP Server

**File:** `1-mcp-server/my_calendar.py`

A more advanced server that manages a personal calendar. Events are stored in memory while the server is running.

**Tools exposed:**

| Tool | Description |
|------|-------------|
| `add_event(date, event)` | Add an event on a date |
| `get_events(date)` | Get all events for a date |
| `list_all_events()` | List every event on the calendar |
| `delete_event(date, event)` | Delete a specific event |
| `clear_date(date)` | Remove all events from a date |

**Date format:** All dates must be `YYYY-MM-DD` (e.g. `2025-12-25`).

**Key concepts introduced:**
- In-memory state management in MCP servers
- Input validation with helpful error messages
- Multiple tool parameters and docstring documentation

**Add to Claude Desktop** (alongside the calculator):

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": ["--directory", "/PATH/TO/1-mcp-server", "run", "my_calculator.py"]
    },
    "calendar": {
      "command": "uv",
      "args": ["--directory", "/PATH/TO/1-mcp-server", "run", "my_calendar.py"]
    }
  }
}
```

Restart Claude Desktop, then try: *"Add a team meeting on 2025-12-10"*

---

### Module 2a — MCP CLI Client

**File:** `2-mcp-client/client_cli.py`

Build your own MCP client! This script connects to any MCP server, loads its tools, and starts an interactive chat loop with Claude.

**Run it:**
```bash
# Connect to the calendar server
uv run 2-mcp-client/client_cli.py 1-mcp-server/my_calendar.py

# Or the calculator
uv run 2-mcp-client/client_cli.py 1-mcp-server/my_calculator.py
```

**Try these prompts:**
```
Add a birthday event on 2025-12-20
Show me all my events
What's the square root of 256?
Delete the birthday event on 2025-12-20
```

**Key concepts introduced:**
- `ClientSession` — MCP client session management
- `stdio_client` — connecting to a server over standard I/O
- The **agentic loop** — Claude calls a tool → tool runs → result goes back to Claude → repeat
- `AsyncExitStack` for async context management

---

### Module 2b — MCP Web GUI Client

**File:** `2-mcp-client/client_gui.py`

A Flask web application that wraps the MCP client in a clean browser UI.

**Run it:**
```bash
python 2-mcp-client/client_gui.py
```

Then open **http://127.0.0.1:5000** in your browser.

**To connect to a different server:**
```bash
MCP_SERVER=1-mcp-server/my_calculator.py python 2-mcp-client/client_gui.py
```

**Key concepts introduced:**
- Running async MCP code in a background thread from Flask
- REST API endpoints for chat and conversation management
- Full conversation history management across requests

---

### Module 3 — Real-World MCP: Asana + Notion (Bonus Demo)

**File:** `3-real-world-mcp/GUIDE.md`

The live demo module. No code to write — just connect Claude Code to two real tools and watch it work across both simultaneously.

**Tools connected:**
- **Asana** — fetch and update real tasks
- **Notion** — create and populate real pages

**Setup (run once before the workshop):**

```bash
# Add both MCP servers
claude mcp add --transport sse asana https://mcp.asana.com/sse
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Authenticate both inside a Claude Code session
claude
/mcp
```

**The centrepiece demo prompt:**

```
I want a weekly planning summary. Do all of this:
1. Fetch all my incomplete Asana tasks due this week
2. Group them by project
3. Create a new Notion page called "CBC Weekly Plan — [today's date]"
4. On that page, create a section for each project with tasks as checkboxes
5. Add a "Priority focus" section at the top with the 3 most urgent tasks
Report what you created when done.
```

**Key concepts introduced:**
- Remote MCP servers (hosted by the tool provider, not on your machine)
- OAuth authentication via `/mcp`
- `claude mcp add` command
- Multi-tool workflows — one prompt, two live services

Full guide with troubleshooting and facilitator prep checklist: `3-real-world-mcp/GUIDE.md`

---

## How the Agentic Loop Works

This is the core pattern behind every MCP client:

```
1. User sends a message
        │
        ▼
2. Claude receives the message + list of available tools
        │
        ▼
3. Claude decides: "I need to use a tool"
        │
        ▼
4. MCP client receives the tool call → executes it on the server
        │
        ▼
5. Tool result is sent back to Claude
        │
        ▼
6. Claude uses the result to form its response
        │
        ▼
7. If Claude wants another tool → go to step 3
   Otherwise → return final response to user
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `mcp[cli]` | Model Context Protocol SDK |
| `anthropic` | Anthropic Claude API |
| `python-dotenv` | Load `.env` API keys |
| `flask` | Web server for the GUI client |

---

## Troubleshooting

**`ANTHROPIC_API_KEY not found`**
→ Make sure you copied `.env.example` to `.env` and added your key.

**`uv: command not found`**
→ Restart your terminal after installing `uv`, or use its full path (`which uv` on Mac/Linux, `where uv` on Windows).

**Claude Desktop shows no tools**
→ Check that your path in `claude_desktop_config.json` is the *absolute* path with no typos. Restart Claude Desktop after editing.

**`ModuleNotFoundError`**
→ Make sure your virtual environment is activated: `source .venv/bin/activate`

---

## What to Build Next

Once you finish the workshop, try extending what you've built:

- **Add persistence** — save calendar events to a JSON file so they survive restarts
- **New tool** — add a `search_events(keyword)` tool to the calendar server
- **New server** — build an MCP server for a to-do list, a quiz, or a currency converter
- **Remote MCP** — connect to a publicly hosted MCP server (GitHub, Brave Search, etc.)

---

## About CBC

The **Claude Builder Club** at the University of Ghana is a student-led AI community of 600+ members on a mission to make AI accessible across all disciplines — not just tech.

- 🌐 Find us on LinkedIn and Instagram: **@claudebuilderclub**
- 📧 Interested in partnering? Reach out to our leadership team.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Feel free to fork, adapt, and use this workshop for your own community! 🚀
