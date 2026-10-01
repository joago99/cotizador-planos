# -*- coding: utf-8 -*-
"""
ANALIZADOR DE PLANO + COLOCACION DE MAQUINA
==========================================
Dado un DXF de plano de cliente:
  1. Detecta el shaft (núcleo/elevador) — src/detectar_shafts.
  2. Calcula la huella del edificio (bbox de líneas/polilíneas).
  3. Sugiere dónde poner la máquina (TDH/autobomba) resolviendo el
     problema de cobertura: sobre una malla de candidatos en el borde
     libre de la huella, elige el punto que MAXIMIZA el área de losa
     cubierta por el radio de la pluma y MINIMIZA la distancia al shaft
     (formulación tipo Maximal Coverage Location Problem, resuelta por
     fuerza bruta barata — suficiente para un plano).
  4. Dibuja plano + shaft (azul cian) + radio de cobertura + máquina (verde).
  5. Exporta a PDF.

El usuario revisa el PDF y ajusta la posición real de la bomba.
"""
import os
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from shapely.geometry import Point, box, Polygon, MultiPoint
from shapely.ops import unary_union

from src.detectar_shafts import detectar_shafts
from config.ficha_tecnica import FICHA_TECNICA


def _huella(msp):
    xs, ys = [], []
    for e in msp:
        t = e.dxftype()
        if t == "LINE":
            xs += [e.dxf.start.x, e.dxf.end.x]
            ys += [e.dxf.start.y, e.dxf.end.y]
        elif t == "LWPOLYLINE":
            for p in e.get_points("xy"):
                xs.append(p[0]); ys.append(p[1])
    if not xs:
        return None
    return (min(xs), max(xs), min(ys), max(ys))


def _alcance_equipo(tipo: str) -> float:
    """Alcance de pluma (m) según catálogo real de Roberto.
    tipo: 'TDH' o 'BDP'. Usa el MÁXIMO alcance entre todos los modelos
    (Roberto cotiza TDH28/32m, así que tomamos el tope de la línea)."""
    clave = tipo.lower()
    eq = FICHA_TECNICA.get(clave)
    if eq and eq.get("modelos"):
        todos = []
        for m in eq["modelos"]:
            alc = m.get("alcance_horizontal_m")
            if alc:
                todos.append(max(alc))
        if todos:
            return float(max(todos))
    return 30.0


def _sugerir_maquina(shaft, huella, alcance_m):
    """Malla de candidatos en el borde de la huella; elige el que mejor
    cubre la losa (área de intersección círculo∩huella) y más cerca del
    shaft. Lambda pondera distancia al shaft (costo de tendido vertical)."""
    sx, sy = shaft["x_m"] * 1000, shaft["y_m"] * 1000
    xmin, xmax, ymin, ymax = [v for v in huella]
    huella_poly = box(xmin, ymin, xmax, ymax)

    # malla de candidatos en el perímetro de la huella (borde libre)
    paso = max((xmax - xmin), (ymax - ymin)) / 80  # ~80 pts por eje
    cand = []
    x = xmin
    while x <= xmax:
        cand.append((x, ymin)); cand.append((x, ymax)); x += paso
    y = ymin
    while y <= ymax:
        cand.append((xmin, y)); cand.append((xmax, y)); y += paso

    lam = 0.5  # ponderación distancia al shaft
    mejor = None
    for cx, cy in cand:
        circ = Point(cx, cy).buffer(alcance_m * 1000)
        area_cubierta = circ.intersection(huella_poly).area * 1e-6  # m2
        d_shaft = ((cx - sx) ** 2 + (cy - sy) ** 2) ** 0.5 / 1000
        score = area_cubierta - lam * d_shaft
        if mejor is None or score > mejor[0]:
            mejor = (score, cx, cy, area_cubierta, d_shaft)

    _, mx, my, area_c, d_s = mejor
    return {
        "x_m": round(mx / 1000, 1),
        "y_m": round(my / 1000, 1),
        "dist_shaft_m": round(d_s, 1),
        "area_cubierta_m2": round(area_c, 1),
    }


def analizar(ruta_dxf: str, tipo_equipo: str = "TDH", salida_pdf: str = None) -> dict:
    doc = ezdxf.readfile(ruta_dxf)
    msp = doc.modelspace()
    shafts = detectar_shafts(ruta_dxf)
    huella = _huella(msp)
    huella_m = tuple(round(v / 1000, 1) for v in huella) if huella else None

    if not shafts:
        raise ValueError("No se detectó shaft en el plano")

    shaft = shafts[0]
    alcance_m = _alcance_equipo(tipo_equipo)
    maq = _sugerir_maquina(shaft, huella, alcance_m)

    if salida_pdf is None:
        salida_pdf = os.path.join(os.path.dirname(ruta_dxf), "plano_analizado.pdf")

    # --- dibujo ---
    fig, ax = plt.subplots(figsize=(18, 13))
    for e in msp:
        t = e.dxftype()
        if t == "LINE":
            p1, p2 = e.dxf.start, e.dxf.end
            ax.plot([p1.x, p2.x], [p1.y, p2.y], color="#555", lw=0.3)
        elif t == "LWPOLYLINE":
            pts = list(e.get_points("xy"))
            if pts:
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color="#555", lw=0.3)

    sx, sy = shaft["x_m"] * 1000, shaft["y_m"] * 1000
    mx, my = maq["x_m"] * 1000, maq["y_m"] * 1000

    # radio de cobertura (azul cian, según doc)
    cov = Circle((sx, sy), alcance_m * 1000, fill=False, ec="#00bcd4", lw=1.8, ls="--")
    ax.add_patch(cov)

    # shaft (azul cian)
    ax.scatter([sx], [sy], color="#00bcd4", s=420, marker="X", zorder=5)
    ax.annotate("SHAFT / NÚCLEO", (sx, sy), color="#0097a7", fontsize=11,
                fontweight="bold", xytext=(sx + 6000, sy + 5000),
                arrowprops=dict(arrowstyle="->", color="#0097a7"))

    # máquina sugerida (verde)
    ax.scatter([mx], [my], color="#2e7d32", s=420, marker="P", zorder=5)
    ax.annotate(f"MAQUINA ({tipo_equipo})", (mx, my), color="#2e7d32", fontsize=11,
                fontweight="bold", xytext=(mx + 6000, my - 6000),
                arrowprops=dict(arrowstyle="->", color="#2e7d32"))
    ax.plot([sx, mx], [sy, my], color="#2e7d32", lw=1.0, ls=":")

    ax.set_aspect("equal")
    ax.axis("off")
    plt.title(f"Plano analizado — Shaft ({shaft['x_m']}m, {shaft['y_m']}m) | "
              f"Máquina {tipo_equipo} a {maq['dist_shaft_m']}m "
              f"(alcance {alcance_m:g}m, cubre {maq['area_cubierta_m2']:g} m² de losa)",
              fontsize=12)
    plt.tight_layout()
    plt.savefig(salida_pdf, dpi=130, bbox_inches="tight")
    plt.close()

    return {
        "shaft": shaft,
        "huella_m": huella_m,
        "maquina_sugerida": maq,
        "alcance_m": alcance_m,
        "equipo": tipo_equipo,
        "pdf": salida_pdf,
    }


if __name__ == "__main__":
    import sys
    ruta = sys.argv[1] if len(sys.argv) > 1 else "data/planos_reales/tko.dxf"
    eq = sys.argv[2] if len(sys.argv) > 2 else "TDH"
    out = analizar(ruta, eq)
    print("Shaft:", out["shaft"]["x_m"], out["shaft"]["y_m"], "m")
    print("Equipo:", out["equipo"], "| alcance", out["alcance_m"], "m")
    print("Máquina:", out["maquina_sugerida"]["x_m"],
          out["maquina_sugerida"]["y_m"], "m | dist",
          out["maquina_sugerida"]["dist_shaft_m"], "m | cubre",
          out["maquina_sugerida"]["area_cubierta_m2"], "m²")
    print("PDF:", out["pdf"])
