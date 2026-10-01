# -*- coding: utf-8 -*-
"""
Verifica que Tesseract + OCR funcione con un PDF escaneado de prueba.
Genera data/prueba_escaneada.pdf (imagen con texto) y corre el pipeline.

Uso: python verificar_ocr.py
"""
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(BASE, "data", "prueba_escaneada.pdf")


def generar_pdf_escaneado():
    """Crea un PDF que es UNA IMAGEN (sin texto seleccionable)."""
    ancho, alto = 800, 1000
    img = Image.new("RGB", (ancho, alto), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    texto = [
        "COTIZACION DE OBRA - BODEGA LOGISTICA",
        "",
        "Superficie a hormigonar: 4.200,00 m2 en 1 piso.",
        "Perimetro del area de vertido: 320 metros de contorno.",
        "Altura de la estructura: 12 metros de altura.",
        "",
        "El montacarga se ubica en esquina norte, sobre losa de 25 cm.",
        "Acceso de camiones por porton principal 8 m.",
    ]
    y = 60
    for ln in texto:
        d.text((60, y), ln, fill="black", font=font)
        y += 50
    # embeber la imagen como página (sin capa de texto)
    doc = fitz.open()
    pag = doc.new_page(width=ancho, height=alto)
    buf = BytesIO()
    img.save(buf, format="PNG")
    pag.insert_image(fitz.Rect(0, 0, ancho, alto), stream=buf.getvalue())
    doc.save(SALIDA)
    doc.close()


def main():
    from src.pdf_reader import tesseract_disponible, leer_pdf
    from src.extractor import extraer

    print("Verificando Tesseract...")
    if not tesseract_disponible():
        print("  [FALTA] Tesseract no está instalado o no está en PATH.")
        print("  Sigue las instrucciones en INSTALAR_TESSERACT.md")
        return
    print("  [OK] Tesseract disponible.")

    print("Generando PDF escaneado de prueba...")
    generar_pdf_escaneado()
    print(f"  -> {SALIDA}")

    print("Leyendo con OCR...")
    lectura = leer_pdf(SALIDA)
    print(f"  Origen: {lectura['origen']}")
    if lectura["origen"] == "ocr":
        ext = extraer(lectura["texto"])
        print("  Campos detectados:")
        print(f"    m2: {[x['valor'] for x in ext['metros_cuadrados']]}")
        print(f"    perímetro: {[x['valor'] for x in ext['perimetro_m']]}")
        print(f"    altura: {[x['valor'] for x in ext['altura_m']]}")
        print("  [OK] OCR funcionando end-to-end.")
    else:
        print("  [AVISO]", lectura.get("aviso", "No se extrajo texto."))


if __name__ == "__main__":
    main()
