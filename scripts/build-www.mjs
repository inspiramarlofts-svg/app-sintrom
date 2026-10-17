// Builds www/ for the installed app from the same page that is published as the web artifact.
// The page is a body fragment, so it gets a full document; CDN scripts and fonts become local files.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from 'node:fs';

const out = 'www';
mkdirSync(`${out}/lib`, { recursive: true });
mkdirSync(`${out}/fonts`, { recursive: true });

let html = readFileSync('src/app.html', 'utf8');
const cdn = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/';
html = html.split(cdn).join('lib/');
html = html.replace(/<link rel="preconnect"[^>]*>\n?/, '');
html = html.replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^>]*>/,
  `<style>
@font-face{font-family:'Atkinson Hyperlegible';font-weight:400;src:url(fonts/atkinson-400.woff2) format('woff2')}
@font-face{font-family:'Atkinson Hyperlegible';font-weight:700;src:url(fonts/atkinson-700.woff2) format('woff2')}
</style>`);
if (html.includes('https://cdnjs') || html.includes('fonts.googleapis')) throw new Error('remote asset left in page');

const doc = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
</head>
<body>
${html}
</body>
</html>
`;
writeFileSync(`${out}/index.html`, doc);

const pdf = 'node_modules/pdfjs-dist/build/';
copyFileSync(pdf + 'pdf.min.js', `${out}/lib/pdf.min.js`);
copyFileSync(pdf + 'pdf.worker.min.js', `${out}/lib/pdf.worker.min.js`);
const font = 'node_modules/@fontsource/atkinson-hyperlegible/files/atkinson-hyperlegible-latin-';
copyFileSync(font + '400-normal.woff2', `${out}/fonts/atkinson-400.woff2`);
copyFileSync(font + '700-normal.woff2', `${out}/fonts/atkinson-700.woff2`);
console.log('www/ ready');
