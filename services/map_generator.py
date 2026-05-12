"""
Genera el mapa PNG de la Ciénaga Grande de Santa Marta.
Diseño tipo carta náutica — sin tiles de internet, solo matplotlib.
"""
import uuid
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, Polygon as MplPolygon
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from datetime import datetime
from config import MEDIA_DIR

# ---------------------------------------------------------------------------
# Geografía
# ---------------------------------------------------------------------------

# Polígono principal de la Ciénaga Grande (lon, lat) — sentido horario
_CIENAGA = np.array([
    [-74.22, 11.03], [-74.18, 10.97], [-74.19, 10.90],
    [-74.21, 10.82], [-74.27, 10.72], [-74.36, 10.62],
    [-74.48, 10.57], [-74.60, 10.58], [-74.70, 10.65],
    [-74.76, 10.76], [-74.76, 10.88], [-74.68, 10.99],
    [-74.55, 11.05], [-74.40, 11.08], [-74.28, 11.06],
    [-74.22, 11.03],
])

# Caño Clarín — conecta la ciénaga con el Río Magdalena al oeste
_CANO_CLARIN = np.array([
    [-74.76, 10.82], [-74.82, 10.83], [-74.88, 10.85],
])

# Ríos que desembocan por el sur
_RIO_FUNDACION = np.array([
    [-74.36, 10.62], [-74.34, 10.53], [-74.32, 10.46],
])
_RIO_ARACATACA = np.array([
    [-74.48, 10.57], [-74.46, 10.49], [-74.44, 10.43],
])

# Comunidades pesqueras (lon, lat, nombre corto, sector)
_COMMUNITIES = [
    (-74.20, 10.92, "Tasajera",       "carretera"),
    (-74.20, 10.86, "Puebloviejo",    "carretera"),
    (-74.72, 10.83, "Caño Clarín",    "carretera"),
    (-74.67, 10.90, "Sevillano",      "carretera"),
    (-74.48, 10.93, "Nueva Venecia",  "palafítico"),
    (-74.58, 10.78, "Buenavista",     "palafítico"),
    (-74.40, 10.70, "Bcs. Aracataca", "palafítico"),
    (-74.54, 10.62, "Pivijay",        "suroccidente"),
]

# Zonas del análisis multivariable — deben coincidir con zone_analysis.ZONES
# (lon, lat, nombre corto para el mapa)
_ZONE_COORDS = {
    "Boca de la Barra / Zona Marina":            (-74.21, 11.02, "Boca\nde la Barra"),
    "Nueva Venecia – Palafíticos Norte":          (-74.48, 10.92, "Nueva\nVenecia"),
    "Buenavista – Palafíticos Sur":               (-74.58, 10.77, "Buena-\nvista"),
    "Caño Clarín – Sector Carretera Norte":       (-74.70, 10.83, "Caño\nClarín"),
    "Tasajera / Puebloviejo – Sector Carretera Sur": (-74.21, 10.89, "Tasajera /\nPuebloviejo"),
    "Suroccidente – Pivijay / Santa Rita":        (-74.55, 10.62, "Suroc-\ncidente"),
}

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
_BG        = "#0b1826"   # fondo general (azul noche)
_OCEAN     = "#12304d"   # Mar Caribe
_WATER     = "#1a5c8a"   # agua de la ciénaga
_LAND      = "#2d3d22"   # tierra
_RIVER     = "#1a7ab5"   # ríos y caños
_GRID      = "#ffffff"   # grilla

_SEMAPHORE_COLORS = {
    "verde":    "#27ae60",
    "amarillo": "#f0a500",
    "rojo":     "#e74c3c",
}
_SEMAPHORE_LABELS = {
    "verde":    "VERDE — Buen dia pa' la faena",
    "amarillo": "PRECAUCION — Salir con cuidado",
    "rojo":     "NO SALIR — Quedate en tierra",
}

# Gradiente IPP: 0=rojo, 50=amarillo, 100=verde
_IPP_CMAP = LinearSegmentedColormap.from_list(
    "ipp", ["#e74c3c", "#f0a500", "#27ae60"]
)


def _ipp_color(score: float) -> str:
    rgba = _IPP_CMAP(score / 100)
    return "#{:02x}{:02x}{:02x}".format(
        int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255)
    )


def _north_arrow(ax, x=0.96, y=0.94):
    """Dibuja una flecha de norte simple."""
    ax.annotate(
        "N", xy=(x, y + 0.045), xycoords="axes fraction",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color="white",
        path_effects=[pe.withStroke(linewidth=2, foreground=_BG)],
    )
    ax.annotate(
        "", xy=(x, y + 0.04), xytext=(x, y),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color="white", lw=1.5),
    )


def _scale_bar(ax, lon_left=-74.85, lat_bot=10.47, length_deg=0.18):
    """Barra de escala aproximada (~15 km a esa latitud)."""
    ax.plot(
        [lon_left, lon_left + length_deg], [lat_bot, lat_bot],
        color="white", lw=2.5, solid_capstyle="butt",
    )
    ax.plot([lon_left, lon_left], [lat_bot - 0.01, lat_bot + 0.01], color="white", lw=1.5)
    ax.plot([lon_left + length_deg, lon_left + length_deg],
            [lat_bot - 0.01, lat_bot + 0.01], color="white", lw=1.5)
    ax.text(
        lon_left + length_deg / 2, lat_bot - 0.025, "≈ 15 km",
        ha="center", va="top", color="white", fontsize=7,
        path_effects=[pe.withStroke(linewidth=1.5, foreground=_BG)],
    )


def generate_map(
    semaphore_color: str,
    sst: float,
    chlorophyll: float,
    water_quality: dict | None = None,
    zone_ranking: list | None = None,
) -> str:
    """
    Genera el mapa PNG y devuelve el nombre del archivo.
    zone_ranking: lista de dicts con 'name', 'score', 'species', 'arts'
                  (salida de core.zone_analysis.full_ranking)
    """
    sem_color = _SEMAPHORE_COLORS.get(semaphore_color, _SEMAPHORE_COLORS["verde"])

    # --- Figura ---
    fig = plt.figure(figsize=(8, 9.5), facecolor=_BG)

    # Mapa ocupa ~78% del alto, panel de datos el resto abajo
    ax = fig.add_axes([0.05, 0.22, 0.90, 0.72])
    ax.set_facecolor(_OCEAN)
    ax.set_xlim(-74.92, -74.08)
    ax.set_ylim(10.40, 11.18)

    # --- Tierra ---
    land = plt.Polygon(
        [[-74.92, 10.40], [-74.08, 10.40], [-74.08, 11.18],
         [-74.92, 11.18], [-74.92, 10.40]],
        closed=True, facecolor=_LAND, zorder=0,
    )
    ax.add_patch(land)

    # Mar Caribe (franja norte sobre la línea de costa ~11.05)
    mar = plt.Polygon(
        [[-74.92, 11.05], [-74.08, 11.05], [-74.08, 11.18], [-74.92, 11.18]],
        closed=True, facecolor=_OCEAN, zorder=1, alpha=0.6,
    )
    ax.add_patch(mar)
    ax.text(-74.50, 11.12, "MAR CARIBE", ha="center", va="center",
            color="#5dade2", fontsize=8.5, fontstyle="italic", fontweight="bold",
            alpha=0.8, zorder=2)

    # --- Ríos / Caño Clarín ---
    for river in [_CANO_CLARIN, _RIO_FUNDACION, _RIO_ARACATACA]:
        ax.plot(river[:, 0], river[:, 1],
                color=_RIVER, lw=2.2, alpha=0.7, zorder=3, solid_capstyle="round")

    # --- Cuerpo de la Ciénaga ---
    cienaga = MplPolygon(
        _CIENAGA, closed=True,
        facecolor=_WATER, edgecolor="#5dade2", linewidth=1.6, alpha=0.92, zorder=4,
    )
    ax.add_patch(cienaga)

    ax.text(-74.50, 10.83, "CIÉNAGA GRANDE\nDE SANTA MARTA",
            ha="center", va="center", color="white", fontsize=7.5,
            fontstyle="italic", alpha=0.45, zorder=5)

    # --- Comunidades pesqueras ---
    for lon, lat, nombre, sector in _COMMUNITIES:
        ax.scatter(lon, lat, s=28, color="white", zorder=8,
                   edgecolors="#aaaaaa", linewidths=0.6)
        ax.annotate(
            nombre, (lon, lat), xytext=(5, 4), textcoords="offset points",
            color="#dddddd", fontsize=6.2, zorder=9,
            path_effects=[pe.withStroke(linewidth=1.8, foreground=_BG)],
        )

    # --- Zonas de pesca coloreadas por IPP ---
    medals = ["★", "②", "③", "④", "⑤", "⑥"]

    if zone_ranking:
        for i, zone in enumerate(zone_ranking):
            coords = _ZONE_COORDS.get(zone["name"])
            if not coords:
                continue
            lon, lat, label = coords
            score = zone["score"]
            color = _ipp_color(score)
            is_best = (i == 0)

            size = 520 if is_best else 280
            lw   = 2.5 if is_best else 1.2
            edge = "gold" if is_best else "white"

            ax.scatter(lon, lat, s=size, color=color, zorder=10,
                       edgecolors=edge, linewidths=lw, alpha=0.93)

            # Medalla encima del círculo
            ax.text(lon, lat, medals[i], ha="center", va="center",
                    color="white", fontsize=8 if is_best else 6.5,
                    fontweight="bold", zorder=11,
                    path_effects=[pe.withStroke(linewidth=1.5, foreground=color)])

            # Etiqueta con zona + especie principal
            species_short = zone["species"][0] if zone["species"] else ""
            full_label = f"{label}\n{species_short}"
            ax.annotate(
                full_label, (lon, lat),
                xytext=(9, -12), textcoords="offset points",
                color="white", fontsize=6.5, fontweight="bold", zorder=12,
                bbox=dict(
                    boxstyle="round,pad=0.25",
                    facecolor=_BG, edgecolor=color, linewidth=0.8, alpha=0.82,
                ),
                path_effects=[pe.withStroke(linewidth=0.5, foreground=_BG)],
            )
    else:
        # Fallback si no hay ranking: semáforo uniforme en zonas fijas
        for name, (lon, lat, label) in _ZONE_COORDS.items():
            ax.scatter(lon, lat, s=300, color=sem_color, zorder=10,
                       edgecolors="white", linewidths=1.4, alpha=0.90)
            ax.annotate(
                label, (lon, lat), xytext=(8, 4), textcoords="offset points",
                color="white", fontsize=6.5, zorder=11,
                bbox=dict(boxstyle="round,pad=0.2", facecolor=_BG, alpha=0.75),
            )

    # --- Leyenda IPP ---
    legend_items = [
        mpatches.Patch(color=_ipp_color(85), label="Zona excelente"),
        mpatches.Patch(color=_ipp_color(60), label="Zona buena"),
        mpatches.Patch(color=_ipp_color(35), label="Zona regular"),
    ]
    ax.legend(
        handles=legend_items, loc="upper left",
        facecolor=_BG, edgecolor="#5dade2", labelcolor="white",
        fontsize=7.5, framealpha=0.88,
    )

    # --- Norte y escala ---
    _north_arrow(ax)
    _scale_bar(ax)

    # --- Grilla ---
    ax.grid(True, color=_GRID, alpha=0.06, linestyle="--", linewidth=0.5)
    ax.tick_params(colors="#666666", labelsize=6.5)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334455")

    # Título dentro del mapa
    today = datetime.now().strftime("%d %b %Y  %H:%M")
    ax.set_title(
        f"CienRayas  —  Ciénaga Grande de Santa Marta\n{today}",
        color="white", fontsize=10.5, fontweight="bold",
        pad=8, loc="center",
        path_effects=[pe.withStroke(linewidth=2, foreground=_BG)],
    )

    # -----------------------------------------------------------------------
    # Panel de datos (abajo) — fuera del eje del mapa
    # -----------------------------------------------------------------------
    ax_panel = fig.add_axes([0.0, 0.0, 1.0, 0.21])
    ax_panel.set_facecolor("#0d1b2a")
    ax_panel.axis("off")

    # Semáforo (izquierda)
    ax_panel.add_patch(mpatches.FancyBboxPatch(
        (0.02, 0.12), 0.28, 0.78,
        boxstyle="round,pad=0.02", facecolor=sem_color, alpha=0.20,
        transform=ax_panel.transAxes, zorder=1,
    ))
    ax_panel.text(0.16, 0.80, "SEMAFORO DEL DIA",
                  transform=ax_panel.transAxes,
                  ha="center", va="top", color="#aaaaaa", fontsize=7)
    ax_panel.text(0.16, 0.55,
                  _SEMAPHORE_LABELS.get(semaphore_color, ""),
                  transform=ax_panel.transAxes,
                  ha="center", va="center", color="white",
                  fontsize=8.5, fontweight="bold")

    # Datos del agua (centro)
    wq = water_quality or {}
    od  = wq.get("dissolved_oxygen", "?")
    sal = wq.get("salinity", "?")
    season = {"seca": "Epoca seca", "lluvias": "Lluvias",
              "transicion": "Transicion"}.get(wq.get("season", ""), "")

    centro_lines = [
        f"Temp. agua: {sst}°C",
        f"OD: {od} mg/L   Salinidad: {sal} PSU",
        f"Clorofila: {chlorophyll} mg/m³   {season}",
    ]
    ax_panel.text(0.50, 0.82, "CONDICIONES DEL AGUA",
                  transform=ax_panel.transAxes,
                  ha="center", va="top", color="#aaaaaa", fontsize=7)
    for j, line in enumerate(centro_lines):
        ax_panel.text(0.50, 0.62 - j * 0.20, line,
                      transform=ax_panel.transAxes,
                      ha="center", va="center", color="white", fontsize=8)

    # Ranking top 3 (derecha)
    if zone_ranking:
        ax_panel.text(0.84, 0.82, "TOP ZONAS HOY",
                      transform=ax_panel.transAxes,
                      ha="center", va="top", color="#aaaaaa", fontsize=7)
        for j, z in enumerate(zone_ranking[:3]):
            med = ["★ ", "2. ", "3. "][j]
            col = ["gold", "white", "#aaaaaa"][j]
            short = z["name"].split("–")[0].split("/")[0].strip()
            ax_panel.text(
                0.72, 0.60 - j * 0.20,
                f"{med}{short}  ({z['score']:.0f}/100)",
                transform=ax_panel.transAxes,
                ha="left", va="center", color=col, fontsize=7.8,
                fontweight="bold" if j == 0 else "normal",
            )

    # Créditos
    ax_panel.text(0.50, 0.04, "NASA · IDEAM · Open-Meteo · INVEMAR  |  Universidad del Magdalena",
                  transform=ax_panel.transAxes,
                  ha="center", va="bottom", color="#445566", fontsize=6.5)

    # -----------------------------------------------------------------------
    filename = f"mapa_{uuid.uuid4().hex[:8]}.png"
    filepath = Path(MEDIA_DIR) / filename
    Path(MEDIA_DIR).mkdir(exist_ok=True)

    plt.savefig(str(filepath), dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return filename
