// Runs each fictitious user through the real app page (src/app.html) in Chromium, as the installed app:
// "Hacer foto" -> on-device text recognition (precomputed, same shape as ML Kit) -> app reads the days ->
// the user says "Sí, coincide" for every day -> the app is closed and opened again -> what was saved is read back.
// usage: node executa.mjs <app.html> <dir with uXXX.jpg, uXXX.ocr.json, usuaris.json> <out.json> [from] [to]
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)(process.env.PW || 'playwright');
import { readFileSync, writeFileSync } from 'node:fs';

const [, , appPath, dir, outPath, from = '0', to = '9999'] = process.argv;
const KEY = 'mi-sintrom-v1';
let body = readFileSync(appPath, 'utf8');
const html = body.startsWith('<!doctype') ? body : '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + body + '</body></html>';
const users = JSON.parse(readFileSync(dir + '/usuaris.json', 'utf8')).slice(+from, +to);

const mock = ({ ocr, ocrGir, KEY, hoy, fill }) => {
  const any = (o) => new Proxy(o, { get: (t, k) => (k in t ? t[k] : k === 'then' ? undefined : async () => ({})) });
  window.Capacitor = {
    isNativePlatform: () => true, getPlatform: () => 'android',
    convertFileSrc: () => 'http://pautapp.test/foto.jpg',
    Plugins: {
      TextRecognition: { processImage: async ({ path }) => { const g = (path.match(/-g(\d+)\.jpg$/) || [])[1]; window.__gir = g ? +g : 0; return g ? (ocrGir[g] || { text: '', blocks: [] }) : ocr; } },
      Filesystem: { writeFile: async ({ path }) => ({ uri: 'file:///cache/' + path }) },
      LocalNotifications: any({ checkPermissions: async () => ({ display: 'granted' }), requestPermissions: async () => ({ display: 'granted' }), getPending: async () => ({ notifications: [] }) }),
      App: any({ addListener: async () => ({ remove() {} }) })
    }
  };
  if (!localStorage.getItem(KEY)) localStorage.setItem(KEY, JSON.stringify(Object.assign({ legal: { version: 3, fecha: hoy + 'T09:00:00.000Z' }, rol: 'yo' }, fill ? { medicinas: [{ id: 'm1', nombre: 'Omeprazol', cantidad: '1', horas: ['08:00'], foto: 'data:image/jpeg;base64,' + 'A'.repeat(fill) }] } : {})));
};

const browser = await chromium.launch();
const results = [];
for (const u of users) {
  const r = { id: u.id };
  const ctx = await browser.newContext({ viewport: { width: 412, height: 860 } });
  try {
    await ctx.clock.setFixedTime(new Date(u.hoy + 'T10:00:00'));
    const ocr = JSON.parse(readFileSync(`${dir}/${u.id}.ocr.json`, 'utf8'));
    await ctx.route('**/*', (route) => {
      const url = route.request().url();
      if (url === 'http://pautapp.test/') return route.fulfill({ contentType: 'text/html', body: html });
      if (url === 'http://pautapp.test/foto.jpg') return route.fulfill({ contentType: 'image/jpeg', body: readFileSync(`${dir}/${u.id}.jpg`) });
      return route.abort();
    });
    const ocrGir = {};
    for (const g of [90, 180, 270]) { try { ocrGir[g] = JSON.parse(readFileSync(`${dir}/${u.id}.g${g}.ocr.json`, 'utf8')); } catch (e) {} }
    await ctx.addInitScript(mock, { ocr, ocrGir, KEY, hoy: u.hoy, fill: +(process.env.FILL || 0) });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    await page.goto('http://pautapp.test/');
    await page.setInputFiles('#in-foto', `${dir}/${u.id}.jpg`);
    const t0 = Date.now();
    let estado = '', st = null;
    for (;;) {
      await page.waitForTimeout(150);
      st = await page.evaluate((k) => JSON.parse(localStorage.getItem(k) || '{}'), KEY);
      estado = await page.$eval('#pauta-estado', (e) => e.textContent).catch(() => '');
      if (st.pauta && !st.pauta.ejemplo && st.pauta.mode === 'auto') break;
      if (/No he podido|No se ha podido/.test(estado)) break;
      if (Date.now() - t0 > 30000) { estado = 'TIMEOUT ' + estado; break; }
    }
    r.ms = Date.now() - t0;
    r.avisoGuardar = await page.$eval('#aviso-guardar', (e) => !e.hidden && e.textContent).catch(() => null);
    r.llegida = !!(st.pauta && st.pauta.mode === 'auto' && !st.pauta.ejemplo);
    r.missatge = estado;
    if (r.llegida) {
      r.days = st.pauta.days.map((d) => ({ date: d.date, x: d.x, y: d.y, w: d.w, h: d.h, rot: d.rot || 0, exacta: !!d.exacta }));
      r.control = st.control; r.inr = st.inr; r.gir = await page.evaluate(() => window.__gir || 0);
      r.imgW = await page.evaluate(() => new Promise((ok) => { const i = new Image(); i.onload = () => ok([i.naturalWidth, i.naturalHeight]); i.src = JSON.parse(localStorage.getItem('mi-sintrom-v1')).pauta.img; }));
      // the person checks each day from today and says it matches
      for (let k = 0; k < 80; k++) {
        const s = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)).pauta, KEY);
        if (s.confirmed) break;
        const vis = await page.isVisible('#btn-rev-si');
        if (!vis) { await page.waitForTimeout(100); continue; }
        await page.click('#btn-rev-si');
      }
      // close the app and open it again
      const abans = await page.evaluate((k) => localStorage.getItem(k), KEY);
      await page.reload();
      await page.waitForTimeout(400);
      const despres = await page.evaluate((k) => localStorage.getItem(k), KEY);
      const p2 = JSON.parse(despres).pauta;
      r.bytes = despres.length;
      r.confirmada = !!(p2 && p2.confirmed);
      r.persistida = abans === despres && !!p2 && !p2.ejemplo && JSON.stringify(p2.days) === JSON.stringify(st.pauta.days) && p2.img === st.pauta.img;
      r.hoyCrop = await page.$eval('#hoy-crop', (e) => !e.hidden && e.src.startsWith('data:image')).catch(() => false);
      if (+u.id.slice(1) % 16 < 2 || process.env.SHOTS) await page.screenshot({ path: `${dir}/shot-${u.id}.png` });
    }
    r.errors = errors;
  } catch (e) {
    r.excepcio = String(e);
  }
  results.push(r);
  await ctx.close();
  process.stdout.write(`${u.id} ${u.deg} ${r.llegida ? 'llegida ' + r.days.length + ' dies' : 'NO: ' + (r.missatge || r.excepcio)}\n`);
}
await browser.close();
writeFileSync(outPath, JSON.stringify(results));
