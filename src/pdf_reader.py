# -*- coding: utf-8 -*-
"""Lectura de PDF: primero texto nativo; si no hay, OCR local (Tesseract).

Requiere:
  - PyMuPDF (fitz): renderiza páginas a imagen (sin poppler).
  - pytesseract + binario Tesseract instalado y en PATH.
    Instalador Windows: https://github.com/UB-Mannheim/tesseract/wiki
    (marca "Add to PATH" y selecciona Spanish en language data).
"""
import os
import re
import subprocess
from pdfminer.high_level import extract_text as pdfminer_extract

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import pytesseract
except Exception:
    pytesseract = None

TESSERACT_BIN = "tesseract"


def tesseract_disponible() -> bool:
    """Comprueba si el binario tesseract está accesible."""
    if pytesseract is None:
        return False
    try:
        subprocess.run([TESSERACT_BIN, "--version"], capture_output=True,
                       timeout=10, check=True)
        return True
    except Exception:
        return False


def _tiene_texto(texto: str) -> bool:
    if not texto:
        return False
    limpio = re.sub(r"\s+", "", texto)
    return len(limpio) > 40


def _ocr_con_pymupdf(ruta: str) -> str:
    if fitz is None:
        raise RuntimeError("PyMuPDF no instalado")
    doc = fitz.open(ruta)
    partes = []
    for pagina in doc:
        pix = pagina.get_pixmap(dpi=300)
        img = pix.tobytes("png")
        from io import BytesIO
        from PIL import Image
        imagen = Image.open(BytesIO(img))
        # preproceso ligero: escala de grises ya la da PyMuPDF; mejora OCR
        partes.append(pytesseract.image_to_string(imagen, lang="spa+eng"))
    return "\n".join(partes)


def leer_pdf(ruta: str) -> dict:
    """Devuelve {'texto','origen','paginas','aviso?'}."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta)

    try:
        texto = pdfminer_extract(ruta) or ""
    except Exception as e:
        texto = ""
        print(f"[pdf_reader] pdfminer falló: {e}")

    paginas = texto.count("\x0c") + 1 if texto else 1

    if _tiene_texto(texto):
        return {"texto": texto, "origen": "texto", "paginas": paginas}

    # PDF escaneado -> OCR
    if tesseract_disponible():
        try:
            texto_ocr = _ocr_con_pymupdf(ruta)
            if _tiene_texto(texto_ocr):
                return {"texto": texto_ocr, "origen": "ocr", "paginas": paginas}
        except Exception as e:
            print(f"[pdf_reader] OCR falló: {e}")

    return {
        "texto": "",
        "origen": "vacio",
        "paginas": paginas,
        "aviso": "PDF sin texto extraíble y Tesseract no disponible. "
                 "Instala Tesseract (ver INSTALAR_TESSERACT.md) o pega el texto manualmente.",
    }
