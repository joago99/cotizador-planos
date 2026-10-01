# -*- coding: utf-8 -*-
"""
CONVERSOR DWG -> DXF
=====================
Roberto recibe los planos de sus clientes en .dwg (AutoCAD).
Este módulo centraliza la conversión a .dxf, que el sistema SÍ lee
(texto + geometría) vía ezdxf.

MOTOR PRINCIPAL: AutoCAD (accoreconsole.exe, headless).
  - Roberto TIENE AutoCAD -> conversión perfecta: hatches, bloques,
    atributos y capas se conservan. Esto arregla el problema de que
    LibreDWG saltaba los HATCH y el plano se veía "hueco".
  - Busca accoreconsole.exe en C:\Program Files\Autodesk\AutoCAD*\

MOTOR FALLBACK: LibreDWG (dwg2dxf.exe, GPL, tools/libredwg/).
  - Convierte por CLI sin AutoCAD, pero SALTA HATCH y alguns bloques
    (warn "Skip HATCH common handles"). Sirve para extraer shaft/textos,
    pero el render se ve incompleto. Usarlo solo si no hay AutoCAD.

Uso:
  from src.conversor_dwg import convertir
  salida = convertir("ruta/plano.dwg")  # devuelve ruta .dxf o None
"""
import os
import glob
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIBREDWG_DIR = os.path.join(BASE, "tools", "libredwg")
LIBREDWG_EXE = os.path.join(LIBREDWG_DIR, "dwg2dxf.exe")


def _autocad_exe() -> str | None:
    """Busca accoreconsole.exe (AutoCAD headless) en rutas típicas."""
    patrones = [
        r"C:\Program Files\Autodesk\AutoCAD*\accoreconsole.exe",
        r"C:\Program Files\Autodesk\AutoCAD*\acad.exe",
    ]
    for p in patrones:
        found = glob.glob(p)
        if found:
            return found[0]
    return None


def _convertir_autocad(dwg: str, dxf: str) -> bool:
    """AutoCAD headless: abre DWG y exporta DXF 2013 (conserva hatches)."""
    exe = _autocad_exe()
    if not exe:
        return False
    scr = dwg + ".scr"
    with open(scr, "w", encoding="utf-8") as f:
        # DXFOUT usa código de versión: 2013 = 61 en algunos builds;
        # usamos el prompt interactivo con la ruta y luego versión por defecto.
        f.write(f'_.OPEN "{dwg}"\n_.DXFOUT\n"{dxf}"\n_.QUIT\n')
    try:
        subprocess.run([exe, "/b", scr], timeout=180, check=True,
                       capture_output=True)
        ok = os.path.exists(dxf)
        if ok:
            os.remove(scr)
        else:
            print(f"[conversor] AutoCAD no escribió {dxf}")
        return ok
    except Exception as e:
        print(f"[conversor] AutoCAD falló: {e}")
        return False


def _convertir_libredwg(dwg: str, dxf: str) -> bool:
    """LibreDWG dwg2dxf: DWG->DXF por CLI, sin AutoCAD (fallback)."""
    salida = subprocess.run(
        [LIBREDWG_EXE, dwg],
        cwd=os.path.dirname(dwg),
        capture_output=True, text=True, timeout=120
    )
    generado = os.path.splitext(dwg)[0] + ".dxf"
    if os.path.exists(generado) and generado != dxf:
        os.replace(generado, dxf)
    ok = os.path.exists(dxf)
    if not ok:
        print(f"[conversor] LibreDWG salida: {salida.stdout[-300:]}")
    return ok


def convertir(ruta_dwg: str, motor: str = "auto") -> str | None:
    """
    Convierte un .dwg a .dxf.
    motor: 'auto' (AutoCAD primero, luego LibreDWG) | 'autocad' | 'libredwg'
    Devuelve la ruta del .dxf o None si falla.
    """
    if not ruta_dwg.lower().endswith(".dwg"):
        raise ValueError("Se espera un archivo .dwg")
    dest = os.path.splitext(ruta_dwg)[0] + ".dxf"

    if motor in ("auto", "autocad") and _convertir_autocad(ruta_dwg, dest):
        return dest
    if motor in ("auto", "libredwg") and os.path.exists(LIBREDWG_EXE):
        if _convertir_libredwg(ruta_dwg, dest):
            return dest
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.conversor_dwg ruta.dwg")
        sys.exit(1)
    out = convertir(sys.argv[1])
    print("Convertido:", out)
