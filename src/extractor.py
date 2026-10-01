# -*- coding: utf-8 -*-
"""
Extracción de campos clave de una cotización/propuesta de obra de hormigón.
Reconoce el vocabulario REAL de Bombas de Hormigón Chile (Roberto):
  - m², perímetro, altura, pisos
  - shaft / elevador / ascensor / núcleo (donde se monta la máquina)
  - equipos: TDH (torre), BDP (brazo portátil), autobomba/pluma, estacionaria
  - "4BDP", "PLANTA+4BDP", "TDH28/32m" (nomenclatura de propuestas)
  - alcances de pluma: "Alcance 28m", "Alcance 13m"
  - opciones: "OPCIÓN 1", "OPCIÓN 2"
  - nombre de proyecto
Siempre devuelve el fragmento original para verificación humana.
"""
import re

# ---- utilidades de números en español ----
_RE_UNIDAD = re.compile(
    r"(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:[.,]\d+)?)\s*"
    r"(m2|m²|mt2|mts2|metros?\s*cuadrados?)",
    re.IGNORECASE,
)
_RE_PERIMETRO = re.compile(
    r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?)\s*(m|mt|mts|metros?)?\s*(?:de\s*)?"
    r"(per[ií]metro|contorno|borde)",
    re.IGNORECASE,
)
_RE_ALTURA = re.compile(
    r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?)\s*(m|mt|mts|metros?)\s*(?:de\s*)?"
    r"(altura|alto|elevaci[oó]n)",
    re.IGNORECASE,
)
_RE_PISOS = re.compile(r"(\d+)\s*(pisos?|niveles?|plantas?)", re.IGNORECASE)

# Equipos y nomenclatura propia de Roberto (case-insensitive)
_RE_TDH = re.compile(r"\bTDH\s*(\d{2})\s*[/x]\s*(\d{2})\s*m\b", re.IGNORECASE)
_RE_BDP = re.compile(r"(\d+)\s*BDP\b|\bBDP\b", re.IGNORECASE)
_RE_ALCANCE = re.compile(
    r"alcance\s*(\d{1,2})\s*m", re.IGNORECASE
)
_RE_OPCION = re.compile(r"opci[oó]n\s*(\d+)", re.IGNORECASE)
_RE_PROYECTO = re.compile(
    r"(edificio\s+[^\n]{3,60}|proyecto\s+[^\n]{3,60}|multifamiliar\s+[^\n]{3,60})",
    re.IGNORECASE,
)


def _num(txt: str) -> float | None:
    if not txt:
        return None
    t = txt.strip()
    if "." in t and "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t and "." not in t:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def _ctx(texto: str, idx: int, ancho: int = 120) -> str:
    a = max(0, idx - ancho)
    b = min(len(texto), idx + ancho)
    return re.sub(r"\s+", " ", texto[a:b]).strip()


def extraer(texto: str) -> dict:
    res = {
        "metros_cuadrados": [],
        "perimetro_m": [],
        "altura_m": [],
        "pisos": [],
        "shaft": {"encontrado": False, "fragmentos": [], "ubicacion": None},
        "equipos": [],          # TDH, BDP, etc. con cantidad y alcance
        "alcances_m": [],       # alcances de pluma mencionados
        "opciones": [],         # OPCIÓN 1, OPCIÓN 2
        "proyecto": None,
        "accesos": [],
        "restricciones": [],
    }
    if not texto:
        return res

    # m²
    for m in _RE_UNIDAD.finditer(texto):
        val = _num(m.group(1))
        if val:
            res["metros_cuadrados"].append({"valor": val, "fragmento": _ctx(texto, m.start())})

    # perímetro
    for m in _RE_PERIMETRO.finditer(texto):
        val = _num(m.group(1))
        if val:
            res["perimetro_m"].append({"valor": val, "fragmento": _ctx(texto, m.start())})

    # altura
    for m in _RE_ALTURA.finditer(texto):
        val = _num(m.group(1))
        if val:
            res["altura_m"].append({"valor": val, "fragmento": _ctx(texto, m.start())})

    # pisos
    for m in _RE_PISOS.finditer(texto):
        res["pisos"].append({"valor": int(m.group(1)), "fragmento": _ctx(texto, m.start())})

    # PLANO DE CLIENTE: pisos por "PISO N°" / "NIVELES...PISO N"
    for m in re.finditer(r"piso\s+(?:n[º°o]?\.?\s*)?(\d+)", texto, re.IGNORECASE):
        try:
            res["pisos"].append({"valor": int(m.group(1)), "fragmento": _ctx(texto, m.start())})
        except ValueError:
            pass

    # PLANO DE CLIENTE: altura máxima por secuencia de cotas de nivel
    # (ej. en tko.dwg: 14, 15, 16, 17.2, 19.1, 20, 21, 22 = metros de cota)
    cotas = [float(x) for x in re.findall(r"\b(\d{1,2}(?:\.\d)?)\b", texto)]
    cotas = [c for c in cotas if 3 <= c <= 250]  # rango plausible de altura (m)
    if cotas:
        res["altura_m"].append({
            "valor": max(cotas),
            "fragmento": f"cota máxima detectada en plano: {max(cotas):g} m",
            "fuente": "cota_nivel",
        })

    # SHAFT / elevador / ascensor / núcleo
    patrones_shaft = [
        r"(shaft\s*(?:del\s*)?(?:elevador|ascensor)?)",
        r"(hueco\s*(?:de\s*)?ascensor)",
        r"(caja\s*(?:de\s*)?ascensor)",
        r"(n[úu]cleo\s*(?:de\s*)?(?:ascensor|elevador|montacarga)?)",
        r"(elevador|ascensor)",
        r"(montacarga)",
    ]
    for pat in patrones_shaft:
        for m in re.finditer(pat, texto, re.IGNORECASE):
            res["shaft"]["encontrado"] = True
            res["shaft"]["fragmentos"].append(_ctx(texto, m.start()))

    # TDH con alcance (p.ej. TDH28/32m)
    for m in _RE_TDH.finditer(texto):
        res["equipos"].append({
            "tipo": "TDH", "alcance_min": int(m.group(1)),
            "alcance_max": int(m.group(2)), "fragmento": _ctx(texto, m.start())
        })

    # BDP (con o sin cantidad: "4BDP", "PLANTA+4BDP", "BDP")
    for m in _RE_BDP.finditer(texto):
        cant = None
        if m.group(1):
            cant = int(m.group(1))
        res["equipos"].append({
            "tipo": "BDP", "cantidad": cant, "fragmento": _ctx(texto, m.start())
        })

    # alcances de pluma sueltos
    for m in _RE_ALCANCE.finditer(texto):
        res["alcances_m"].append({"valor": int(m.group(1)), "fragmento": _ctx(texto, m.start())})

    # opciones
    for m in _RE_OPCION.finditer(texto):
        res["opciones"].append(int(m.group(1)))

    # nombre de proyecto
    mp = _RE_PROYECTO.search(texto)
    if mp:
        res["proyecto"] = re.sub(r"\s+", " ", mp.group(1)).strip()

    # accesos
    for m in re.finditer(r"(acceso[s]?[^.]{0,80})", texto, re.IGNORECASE):
        res["accesos"].append(_ctx(texto, m.start(), 80))

    # restricciones típicas
    for kw in ["restricci", "altura m[áa]xima", "ancho de calle", "voladura",
               "horario", "tr[áa]nsito", "espacio reducido", "techo", "losa"]:
        for m in re.finditer(kw, texto, re.IGNORECASE):
            res["restricciones"].append(_CTX_RESTR(m, texto))
            break

    return res


def _CTX_RESTR(m, texto):
    a = max(0, m.start() - 40)
    b = min(len(texto), m.start() + 80)
    return re.sub(r"\s+", " ", texto[a:b]).strip()

