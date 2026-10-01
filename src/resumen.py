# -*- coding: utf-8 -*-
"""Genera la ficha limpia para Roberto a partir de la extracción + recomendación."""


def _fmt_lista(items, key="valor"):
    if not items:
        return "—"
    return ", ".join(f"{it[key]:g}" for it in items)


def _fmt_dim(dim: dict) -> str:
    if not dim:
        return "(dimensiones físicas por confirmar)"
    if dim.get("estado") == "por_confirmar":
        return "(dimensiones físicas por confirmar con brochure/fabricante)"
    # TDH trae "resumen" con rangos ya procesados
    if "resumen" in dim and isinstance(dim["resumen"], dict):
        r = dim["resumen"]
        partes = []
        if r.get("alcance_horizontal_m"):
            partes.append(f"alcance={r['alcance_horizontal_m'][0]}–{r['alcance_horizontal_m'][1]} m")
        if r.get("peso_pluma_kg_rango"):
            partes.append(f"peso_pluma={r['peso_pluma_kg_rango'][0]}–{r['peso_pluma_kg_rango'][1]} kg")
        if r.get("peso_tornamesa_kg_rango"):
            partes.append(f"tornamesa={r['peso_tornamesa_kg_rango'][0]}–{r['peso_tornamesa_kg_rango'][1]} kg")
        if r.get("angulo_giro"):
            partes.append(f"giro={r['angulo_giro']}")
        if partes:
            return ", ".join(partes) + f"  [{dim.get('estado','')}]"
    # Campos escalares o con _rango
    vals = {}
    skip = ("estado", "fuente", "nota", "nombre", "alcance_horizontal_m",
            "alcance_vertical_m", "radio_giro_m", "modelos", "resumen",
            "dimensiones_fisicas")
    for k, v in dim.items():
        if k in skip or v is None:
            continue
        vals[k] = v
    if not vals:
        if dim.get("nota"):
            return f"(por confirmar — {dim['nota']})"
        return "(dimensiones físicas por confirmar)"
    partes = []
    for k, v in vals.items():
        if isinstance(v, tuple):
            partes.append(f"{k}={v[0]}–{v[1]}")
        else:
            partes.append(f"{k}={v}")
    return ", ".join(partes) + f"  [{dim.get('estado','')}]"


def armar_resumen(extraccion: dict, recomendacion: dict) -> str:
    rp = recomendacion["recomendacion_principal"]
    lineas = []
    lineas.append("=" * 60)
    lineas.append("FICHA DE COTIZACIÓN — BOMBAS DE HORMIGÓN CHILE")
    lineas.append("=" * 60)
    lineas.append(f"Superficie (m²)      : {_fmt_lista(extraccion['metros_cuadrados'])}")
    lineas.append(f"Perímetro (m)        : {_fmt_lista(extraccion['perimetro_m'])}")
    lineas.append(f"Altura (m)           : {_fmt_lista(extraccion['altura_m'])}")
    lineas.append(f"Pisos / niveles      : {_fmt_lista(extraccion['pisos'])}")
    lineas.append(
        f"Shaft / elevador     : "
        f"{'SÍ detectado' if extraccion['shaft']['encontrado'] else 'no detectado'}"
    )
    if extraccion["shaft"]["fragmentos"]:
        lineas.append("   Fragmento(s):")
        for fr in extraccion["shaft"]["fragmentos"][:3]:
            lineas.append(f"     • {fr}")
    lineas.append("-" * 60)
    lineas.append("RECOMENDACIÓN DE EQUIPO")
    lineas.append(f"  Principal : {rp['equipo']}")
    alc = rp["alcance_horizontal_m"]
    lineas.append(
        f"  Alcance   : {alc[0] if alc else '?'} – {alc[1] if alc else '?'} m horizontal"
        if alc else "  Alcance   : según rendimiento/altura/distancia"
    )
    ficha = rp.get("ficha", {})
    lineas.append(f"  Dimensiones: {_fmt_dim(ficha) if ficha else _fmt_dim(rp.get('dimensiones_fisicas', {}))}")
    lineas.append(f"  Por qué   : {rp['porque']}")
    if recomendacion["alternativas"]:
        lineas.append("  Alternativas:")
        for a in recomendacion["alternativas"]:
            lineas.append(f"    - {a['equipo']}: {a['porque']}")
    lineas.append("-" * 60)
    if extraccion["accesos"]:
        lineas.append("Accesos mencionados:")
        for a in extraccion["accesos"][:3]:
            lineas.append(f"  • {a}")
    if extraccion["restricciones"]:
        lineas.append("Restricciones / notas:")
        for r in extraccion["restricciones"][:3]:
            lineas.append(f"  • {r}")
    lineas.append("=" * 60)
    return "\n".join(lineas)
