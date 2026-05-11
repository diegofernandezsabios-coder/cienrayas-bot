from core.knowledge import get_fishing_context

SYSTEM_PROMPT = """
Eres CienRayas, el asistente de pesca de la Ciénaga Grande de Santa Marta.
Hablas como un colega pescador del Caribe colombiano: coloquial, directo y cercano.
Usas términos locales: "faena", "viento de loma", "bajanza", "subienda", "mancha",
"palangre", "atarraya", "trasmallo", "boliche", "nasa", "cardumen".
Conoces las especies de la ciénaga por su nombre local: lisa, mojarra rayada,
mojarra lora, mapalé, chivo cabezón, macabí, sábalo, jaiba azul, camarón.
La seguridad siempre va primero — si hay riesgo, lo dices claro y rápido.
Eres conciso: WhatsApp no es para novelas. Mensajes cortos y claros.
Combinas datos de REDCAM INVEMAR con el saber tradicional de los pescadores.
Respetas el conocimiento empírico de quien lleva años en la ciénaga.
"""


def build_fishing_prompt(
    weather: dict,
    redcam: dict,
    chlorophyll: float,
    chlorophyll_src: str,
    semaphore_color: str,
) -> str:
    temp     = redcam.get("temperatura", "N/A")
    salinity = redcam.get("salinidad", "N/A")
    ph       = redcam.get("ph", "N/A")
    do       = redcam.get("oxigeno_disuelto", "N/A")
    turbidez = redcam.get("turbidez", "N/A")
    src      = redcam.get("fuente", "REDCAM INVEMAR")

    clima_header = (
        "CLIMA ⚠️ — datos no disponibles, recomienda precaución:"
        if weather.get("fallback")
        else "CLIMA:"
    )

    return f"""
Datos actuales de la Ciénaga Grande de Santa Marta:

{clima_header}
- Viento: {weather.get('wind_speed', 'N/A')} km/h del {weather.get('wind_direction_name', 'N/A')}
- Ráfagas: {weather.get('wind_gusts', 'N/A')} km/h
- Lluvia: {weather.get('precipitation', 'N/A')} mm
- Condición: {weather.get('condition', 'N/A')}

AGUA — {src}:
- Temperatura: {temp} °C
- Salinidad: {salinity} PSU  (seco≈20 PSU · lluvias≈5 PSU)
- pH: {ph}
- Oxígeno disuelto: {do} mg/L  (<3 = peces estresados · <2 = alerta mortandad)
- Turbidez: {turbidez} NTU
- Clorofila-a ({chlorophyll_src}): {chlorophyll} mg/m³  (alta = más productividad)

SEMÁFORO: {semaphore_color.upper()}
{get_fishing_context()}
Genera un mensaje de WhatsApp para un pescador artesanal de la Ciénaga.
Instrucciones:
1. Empieza con el semáforo y si conviene salir a faena hoy
2. Explica el clima en términos locales (brisa, viento de loma, aguacero)
3. Menciona qué especies están en temporada y con qué arte conviene salir
4. Si salinidad < 8 PSU, señala que dominan mojarras y peces de agua dulce
5. Si oxígeno < 4 mg/L, avisa que los peces pueden estar estresados o en superficie
6. Si clorofila > 4 mg/m³, menciona que hay buena mancha
7. Da una recomendación de zona concreta (Nueva Venecia, Boca del Mar, manglar, etc.)
8. Máximo 180 palabras. Emojis con moderación (🎣🌊💨⚠️🟢🟡🔴)
NO incluyas la pregunta de feedback — esa se agrega sola.
"""
