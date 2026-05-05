"""
Genera un mapa PNG de la Ciénaga Grande con semáforo de zonas de pesca.
Usa solo matplotlib + numpy — sin dependencia de tiles de internet.
"""
import uuid
import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend sin pantalla — obligatorio en servidores
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPolygon
from pathlib import Path
from datetime import datetime
from config import MEDIA_DIR

# Polígono aproximado de la Ciénaga Grande (longitud, latitud)
_CIENAGA = np.array([
    [-74.22, 11.05], [-74.15, 10.98], [-74.18, 10.88],
    [-74.22, 10.78], [-74.30, 10.68], [-74.42, 10.60],
    [-74.56, 10.58], [-74.68, 10.65], [-74.73, 10.78],
    [-74.70, 10.92], [-74.58, 11.00], [-74.42, 11.06],
    [-74.30, 11.08], [-74.22, 11.05],
])

# Zonas de pesca (lon, lat, nombre)
_ZONES = [
    (-74.25, 11.00, "Boca del\nMar"),
    (-74.40, 10.87, "Nueva\nVenecia"),
    (-74.55, 10.70, "Buenavista"),
    (-74.63, 10.83, "Zona\nOeste"),
]

_COLORS = {
    "verde":    "#27ae60",
    "amarillo": "#f39c12",
    "rojo":     "#e74c3c",
}

_LABELS = {
    "verde":    "🟢 VERDE — ¡Buen día pa' la faena!",
    "amarillo": "🟡 PRECAUCIÓN — Salir con cuidado",
    "rojo":     "🔴 NO SALIR — Quédate en tierra",
}


def generate_map(semaphore_color: str, sst: float, chlorophyll: float) -> str:
    """Retorna el nombre del archivo PNG generado (guardado en MEDIA_DIR)."""
    zone_color = _COLORS.get(semaphore_color, _COLORS["verde"])

    fig, ax = plt.subplots(figsize=(7, 8), facecolor="#0d1b2a")
    ax.set_facecolor("#1a3a5c")

    ax.set_xlim(-74.90, -74.05)
    ax.set_ylim(10.45, 11.20)

    # Fondo terrestre (simple rectángulo detrás del agua)
    ax.set_facecolor("#2c4a2e")

    # Agua de la ciénaga
    cienaga_patch = MplPolygon(
        _CIENAGA, closed=True,
        facecolor="#1e6f9f", edgecolor="#5dade2", linewidth=1.8, alpha=0.85,
    )
    ax.add_patch(cienaga_patch)

    # Zonas de pesca con círculos de color semáforo
    for lon, lat, name in _ZONES:
        ax.scatter(lon, lat, s=350, color=zone_color, zorder=5,
                   edgecolors="white", linewidths=1.8, alpha=0.92)
        ax.annotate(
            name, (lon, lat),
            xytext=(6, 6), textcoords="offset points",
            color="white", fontsize=7.5, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#0d1b2a", alpha=0.75),
        )

    # Título
    today = datetime.now().strftime("%d/%m/%Y  %H:%M")
    ax.set_title(
        f"CienRayas  ·  {today}\nCiénaga Grande de Santa Marta",
        color="white", fontsize=11, fontweight="bold", pad=10,
    )

    # Caja de semáforo (abajo izquierda)
    ax.text(
        0.02, 0.02, _LABELS.get(semaphore_color, ""),
        transform=ax.transAxes,
        color="white", fontsize=9.5, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=zone_color, alpha=0.88),
        verticalalignment="bottom",
    )

    # Datos satelitales (abajo derecha)
    data_txt = f"SST: {sst}°C  |  Clorofila: {chlorophyll} mg/m³"
    ax.text(
        0.98, 0.02, data_txt,
        transform=ax.transAxes,
        color="#cccccc", fontsize=7.5, ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#0d1b2a", alpha=0.8),
    )

    # Leyenda
    legend_patches = [
        mpatches.Patch(color=_COLORS["verde"], label="Zona buena"),
        mpatches.Patch(color=_COLORS["amarillo"], label="Precaución"),
        mpatches.Patch(color=_COLORS["rojo"], label="No recomendado"),
    ]
    leg = ax.legend(
        handles=legend_patches, loc="upper right",
        facecolor="#0d1b2a", edgecolor="#5dade2",
        labelcolor="white", fontsize=8,
    )

    # Estética de ejes
    ax.grid(True, color="white", alpha=0.08, linestyle="--")
    ax.tick_params(colors="#888888", labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")
    ax.set_xlabel("Longitud", color="#888888", fontsize=8)
    ax.set_ylabel("Latitud", color="#888888", fontsize=8)

    filename = f"mapa_{uuid.uuid4().hex[:8]}.png"
    filepath = Path(MEDIA_DIR) / filename
    Path(MEDIA_DIR).mkdir(exist_ok=True)

    plt.tight_layout()
    plt.savefig(str(filepath), dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return filename
