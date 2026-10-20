// The family-link API, written against a tiny storage interface so the same code runs on Firebase and in tests.
// Each phone keeps a random secret ("clau"); the server only stores its hash.
'use strict';
const L = require('./logica');

function error(codi, msg) { const e = new Error(msg); e.codi = codi; return e; }

module.exports = function crearApi(db) {
  async function familiaDe(fid, clau) {
    const f = fid && await db.get('familias', fid);
    if (!f || f.pacientClau !== L.hash(clau)) throw error(403, 'familia');
    return f;
  }
  async function membreDe(fid, mid, clau) {
    const m = fid && mid && await db.get('familias/' + fid + '/membres', mid);
    if (!m || m.clau !== L.hash(clau)) throw error(403, 'membre');
    return m;
  }
  async function codiNou(fid) {
    const codi = L.nouCodi();
    await db.set('codis', codi, { fid, caduca: Date.now() + L.CODI_DIES * 864e5 });
    return codi;
  }
  async function membres(fid) {
    return (await db.list('familias/' + fid + '/membres')).map(([id, m]) => ({ id, nom: m.nom }));
  }

  const rutes = {
    // patient: start a family link
    async crear(b) {
      if (!b.clau || String(b.clau).length < 20) throw error(400, 'clau');
      const fid = L.nouId();
      await db.set('familias', fid, { pacientClau: L.hash(b.clau), nom: L.text(b.nom, 40), items: [], avisats: [], minutsAvis: 60, properAvis: null, actualitzat: Date.now(), creat: Date.now() });
      return { fid, codi: await codiNou(fid) };
    },
    // patient: a fresh code for another relative
    async codi(b) { await familiaDe(b.fid, b.clau); return { codi: await codiNou(b.fid) }; },
    // patient: today's doses and whether they were confirmed
    async sync(b) {
      const f = await familiaDe(b.fid, b.clau);
      const items = L.netejaItems(b.items);
      const ids = new Set(items.map((x) => x.id));
      const nova = { ...f, nom: L.text(b.nom, 40) || f.nom, items, minutsAvis: L.minutsValids(b.minutsAvis), avisats: (f.avisats || []).filter((id) => ids.has(id)), actualitzat: Date.now() };
      nova.properAvis = L.properAvis(nova);
      await db.set('familias', b.fid, nova);
      return { membres: await membres(b.fid) };
    },
    // patient: disconnect one relative, or everybody
    async treure(b) {
      await familiaDe(b.fid, b.clau);
      for (const m of await membres(b.fid)) if (!b.mid || m.id === b.mid) await db.del('familias/' + b.fid + '/membres', m.id);
      return { membres: await membres(b.fid) };
    },
    async esborrar(b) {
      await familiaDe(b.fid, b.clau);
      for (const m of await membres(b.fid)) await db.del('familias/' + b.fid + '/membres', m.id);
      await db.del('familias', b.fid);
      return {};
    },
    // relative: join with the code shown on the patient's phone
    async unir(b) {
      const codi = L.netejaCodi(b.codi);
      const c = codi && await db.get('codis', codi);
      if (!c || c.caduca < Date.now()) throw error(404, 'codi');
      const f = await db.get('familias', c.fid);
      if (!f) throw error(404, 'codi');
      if (!b.clau || String(b.clau).length < 20) throw error(400, 'clau');
      const mid = L.nouId();
      await db.set('familias/' + c.fid + '/membres', mid, { clau: L.hash(b.clau), nom: L.text(b.nom, 40), token: L.text(b.token, 4096), idioma: L.text(b.idioma, 5), creat: Date.now() });
      await db.del('codis', codi);
      return { fid: c.fid, mid, nom: f.nom };
    },
    // relative: new push token or language
    async token(b) {
      const m = await membreDe(b.fid, b.mid, b.clau);
      await db.set('familias/' + b.fid + '/membres', b.mid, { ...m, token: L.text(b.token, 4096), idioma: L.text(b.idioma, 5) || m.idioma });
      return {};
    },
    // relative: how the people they follow are doing today
    async estat(b) {
      const r = [];
      for (const s of (Array.isArray(b.seguits) ? b.seguits.slice(0, 20) : [])) {
        try {
          await membreDe(s.fid, s.mid, s.clau);
          const f = await db.get('familias', s.fid);
          r.push({ fid: s.fid, nom: f.nom, actualitzat: f.actualitzat, items: f.items });
        } catch (e) { r.push({ fid: s.fid, desconnectat: true }); }
      }
      return { seguits: r };
    },
    async sortir(b) { await membreDe(b.fid, b.mid, b.clau); await db.del('familias/' + b.fid + '/membres', b.mid); return {}; }
  };

  // scheduled: send a push to the relatives for every dose that is overdue
  async function revisar(ara, enviar) {
    let enviats = 0;
    for (const [fid, f] of await db.dueBefore(ara)) {
      const p = L.pendents(f, ara);
      if (p.length) {
        for (const [, m] of await db.list('familias/' + fid + '/membres')) {
          if (!m.token) continue;
          try { await enviar(m.token, L.textAvis(m.idioma, f.nom, p), { fid }); enviats++; } catch (e) { console.warn('push', e.message); }
        }
      }
      const nova = { ...f, avisats: [...(f.avisats || []), ...p.map((x) => x.id)] };
      nova.properAvis = L.properAvis(nova);
      await db.set('familias', fid, nova);
    }
    return enviats;
  }

  async function atendre(ruta, cos) {
    const f = rutes[ruta];
    if (!f) throw error(404, 'ruta');
    return f(cos || {});
  }
  return { atendre, revisar };
};
