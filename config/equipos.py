# -*- coding: utf-8 -*-
"""
Catálogo de equipos de Bombas de Hormigón Chile.
Datos de alcance extraídos de https://bombasdehormigonchile.com (agosto 2026).
Las DIMENSIONES FÍSICAS (largo/ancho/alto/peso/radio de giro) NO están en el
sitio web: se marcan como "por_confirmar" y deben llenarse desde el brochure
del fabricante o lo que Roberto dicte. NO se inventan cifras.
"""

EQUIPOS = [
    {
        "id": "tdh",
        "nombre": "Torre Distribuidora de Hormigón (TDH / Placing Boom)",
        "tipo": "fijo_interior_exterior",
        "alcance_horizontal_m": (24, 32),
        "alcance_vertical_m": None,        # no publicado
        "notas": "Se monta interior o exterior de edificio. Alta eficiencia y autonomía.",
        "dimensiones_fisicas": {
            "largo_m": None, "ancho_m": None, "alto_m": None,
            "peso_kg": None, "radio_giro_m": None,
            "estado": "por_confirmar"
        },
    },
    {
        "id": "bdp",
        "nombre": "Brazo Distribuidor Portátil (BDP)",
        "tipo": "fijo_movil_planta",
        "alcance_horizontal_m": (13, 15),
        "alcance_vertical_m": None,
        "notas": "Independencia del uso de capachos o grúa. Se mueve dentro de la planta.",
        "dimensiones_fisicas": {
            "largo_m": None, "ancho_m": None, "alto_m": None,
            "peso_kg": None, "radio_giro_m": None,
            "estado": "por_confirmar"
        },
    },
    {
        "id": "autobomba",
        "nombre": "Camión Telescópico / Autobomba (bomba pluma)",
        "tipo": "spot_camion",
        "alcance_horizontal_m": (28, 36),
        "alcance_vertical_m": (28, 36),
        "notas": "Fácil y rápida instalación en obra. Versátil para inicios de obra.",
        "dimensiones_fisicas": {
            "largo_m": None, "ancho_m": None, "alto_m": None,
            "peso_kg": None, "radio_giro_m": None,
            "estado": "por_confirmar"
        },
    },
    {
        "id": "estacionaria",
        "nombre": "Bomba de Hormigón Estacionaria",
        "tipo": "fijo_tuberia",
        "alcance_horizontal_m": None,      # depende de rendimiento/altura/distancia
        "alcance_vertical_m": None,
        "notas": "El tipo de bomba depende de rendimientos, alturas y distancias horizontales.",
        "dimensiones_fisicas": {
            "largo_m": None, "ancho_m": None, "alto_m": None,
            "peso_kg": None, "radio_giro_m": None,
            "estado": "por_confirmar"
        },
    },
    {
        "id": "bombeo_tecnico",
        "nombre": "Bombeo Técnico (larga distancia)",
        "tipo": "fijo_tuberia_larga",
        "alcance_horizontal_m": (0, 2000),
        "alcance_vertical_m": None,
        "notas": "Alcance de hasta 2000 m de distancia horizontal con bombas de gran potencia.",
        "dimensiones_fisicas": {
            "largo_m": None, "ancho_m": None, "alto_m": None,
            "peso_kg": None, "radio_giro_m": None,
            "estado": "por_confirmar"
        },
    },
]

# Servicios relevantes para la recomendación
SERVICIOS = {
    "bombeo_fijo": "Instalación con tubería, TDH o BDP en obra fija.",
    "bombeo_spot": "Camión telescópico (28-36 m) o autobomba, sin equipo fijo.",
    "bombeo_tecnico": "Hasta 2000 m horizontales con bombas de gran potencia.",
    "arriendo": "Opción de arriendo de equipos si ya tienen logística.",
}

CONTACTO = {
    "empresa": "Bombas de Hormigón Chile (SDB)",
    "web": "https://bombasdehormigonchile.com",
    "mail": "contacto@bombasdb.cl",
    "telefono": "+569 7791 0410",
    "direccion": "Av. Américo Vespucio 1640, Quilicura",
}
