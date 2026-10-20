// Pure rules shared by the Cloud Functions and the local test server: no Firebase here.
'use strict';
const crypto = require('node:crypto');

const LLETRES = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // no 0/O or 1/I, easy to read aloud
const CODI_DIES = 7;
const MAX_ITEMS = 200;
const FINESTRA = 6 * 3600e3; // items older than this are not alerted any more

const hash = (s) => crypto.createHash('sha256').update(String(s)).digest('hex');
const nouCodi = () => Array.from(crypto.randomBytes(6), (b) => LLETRES[b % LLETRES.length]).join('');
const nouId = () => crypto.randomBytes(12).toString('hex');
const netejaCodi = (c) => String(c || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
const text = (s, n) => String(s || '').trim().slice(0, n);

// items come from the patient's phone: [{ id, at (epoch ms), nom, fet }]
function netejaItems(items) {
  if (!Array.isArray(items)) return [];
  return items.slice(0, MAX_ITEMS)
    .filter((x) => x && typeof x.at === 'number' && isFinite(x.at))
    .map((x) => ({ id: text(x.id, 80), at: Math.round(x.at), nom: text(x.nom, 60), fet: !!x.fet }));
}
const minutsValids = (m) => ([30, 60, 120].includes(Number(m)) ? Number(m) : 60);

// what is overdue now and has not been alerted yet
function pendents(f, ara) {
  const avisats = new Set(f.avisats || []);
  const espera = minutsValids(f.minutsAvis) * 60e3;
  return (f.items || []).filter((x) => !x.fet && !avisats.has(x.id) && x.at + espera <= ara && ara - x.at <= FINESTRA);
}
// when the scheduled check next needs to look at this family (null: nothing left)
function properAvis(f) {
  const avisats = new Set(f.avisats || []);
  const espera = minutsValids(f.minutsAvis) * 60e3;
  const t = (f.items || []).filter((x) => !x.fet && !avisats.has(x.id)).map((x) => x.at + espera);
  return t.length ? Math.min(...t) : null;
}

const TXT = {
  es: { t: '{0} no ha confirmado', b: 'Todavía no ha confirmado: {0}. Puede que se le haya olvidado o que el móvil no tenga internet.' },
  ca: { t: '{0} no ho ha confirmat', b: 'Encara no ha confirmat: {0}. Pot ser que se li hagi oblidat o que el mòbil no tingui internet.' },
  gl: { t: '{0} non o confirmou', b: 'Aínda non confirmou: {0}. Pode que se lle esquecese ou que o móbil non teña internet.' },
  eu: { t: '{0}(e)k ez du berretsi', b: 'Oraindik ez du berretsi: {0}. Agian ahaztu egin zaio edo mugikorrak ez du Internetik.' }
};
const hhmm = (ms) => new Date(ms).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' });
function textAvis(idioma, nomPacient, items) {
  const t = TXT[idioma] || TXT.es;
  const llista = items.map((x) => x.nom + ' (' + hhmm(x.at) + ')').join(', ');
  return { title: t.t.replace('{0}', nomPacient), body: t.b.replace('{0}', llista) };
}

module.exports = { hash, nouCodi, nouId, netejaCodi, text, netejaItems, minutsValids, pendents, properAvis, textAvis, CODI_DIES };
