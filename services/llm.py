import asyncio
import logging
from groq import Groq
from config import GROQ_API_KEY
from core.prompts import SYSTEM_PROMPT, build_fishing_prompt

logger = logging.getLogger(__name__)

_client = Groq(api_key=GROQ_API_KEY)
_MODEL = "llama-3.3-70b-versatile"


def _call_groq(prompt: str) -> str:
    last_exc = None
    for attempt in range(3):
        try:
            response = _client.chat.completions.create(
                model=_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=400,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_exc = e
            if "429" in str(e) or "rate_limit" in str(e).lower():
                wait = 8 * (attempt + 1)
                logger.warning(f"Groq 429 intento {attempt + 1} — esperando {wait}s")
                import time
                time.sleep(wait)
            else:
                raise
    raise last_exc


async def generate_fishing_response(
    weather: dict, satellite: dict, water_quality: dict, semaphore_color: str
) -> str:
    prompt = build_fishing_prompt(weather, satellite, water_quality, semaphore_color)
    return await asyncio.to_thread(_call_groq, prompt)


async def generate_feedback_ack(feedback_text: str) -> str:
    prompt = (
        f"Un pescador de la Ciénaga Grande respondió esto: \"{feedback_text}\"\n"
        "Escríbele un agradecimiento muy corto (máx 2 líneas), en lenguaje sencillo "
        "y caribeño, como si fueras un compañero pescador. "
        "Menciona que su reporte ayuda a mejorar el sistema."
    )
    return await asyncio.to_thread(_call_groq, prompt)
