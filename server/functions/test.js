'use strict';
const assert = require('node:assert');
const crearApi = require('./api');
const memoria = require('./memoria');

(async () => {
  const api = crearApi(memoria());
  const clauP = 'p'.repeat(32), clauF = 'f'.repeat(32);
  const { fid, codi } = await api.atendre('crear', { clau: clauP, nom: 'Mare' });
  await assert.rejects(api.atendre('sync', { fid, clau: 'x'.repeat(32) }), /familia/);
  const u = await api.atendre('unir', { codi: codi.toLowerCase().split('').join(' '), clau: clauF, nom: 'Pau', token: 'tok', idioma: 'ca' });
  assert.equal(u.nom, 'Mare');
  await assert.rejects(api.atendre('unir', { codi, clau: clauF }), /codi/); // a code works once

  const t0 = Date.UTC(2026, 9, 20, 18, 0); // 20:00 in Madrid
  const s = await api.atendre('sync', { fid, clau: clauP, minutsAvis: 60, items: [
    { id: 'd@sintrom', at: t0, nom: 'Sintrom', fet: false },
    { id: 'd@ome', at: t0 - 3600e3, nom: 'Omeprazol', fet: true }] });
  assert.deepEqual(s.membres.map((m) => m.nom), ['Pau']);

  const enviats = [];
  const enviar = async (token, n) => enviats.push([token, n]);
  assert.equal(await api.revisar(t0 + 59 * 60e3, enviar), 0);          // not yet
  assert.equal(await api.revisar(t0 + 61 * 60e3, enviar), 1);          // overdue
  assert.match(enviats[0][1].title, /Mare no ho ha confirmat/);
  assert.match(enviats[0][1].body, /Sintrom \(20:00\)/);
  assert.equal(await api.revisar(t0 + 90 * 60e3, enviar), 0);          // only once

  // confirmed in time: no alert
  await api.atendre('sync', { fid, clau: clauP, items: [{ id: 'e@sintrom', at: t0 + 864e5, nom: 'Sintrom', fet: true }] });
  assert.equal(await api.revisar(t0 + 864e5 + 2 * 3600e3, enviar), 0);

  const e = await api.atendre('estat', { seguits: [{ fid, mid: u.mid, clau: clauF }, { fid, mid: u.mid, clau: 'nope'.repeat(8) }] });
  assert.equal(e.seguits[0].nom, 'Mare'); assert.ok(e.seguits[1].desconnectat);

  await api.atendre('treure', { fid, clau: clauP, mid: u.mid });
  const e2 = await api.atendre('estat', { seguits: [{ fid, mid: u.mid, clau: clauF }] });
  assert.ok(e2.seguits[0].desconnectat);
  await api.atendre('esborrar', { fid, clau: clauP });
  console.log('ok');
})().catch((e) => { console.error(e); process.exit(1); });
