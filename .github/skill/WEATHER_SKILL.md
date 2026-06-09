---
name: Weather Checker
description: Use this skill when the user asks about weather using question patterns like "what is the weather in X", "what's the weather like in X", "how is the weather in X", "what is the forecast for X", "will it rain in X", "is it hot in X". Extract the city name and return a full daily forecast.
---

# Weather Checker Skill

## Triggers
Activate this skill when the user asks any weather-related question mentioning a city. Examples:
- "What is the weather in Mumbai?"
- "What's the forecast for London today?"
- "How is the weather in Tokyo?"
- "Will it rain in Delhi tomorrow?"
- "Is it cold in New York?"

---

## Step 1 — Extract City Name

Parse the user's question and extract the **city name**. If no city is mentioned, ask:
> "Which city would you like the weather forecast for? 🌍"

---

## Step 2 — Fetch & Display Full Daily Forecast

Use the reference script `scripts/weather_checker.py` to fetch and display the forecast.

Display the forecast in this format:

```
🌤️ Weather Forecast for {City}
📅 {Day}, {Date}
─────────────────────────────
🌡️  Temperature : {min}°C – {max}°C (Feels like {feels_like}°C)
🌥️  Condition   : {description}
💧  Humidity    : {humidity}%
💨  Wind        : {wind_speed} km/h {wind_direction}
🌧️  Rain Chance : {rain_chance}%
🌅  Sunrise     : {sunrise}
🌇  Sunset      : {sunset}
─────────────────────────────
⏰ Hourly Highlights:
   Morning   : {morning_temp}°C — {morning_condition}
   Afternoon : {afternoon_temp}°C — {afternoon_condition}
   Evening   : {evening_temp}°C — {evening_condition}
   Night     : {night_temp}°C — {night_condition}
─────────────────────────────
💡 Tip: {weather_tip}
```

---

## Step 3 — Weather Tips (Conditional Logic)

Based on the forecast, automatically add a helpful tip:

| Condition                  | Tip                                              |
|---------------------------|--------------------------------------------------|
| Rain chance > 60%          | ☂️ "Carry an umbrella today!"                   |
| Temperature > 35°C         | 🥵 "Stay hydrated and avoid direct sunlight!"   |
| Temperature < 10°C         | 🧥 "Bundle up — it's cold outside!"             |
| Wind speed > 40 km/h       | 💨 "Strong winds today — secure loose items!"   |
| Condition has "storm"      | ⚡ "Storm alert! Stay indoors if possible."      |
| Condition has "snow"       | ❄️ "Snow expected — drive carefully!"           |
| All clear                  | 😎 "Great day to head outside!"                 |

---

## Step 4 — Ask to Continue

After showing the forecast, ask:
> "Want to check the weather for another city? 🌍"

---

## Reference Script

See `scripts/weather_checker.py` for the full implementation.

Run it directly:
```bash
python scripts/weather_checker.py --city "Mumbai"
python scripts/weather_checker.py --city "London" --days 3
```

Use in your code:
```python
from scripts.weather_checker import get_forecast, get_weather_tip

forecast = get_forecast("Tokyo")
tip = get_weather_tip(forecast)
print(forecast)
print(tip)
```

---

## Example Interaction

**User:** What is the weather in Mumbai?
**Claude:**
🌤️ Weather Forecast for Mumbai
📅 Tuesday, 09 Jun 2026
─────────────────────────────
🌡️  Temperature : 28°C – 36°C (Feels like 38°C)
🌥️  Condition   : Partly Cloudy with Humid Spells
💧  Humidity    : 82%
💨  Wind        : 18 km/h SW
🌧️  Rain Chance : 45%
🌅  Sunrise     : 06:02 AM
🌇  Sunset      : 07:14 PM
─────────────────────────────
⏰ Hourly Highlights:
   Morning   : 29°C — Cloudy
   Afternoon : 36°C — Partly Sunny
   Evening   : 32°C — Humid
   Night     : 28°C — Clear
─────────────────────────────
💡 Tip: 🥵 Stay hydrated and avoid direct sunlight!

Want to check the weather for another city? 🌍
