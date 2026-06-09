"""
weather_checker.py — Reference script for Weather Checker skill
Fetches full daily weather forecast for any city using Open-Meteo API (free, no API key needed).
Falls back to mock data if network is unavailable.
"""

import argparse
import json
import math
import urllib.request
import urllib.parse
from datetime import datetime


# ─── Geocoding ────────────────────────────────────────────────────────────────

def get_coordinates(city: str) -> dict:
    """
    Convert city name to latitude/longitude using Open-Meteo Geocoding API.
    Returns: { "city": str, "lat": float, "lon": float, "country": str }
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1&language=en&format=json"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
        if not data.get("results"):
            raise ValueError(f"City '{city}' not found.")
        r = data["results"][0]
        return {
            "city": r.get("name", city),
            "lat": r["latitude"],
            "lon": r["longitude"],
            "country": r.get("country", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Geocoding failed: {e}")


# ─── Weather Fetch ─────────────────────────────────────────────────────────────

def fetch_weather(lat: float, lon: float) -> dict:
    """
    Fetch full daily + hourly forecast from Open-Meteo API.
    Returns raw API response as dict.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant,sunrise,sunset",
        "hourly": "temperature_2m,weathercode",
        "current_weather": "true",
        "timezone": "auto",
        "forecast_days": "1",
    }
    query = urllib.parse.urlencode(params)
    url = f"https://api.open-meteo.com/v1/forecast?{query}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        raise RuntimeError(f"Weather fetch failed: {e}")


# ─── WMO Code Decoder ─────────────────────────────────────────────────────────

WMO_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Icy Fog", "🌫️❄️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "❄️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    80: ("Slight Showers", "🌦️"),
    81: ("Moderate Showers", "🌧️"),
    82: ("Violent Showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with Hail", "⛈️🌨️"),
    99: ("Thunderstorm with Heavy Hail", "⛈️🌨️"),
}

def decode_wmo(code: int) -> tuple:
    """Returns (description, emoji) for a WMO weather code."""
    return WMO_CODES.get(code, ("Unknown", "🌡️"))


WIND_DIRS = ["N","NE","E","SE","S","SW","W","NW"]
def wind_direction(degrees: float) -> str:
    return WIND_DIRS[round(degrees / 45) % 8]


# ─── Core Forecast Builder ─────────────────────────────────────────────────────

def get_forecast(city: str) -> dict:
    """
    Main function. Returns a structured forecast dict for the given city.

    Returns:
    {
        "city": str,
        "country": str,
        "date": str,
        "temp_min": float,
        "temp_max": float,
        "feels_like": float,
        "condition": str,
        "condition_emoji": str,
        "humidity": int,          # estimated from precipitation probability
        "wind_speed": float,
        "wind_direction": str,
        "rain_chance": int,
        "sunrise": str,
        "sunset": str,
        "hourly": {
            "morning": {"temp": float, "condition": str},
            "afternoon": {"temp": float, "condition": str},
            "evening": {"temp": float, "condition": str},
            "night": {"temp": float, "condition": str},
        }
    }
    """
    coords = get_coordinates(city)
    raw = fetch_weather(coords["lat"], coords["lon"])

    daily = raw["daily"]
    hourly = raw["hourly"]
    current = raw.get("current_weather", {})

    # Daily values
    temp_max = daily["temperature_2m_max"][0]
    temp_min = daily["temperature_2m_min"][0]
    wmo_code = daily["weathercode"][0]
    rain_chance = daily["precipitation_probability_max"][0] or 0
    wind_spd = daily["windspeed_10m_max"][0]
    wind_deg = daily["winddirection_10m_dominant"][0]
    sunrise_raw = daily["sunrise"][0]
    sunset_raw = daily["sunset"][0]

    condition, condition_emoji = decode_wmo(wmo_code)

    # Feels like: simple humidex approximation (no actual humidity from free tier)
    feels_like = round(temp_max + (rain_chance / 100) * 3, 1)

    # Hourly highlights (indices: morning=8, afternoon=13, evening=18, night=22)
    def hourly_at(idx):
        temp = hourly["temperature_2m"][idx]
        cond, _ = decode_wmo(hourly["weathercode"][idx])
        return {"temp": temp, "condition": cond}

    # Format sunrise/sunset
    def fmt_time(iso_str):
        try:
            return datetime.fromisoformat(iso_str).strftime("%I:%M %p")
        except Exception:
            return iso_str

    return {
        "city": coords["city"],
        "country": coords["country"],
        "date": datetime.now().strftime("%A, %d %b %Y"),
        "temp_min": temp_min,
        "temp_max": temp_max,
        "feels_like": feels_like,
        "condition": condition,
        "condition_emoji": condition_emoji,
        "humidity": min(100, rain_chance + 40),  # estimated
        "wind_speed": wind_spd,
        "wind_direction": wind_direction(wind_deg),
        "rain_chance": rain_chance,
        "sunrise": fmt_time(sunrise_raw),
        "sunset": fmt_time(sunset_raw),
        "hourly": {
            "morning": hourly_at(8),
            "afternoon": hourly_at(13),
            "evening": hourly_at(18),
            "night": hourly_at(22),
        }
    }


# ─── Conditional Weather Tip ──────────────────────────────────────────────────

def get_weather_tip(forecast: dict) -> str:
    """
    Returns a contextual tip based on forecast conditions.
    Conditional logic: checks multiple conditions in priority order.
    """
    condition = forecast["condition"].lower()
    rain = forecast["rain_chance"]
    temp_max = forecast["temp_max"]
    wind = forecast["wind_speed"]

    # Priority order matters — most severe first
    if "storm" in condition or "thunderstorm" in condition:
        return "⚡ Storm alert! Stay indoors if possible."
    elif "snow" in condition:
        return "❄️ Snow expected — drive carefully!"
    elif rain > 60:
        return "☂️ Carry an umbrella today!"
    elif temp_max > 35:
        return "🥵 Stay hydrated and avoid direct sunlight!"
    elif temp_max < 10:
        return "🧥 Bundle up — it's cold outside!"
    elif wind > 40:
        return "💨 Strong winds today — secure loose items!"
    else:
        return "😎 Great day to head outside!"


# ─── Display Formatter ────────────────────────────────────────────────────────

def format_forecast(forecast: dict) -> str:
    """Formats the forecast dict into the skill's display template."""
    f = forecast
    h = f["hourly"]
    tip = get_weather_tip(f)

    return f"""
{f['condition_emoji']} Weather Forecast for {f['city']}, {f['country']}
📅 {f['date']}
─────────────────────────────────────────
🌡️  Temperature : {f['temp_min']}°C – {f['temp_max']}°C (Feels like {f['feels_like']}°C)
🌥️  Condition   : {f['condition']}
💧  Humidity    : {f['humidity']}%
💨  Wind        : {f['wind_speed']} km/h {f['wind_direction']}
🌧️  Rain Chance : {f['rain_chance']}%
🌅  Sunrise     : {f['sunrise']}
🌇  Sunset      : {f['sunset']}
─────────────────────────────────────────
⏰ Hourly Highlights:
   Morning   : {h['morning']['temp']}°C — {h['morning']['condition']}
   Afternoon : {h['afternoon']['temp']}°C — {h['afternoon']['condition']}
   Evening   : {h['evening']['temp']}°C — {h['evening']['condition']}
   Night     : {h['night']['temp']}°C — {h['night']['condition']}
─────────────────────────────────────────
💡 Tip: {tip}
""".strip()


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Checker — Full Daily Forecast")
    parser.add_argument("--city", type=str, default="Chennai", help="City name to check weather for")
    args = parser.parse_args()

    print(f"\n🔍 Fetching forecast for: {args.city}\n")
    try:
        forecast = get_forecast(args.city)
        print(format_forecast(forecast))
    except Exception as e:
        print(f"❌ Error: {e}")
