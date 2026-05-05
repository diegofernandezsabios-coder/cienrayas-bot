"""
Gestión en memoria del estado de conversación por número de teléfono.
En producción reemplazar por Redis o base de datos.
"""
from datetime import datetime

_conversations: dict[str, dict] = {}

FEEDBACK_KEYWORDS = [
    "bien", "mal", "regular", "buena", "mala", "buenísimo", "malísimo",
    "pescamos", "no pescamos", "poquito", "bastante", "excelente", "nada",
    "sí", "no", "si", "lleno", "vacío", "vacio", "regular", "más o menos",
]


def get_state(phone: str) -> dict:
    return _conversations.get(phone, {})


def set_state(phone: str, data: dict):
    _conversations[phone] = {**_conversations.get(phone, {}), **data}


def record_query(phone: str):
    set_state(phone, {
        "last_query": datetime.now().isoformat(),
        "awaiting_feedback": True,
    })


def record_feedback(phone: str, text: str):
    state = get_state(phone)
    feedbacks = state.get("feedbacks", [])
    feedbacks.append({
        "text": text,
        "timestamp": datetime.now().isoformat(),
    })
    set_state(phone, {"feedbacks": feedbacks, "awaiting_feedback": False})


def is_awaiting_feedback(phone: str) -> bool:
    return _conversations.get(phone, {}).get("awaiting_feedback", False)


def looks_like_feedback(message: str) -> bool:
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in FEEDBACK_KEYWORDS)
