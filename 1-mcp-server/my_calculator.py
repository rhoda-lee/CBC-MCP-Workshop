"""
CBC MCP Workshop — Module 1
Calculator MCP Server

This server exposes basic and advanced math tools to Claude via MCP.
Claude Builder Club | University of Ghana
"""

import math
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CBC Calculator")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a.

    Args:
        a: First number
        b: Number to subtract
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b.

    Args:
        a: Numerator
        b: Denominator (must not be zero)
    """
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent.

    Args:
        base: The base number
        exponent: The exponent
    """
    return base ** exponent


@mcp.tool()
def square_root(number: float) -> float:
    """Calculate the square root of a number.

    Args:
        number: The number to find the square root of (must be >= 0)
    """
    if number < 0:
        raise ValueError("Cannot take square root of a negative number!")
    return math.sqrt(number)


@mcp.prompt()
def math_helper() -> str:
    """A prompt template that tells Claude to act as a helpful math tutor."""
    return (
        "You are a friendly math tutor. When solving problems, "
        "show your working step by step and explain each operation clearly. "
        "Use the available calculator tools to perform calculations."
    )


if __name__ == "__main__":
    mcp.run()
