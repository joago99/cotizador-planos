# -*- coding: utf-8 -*-
"""
Agente 3: INTEGRADOR CORREO -> WHATSAPP
---------------------------------------
Monitor de correo que, al encontrar cotizaciones nuevas, las procesa y
envía un AVISO por WhatsApp a Roberto (o al número que configure).

Canal WhatsApp (plugable, por env vars):
  - Twilio: BHC_TWILIO_SID, BHC_TWILIO_TOKEN, BHC_WHATSAPP_FROM, BHC_WHATSAPP_TO
  - Fallback local (test): escribe el mensaje a data/whatsapp_outbox.txt y lo
    imprime, para validar sin credenciales.

Uso:
  python agente_mail_whatsapp.py          # loop infinito (revisa cada INTERVALO)
  python agente_mail_whatsapp.py --once   # una pasada (test)
"""
import os
import sys
import time
from datetime import datetime

from config import settings as S
from src.pipeline import procesar
import monitor_correo as mc  # reutiliza la lógica IMAP ya hecha


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTBOX = os.path.join(BASE, "data", "whatsapp_outbox.txt")

TWILIO_SID = os.environ.get("BHC_TWILIO_SID", "")
TWILIO_TOKEN = os.environ.get("BHC_TWILIO_TOKEN", "")
WA_FROM = os.environ.get("BHC_WHATSAPP_FROM", "")   # ej: whatsapp:+14155238886
WA_TO = os.environ.get("BHC_WHATSAPP_TO", "")        # ej: whatsapp:+569...


def _mensaje(asunto, resumen):
    lineas = [
        "🏗️ *Nueva cotización de obra*",
        f"_{asunto}_",
        "",
        "Resumen rápido:",
    ]
    for ln in resumen.splitlines():
        if any(k in ln for k in ("Superficie", "Perímetro", "Altura", "Shaft", "Principal")):
            lineas.append(ln.strip())
    lineas.append("")
    lineas.append("Revisa el detalle en el digest del día.")
    return "\n".join(lineas)


def enviar_whatsapp(mensaje):
    if TWILIO_SID and TWILIO_TOKEN and WA_FROM and WA_TO:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            client.messages.create(
                from_=WA_FROM, to=WA_TO, body=mensaje
            )
            return "enviado_twilio"
        except Exception as e:
            return f"error_twilio: {e}"
    # Fallback: outbox local
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}]\n{mensaje}\n{'-'*40}\n")
    return "outbox_local (sin Twilio configurado)"


def procesar_y_avisar():
    resultados = mc.pasada(reporte=True)
    estados = []
    for r in resultados:
        msg = _mensaje(r["asunto"], r["resumen"])
        est = enviar_whatsapp(msg)
        estados.append((r["asunto"], est))
    return estados


def loop():
    print(f"[mail->WA] monitor activo. Intervalo {S.INTERVALO_SEG}s. Ctrl+C para salir.")
    while True:
        try:
            estados = procesar_y_avisar()
            for asunto, est in estados:
                print(f"[{datetime.now():%H:%M:%S}] {asunto} -> WA: {est}")
        except Exception as e:
            print(f"[mail->WA] error: {e}")
        time.sleep(S.INTERVALO_SEG)


if __name__ == "__main__":
    if "--once" in sys.argv:
        for a, e in procesar_y_avisar():
            print(f"{a} -> {e}")
    else:
        loop()
