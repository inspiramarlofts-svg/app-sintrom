# Servidor de l'avís a la família

Fa que, si la persona no confirma una presa, li arribi un avís al mòbil del fill o la filla. És opcional: sense aquest servidor, l'app funciona igual i el botó «Avisar a la meva família» diu que encara no està activat.

- `functions/api.js`: les rutes (`crear`, `codi`, `sync`, `treure`, `esborrar`, `unir`, `token`, `estat`, `sortir`).
- `functions/index.js`: el mateix a Firebase (Cloud Functions a `europe-west1`, Firestore tancat als mòbils) i la revisió cada 5 minuts que envia els avisos.
- `functions/local.js`: servidor de prova a `http://localhost:8790`, sense Firebase. `npm test` prova les regles.

Què es guarda: el nom amb què es veu la persona, l'hora de cada presa, el nom de la medicina i si s'ha confirmat; de cada familiar, el seu nom i l'identificador del mòbil. Mai la foto ni les dosis.

## Posar-lo en marxa (una vegada)

1. Crear un projecte a https://console.firebase.google.com (pla Blaze; l'ús normal entra a la quota gratuïta) i una base de dades Firestore a Europa.
2. Afegir-hi una app Android amb el nom de paquet `es.inspiramar.mipauta` i baixar `google-services.json`.
3. Al repositori de GitHub, a Settings → Secrets and variables → Actions:
   - secret `GOOGLE_SERVICES_JSON` amb el contingut de `google-services.json`;
   - variable `FAMILIA_API_URL` amb `https://europe-west1-<projecte>.cloudfunctions.net/api`.
4. Publicar el servidor: des d'aquesta carpeta, `npx firebase-tools deploy --only functions,firestore`.
