"""
Clorofila-a desde NASA ERDDAP/MODIS Aqua (compuesto 8 días).
La temperatura superficial ya viene de REDCAM INVEMAR (services/redcam.py).
"""
import httpx
from datetime import datetime, timedelta, timezone
from config import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX

_ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"

# Clorofila mensual CGSM cuando falla la API (mg/m³)
_CHL_MONTHLY = {
    1: 5.0, 2: 4.5, 3: 4.0, 4: 4.5, 5: 5.5,
    6: 6.0, 7: 6.5, 8: 7.0, 9: 6.5, 10: 6.0,
    11: 5.5, 12: 5.0,
}


async def get_chlorophyll() -> tuple[float, str]:
    """Devuelve (chl_mg_m3, fuente)."""
    time_str = (datetime.now(timezone.utc) - timedelta(days=4)).strftime("%Y-%m-%dT00:00:00Z")
    lat0, lat1 = LAT_MIN + 0.15, LAT_MAX - 0.15
    lon0, lon1 = LON_MIN + 0.15, LON_MAX - 0.15
    url = (
        f"{_ERDDAP}/erdMH1chla8day.json"
        f"?chlorophyll[({time_str})]"
        f"[({lat0:.2f}):({lat1:.2f})]"
        f"[({lon0:.2f}):({lon1:.2f})]"
    )
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(url)
            r.raise_for_status()
            rows = r.json()["table"]["rows"]
        values = [row[3] for row in rows if row[3] is not None and 0 < row[3] < 100]
        if values:
            return round(sum(values) / len(values), 2), "NASA MODIS Aqua"
    except Exception:
        pass

    return _CHL_MONTHLY.get(datetime.now().month, 5.0), "climatología estacional CGSM"
