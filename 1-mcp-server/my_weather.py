"""
CBC MCP Workshop — Module 3 (External API)
Weather MCP Server

This server exposes weather tools to Claude via MCP.
It uses the Open-Meteo API — completely free, no API key required.

Claude Builder Club | University of Ghana
"""

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CBC Weather")

# ── City coordinates ──────────────────────────────────────────────────────────
# Add more Ghanaian and African cities here as needed
CITIES = {
    "accra": {"lat": 5.6037, "lon": -0.1870, "name": "Accra"},
    "kumasi": {"lat": 6.6885, "lon": -1.6244, "name": "Kumasi"},
    "tamale": {"lat": 9.4008, "lon": -0.8393, "name": "Tamale"},
    "cape coast": {"lat": 5.1053, "lon": -1.2466, "name": "Cape Coast"},
    "takoradi": {"lat": 4.8845, "lon": -1.7554, "name": "Takoradi"},
    "sunyani": {"lat": 7.3349, "lon": -2.3123, "name": "Sunyani"},
    "lagos": {"lat": 6.5244, "lon": 3.3792, "name": "Lagos"},
    "nairobi": {"lat": -1.2921, "lon": 36.8219, "name": "Nairobi"},
    "london": {"lat": 51.5074, "lon": -0.1278, "name": "London"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "name": "New York"},
}

# ── Weather code descriptions ─────────────────────────────────────────────────
WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Icy fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow 🌨️",
    73: "Moderate snow 🌨️",
    75: "Heavy snow ❄️",
    80: "Slight showers 🌦️",
    81: "Moderate showers 🌧️",
    82: "Violent showers ⛈️",
    95: "Thunderstorm ⛈️",
    99: "Thunderstorm with hail ⛈️",
}


def _get_condition(code: int) -> str:
    """Return a human-readable weather condition from a WMO weather code."""
    return WEATHER_CODES.get(code, "Unknown conditions")


@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city (e.g. Accra, Kumasi, Lagos, London)
    """
    key = city.lower().strip()
    if key not in CITIES:
        available = ", ".join(c["name"] for c in CITIES.values())
        return f"Sorry, I don't have coordinates for '{city}'. Available cities: {available}"

    coords = CITIES[key]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": "temperature_2m,relative_humidity_2m,windspeed_10m,weathercode",
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    condition = _get_condition(current["weathercode"])

    return (
        f"🌍 Weather in {coords['name']}:\n"
        f"  Condition:    {condition}\n"
        f"  Temperature:  {current['temperature_2m']}°C\n"
        f"  Humidity:     {current['relative_humidity_2m']}%\n"
        f"  Wind speed:   {current['windspeed_10m']} km/h"
    )


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get a multi-day weather forecast for a city.

    Args:
        city: Name of the city (e.g. Accra, Kumasi, Lagos, London)
        days: Number of days to forecast (1-7, default is 3)
    """
    key = city.lower().strip()
    if key not in CITIES:
        available = ", ".join(c["name"] for c in CITIES.values())
        return f"Sorry, I don't have coordinates for '{city}'. Available cities: {available}"

    days = max(1, min(days, 7))
    coords = CITIES[key]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum",
        "timezone": "auto",
        "forecast_days": days,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    daily = data["daily"]
    lines = [f"📅 {days}-day forecast for {coords['name']}:\n"]

    for i in range(days):
        date = daily["time"][i]
        high = daily["temperature_2m_max"][i]
        low = daily["temperature_2m_min"][i]
        rain = daily["precipitation_sum"][i]
        condition = _get_condition(daily["weathercode"][i])

        lines.append(
            f"  {date}: {condition}\n"
            f"           High {high}°C / Low {low}°C / Rain {rain}mm"
        )

    return "\n".join(lines)


@mcp.tool()
async def compare_weather(city1: str, city2: str) -> str:
    """Compare current weather between two cities.

    Args:
        city1: First city name
        city2: Second city name
    """
    result1 = await get_current_weather(city1)
    result2 = await get_current_weather(city2)
    return f"{result1}\n\n{result2}"


@mcp.tool()
def list_available_cities() -> str:
    """List all cities available for weather lookup."""
    cities = [c["name"] for c in CITIES.values()]
    return "🌍 Available cities:\n" + "\n".join(f"  • {c}" for c in cities)


@mcp.prompt()
def weather_assistant() -> str:
    """A prompt template for a helpful weather assistant."""
    return (
        "You are a friendly weather assistant. When reporting weather, "
        "always mention what the conditions mean practically — for example, "
        "suggest bringing an umbrella if rain is likely, or recommend light "
        "clothing if it's hot. Use the available weather tools for all lookups."
    )


if __name__ == "__main__":
    mcp.run()
