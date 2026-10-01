# -*- coding: utf-8 -*-
"""
Agente de equipos: cruza los datos extraídos de la cotización con el catálogo
real de Bombas de Hormigón Chile y recomienda el equipo más adecuado.
Lógica determinista y explicable (cada recomendación trae su justificación).
"""
from config.equipos import EQUIPOS, CONTACTO
from config.ficha_tecnica import FICHA_TECNICA


def _mejor_alcance(equipo, horizontal=True):
    rng = equipo["alcance_horizontal_m"] if horizontal else equipo["alcance_vertical_m"]
    if not rng:
        return None
    return rng[1]  # tomamos el máximo publicado


def _ficha_para(clave):
    """Devuelve resumen de dimensiones físicas de la ficha técnica."""
    try:
        return FICHA_TECNICA.get(clave, {})
    except Exception:
        return {}


def recomendar(extraccion: dict) -> dict:
    m2_list = [x["valor"] for x in extraccion.get("metros_cuadrados", [])]
    altura_list = [x["valor"] for x in extraccion.get("altura_m", [])]
    shaft = extraccion.get("shaft", {}).get("encontrado", False)

    m2 = max(m2_list) if m2_list else None
    altura = max(altura_list) if altura_list else None

    candidatos = []

    # Regla 1: shaft / núcleo de edificio -> TDH o BDP (montaje interior)
    if shaft:
        tdh = next(e for e in EQUIPOS if e["id"] == "tdh")
        bdp = next(e for e in EQUIPOS if e["id"] == "bdp")
        candidatos.append({
            "equipo": tdh, "score": 0.9,
            "porque": "La cotización menciona shaft/elevador (núcleo de edificio): "
                      "la TDH se monta interior o exterior y es ideal para hormigonar "
                      "núcleos de ascensor sin capachos.",
            "ficha": _ficha_para("tdh"),
        })
        candidatos.append({
            "equipo": bdp, "score": 0.7,
            "porque": "El BDP es portátil dentro de la planta; útil si el alcance "
                      "necesario es menor (13-15 m).",
        })

    # Regla 2: altura considerable (pisos altos) -> autobomba / pluma
    if altura and altura >= 20:
        auto = next(e for e in EQUIPOS if e["id"] == "autobomba")
        candidatos.append({
            "equipo": auto, "score": 0.8,
            "porque": f"Altura detectada ~{altura:g} m: la autobomba/pluma "
                      f"(28-36 m) cubre el vertido sin equipo fijo.",
        })

    # Regla 3: obra grande / larga distancia -> estacionaria o bombeo técnico
    if m2 and m2 >= 500:
        est = next(e for e in EQUIPOS if e["id"] == "estacionaria")
        cand = next(e for e in EQUIPOS if e["id"] == "bombeo_tecnico")
        candidatos.append({
            "equipo": est, "score": 0.6,
            "porque": f"Superficie ~{m2:g} m²: bomba estacionaria con línea de "
                      f"tubería sostiene grandes volúmenes de forma continua.",
        })
        candidatos.append({
            "equipo": cand, "score": 0.5,
            "porque": "Si la distancia al punto de vertido es grande, el bombeo "
                      "técnico llega hasta 2000 m horizontales.",
        })

    # Regla 4: por defecto si no hay datos claros -> autobomba (más versátil)
    if not candidatos:
        auto = next(e for e in EQUIPOS if e["id"] == "autobomba")
        candidatos.append({
            "equipo": auto, "score": 0.4,
            "porque": "No se detectaron datos suficientes; la autobomba es la "
                      "opción más versátil para una primera visita/spot.",
        })

    candidatos.sort(key=lambda c: c["score"], reverse=True)
    return {
        "m2_detectado": m2,
        "altura_detectada": altura,
        "shaft_detectado": shaft,
        "recomendacion_principal": {
            "equipo": candidatos[0]["equipo"]["nombre"],
            "alcance_horizontal_m": candidatos[0]["equipo"]["alcance_horizontal_m"],
            "dimensiones_fisicas": candidatos[0]["equipo"]["dimensiones_fisicas"],
            "ficha": candidatos[0].get("ficha", {}),
            "porque": candidatos[0]["porque"],
        },
        "alternativas": [
            {
                "equipo": c["equipo"]["nombre"],
                "alcance_horizontal_m": c["equipo"]["alcance_horizontal_m"],
                "porque": c["porque"],
            }
            for c in candidatos[1:]
        ],
    }
