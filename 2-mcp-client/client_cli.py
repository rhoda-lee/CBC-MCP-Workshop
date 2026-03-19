"""
CBC MCP Workshop — Module 2
MCP CLI Client

Connects to an MCP server and lets you chat with Claude
using the server's tools — all from your terminal.

Usage:
    uv run 2-mcp-client/client_cli.py 1-mcp-server/my_calendar.py

Claude Builder Club | University of Ghana
"""

import asyncio
import sys
from contextlib import AsyncExitStack

import anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 1024


async def run_chat(server_script: str) -> None:
    """Start an interactive chat session with Claude + the given MCP server."""

    client = anthropic.AsyncAnthropic()

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

        # Fetch available tools from the MCP server
        tools_result = await session.list_tools()
        tools = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in tools_result.tools
        ]

        tool_names = [t["name"] for t in tools]
        print(f"\n🔧 Connected! Tools available: {', '.join(tool_names)}")
        print("💬 Type your message (or 'quit' to exit)\n")
        print("─" * 50)

        conversation_history = []

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGoodbye! 👋")
                break

            if user_input.lower() in ("quit", "exit", "q"):
                print("\nGoodbye! 👋")
                break

            if not user_input:
                continue

            conversation_history.append({"role": "user", "content": user_input})

            # Agentic loop: keep calling Claude until no more tool calls
            while True:
                response = await client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    tools=tools,
                    messages=conversation_history,
                )

                # Collect all text + tool use blocks
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

                conversation_history.append(
                    {"role": "assistant", "content": assistant_content}
                )

                # If no tool calls, print response and break the inner loop
                if response.stop_reason == "end_turn" or not tool_calls_made:
                    for block in response.content:
                        if hasattr(block, "text"):
                            print(f"\nClaude: {block.text}")
                    break

                # Execute tool calls and feed results back
                tool_results = []
                for tool_call in tool_calls_made:
                    print(f"\n  ⚙️  Using tool: {tool_call.name}({tool_call.input})")
                    try:
                        result = await session.call_tool(tool_call.name, tool_call.input)
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

                conversation_history.append({"role": "user", "content": tool_results})


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run 2-mcp-client/client_cli.py <path-to-mcp-server.py>")
        print("Example: uv run 2-mcp-client/client_cli.py 1-mcp-server/my_calendar.py")
        sys.exit(1)

    server_script = sys.argv[1]
    print(f"\n🚀 CBC MCP Workshop — CLI Client")
    print(f"   Connecting to server: {server_script}\n")
    asyncio.run(run_chat(server_script))


if __name__ == "__main__":
    main()
