# -*- coding: utf-8 -*-
"""
App web local (Flask) para Roberto: arrastra el PDF y lee la ficha al instante.
Uso:  python app.py   ->  abrir http://127.0.0.1:5000
"""
import os
import tempfile
from flask import Flask, request, render_template_string, send_file
from werkzeug.utils import secure_filename

from src.pipeline import procesar

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))

HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Cotizador Bombas de Hormigón</title>
<style>
 body{font-family:Segoe UI,Roboto,sans-serif;margin:0;background:#0f172a;color:#e2e8f0}
 header{background:#ea7317;color:#1a1206;padding:14px 20px;font-weight:700;font-size:20px}
 .wrap{max-width:980px;margin:24px auto;padding:0 16px}
 .drop{border:2px dashed #ea7317;border-radius:10px;padding:30px;text-align:center;background:#1a1206}
 input[type=text]{padding:8px;width:240px;border-radius:6px;border:1px solid #444;background:#0f172a;color:#e2e8f0;margin-right:8px}
 button{background:#ea7317;color:#1a1206;border:0;padding:10px 16px;border-radius:6px;font-weight:700;cursor:pointer}
 pre{background:#1a1206;border:1px solid #333;border-radius:8px;padding:16px;white-space:pre-wrap;font-size:13px;line-height:1.5;overflow-x:auto}
 .aviso{background:#422006;color:#fbbf24;padding:10px;border-radius:6px;margin-top:12px}
</style>
</head>
<body>
<header>🏗️ Cotizador Bombas de Hormigón Chile</header>
<div class="wrap">
  <form method="post" enctype="multipart/form-data" class="drop">
    <p>Arrastra o selecciona la cotización en PDF</p>
    <input type="file" name="pdf" accept="application/pdf" required>
    <p>Cliente (opcional): <input type="text" name="cliente" placeholder="Nombre obra/cliente"></p>
    <button type="submit">Analizar cotización</button>
  </form>
  {% if resumen %}
    <h3>Resultado</h3>
    <pre>{{ resumen }}</pre>
    {% if aviso %}<div class="aviso">{{ aviso }}</div>{% endif %}
  {% endif %}
</div>
</body>
</html>"""


@app.route("/", methods=["GET", "POST"])
def index():
    resumen = None
    aviso = None
    if request.method == "POST":
        f = request.files.get("pdf")
        cliente = request.form.get("cliente", "")
        if f and f.filename.lower().endswith(".pdf"):
            tmp = os.path.join(tempfile.gettempdir(), secure_filename(f.filename))
            f.save(tmp)
            out = procesar(tmp, cliente)
            resumen = out["resumen"]
            aviso = out.get("aviso")
    return render_template_string(HTML, resumen=resumen, aviso=aviso)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
