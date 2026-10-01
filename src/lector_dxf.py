# -*- coding: utf-8 -*-
"""
Lector de planos en formato DXF (salida de AutoCAD / exportado desde DWG).
Usa ezdxf para extraer el TEXTO de las entidades TEXT y MTEXT, que es donde
típicamente van las cotas, superficies, ejes y observaciones del plano.

NOTA SOBRE DWG: los archivos .dwg NO se leen directo (requieren AutoCAD u
ODA File Converter). Pedir al cliente el plano en .dxf o .pdf. Si llega .dwg,
convertir con AutoCAD "Guardar como DXF" o con ODA File Converter (gratis,
requiere cuenta en opendesign.com).
"""
import os
import re
import ezdxf


def leer_dxf(ruta: str) -> dict:
    """Devuelve {'texto','origen','entidades','aviso?'}."""
    if not ruta.lower().endswith(".dxf"):
        return {"texto": "", "origen": "no_dxf",
                "aviso": "El archivo no es .dxf"}
    try:
        doc = ezdxf.readfile(ruta)
    except Exception as e:
        return {"texto": "", "origen": "error",
                "aviso": f"No se pudo abrir DXF: {e}"}

    msp = doc.modelspace()
    lineas = []
    n_text = 0
    n_mtext = 0
    for e in msp.query("TEXT MTEXT"):
        txt = e.dxf.text if hasattr(e.dxf, "text") else getattr(e.dxf, "text", "")
        # MTEXT puede traer formato {\...}; lo limpiamos
        txt = re.sub(r"\{[^}]*\}", "", txt)
        txt = txt.replace("\\P", "\n").replace("\\X", "\n")
        if txt.strip():
            lineas.append(txt.strip())
            if e.dxftype() == "TEXT":
                n_text += 1
            else:
                n_mtext += 1

    texto = "\n".join(lineas)
    return {
        "texto": texto,
        "origen": "dxf",
        "entidades": len(list(msp)),
        "n_text": n_text,
        "n_mtext": n_mtext,
        "aviso": None if texto.strip() else "DXF sin texto útil (solo geometría).",
    }
