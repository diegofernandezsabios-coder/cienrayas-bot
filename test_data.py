"""
Prueba rápida de todas las fuentes de datos y el análisis de zonas.
NO necesita WhatsApp ni credenciales — solo verifica que los datos llegan.

Uso:
    cd cienrayas
    python test_data.py
"""
import asyncio
from services.weather import get_weather
from services.satellite import get_satellite_data
from services.water_quality import get_water_quality
from services.map_generator import generate_map
from core.semaphore import evaluate
from core.zone_analysis import full_ranking


async def main():
    print("=" * 60)
    print("  CienRayas v1.1 — Test de datos (sin WhatsApp)")
    print("=" * 60)

    print("\n[1/4] Clima (wttr.in)...")
    weather = await get_weather()
    flag = " ⚠️ FALLBACK" if weather.get("fallback") else ""
    print(f"  Viento    : {weather['wind_speed']} km/h del {weather['wind_direction_name']}{flag}")
    print(f"  Rafagas   : {weather['wind_gusts']} km/h")
    print(f"  Lluvia    : {weather['precipitation']} mm")
    print(f"  Condicion : {weather['condition']}")

    print("\n[2/4] Datos satelitales (NASA ERDDAP)...")
    satellite = await get_satellite_data()
    print(f"  SST       : {satellite['sst']} C  ({satellite['sst_source']})")
    print(f"  Clorofila : {satellite['chlorophyll']} mg/m3  ({satellite['chlorophyll_source']})")

    print("\n[3/4] Calidad del agua (IDEAM / referencia estacional)...")
    wq = await get_water_quality()
    flag_wq = " [referencia estacional]" if wq.get("fallback") else " [IDEAM tiempo real]"
    print(f"  Fuente           : {wq['source']}{flag_wq}")
    print(f"  Oxigeno disuelto : {wq['dissolved_oxygen']} mg/L  (ideal >5)")
    print(f"  pH               : {wq['ph']}  (rango sano 6.5-9)")
    print(f"  Salinidad        : {wq['salinity']} PSU")
    print(f"  Turbidez         : {wq['turbidity']} NTU")
    print(f"  Temporada        : {wq['season']}")

    print("\n--- ANALISIS MULTIVARIABLE DE ZONAS (IPP 0-100) ---")
    ranking = full_ranking(satellite, wq)
    medals = ["[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]
    for i, z in enumerate(ranking):
        sp = ", ".join(z["species"])
        arts = ", ".join(z["arts"][:2])
        print(f"  {medals[i]} {z['score']:5.1f}  {z['name']}")
        print(f"          Especies: {sp}")
        print(f"          Artes   : {arts}")

    result = evaluate(weather, satellite, wq)
    print(f"\n--- SEMAFORO: {result.color.upper()} ---")
    print(f"  Razon : {result.reason}")
    print(f"  Seguro: {'SI' if result.safe else 'NO - no salir a faena'}")

    print("\n[4/4] Generando mapa...")
    filename = generate_map(result.color, satellite["sst"], satellite["chlorophyll"])
    print(f"  Mapa guardado en: media/{filename}")

    print("\n" + "=" * 60)
    mejor = ranking[0]
    print(f"  RECOMENDACION DEL DIA")
    print(f"  Zona   : {mejor['name']}")
    print(f"  IPP    : {mejor['score']:.0f}/100")
    print(f"  Peces  : {', '.join(mejor['species'])}")
    print(f"  Arte   : {', '.join(mejor['arts'])}")
    print("=" * 60)
    print("  Todo OK. Listo para conectar con WhatsApp.\n")


if __name__ == "__main__":
    asyncio.run(main())
