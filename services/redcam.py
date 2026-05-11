"""
Datos de calidad del agua desde REDCAM INVEMAR
(Red de Vigilancia para la Conservación y Protección de las Aguas Marinas y Costeras).
Fuente primaria : ArcGIS REST — gis.invemar.org.co/arcgis/rest/services/Hosted/REDCAM
Fallback        : climatología mensual CGSM — Informes REDCAM-INVEMAR 2001-2023
"""
import httpx
from datetime import datetime

# Endpoint ArcGIS REST del servicio Hosted/REDCAM de INVEMAR
_REDCAM_URL = (
    "https://gis.invemar.org.co/arcgis/rest/services/Hosted/REDCAM/MapServer/0/query"
)

# Estaciones REDCAM activas en la Ciénaga Grande de Santa Marta
_CGSM_STATIONS = ["Tasajera", "Mercadito", "Aracataca", "Km 15", "Torno"]

# ---------------------------------------------------------------------------
# Climatología mensual CGSM — zona central/norte
# Fuente: Informes anuales REDCAM-INVEMAR 2001-2023
# Período seco/brisa: dic-mar → menor caudal fluvial, mayor salinidad
# Período lluvioso: may-oct → ríos Fundación, Aracataca, Sevilla aportan dulce
# ---------------------------------------------------------------------------

_TEMP_MONTHLY = {
    1: 27.5, 2: 27.5, 3: 28.0, 4: 28.5, 5: 29.5,
    6: 30.0, 7: 30.0, 8: 30.5, 9: 30.0, 10: 29.5,
    11: 29.0, 12: 28.0,
}

_SALINITY_MONTHLY = {
    # PSU — promedio zona central CGSM
    1: 18.0, 2: 20.0, 3: 22.0, 4: 15.0, 5:  9.0,
    6:  5.5, 7:  5.0, 8:  4.5, 9:  5.0, 10:  6.0,
    11: 10.0, 12: 15.0,
}

_PH_MONTHLY = {
    # Ligeramente básico en seco (mayor fotosíntesis), más ácido en lluvias
    1: 7.9, 2: 8.0, 3: 8.1, 4: 7.9, 5: 7.7,
    6: 7.5, 7: 7.4, 8: 7.4, 9: 7.5, 10: 7.6,
    11: 7.7, 12: 7.8,
}

_DO_MONTHLY = {
    # Oxígeno disuelto (mg/L) — promedio superficie
    # Seco: brisas mejoran oxigenación; lluvias: mayor carga orgánica reduce DO
    1: 6.5, 2: 6.8, 3: 6.5, 4: 6.0, 5: 5.5,
    6: 5.0, 7: 5.2, 8: 5.0, 9: 5.0, 10: 5.2,
    11: 5.5, 12: 6.0,
}

_TURBIDITY_MONTHLY = {
    # Turbidez NTU — menor en seco, mayor en lluvias (sedimentos fluviales)
    1: 25, 2: 22, 3: 20, 4: 28, 5: 45,
    6: 60, 7: 65, 8: 65, 9: 60, 10: 55,
    11: 40, 12: 30,
}


async def _fetch_live() -> dict | None:
    """Consulta la API REST de REDCAM INVEMAR para datos recientes de CGSM."""
    where = " OR ".join(f"NOM_ESTACION LIKE '%{s}%'" for s in _CGSM_STATIONS)
    params = {
        "f": "json",
        "where": where,
        "outFields": "NOM_ESTACION,TEMPERATURA,SALINIDAD,PH,OD,TURBIDEZ,FECHA_MUESTREO",
        "orderByFields": "FECHA_MUESTREO DESC",
        "resultRecordCount": "10",
    }
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(_REDCAM_URL, params=params)
        r.raise_for_status()
        features = r.json().get("features", [])

    if not features:
        return None

    temps, sals, phs, dos, turbs = [], [], [], [], []
    for f in features:
        a = f.get("attributes", {})
        if a.get("TEMPERATURA") is not None:
            temps.append(float(a["TEMPERATURA"]))
        if a.get("SALINIDAD") is not None:
            sals.append(float(a["SALINIDAD"]))
        if a.get("PH") is not None:
            phs.append(float(a["PH"]))
        if a.get("OD") is not None:
            dos.append(float(a["OD"]))
        if a.get("TURBIDEZ") is not None:
            turbs.append(float(a["TURBIDEZ"]))

    result: dict = {}
    if temps:
        result["temperatura"] = round(sum(temps) / len(temps), 1)
    if sals:
        result["salinidad"] = round(sum(sals) / len(sals), 1)
    if phs:
        result["ph"] = round(sum(phs) / len(phs), 2)
    if dos:
        result["oxigeno_disuelto"] = round(sum(dos) / len(dos), 1)
    if turbs:
        result["turbidez"] = round(sum(turbs) / len(turbs), 0)
    return result or None


async def get_redcam_data() -> dict:
    """
    Retorna calidad del agua de la CGSM desde REDCAM INVEMAR.
    Intenta la API en tiempo real; si falla usa climatología mensual.
    """
    month = datetime.now().month

    try:
        live = await _fetch_live()
        if live:
            # Rellenar turbidez con climatología si la API no la incluye
            live.setdefault("turbidez", _TURBIDITY_MONTHLY.get(month, 40))
            return {**live, "fuente": "REDCAM INVEMAR (tiempo real)", "live": True}
    except Exception:
        pass

    return {
        "temperatura":       _TEMP_MONTHLY.get(month, 29.0),
        "salinidad":         _SALINITY_MONTHLY.get(month, 12.0),
        "ph":                _PH_MONTHLY.get(month, 7.7),
        "oxigeno_disuelto":  _DO_MONTHLY.get(month, 5.5),
        "turbidez":          _TURBIDITY_MONTHLY.get(month, 40),
        "fuente":            "REDCAM INVEMAR (climatología mensual CGSM 2001-2023)",
        "live":              False,
    }
