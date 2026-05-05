import httpx
from config import CIENAGA_LAT, CIENAGA_LON

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

_WIND_DIRS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO",
]

_WMO_CONDITIONS = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna leve", 53: "Llovizna moderada", 55: "Llovizna densa",
    61: "Lluvia leve", 63: "Lluvia moderada", 65: "Lluvia fuerte",
    80: "Chubascos leves", 81: "Chubascos moderados", 82: "Chubascos fuertes",
    95: "Tormenta", 96: "Tormenta con granizo leve", 99: "Tormenta con granizo fuerte",
}


def _direction_name(degrees: float) -> str:
    idx = round(degrees / 22.5) % 16
    return _WIND_DIRS[idx]


async def get_weather() -> dict:
    params = {
        "latitude": CIENAGA_LAT,
        "longitude": CIENAGA_LON,
        "current": [
            "temperature_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation",
            "weather_code",
        ],
        "wind_speed_unit": "kmh",
        "timezone": "America/Bogota",
        "forecast_days": 1,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    wind_dir = current.get("wind_direction_10m", 0)
    weather_code = current.get("weather_code", 0)

    return {
        "temperature": current.get("temperature_2m"),
        "wind_speed": round(current.get("wind_speed_10m", 0)),
        "wind_direction": wind_dir,
        "wind_direction_name": _direction_name(wind_dir),
        "wind_gusts": round(current.get("wind_gusts_10m", 0)),
        "precipitation": round(current.get("precipitation", 0), 1),
        "condition": _WMO_CONDITIONS.get(weather_code, "Desconocido"),
        "weather_code": weather_code,
    }
