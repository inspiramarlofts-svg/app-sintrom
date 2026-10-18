# PautApp

Recordatorio diario del Sintrom que enseña, cada día, el recorte de la hoja de pauta original del hospital.

- `src/app.html`: la app (la misma página que se publica como artefacto web).
- `scripts/build-www.mjs`: prepara `www/` para la app instalada (pdf.js y la letra en local).
- `android/`: proyecto Android de Capacitor. Avisos con `@capacitor/local-notifications`.
- Cada cambio en `main` genera el APK en GitHub Actions y lo publica en la versión "ultima".

Esta app es solo un recordatorio. Ante cualquier duda, sigue la pauta de tu médico.

## Textos legales

- [Aviso legal y condiciones de uso](legal/aviso-legal.md)
- [Política de privacidad](legal/privacidad.md) (enlace para Google Play)

Los datos del titular se rellenan en `TITULAR` dentro de `src/app.html` y en estos dos archivos.

## Farmacia patrocinadora

Para la versión de una farmacia, copia `farmacia.ejemplo.json` como `farmacia.json` y rellena sus datos (el logo puede ser una imagen en `data:`). Sin `farmacia.json` la app solo muestra los botones de la farmacia más cercana y la de guardia.

## Idiomas

La app está en castellano, català, valencià, galego y euskara. El texto de `src/app.html` en castellano es la clave; las traducciones están en `i18n/ui.py` (interfaz) y `i18n/legal_*.html` (aviso legal y privacidad). El valenciano se obtiene del catalán con las formas de `VALENCIA`. Tras cambiarlas: `python3 i18n/build.py src/app.html`.
