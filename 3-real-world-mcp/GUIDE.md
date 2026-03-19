# Module 3 — Real-World MCP: Connecting to Live Tools

This is the bonus module. Everything in Modules 1 and 2 used
self-contained servers with no external connections.

Now we go further — connecting Claude to tools you actually use every day:
**Asana** (task management) and **Notion** (notes and docs).

You will watch Claude manage tasks and create documents across two
real apps, from a single terminal session, without opening either app once.

---

## What makes this different

In Modules 1 and 2, you built MCP servers from scratch.
Those servers lived entirely on your machine.

Real-world MCP servers are different:
- They are **hosted remotely** by the tool provider (Asana, Notion, etc.)
- You connect to them over the internet
- You authenticate with your existing account — no code required
- Claude Code connects using the `/mcp` command or `claude mcp add`

You are not building anything in this module.
You are **connecting** Claude to tools that already exist.

---

## The demo scenario

> *"I want Claude to check my Asana tasks for this week,
> then create a Notion page summarising everything I need to do —
> all from the terminal, without opening either app."*

One terminal session. Two live tools. Real data.

---

## Part 1 — Connect Asana

### Step 1: Add the Asana MCP server

Open your terminal and run:

```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

This registers the Asana MCP server with Claude Code.
You only need to do this once — it saves to your Claude Code config.

### Step 2: Authenticate inside Claude Code

Start a Claude Code session:

```bash
claude
```

Then type:

```
/mcp
```

You will see a list of connected MCP servers. Find Asana and
select it to authenticate. Claude Code will open your browser
for OAuth login — sign in with your Asana account.

Once authenticated, Claude Code has access to your Asana workspace.

### Step 3: Try it

Ask Claude:

```
List all my incomplete tasks in Asana that are due this week.
Show the task name, project, and due date for each one.
```

Watch the agentic loop:
- Claude calls the Asana MCP server
- Asana returns your real task data
- Claude formats it into a readable summary

Then try:

```
Mark the first task on that list as complete.
```

Claude will call the Asana tool, make the change, and confirm.
Open Asana in your browser and refresh — the task is actually done.

**That is the moment.** The audience sees real-world impact in real time.

---

## Part 2 — Connect Notion

### Step 1: Add the Notion MCP server

In your terminal (outside a Claude session):

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

### Step 2: Authenticate

Start Claude Code and run `/mcp` again.
Select Notion and sign in with your Notion account via OAuth.

### Step 3: Try it

Ask Claude:

```
Create a new Notion page called "This Week's Tasks".
Add today's date as a subtitle.
List the Asana tasks we just reviewed as a checklist on the page.
```

Claude will:
1. Use the Asana MCP to re-fetch the task list (if needed)
2. Use the Notion MCP to create the page
3. Populate it with the task checklist

Open Notion — the page is there, populated, ready to use.

---

## Part 3 — The combined workflow (live demo centrepiece)

This is the full demo prompt to use in front of the audience.
Run it as one single message after both tools are connected:

```
I want a weekly planning summary. Do all of this:

1. Fetch all my incomplete Asana tasks due this week
2. Group them by project
3. Create a new Notion page called "CBC Weekly Plan — [today's date]"
4. On that page, create a section for each Asana project with
   its tasks listed as checkboxes
5. Add a "Priority focus" section at the top with the 3 most
   urgent tasks highlighted

Report what you created when done.
```

One prompt. Two tools. A genuinely useful output.

---

## What to point out to the audience

**During the demo, narrate these moments:**

1. **When Claude calls a tool** — point out the tool call appearing in the
   terminal. This is the agentic loop from Module 2 happening in real life.

2. **When Claude switches tools** — "notice Claude is now switching from
   Asana to Notion — it's deciding which tool to use for each step."

3. **When the output appears in Notion** — open Notion live and show the
   page. "We didn't touch Notion once. Claude did all of that."

4. **The key point** — "This is what MCP makes possible. Any tool with an
   MCP server can be connected to Claude this way. Asana, Notion, GitHub,
   your database, your own custom tools."

---

## Troubleshooting

**`/mcp` shows the server but says "not connected"**
→ Re-authenticate by selecting the server in `/mcp` and going through OAuth again.

**Claude says it can't find my tasks**
→ Check that your Asana workspace is the one connected.
   Ask: "Which Asana workspace are you connected to?"

**Notion page not appearing**
→ Check that Claude has access to the correct Notion workspace.
   Ask: "Which Notion workspace are you connected to?"

**Authentication keeps failing**
→ Try removing and re-adding the server:
```bash
claude mcp remove asana
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

---

## Checking your connected servers

At any time, list all your MCP servers:

```bash
claude mcp list
```

Or inside a session:

```
/mcp
```

---

## Key concepts introduced in this module

| Concept | What it means |
|---------|--------------|
| Remote MCP server | An MCP server hosted by the tool provider, not on your machine |
| OAuth authentication | Securely connecting Claude to your account without sharing passwords |
| `/mcp` command | Claude Code's built-in tool for managing MCP connections |
| `claude mcp add` | Terminal command to register a new MCP server |
| Multi-tool workflow | One Claude prompt that uses multiple MCP servers in sequence |

---

## What else can you connect?

These tools all have official MCP servers that work the same way:

| Tool | Command |
|------|---------|
| GitHub | `claude mcp add --transport http github https://api.githubcopilot.com/mcp/` |
| Notion | `claude mcp add --transport http notion https://mcp.notion.com/mcp` |
| Asana | `claude mcp add --transport sse asana https://mcp.asana.com/sse` |
| Linear | `claude mcp add --transport http linear https://mcp.linear.app/sse` |

The pattern is always the same:
1. `claude mcp add` with the server URL
2. Authenticate via `/mcp`
3. Start asking Claude to use it in plain language

---

## Before the workshop — facilitator prep checklist

Do this the day before you teach this module:

- [ ] Run `claude mcp add` for both Asana and Notion
- [ ] Authenticate both via `/mcp`
- [ ] Run the combined workflow prompt once privately
- [ ] Confirm the Notion page appears correctly
- [ ] Have Asana open in one browser tab and Notion in another
      ready to show the live output during the demo
- [ ] Know which Asana project you'll use (pick one with 3-5 real tasks)

The worst thing that can happen in a live demo is an auth error in front
of the audience. Running it privately the day before eliminates that risk.
