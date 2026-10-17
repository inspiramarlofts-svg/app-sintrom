# MiPauta

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
