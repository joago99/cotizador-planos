# -*- coding: utf-8 -*-
"""
AGENTE 1: CORPUS DE PLANOS REALES
=================================
En vez de generar planos sintéticos, este agente ORGANIZA los planos
reales que Roberto recibe (data/planos_reales/) y prepara el flujo de
conversión DWG -> DXF/PDF para que el pipeline los pueda leer.

Qué hace:
  1. Lista los .dwg reales en data/planos_reales/.
  2. Intenta convertirlos a .dxf (AutoCAD o LibreCAD) usando
     src.conversor_dwg.
  3. Reporta qué planos están listos para procesar.

Los planos de ejemplo reales (tko-.dwg) ya están en data/planos_reales/.
Este agente NO inventa datos: usa lo que Roberto realmente recibe.
"""
import os
import glob
import os.path as op

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANOS_DIR = os.path.join(BASE, "data", "planos_reales")


def organizar():
    print(f"[corpus] Carpeta: {PLANOS_DIR}")
    dwgs = glob.glob(op.join(PLANOS_DIR, "*.dwg"))
    pdfs = glob.glob(op.join(PLANOS_DIR, "*.pdf"))
    dxfs = glob.glob(op.join(PLANOS_DIR, "*.dxf"))
    print(f"  DWG : {len(dwgs)}  |  PDF : {len(pdfs)}  |  DXF : {len(dxfs)}")
    for d in dwgs:
        print(f"  - DWG: {op.basename(d)} (requiere conversión a DXF/PDF)")
    for p in pdfs:
        print(f"  - PDF: {op.basename(p)} (listo para leer)")
    for x in dxfs:
        print(f"  - DXF: {op.basename(x)} (listo para leer)")
    return {"dwg": dwgs, "pdf": pdfs, "dxf": dxfs}


def convertir_dwgs():
    """Convierte los DWG reales a DXF para el pipeline."""
    from src.conversor_dwg import convertir
    dwgs = glob.glob(op.join(PLANOS_DIR, "*.dwg"))
    resultados = []
    for d in dwgs:
        out = convertir(d)
        resultados.append((op.basename(d), out))
        print(f"[corpus] {op.basename(d)} -> {out or 'NO convertido'}")
    return resultados


if __name__ == "__main__":
    organizar()
    print("\n[corpus] Convirtiendo DWG (si hay motor disponible)...")
    convertir_dwgs()
