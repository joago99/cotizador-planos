# -*- coding: utf-8 -*-
"""
DETECTOR DE SHAFTS (huecos de elevador/ascensor/núcleo) en planos DXF
=====================================================================
Los planos de cliente NO suelen decir literalmente "shaft". En planos
chilenos el shaft se identifica por:
  - Texto explícito: shaft, elevador, ascensor, núcleo, montacarga.
  - Muros de hormigón armado MUY gruesos (M.H.A. e=600, e=800) que
    rodean el núcleo central de ascensores/escaleras.

Estrategia:
  1. Buscar textos explícitos (más fiable cuando existen).
  2. Si no hay, usar el centroide de los muros M.H.A. más gruesos
     (e>=600) como ubicación del núcleo/shaft. El shaft está en el
     centro del edificio, rodeado de esos muros.

Devuelve lista de shafts con coordenadas en metros y método de detección.
"""
import re
import ezdxf


def _extraer_textos(msp):
    """Devuelve [(x, y, texto)] de todas las entidades de texto."""
    out = []
    for e in msp.query("TEXT MTEXT"):
        t = (e.text if hasattr(e, "text") else e.get_text()).replace("\n", " ").strip()
        try:
            p = e.dxf.insert
            out.append((p.x, p.y, t))
        except Exception:
            continue
    return out


def _espesor_mha(texto: str):
    """Extrae el espesor e=NNN de un texto M.H.A. Devuelve int o None."""
    m = re.search(r"e\s*=\s*(\d+)", texto, re.IGNORECASE)
    return int(m.group(1)) if m else None


def detectar_shafts(ruta_dxf: str) -> list:
    doc = ezdxf.readfile(ruta_dxf)
    msp = doc.modelspace()
    textos = _extraer_textos(msp)

    shafts = []

    # 1. Textos explícitos
    patrones = [r"shaft", r"elevador", r"ascensor", r"n[úu]cleo", r"montacarga"]
    for x, y, t in textos:
        if any(re.search(p, t, re.IGNORECASE) for p in patrones):
            shafts.append({
                "x_m": round(x / 1000, 1),
                "y_m": round(y / 1000, 1),
                "metodo": "texto_explicito",
                "etiqueta": t[:40],
            })

    # 2. Centroide de muros M.H.A. gruesos (núcleo/shaft implícito)
    gruesos = [(x, y) for x, y, t in textos
               if "M.H.A" in t.upper() and (_espesor_mha(t) or 0) >= 600]
    if gruesos:
        cx = sum(p[0] for p in gruesos) / len(gruesos)
        cy = sum(p[1] for p in gruesos) / len(gruesos)
        shafts.append({
            "x_m": round(cx / 1000, 1),
            "y_m": round(cy / 1000, 1),
            "metodo": "centroide_muros_MHA_gruesos",
            "etiqueta": f"núcleo/shaft (centroide de {len(gruesos)} muros M.H.A. e>=600)",
            "muros_detectados": len(gruesos),
        })

    return shafts


if __name__ == "__main__":
    import sys
    ruta = sys.argv[1] if len(sys.argv) > 1 else "data/planos_reales/tko.dxf"
    for s in detectar_shafts(ruta):
        print(f"Shaft @ X={s['x_m']}m Y={s['y_m']}m  [{s['metodo']}]  {s['etiqueta']}")
