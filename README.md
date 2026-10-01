# Cotizador de Planos — Bombas de Hormigón

**ES** · **EN** (bilingüe / bilingual)

Cotizador automático que lee un plano de obra (CAD o PDF), extrae los datos del edificio (pisos, altura, superficie, ubicación de shaft) y recomienda el equipo de bombeo de hormigón adecuado, generando una propuesta lista para enviar.

Automated quoting tool that reads a construction plan (CAD or PDF), extracts building data (floors, height, area, shaft location) and recommends the right concrete pump, generating a ready-to-send proposal.

---

## Qué resuelve · What it solves

Un ingeniero o vendedor de bombas de hormigón recibe planos en formatos distintos (DWG, DXF, PDF escaneado) y debe responder con una propuesta técnica. Este pipeline automatiza el camino **plano → datos → recomendación → propuesta**, dejando siempre el fragmento original para verificación humana.

A concrete-pump engineer or salesperson receives plans in different formats (DWG, DXF, scanned PDF) and must reply with a technical proposal. This pipeline automates the path **plan → data → recommendation → proposal**, always keeping the original fragment for human verification.

## Pipeline

```
DWG ──(conversor_dwg)──▶ DXF ──(lector_dxf)──▶ texto
PDF (escaneado) ──(pdf_reader + OCR Tesseract)──▶ texto
                                      │
                                      ▼
                              (extractor) campos clave
                              m², perímetro, altura, pisos, shaft, equipo
                                      │
                                      ▼
                              (recomendador) TDH / BDP / autobomba
                                      │
                                      ▼
                              (borrador_respuesta) propuesta + (resumen)
```

## Qué extrae · What it extracts

- **Superficie** (m²), **perímetro**, **altura** (m) y **pisos**
- **Shaft / elevador / núcleo** — donde se monta la máquina
- **Equipos**: TDH (torre), BDP (brazo portátil), autobomba/pluma, estacionaria
- **Nomenclatura de propuestas**: "4BDP", "PLANTA+4BDP", "TDH28/32m", "Alcance 28m"
- **Opciones** (OPCIÓN 1 / 2) y nombre de proyecto

## Cómo correr · How to run

```bash
# 1. Dependencias
pip install -r requirements.txt

# 2. App web local (arrastra un PDF y lee la ficha al instante)
python app.py          # → http://127.0.0.1:5000

# 3. O por línea de comandos, procesa un DXF/PDF directamente
python -m src.pipeline samples/plano_ejemplo.dxf
```

### Dependencias externas (no pip) · External dependencies (non-pip)

- **Tesseract OCR** (para PDFs escaneados): `winget install UB-Mannheim.TesseractOCR -e` + idioma español. Ver `INSTALAR_TESSERACT.md`.
- **DWG→DXF**: usa [LibreDWG](https://www.gnu.org/software/libredwg/) (`dwg2dxf.exe`) o AutoCAD. Si ya tienes un DXF, omite este paso.

## Estructura · Structure

| Carpeta · Folder | Contenido · Contents |
|---|---|
| `src/` | Pipeline: conversión, lectura DXF/PDF, extracción, recomendación, propuesta |
| `config/` | Equipos, ficha técnica y configuración de entorno |
| `samples/` | Plano DXF de ejemplo (ilustrativo) |
| `app.py` | App web Flask para demo interactiva |
| `orquestador.py` | Corre los agentes en secuencia |

## Estado · Status

Funcional para el dominio de bombas de hormigón (Chile). El vocabulario de extracción está calibrado para planos y propuestas reales. / Working for the concrete-pump domain (Chile). Extraction vocabulary calibrated on real plans and proposals.

## Stack

Python · Flask · ezdxf · Tesseract OCR · PyMuPDF (fitz) · matplotlib · shapely
