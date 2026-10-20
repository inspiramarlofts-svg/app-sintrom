// In-memory storage with the same interface as the Firestore one, for tests and the local test server.
'use strict';
module.exports = function memoria() {
  const cols = new Map();
  const col = (c) => { if (!cols.has(c)) cols.set(c, new Map()); return cols.get(c); };
  const copia = (x) => (x == null ? null : JSON.parse(JSON.stringify(x)));
  return {
    async get(c, id) { return copia(col(c).get(id)); },
    async set(c, id, d) { col(c).set(id, copia(d)); },
    async del(c, id) { col(c).delete(id); },
    async list(c) { return [...col(c)].map(([id, d]) => [id, copia(d)]); },
    async dueBefore(t) { return [...col('familias')].filter(([, f]) => f.properAvis != null && f.properAvis <= t).map(([id, d]) => [id, copia(d)]); }
  };
};
