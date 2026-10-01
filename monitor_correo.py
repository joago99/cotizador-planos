# -*- coding: utf-8 -*-
"""
Monitor de correo (segundo plano).
Revisa IMAP cada INTERVALO_SEG, descarga adjuntos PDF de correos que parezcan
cotizaciones, corre el pipeline y genera un digest diario para Roberto.

Uso:  python monitor_correo.py
      (opcional) python monitor_correo.py --once   # una sola pasada (test)

Requiere config/settings.py con IMAP_HOST/USER/PASS.
"""
import imaplib
import email
import os
import time
import email.utils as eut
from datetime import datetime

from config import settings as S
from src.pipeline import procesar

try:
    import imapclient  # opcional, más simple; si no está usamos imaplib puro
    _USAR_IMAPCLIENT = True
except Exception:
    _USAR_IMAPCLIENT = False


def _descargar_adjuntos(msg, destino_dir):
    """Devuelve lista de rutas a PDF descargados."""
    rutas = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        fn = part.get_filename()
        if not fn:
            continue
        if not fn.lower().endswith(".pdf"):
            continue
        path = os.path.join(destino_dir, fn)
        with open(path, "wb") as f:
            f.write(part.get_payload(decode=True))
        rutas.append(path)
    return rutas


def _es_cotizacion(asunto, cuerpo, remitente):
    texto = f"{asunto} {cuerpo} {remitente}".lower()
    hits = [p for p in S.PALABRAS_COTIZACION if p in texto]
    return len(hits) >= 2, hits


def _cargar_procesados():
    if not os.path.exists(S.PROCESADOS):
        return set()
    with open(S.PROCESADOS, "r", encoding="utf-8") as f:
        return set(l.strip() for l in f if l.strip())


def _marcar_procesado(uid):
    with open(S.PROCESADOS, "a", encoding="utf-8") as f:
        f.write(uid + "\n")


def pasada(reporte=False):
    """Una pasada del buzón. Devuelve lista de resúmenes procesados."""
    resultados = []
    procesados = _cargar_procesados()

    if _USAR_IMAPCLIENT:
        from imapclient import IMAPClient
        with IMAPClient(S.IMAP_HOST, ssl=True) as c:
            c.login(S.IMAP_USER, S.IMAP_PASS)
            c.select_folder(S.IMAP_FOLDER)
            uids = c.search("UNSEEN")
            for uid in uids:
                if str(uid) in procesados:
                    continue
                raw = c.fetch([uid], ["BODY[]"])[uid][b"BODY[]"]
                msg = email.message_from_bytes(raw)
                _procesar_msg(msg, uid, resultados)
    else:
        c = imaplib.IMAP4_SSL(S.IMAP_HOST, S.IMAP_PORT)
        c.login(S.IMAP_USER, S.IMAP_PASS)
        c.select(S.IMAP_FOLDER)
        _, data = c.search(None, "UNSEEN")
        for num in data[0].split():
            if num.decode() in procesados:
                continue
            _, msg_data = c.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            _procesar_msg(msg, num.decode(), resultados)
        c.logout()

    if report and resultados:
        _generar_digest(resultados)
    return resultados


def _procesar_msg(msg, uid, resultados):
    asunto = email.header.make_header(email.header.decode_header(msg["subject"] or ""))
    remitente = msg.get("From", "")
    cuerpo = ""
    if msg.is_multipart():
        for p in msg.walk():
            if p.get_content_type() == "text/plain":
                try:
                    cuerpo += p.get_payload(decode=True).decode("utf-8", "ignore")
                except Exception:
                    pass
    else:
        try:
            cuerpo = msg.get_payload(decode=True).decode("utf-8", "ignore")
        except Exception:
            pass

    es_cot, hits = _es_cotizacion(str(asunto), cuerpo, remitente)
    if not es_cot:
        return

    adjuntos = _descargar_adjuntos(msg, S.INBOX_DIR)
    if not adjuntos:
        return

    for pdf in adjuntos:
        out = procesar(pdf, cliente=str(asunto))
        resultados.append({"asunto": str(asunto), "resumen": out["resumen"]})
        _marcar_procesado(uid)


def _generar_digest(resultados):
    hoy = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(S.DIGEST_DIR, f"digest_{hoy}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"DIGEST DE COTIZACIONES — {hoy}\n")
        f.write("=" * 60 + "\n\n")
        for r in resultados:
            f.write(f"• {r['asunto']}\n")
            f.write(r["resumen"])
            f.write("\n\n" + "-" * 60 + "\n\n")
    print(f"[digest] generado {path} con {len(resultados)} cotización(es)")


def loop():
    print(f"[monitor] iniciado. Revisando cada {S.INTERVALO_SEG}s. Ctrl+C para salir.")
    while True:
        try:
            res = pasada(reporte=True)
            if res:
                print(f"[{datetime.now():%H:%M:%S}] {len(res)} cotización(es) procesada(s)")
        except Exception as e:
            print(f"[monitor] error: {e}")
        time.sleep(S.INTERVALO_SEG)


if __name__ == "__main__":
    import sys
    if "--once" in sys.argv:
        r = pasada(reporte=True)
        print(f"Pasada única: {len(r)} cotización(es) encontrada(s)")
    else:
        loop()
