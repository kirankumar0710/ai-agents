# weather.py
import urllib.parse
import urllib.request
import urllib.error
import json
import socket
import httpx


# ── URL builders ─────────────────────────────────────────


def _geo_url(city: str) -> str:
    encoded = urllib.parse.quote(city.strip())
    return f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1"


def _weather_url(latitude: float, longitude: float) -> str:
    return (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}&current_weather=true"
    )


# ── Response parsers ─────────────────────────────────────


def _parse_geo(geo_data: dict, city: str) -> tuple[float, float]:
    if "results" not in geo_data or len(geo_data["results"]) == 0:
        raise ValueError(f"Location '{city}' not found")

    result = geo_data["results"][0]
    latitude = result.get("latitude")
    longitude = result.get("longitude")

    if latitude is None or longitude is None:
        raise RuntimeError("Invalid city data received")

    return latitude, longitude


def _parse_weather(data: dict, city: str) -> str:
    if "current_weather" not in data:
        raise RuntimeError("Weather data unavailable")

    current = data["current_weather"]
    temperature = current.get("temperature")
    windspeed = current.get("windspeed")
    time = current.get("time")

    if any(v is None for v in [temperature, windspeed, time]):
        raise RuntimeError("Incomplete weather data received")

    return (
        f"Location: {city}, "
        f"Temperature: {temperature}°C, "
        f"Wind Speed: {windspeed} km/h, "
        f"Time: {time}"
    )


# ── Error wrapper (shared) ────────────────────────────────


def _wrap_errors(exc: Exception) -> Exception:
    if isinstance(exc, socket.timeout):
        return TimeoutError("Request timed out")
    if isinstance(exc, urllib.error.HTTPError):
        return RuntimeError(f"HTTP {exc.code} — {exc.reason}")
    if isinstance(exc, urllib.error.URLError):
        return ConnectionError(f"Network error — {exc.reason}")
    if isinstance(exc, json.JSONDecodeError):
        return ValueError("Failed to parse API response")
    return exc


# ── Sync ─────────────────────────────────────────────────


def get_weather(city: str) -> str:
    if not city or not city.strip():
        return "Error: Location cannot be empty"

    try:
        with urllib.request.urlopen(_geo_url(city), timeout=5) as r:
            latitude, longitude = _parse_geo(json.loads(r.read().decode()), city)

        with urllib.request.urlopen(_weather_url(latitude, longitude), timeout=5) as r:
            return _parse_weather(json.loads(r.read().decode()), city)

    except Exception as e:
        raise _wrap_errors(e) from e


# ── Async ─────────────────────────────────────────────────


async def get_weather_async(city: str) -> str:
    if not city or not city.strip():
        return "Error: Location cannot be empty"

    try:
        async with httpx.AsyncClient(timeout=5) as http:
            geo_resp = await http.get(_geo_url(city))
            latitude, longitude = _parse_geo(geo_resp.json(), city)

            weather_resp = await http.get(_weather_url(latitude, longitude))
            return _parse_weather(weather_resp.json(), city)

    except Exception as e:
        raise _wrap_errors(e) from e
