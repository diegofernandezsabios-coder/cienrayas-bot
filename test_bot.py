"""
Simulador completo del bot — sin WhatsApp ni ngrok.
Muestra exactamente el mensaje que recibiria el pescador.

Uso:
    cd cienrayas
    python test_bot.py
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Verificar credencial antes de arrancar
if not os.getenv("GROQ_API_KEY"):
    print()
    print("  Falta la GROQ_API_KEY en el archivo .env")
    print("  1. Ve a https://console.groq.com y crea una API key gratis")
    print("  2. Crea el archivo .env en esta carpeta con:")
    print("     GROQ_API_KEY=gsk_tu_key_aqui")
    print()
    exit(1)

from services.weather import get_weather
from services.satellite import get_satellite_data
from services.water_quality import get_water_quality
from services.llm import generate_fishing_response
from core.semaphore import evaluate
from core.zone_analysis import recommend_zone, full_ranking


async def main():
    print()
    print("=" * 55)
    print("  CienRayas — Simulador de mensaje al pescador")
    print("=" * 55)

    print("\nObteniendo datos...")
    weather, satellite, water_quality = await asyncio.gather(
        get_weather(),
        get_satellite_data(),
        get_water_quality(),
    )

    result = evaluate(weather, satellite, water_quality)
    best_zone = recommend_zone(satellite, water_quality)

    print(f"  Clima     : {weather['wind_speed']} km/h del {weather['wind_direction_name']}, {weather['precipitation']} mm lluvia")
    print(f"  Agua      : {satellite['sst']}°C, clorofila {satellite['chlorophyll']} mg/m3")
    print(f"  Calidad   : OD {water_quality['dissolved_oxygen']} mg/L, salinidad {water_quality['salinity']} PSU")
    print(f"  Semaforo  : {result.color.upper()} — {result.reason}")
    print(f"  Mejor zona: {best_zone['name']} ({best_zone['score']:.0f}/100)")

    print("\nGenerando respuesta con IA (Groq)...")
    mensaje = await generate_fishing_response(weather, satellite, water_quality, result.color)

    footer = f"\n\n━━━━━━━━━━━━━\n_{result.reason}_\n_Datos: NASA · IDEAM · clima en tiempo real_"

    print()
    print("=" * 55)
    print("  ASI LLEGARIA EL MENSAJE AL PESCADOR:")
    print("=" * 55)
    print()
    print(mensaje + footer)
    print()
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
