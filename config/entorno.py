# -*- coding: utf-8 -*-
"""
Configuracion de entorno para el cotizador.
Prepara Tesseract (OCR espanol) buscando los datos en este orden:
  1. C:/Users/joaqu/tessdata  (instalacion manual de este equipo)
  2. tools/tesseract-data/    (respaldado en el proyecto, para replicar)
"""
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Carpeta propia del usuario (donde pusimos spa en este equipo)
TESSDATA_DIR = "C:\\Users\\joaqu\\tessdata"
# 2. Respaldo dentro del proyecto (autocontenido para replicar en otro PC)
TESSDATA_PROY = os.path.join(_BASE, "tools", "tesseract-data")

if os.path.isdir(TESSDATA_PROY) and "TESSDATA_PREFIX" not in os.environ:
    # ruta Windows nativa (tesseract.exe es binario Windows)
    os.environ["TESSDATA_PREFIX"] = TESSDATA_PROY.replace("/", "\\")
elif os.path.isdir(TESSDATA_DIR) and "TESSDATA_PREFIX" not in os.environ:
    os.environ["TESSDATA_PREFIX"] = TESSDATA_DIR

# Si tesseract.exe no esta en PATH, anadirlo (ruta tipica de instalacion)
_TESS_BIN = "C:\\Program Files\\Tesseract-OCR"
if os.path.isdir(_TESS_BIN) and _TESS_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _TESS_BIN + os.pathsep + os.environ.get("PATH", "")
