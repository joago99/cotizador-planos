# -*- coding: utf-8 -*-
"""
GENERADOR DE BORRADOR DE RESPUESTA (propuesta tipo Roberto)
============================================================
A partir de la extracción del plano del cliente + la recomendación,
arma un borrador de propuesta en el FORMATO que usa Roberto:
  - Nombre del proyecto
  - OPCIÓN 1: 1 TDH (torre) central, con alcance
  - OPCIÓN 2: N BDP (brazos portátiles) distribuidos, con alcance
  - Encabezado empresa / contacto
  - Nota de que falta lámina 02 (precios) para cerrar

El borrador es PARA QUE ROBERTO LO EDITE y luego lo vuelva plano.
No se envía solo.
"""
from config.ficha_tecnica import FICHA_TECNICA

EMPRESA = "Bombas de Hormigón Chile"
WEB = "www.bombasdb.cl"
CONTACTO = "contacto@bombasdb.cl"


def generar_borrador(extraccion: dict, recomendacion: dict) -> str:
    proyecto = extraccion.get("proyecto") or "PROYECTO (nombre por completar)"
    tdh = FICHA_TECNICA["tdh"]["resumen"]
    bdp = FICHA_TECNICA["bdp"]["resumen"]

    # Cantidad de BDP sugerida según tamaño (heurística simple)
    m2 = max([x["valor"] for x in extraccion["metros_cuadrados"]], default=0)
    if m2 > 3000:
        n_bdp = 4
    elif m2 > 1500:
        n_bdp = 3
    elif m2 > 600:
        n_bdp = 2
    else:
        n_bdp = 1

    alc_tdh = f"{tdh['alcance_horizontal_m'][0]}–{tdh['alcance_horizontal_m'][1]} m"
    alc_bdp = f"{bdp['alcance_horizontal_m'][0]}–{bdp['alcance_horizontal_m'][1]} m"

    lineas = []
    lineas.append("=" * 60)
    lineas.append("BORRADOR DE PROPUESTA — (editar antes de enviar)")
    lineas.append("=" * 60)
    lineas.append(f"PROYECTO : {proyecto}")
    if extraccion["metros_cuadrados"]:
        lineas.append(f"SUPERFICIE: {m2:g} m²  |  PISOS: "
                      f"{[x['valor'] for x in extraccion['pisos']]}")
    lineas.append("")
    lineas.append("OPCIÓN 1: PLANTA + TDH (torre distribuidora)")
    lineas.append(f"   - 1 equipo TDH, alcance {alc_tdh}")
    lineas.append("   - Ubicación sugerida: núcleo/elevador central")
    lineas.append("")
    lineas.append(f"OPCIÓN 2: PLANTA + {n_bdp} BDP (brazos portátiles)")
    lineas.append(f"   - {n_bdp} equipos BDP, alcance {alc_bdp} c/u")
    lineas.append("   - Distribuidos en la losa para cubrir toda el área")
    lineas.append("")
    if extraccion["shaft"]["encontrado"]:
        lineas.append("NOTA: se detectó shaft/elevador en el plano del cliente.")
    lineas.append("")
    lineas.append("--- FALTAN DATOS PARA CERRAR (lámina 02) ---")
    lineas.append("  [ ] Precios por opción")
    lineas.append("  [ ] Metros cúbicos de hormigón estimados")
    lineas.append("  [ ] Plazos y turnos de bombeo")
    lineas.append("  [ ] Condiciones comerciales")
    lineas.append("")
    lineas.append(f"{EMPRESA}  |  {WEB}  |  {CONTACTO}")
    lineas.append("=" * 60)
    return "\n".join(lineas)
