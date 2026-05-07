"""
Conocimiento técnico y empírico de la Ciénaga Grande de Santa Marta.
Fuente técnica: INVEMAR — Proyecto GEF7-CGSM "Cogestión pesquera" (2025).
Fuente empírica: saber tradicional de pescadores artesanales (en construcción).
"""
from datetime import datetime

# ---------------------------------------------------------------------------
# Puntos de monitoreo INVEMAR (Sipein — activos desde 1994)
# ---------------------------------------------------------------------------
MONITORING_POINTS = [
    "Tasajera (muelle pesquero)",
    "Mercadito",
    "Bocas de Aracataca",
    "Km 15 vía Barranquilla",
    "Ciénaga de Torno",
]

# ---------------------------------------------------------------------------
# Especies principales y su comportamiento estacional
# Fuente: 30 años de monitoreo Sipein / INVEMAR
# ---------------------------------------------------------------------------
SPECIES = {
    "lisa": {
        "nombre_cientifico": "Mugil incilis",
        "temporada_alta": [11, 12, 1, 2],   # nov-feb: bajanza/brisa fuerte
        "temporada_baja": [5, 6, 7, 8],
        "artes": ["atarraya lisera", "trasmallo", "boliche"],
        "talla_minima_cm": 24,
        "nota": "Especie más capturada. Baja a la mar en noviembre con la brisa.",
    },
    "mojarra_rayada": {
        "nombre_cientifico": "Eugerres plumieri",
        "temporada_alta": [3, 4, 5, 9, 10],
        "temporada_baja": [12, 1, 2],
        "artes": ["atarraya mojarrera", "chinchorro"],
        "talla_minima_cm": 22,
        "nota": "Abunda más en aguas con buena salinidad.",
    },
    "mojarra_lora": {
        "nombre_cientifico": "Oreochromis niloticus",
        "temporada_alta": [4, 5, 6, 7, 8],   # aguas dulces / lluvias
        "temporada_baja": [12, 1, 2],
        "artes": ["chinchorra", "atarraya mojarrera"],
        "talla_minima_cm": 22,
        "nota": "Especie introducida. Domina en épocas de lluvia y aguas dulces.",
    },
    "mapale": {
        "nombre_cientifico": "Cathorops mapale",
        "temporada_alta": [1, 2, 3, 10, 11, 12],
        "temporada_baja": [6, 7, 8],
        "artes": ["palangre", "atarraya"],
        "talla_minima_cm": 17,
        "nota": "Fondo de la ciénaga. El palangre va bien cerca del manglar.",
    },
    "chivo_cabezon": {
        "nombre_cientifico": "Ariopsis canteri",
        "temporada_alta": [10, 11, 12, 1, 2],
        "temporada_baja": [5, 6, 7],
        "artes": ["palangre"],
        "talla_minima_cm": 30,
        "nota": "Sale con las primeras brisas. Palangre en el fondo.",
    },
    "macabi": {
        "nombre_cientifico": "Elops smithi",
        "temporada_alta": [3, 4, 5],
        "temporada_baja": [9, 10],
        "artes": ["atarraya robalera", "red de enmalle"],
        "talla_minima_cm": 30,
        "nota": "Especie fuerte, salta. Se detecta por movimiento en superficie.",
    },
    "sabalo": {
        "nombre_cientifico": "Megalops atlanticus",
        "temporada_alta": [1, 2, 3, 4],
        "temporada_baja": [8, 9],
        "artes": ["red de enmalle", "boliche"],
        "talla_minima_cm": 40,
        "nota": "Especie grande, salta. Indica aguas bien oxigenadas.",
    },
    "jaiba_azul": {
        "nombre_cientifico": "Callinectes sapidus",
        "temporada_alta": [3, 4, 5, 6],
        "temporada_baja": [11, 12],
        "artes": ["nasas"],
        "talla_minima_cm": 9,   # ancho del caparazón
        "nota": "Nasa en zonas de fondo blando. Más activa de noche.",
    },
    "camaron": {
        "nombre_cientifico": "Penaeus schmitti / P. notialis",
        "temporada_alta": [9, 10, 11],
        "temporada_baja": [3, 4, 5],
        "artes": ["red camaronera / releo"],
        "talla_minima_cm": 7,
        "nota": "Aparece en época seca-brisa. Máx 4 redes/faena.",
    },
}

# ---------------------------------------------------------------------------
# Señales ambientales que usan los pescadores (saber empírico)
# Por completar con resultados de entrevistas — reunión 2026-05-07
# ---------------------------------------------------------------------------
TRADITIONAL_SIGNALS = {
    "agua_verde_turbia": "Indica alta clorofila — buena señal de peces (mancha)",
    "agua_clara_azulada": "Salinidad alta, posible entrada de agua marina — buen momento para lisa",
    "agua_oscura_negra": "Agua baja en oxígeno — peces se alejan del fondo",
    "brisa_norte": "Viento de loma del norte — señal de bajanza de lisa en noviembre-febrero",
    "aves_sobrevolando": "Cardumen cerca de la superficie — boliche o atarraya robalera",
    "peces_saltando": "Macabí o sábalo activos — usar red de enmalle o atarraya grande",
    # Más señales se agregarán después de la entrevista con pescadores
}

# ---------------------------------------------------------------------------
# Zonas de pesca conocidas (a enriquecer con saber local)
# ---------------------------------------------------------------------------
FISHING_ZONES = [
    "Boca del Mar (zona norte, alta salinidad — lisa y mapalé)",
    "Nueva Venecia (zona central — mojarra rayada y jaiba)",
    "Buenavista (zona centro-occidental — mojarra lora en lluvias)",
    "Bocas de Aracataca (zona sur — aguas dulces, mojarra lora)",
    "Zona del manglar (fondo — palangre para mapalé y chivo cabezón)",
]


# ---------------------------------------------------------------------------
# Función principal: contexto de conocimiento para el prompt
# ---------------------------------------------------------------------------
def get_fishing_context() -> str:
    """
    Genera un bloque de contexto para incluir en el prompt del LLM.
    Combina datos técnicos de INVEMAR con el mes actual para dar
    recomendaciones estacionales relevantes.
    """
    month = datetime.now().month

    # Especies en temporada alta este mes
    en_temporada = [
        name for name, data in SPECIES.items()
        if month in data["temporada_alta"]
    ]
    # Nombres amigables
    nombres = {
        "lisa": "lisa", "mojarra_rayada": "mojarra rayada",
        "mojarra_lora": "mojarra lora", "mapale": "mapalé",
        "chivo_cabezon": "chivo cabezón", "macabi": "macabí",
        "sabalo": "sábalo", "jaiba_azul": "jaiba azul", "camaron": "camarón",
    }
    especies_hoy = [nombres.get(e, e) for e in en_temporada]

    artes_relevantes = list({
        arte
        for name in en_temporada
        for arte in SPECIES[name]["artes"]
    })

    bloque = f"""
CONOCIMIENTO PESQUERO DE LA CIÉNAGA GRANDE (INVEMAR/Sipein + saber local):
- Especies en temporada este mes: {', '.join(especies_hoy) if especies_hoy else 'consultar con pescadores locales'}
- Artes recomendados: {', '.join(artes_relevantes[:4]) if artes_relevantes else 'según especie objetivo'}
- Tallas mínimas legales: lisa≥24cm, mojarra≥22cm, mapalé≥17cm, chivo cabezón≥30cm, jaiba≥9cm caparazón
- Zonas activas: Nueva Venecia, Boca del Mar, Bocas de Aracataca, zona del manglar
- Monitoreo INVEMAR activo en: Tasajera, Mercadito, Bocas de Aracataca, Km15, Ciénaga de Torno

SEÑALES DEL AGUA QUE USAN LOS PESCADORES:
- Agua verdosa/turbia → hay mancha, buenos peces
- Aves sobrevolando → cardumen en superficie
- Peces saltando → macabí o sábalo activos
- Brisa del norte fuerte → señal de bajanza de lisa (nov-feb)
"""
    return bloque
