# -*- coding: utf-8 -*-
"""Pipeline principal: archivo (PDF/DXF) -> extracción -> recomendación -> resumen + log CSV."""
import csv
import os
import datetime as dt

import config.entorno  # configura Tesseract/OCR al importar

from src.pdf_reader import leer_pdf
from src.lector_dxf import leer_dxf
from src.extractor import extraer
from src.recomendador import recomendar
from src.resumen import armar_resumen
from src.borrador_respuesta import generar_borrador

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cotizaciones_log.csv")


def procesar(ruta: str, nombre_cliente: str = "") -> dict:
    if ruta.lower().endswith(".dxf"):
        lectura = leer_dxf(ruta)
        lectura["paginas"] = lectura.get("entidades", 1)
        # detección de shafts (huecos de elevador/núcleo) en el plano
        from src.detectar_shafts import detectar_shafts
        shafts = detectar_shafts(ruta)
    else:
        lectura = leer_pdf(ruta)
        shafts = []

    extraccion = extraer(lectura["texto"])
    # si el detector geométrico encontró shaft, marcarlo en la extracción
    if shafts:
        extraccion["shaft"]["encontrado"] = True
        extraccion["shaft"]["ubicacion"] = shafts[0]
    recomendacion = recomendar(extraccion)
    resumen = armar_resumen(extraccion, recomendacion)
    borrador = generar_borrador(extraccion, recomendacion)

    _registrar_log(ruta, nombre_cliente, lectura["origen"], extraccion, recomendacion)

    return {
        "origen_texto": lectura["origen"],
        "paginas": lectura["paginas"],
        "extraccion": extraccion,
        "shafts": shafts,
        "recomendacion": recomendacion,
        "resumen": resumen,
        "borrador_respuesta": borrador,
        "aviso": lectura.get("aviso"),
    }


def _registrar_log(ruta, cliente, origen, extrac, recom):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    fila = {
        "fecha": dt.datetime.now().isoformat(timespec="seconds"),
        "archivo": os.path.basename(ruta),
        "cliente": cliente,
        "origen": origen,
        "m2": max([x["valor"] for x in extrac["metros_cuadrados"]], default=""),
        "altura_m": max([x["valor"] for x in extrac["altura_m"]], default=""),
        "shaft": "si" if extrac["shaft"]["encontrado"] else "no",
        "equipo_principal": recom["recomendacion_principal"]["equipo"],
    }
    campos = list(fila.keys())
    existe = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            w.writeheader()
        w.writerow(fila)
