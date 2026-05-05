import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini (gratis)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Meta WhatsApp Cloud API (gratis)
WHATSAPP_TOKEN           = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WEBHOOK_VERIFY_TOKEN     = os.getenv("WEBHOOK_VERIFY_TOKEN", "cienrayas_secreto")

# Servidor — RENDER_EXTERNAL_URL se inyecta automáticamente en Render
BASE_URL  = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("BASE_URL", "http://localhost:8000")
MEDIA_DIR = os.getenv("MEDIA_DIR", "media")

# Ciénaga Grande — coordenadas centrales y bounding box
CIENAGA_LAT = 10.8
CIENAGA_LON = -74.4
LAT_MIN, LAT_MAX = 10.5, 11.2
LON_MIN, LON_MAX = -74.85, -73.9
