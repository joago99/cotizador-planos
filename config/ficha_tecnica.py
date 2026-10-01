# -*- coding: utf-8 -*-
"""
ARCHIVO TÉCNICO DE DIMENSIONES FÍSICAS DE EQUIPOS
=================================================
DATOS REALES extraídos de las fichas técnicas de Bombas de Hormigón Chile
(archivos L1-*.pdf y la tabla web de TDH). Todos los datos acá marcados
"catalogo_roberto" provienen de documentos de la propia empresa.

Fichas fuente en el proyecto:
  data/specs_maquinas/L1-TRUEMAX28.pdf  -> TRUEMAX HG28  (TDH 28m)
  data/specs_maquinas/L1-TRUEMAX32.pdf  -> TRUEMAX HG32  (TDH 32m)
  data/specs_maquinas/L1-HG13.pdf       -> HG13 (BDP, brazo portátil)
  web bombeo: TDH Putzmeister/Truemax/DKTec

CAMPOS:
  peso_kg / desglose     : peso del equipo (kg)
  alcance_horizontal_m   : (min, max) alcance de pluma (m)
  angulo_giro            : grados
  diametro_tuberia_mm    : Ø tubería (mm)
  potencia_kw            : potencia motor (kW)
  estado                 : "catalogo_roberto" | "referencia_mercado" | "por_confirmar"
"""
from datetime import datetime

FICHA_TECNICA = {
    "tdh": {
        "nombre": "Torre Distribuidora de Hormigón (TDH / Placing Boom)",
        "modelos": [
            {
                "marca": "PUTZMEISTER", "modelo": "MXR 24/28 Z",
                "alcance_horizontal_m": (24, 28), "potencia_kw": 15,
                "angulo_giro": 365, "peso_pluma_kg": 4400,
                "peso_tornamesa_kg": 2700, "peso_torre_kg": "4X2000",
                "estado": "catalogo_roberto", "fuente": "web TDH bombasdb",
            },
            {
                "marca": "PUTZMEISTER", "modelo": "MXR 32/36 Z",
                "alcance_horizontal_m": (32, 36), "potencia_kw": 15,
                "angulo_giro": 365, "peso_pluma_kg": 6200,
                "peso_tornamesa_kg": 2700, "peso_torre_kg": "4X2000",
                "estado": "catalogo_roberto", "fuente": "web TDH bombasdb",
            },
            {
                "marca": "TRUEMAX", "modelo": "HG28M",
                "alcance_horizontal_m": (27.7, 28), "potencia_kw": 11,
                "angulo_giro": 360, "diametro_tuberia_mm": 133,
                "peso_pluma_kg": 3300, "peso_tornamesa_kg": 3800,
                "peso_columna_kg": "2000x4", "largo_max_columna_m": 5,
                "estado": "catalogo_roberto", "fuente": "L1-TRUEMAX28.pdf",
            },
            {
                "marca": "TRUEMAX", "modelo": "HG32M",
                "alcance_horizontal_m": (31.7, 32), "potencia_kw": 15,
                "angulo_giro": 360, "diametro_tuberia_mm": 134,
                "peso_pluma_kg": 4000, "peso_tornamesa_kg": 4000,
                "peso_columna_kg": "2000x4", "peso_contrapesos_kg": 2000,
                "estado": "catalogo_roberto", "fuente": "L1-TRUEMAX32.pdf",
            },
            {
                "marca": "DKTEC", "modelo": "HG28",
                "alcance_horizontal_m": (28, 28), "potencia_kw": 11,
                "angulo_giro": 360, "peso_pluma_kg": 3000,
                "peso_tornamesa_kg": 3400, "peso_torre_kg": "4X2000",
                "estado": "catalogo_roberto", "fuente": "web TDH bombasdb",
            },
        ],
        "resumen": {
            "alcance_horizontal_m": (24, 36),
            "peso_pluma_kg_rango": (3000, 6200),
            "peso_tornamesa_kg_rango": (2700, 4000),
            "peso_torre_kg_por_modulo": 2000,
            "angulo_giro": "360°-365°",
            "estado": "catalogo_roberto",
        },
    },

    "bdp": {
        "nombre": "Brazo Distribuidor Portátil (BDP)",
        "modelos": [
            {
                "marca": "TRUEMAX", "modelo": "HG13",
                "alcance_horizontal_m": (14, 16), "potencia_kw": 4,
                "revoluciones_rpm": 1440, "angulo_giro": 360,
                "diametro_tuberia_mm": 125,
                "peso_total_kg": (2700, 4500),  # sin / con contrapeso
                "estado": "catalogo_roberto", "fuente": "L1-HG13.pdf",
                "nota": "Datos reales de la ficha HG13 de Bombas de Hormigón Chile.",
            },
        ],
        "resumen": {
            "alcance_horizontal_m": (14, 16),
            "peso_total_kg_rango": (2700, 4500),
            "angulo_giro": 360,
            "estado": "catalogo_roberto",
        },
    },

    "autobomba": {
        "nombre": "Camión Telescópico / Autobomba (bomba pluma)",
        "alcance_horizontal_m": (28, 36),
        "alcance_vertical_m": (28, 36),
        # Referencia de mercado para autobomba 36 m típica (por confirmar chasis)
        "largo_m": 11.10, "ancho_m": 2.50, "alto_m": 4.04,
        "estado": "referencia_mercado",
        "fuente": "Putzmeister BSF 36-4 brochure (referencia)",
        "nota": "Roberto debe confirmar modelo/chasis exacto de su autobomba.",
    },

    "estacionaria": {
        "nombre": "Bomba de Hormigón Estacionaria (bomba de línea / trailer)",
        "alcance_horizontal_m": None,
        "largo_m_rango": (4.5, 6.3), "ancho_m_rango": (1.75, 2.10),
        "alto_m_rango": (1.6, 2.35), "peso_kg_rango": (3200, 6900),
        "estado": "referencia_mercado",
        "fuente": "AIMIX/Luton concrete line pump specs (referencia)",
        "nota": "La web de Roberto no lista modelo de estacionaria. Cifras de "
                "bombas de línea estándar de 30-90 m3/h.",
    },

    "bombeo_tecnico": {
        "nombre": "Bombeo Técnico (larga distancia, hasta 2000 m)",
        "alcance_horizontal_m": (0, 2000),
        "dimensiones_fisicas": "según bomba estacionaria + línea de tubería",
        "estado": "catalogo_roberto",
        "fuente": "bombasdehormigonchile.com servicios",
        "nota": "No aplica dimensiones de pluma; es bombeo por tubería.",
    },
}

GENERADO = datetime.now().strftime("%Y-%m-%d")


def resumen_corto():
    """Devuelve un dict ligero para mostrar en la app/resumen."""
    out = {}
    for k, v in FICHA_TECNICA.items():
        if "modelos" in v:
            out[k] = {
                "nombre": v["nombre"],
                "alcance_horizontal_m": v["resumen"]["alcance_horizontal_m"],
                "estado": v["resumen"]["estado"],
            }
        else:
            out[k] = {
                "nombre": v["nombre"],
                "alcance_horizontal_m": v.get("alcance_horizontal_m"),
                "estado": v.get("estado"),
                "nota": v.get("nota"),
            }
    return out
