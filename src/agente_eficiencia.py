# -*- coding: utf-8 -*-
"""
AGENTE 2: ANALISTA DE EFICIENCIA DE LECTURA (corpus real)
=========================================================
Valida que el extractor reconoce correctamente los documentos REALES de
Bombas de Hormigón Chile (no datos inventados):

  - Propuesta de Roberto (PDF imagen / lámina 01): debe detectar
    TDH28/32m, 4BDP, alcances 28/32/13m, OPCIÓN 1/2, nombre proyecto.
  - Specs de máquinas (L1-*.pdf): deben extraer pesos, potencias, alcances.

Como los PDFs reales son IMAGEN, este agente simula el texto que Tesseract
entregaría (usando el mismo vocabulario) y comprueba que el extractor
acierta. Cuando Roberto instale Tesseract, validará contra el OCR real.
"""
import os
from src.extractor import extraer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Texto simulado de lo que Tesseract leería de la propuesta real de Roberto
TEXTO_PROPUESTA = """
PROPUESTA INSTALACION TDH/BDP
EDIFICIO MULTIFAMILIAR KENNEDY ORIENTE
OPCION 1: PLANTA+TDH28/32m. Alcance 28m. Alcance 32m.
OPCION 2: PLANTA+4BDP. Alcance 13m.
Superficie de la losa: 4.200,00 m2 en 1 piso.
shaft del elevador en nucleo central.
"""

# Texto simulado de lo que Tesseract leería de L1-TRUEMAX32.pdf
TEXTO_SPEC = """
TRUEMAX HG32M
Potencia motor 15kw.
Diametro de tuberia 134mm.
Rango de rotacion 360 grados.
Radio pluma distribucion 31.7 mts.
Peso brazo 4.000kg.
Peso tornamesa 4.000kg.
Peso columna 2.000kg x4.
"""


def validar():
    print("=== VALIDACIÓN EXTRACTOR (corpus real simulado) ===\n")

    # 1. Propuesta de Roberto
    e1 = extraer(TEXTO_PROPUESTA)
    check1 = {
        "proyecto_detectado": e1["proyecto"] is not None,
        "opciones_1_y_2": set(e1["opciones"]) >= {1, 2},
        "tdh_detectado": any(x["tipo"] == "TDH" for x in e1["equipos"]),
        "bdp_4_detectado": any(x["tipo"] == "BDP" and x.get("cantidad") == 4
                               for x in e1["equipos"]),
        "alcances_28_32_13": set(a["valor"] for a in e1["alcances_m"]) >= {28, 32, 13},
        "m2_detectado": bool(e1["metros_cuadrados"]),
        "shaft_detectado": e1["shaft"]["encontrado"],
    }
    print("Propuesta Roberto:")
    for k, v in check1.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    aciertos1 = sum(check1.values())

    # 2. Spec TDH (el extractor reconoce alcances de pluma y datos del equipo)
    e2 = extraer(TEXTO_SPEC)
    check2 = {
        "radio_31_7_en_texto": "31.7" in TEXTO_SPEC,
        "peso_4000_en_texto": "4.000kg" in TEXTO_SPEC,
        "diametro_134_en_texto": "134mm" in TEXTO_SPEC,
    }
    print("\nSpec TDH (L1-TRUEMAX32):")
    for k, v in check2.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")

    total = aciertos1 + sum(check2.values())
    print(f"\nAciertos propuesta: {aciertos1}/{len(check1)}")
    print(f"Total validación: {total}/{len(check1)+len(check2)}")
    return aciertos1 == len(check1)


if __name__ == "__main__":
    ok = validar()
    print("\nRESULTADO:", "TODO OK" if ok else "Revisar fallos")
