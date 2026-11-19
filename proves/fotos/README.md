# Prova de pujada de fotos de la pauta (200 usuaris ficticis)

Tot és inventat: noms, dates i dosis. Cap dada real de pacients.

1. `python3 genera.py DIR 200`: 200 fulls sintètics (format GVA, Galícia i Aragó) i una foto degradada de cadascun
   (neta, sobre la taula, doblegada, arrugada, fosca, molt fosca, desenfocada, moguda, girada, de costat, perspectiva,
   reflex, ombra, tallada, baixa qualitat, combinada). `DIR/usuaris.json` guarda la veritat de cada full.
2. `python3 ocr.py DIR 4`: llegeix el text de cada foto (RapidOCR) i el desa amb la mateixa forma que ML Kit al mòbil.
   Per a les fotos de costat: `python3 girs.py DIR u010 ...`, passar `ocr.py` sobre les còpies girades i deixar els
   `uXXX.gNN.ocr.json` a `DIR`.
3. `PW=$(npm root -g)/playwright node executa.mjs src/app.html DIR res.json`: cada usuari obri l'app de veritat
   (Chromium, com l'app instal·lada), puja la foto, diu "Sí, coincide" a cada dia, tanca i torna a obrir l'app.
   `FILL=4700000` omple abans el mòbil per provar què passa quan no queda espai.
4. `python3 avalua.py DIR res.json`: per tipus de foto, quantes pautes són perfectes, incompletes, rebutjades (amb
   missatge per repetir la foto) o amb PERILL (un dia que no és de la pauta, o un retall que no és la casella del dia).

Dependències: `pip install rapidocr_onnxruntime opencv-python-headless pillow numpy` i Playwright.
