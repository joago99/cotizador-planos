# Instalación de Tesseract (OCR para PDFs/DXF escaneados)

Roberto necesita esto solo si recibe planos/cotizaciones como **imagen**
(PDF escaneado o sin texto seleccionable). Si el PDF ya tiene texto, el
sistema lo lee sin Tesseract.

## Descarga oficial (Windows)
El binario de Tesseract para Windows lo mantiene la Universidad de Mannheim:
**https://github.com/UB-Mannheim/tesseract/wiki**
-> `tesseract-ocr-w64-setup-5.x.x.exe`

(El repo principal github.com/tesseract-ocr/tesseract es solo el código
fuente; el instalador de Windows está en el link de arriba.)

## Pasos
1. Descargar el instalador y ejecutarlo.
2. En el asistente:
   - Marcar **"Add Tesseract to PATH"** (importantísimo).
   - En "Additional language data" seleccionar **Spanish** (y English).
3. Abrir cmd y verificar:
   ```
   tesseract --version
   ```
4. Probar el sistema:
   ```
   python verificar_ocr.py
   ```

## Notas
- Queda en `C:\Program Files\Tesseract-OCR\`.
- La terminal donde corras el cotizador debe abrirse DESPUÉS de instalar.
- Spanish debe estar en `C:\Program Files\Tesseract-OCR\tessdata\spa.traineddata`.
- Si el sitio de Mannheim no carga, espejo en SourceForge:
  https://sourceforge.net/projects/tesseract-ocr.mirror/
