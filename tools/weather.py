import urllib.request
import urllib.parse
import json
import socket


def get_weather(city: str) -> str:

    # Guard: empty or whitespace input
    if not city or not city.strip():
        return "Error: Location cannot be empty"

    try:
        encoded_location = urllib.parse.quote(city.strip())

        # Step 1: Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_location}&count=1"

        with urllib.request.urlopen(geo_url, timeout=5) as response:
            geo_data = json.loads(response.read().decode())

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return ValueError(f"Location '{city}' not found")

        result = geo_data["results"][0]
        latitude = result.get("latitude")
        longitude = result.get("longitude")

        if latitude is None or longitude is None:
            raise RuntimeError("Invalid city data received")

        # Step 2: Weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}&current_weather=true"
        )

        with urllib.request.urlopen(weather_url, timeout=5) as response:
            data = json.loads(response.read().decode())

        if "current_weather" not in data:
            raise RuntimeError("Weather data unavailable")

        current = data["current_weather"]

        temperature = current.get("temperature")
        windspeed = current.get("windspeed")
        time = current.get("time")

        # Guard: missing fields in weather response
        if any(v is None for v in [temperature, windspeed, time]):
            raise RuntimeError("Incomplete weather data received")

        return (
            f"Location: {city}, "
            f"Temperature: {temperature}°C, "
            f"Wind Speed: {windspeed} km/h, "
            f"Time: {time}"
        )

    except socket.timeout as e:
        raise TimeoutError("Request timed out") from e

    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} — {e.reason}") from e

    except urllib.error.URLError as e:
        raise ConnectionError(f"Network error — {e.reason}") from e

    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse API response") from e

    except Exception:
        raise
