# -*- coding: utf-8 -*-
"""
Orquestador: corre los 3 agentes en secuencia y reporta.
  python orquestador.py          -> planos + eficiencia + estado mail/WA
  python orquestador.py --planos -> solo regenera planos de prueba
  python orquestador.py --efi    -> solo informe de eficiencia
"""
import sys
import subprocess

def run(modulo):
    print(f"\n>>> Ejecutando {modulo}")
    r = subprocess.run([sys.executable, "-m", modulo])
    return r.returncode == 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--planos" in args:
        run("src.agente_planos")
    elif "--efi" in args:
        run("src.agente_eficiencia")
    else:
        ok1 = run("src.agente_planos")
        ok2 = run("src.agente_eficiencia")
        print("\n=== RESUMEN ===")
        print(f"Planos     : {'OK' if ok1 else 'FALLO'}")
        print(f"Eficiencia : {'OK' if ok2 else 'FALLO'}")
        print("Mail->WA   : ver agente_mail_whatsapp.py (requiere config/settings.py)")
