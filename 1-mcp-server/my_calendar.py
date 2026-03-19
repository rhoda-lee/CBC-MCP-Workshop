"""
CBC MCP Workshop — Module 1
Calendar MCP Server

This server exposes event management tools to Claude via MCP.
It stores events in memory (they reset when the server stops).
Claude Builder Club | University of Ghana
"""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CBC Calendar")

# In-memory event store: { "YYYY-MM-DD": ["event1", "event2", ...] }
events: dict[str, list[str]] = {}


def _validate_date(date: str) -> None:
    """Raise ValueError if date is not in YYYY-MM-DD format."""
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"Invalid date '{date}'. Please use YYYY-MM-DD format (e.g. 2025-12-25).") from exc


@mcp.tool()
def add_event(date: str, event: str) -> str:
    """Add an event to the calendar on a specific date.

    Args:
        date: Date in YYYY-MM-DD format (e.g. 2025-12-25)
        event: Description of the event or reminder
    """
    _validate_date(date)
    if date not in events:
        events[date] = []
    events[date].append(event)
    return f"✅ Added '{event}' on {date}."


@mcp.tool()
def get_events(date: str) -> str:
    """Get all events for a specific date.

    Args:
        date: Date in YYYY-MM-DD format (e.g. 2025-12-25)
    """
    _validate_date(date)
    if date not in events or not events[date]:
        return f"No events found for {date}."
    event_list = "\n".join(f"  • {e}" for e in events[date])
    return f"📅 Events on {date}:\n{event_list}"


@mcp.tool()
def list_all_events() -> str:
    """List all events across all dates in the calendar."""
    if not events:
        return "Your calendar is empty. Try adding some events!"

    lines = ["📆 All upcoming events:\n"]
    for date in sorted(events.keys()):
        lines.append(f"  {date}:")
        for event in events[date]:
            lines.append(f"    • {event}")
    return "\n".join(lines)


@mcp.tool()
def delete_event(date: str, event: str) -> str:
    """Delete a specific event from the calendar.

    Args:
        date: Date in YYYY-MM-DD format (e.g. 2025-12-25)
        event: The exact event description to delete
    """
    _validate_date(date)
    if date not in events or event not in events[date]:
        return f"❌ Could not find '{event}' on {date}."
    events[date].remove(event)
    if not events[date]:
        del events[date]
    return f"🗑️ Deleted '{event}' from {date}."


@mcp.tool()
def clear_date(date: str) -> str:
    """Remove all events from a specific date.

    Args:
        date: Date in YYYY-MM-DD format (e.g. 2025-12-25)
    """
    _validate_date(date)
    if date not in events:
        return f"No events to clear on {date}."
    count = len(events[date])
    del events[date]
    return f"🧹 Cleared {count} event(s) from {date}."


@mcp.prompt()
def calendar_assistant() -> str:
    """A prompt template for a helpful calendar assistant."""
    return (
        "You are a helpful personal assistant managing a calendar. "
        "When adding events, always confirm the date and event details with the user. "
        "Use the YYYY-MM-DD date format for all calendar operations. "
        "Be proactive — after adding an event, offer to show all events for that day."
    )


if __name__ == "__main__":
    mcp.run()
