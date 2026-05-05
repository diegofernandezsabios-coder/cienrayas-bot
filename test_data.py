"""
Prueba rápida de las APIs de datos y el mapa.
NO necesita WhatsApp ni ninguna credencial — solo verifica que los datos llegan.

Uso:
    cd cienrayas
    python test_data.py
"""
import asyncio
from services.weather import get_weather
from services.satellite import get_satellite_data
from services.map_generator import generate_map
from core.semaphore import evaluate


async def main():
    print("=" * 55)
    print("  CienRayas — Test de datos (sin WhatsApp)")
    print("=" * 55)

    print("\n[1/3] Obteniendo clima (Open-Meteo)...")
    weather = await get_weather()
    print(f"  Viento    : {weather['wind_speed']} km/h del {weather['wind_direction_name']}")
    print(f"  Ráfagas   : {weather['wind_gusts']} km/h")
    print(f"  Lluvia    : {weather['precipitation']} mm")
    print(f"  Condición : {weather['condition']}")

    print("\n[2/3] Obteniendo datos satelitales (NASA ERDDAP)...")
    satellite = await get_satellite_data()
    print(f"  SST       : {satellite['sst']}°C  ({satellite['sst_source']})")
    print(f"  Clorofila : {satellite['chlorophyll']} mg/m³  ({satellite['chlorophyll_source']})")

    result = evaluate(weather, satellite)
    print(f"\n  SEMÁFORO  : {result.emoji} {result.color.upper()} — {result.reason}")

    print("\n[3/3] Generando mapa...")
    filename = generate_map(result.color, satellite["sst"], satellite["chlorophyll"])
    print(f"  Mapa guardado: media/{filename}")
    print(f"  Abrir el archivo para ver cómo queda el mapa ↑")

    print("\n✅ Todo OK — listo para conectar con WhatsApp.\n")


if __name__ == "__main__":
    asyncio.run(main())
