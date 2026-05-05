"""
Envío de mensajes via Meta WhatsApp Cloud API (gratuito).
Documentación: https://developers.facebook.com/docs/whatsapp/cloud-api/messages
"""
import httpx
from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID

_API_URL = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
_HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json",
}


async def send_text(to: str, body: str):
    """Envía un mensaje de texto simple."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body, "preview_url": False},
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(_API_URL, headers=_HEADERS, json=payload)
        r.raise_for_status()


async def send_image(to: str, image_url: str, caption: str = ""):
    """Envía una imagen con caption opcional."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url, "caption": caption},
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(_API_URL, headers=_HEADERS, json=payload)
        r.raise_for_status()


async def send(to: str, body: str, image_url: str = None):
    """Helper único: envía texto y, si hay imagen, la envía con caption."""
    if image_url:
        await send_image(to, image_url, caption=body)
    else:
        await send_text(to, body)
