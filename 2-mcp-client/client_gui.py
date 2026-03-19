"""
CBC MCP Workshop — Module 2
MCP Web GUI Client

A Flask web app that connects to an MCP server and lets you
chat with Claude through a browser interface.

Usage:
    uv run 2-mcp-client/client_gui.py

Then open: http://127.0.0.1:5000

Claude Builder Club | University of Ghana
"""

import asyncio
import os
import threading
from contextlib import AsyncExitStack

import anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 1024
DEFAULT_SERVER = "1-mcp-server/my_calendar.py"

app = Flask(__name__)

# Shared state for the async MCP session (one session per app instance)
_session_lock = threading.Lock()
_loop: asyncio.AbstractEventLoop | None = None
_session_ready = threading.Event()
_mcp_session: ClientSession | None = None
_tools: list[dict] = []
_conversation_history: list[dict] = []
_client = anthropic.AsyncAnthropic()


async def _start_mcp_session(server_script: str) -> None:
    """Initialize the MCP session. Runs in a dedicated async thread."""
    global _mcp_session, _tools

    server_params = StdioServerParameters(
        command="uv",
        args=["run", server_script],
        env=None,
    )

    async with AsyncExitStack() as stack:
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()

        tools_result = await session.list_tools()
        _tools = [
            {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,
            }
            for t in tools_result.tools
        ]
        _mcp_session = session
        _session_ready.set()

        # Keep running until the app stops
        await asyncio.get_event_loop().create_future()


def _run_async_loop(server_script: str) -> None:
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(_start_mcp_session(server_script))


async def _chat(user_message: str) -> str:
    """Send a message to Claude and handle tool calls. Returns Claude's final reply."""
    _conversation_history.append({"role": "user", "content": user_message})

    while True:
        response = await _client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=_tools,
            messages=_conversation_history,
        )

        assistant_content = []
        tool_calls_made = []

        for block in response.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )
                tool_calls_made.append(block)

        _conversation_history.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason == "end_turn" or not tool_calls_made:
            final_text = " ".join(
                b.text for b in response.content if hasattr(b, "text")
            )
            return final_text

        # Execute tool calls
        tool_results = []
        for tool_call in tool_calls_made:
            try:
                result = await _mcp_session.call_tool(tool_call.name, tool_call.input)
                result_text = (
                    result.content[0].text
                    if result.content
                    else "Tool returned no output."
                )
            except Exception as e:
                result_text = f"Tool error: {e}"

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result_text,
                }
            )

        _conversation_history.append({"role": "user", "content": tool_results})


# ─── Flask routes ────────────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html", tools=_tools)


@app.route("/chat", methods=["POST"])
def chat():
    if not _session_ready.is_set():
        return jsonify({"error": "MCP session not ready yet. Please wait a moment."}), 503

    data = request.get_json()
    user_message = (data or {}).get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    future = asyncio.run_coroutine_threadsafe(_chat(user_message), _loop)
    try:
        reply = future.result(timeout=30)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    _conversation_history.clear()
    return jsonify({"status": "Conversation history cleared."})


@app.route("/tools")
def list_tools():
    return jsonify({"tools": [t["name"] for t in _tools]})


# ─── Entry point ─────────────────────────────────────────────────────────────


if __name__ == "__main__":
    server_script = os.environ.get("MCP_SERVER", DEFAULT_SERVER)
    print(f"\n🚀 CBC MCP Workshop — Web GUI Client")
    print(f"   MCP server: {server_script}")
    print(f"   Starting at: http://127.0.0.1:5000\n")

    thread = threading.Thread(target=_run_async_loop, args=(server_script,), daemon=True)
    thread.start()

    # Wait for MCP session before accepting requests
    print("⏳ Waiting for MCP session to initialize...")
    _session_ready.wait(timeout=15)
    if _session_ready.is_set():
        tool_names = [t["name"] for t in _tools]
        print(f"✅ Ready! Tools loaded: {', '.join(tool_names)}")
    else:
        print("⚠️  MCP session timed out. Check your server script path.")

    app.run(debug=False, port=5000)
