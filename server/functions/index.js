// Firebase Cloud Functions for PautApp's optional family link. Region in Europe; Firestore is closed to clients (see firestore.rules).
'use strict';
const { onRequest } = require('firebase-functions/v2/https');
const { onSchedule } = require('firebase-functions/v2/scheduler');
const { setGlobalOptions } = require('firebase-functions/v2');
const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { getMessaging } = require('firebase-admin/messaging');
const crearApi = require('./api');

initializeApp();
setGlobalOptions({ region: 'europe-west1', maxInstances: 5 });
const fs = getFirestore();

const db = {
  async get(col, id) { const d = await fs.collection(col).doc(id).get(); return d.exists ? d.data() : null; },
  async set(col, id, data) { await fs.collection(col).doc(id).set(data); },
  async del(col, id) { await fs.collection(col).doc(id).delete(); },
  async list(col) { const q = await fs.collection(col).get(); return q.docs.map((d) => [d.id, d.data()]); },
  async dueBefore(t) { const q = await fs.collection('familias').where('properAvis', '<=', t).limit(500).get(); return q.docs.map((d) => [d.id, d.data()]); }
};
const api = crearApi(db);

exports.api = onRequest({ cors: true }, async (req, res) => {
  if (req.method !== 'POST') { res.status(405).send(''); return; }
  try {
    res.json(await api.atendre(req.path.replace(/^\/+/, ''), req.body));
  } catch (e) {
    res.status(e.codi || 500).json({ error: e.codi ? e.message : 'error' });
    if (!e.codi) console.error(e);
  }
});

exports.revisar = onSchedule({ schedule: 'every 5 minutes', timeZone: 'Europe/Madrid' }, async () => {
  const n = await api.revisar(Date.now(), (token, n, data) => getMessaging().send({
    token, notification: n, data,
    android: { priority: 'high', notification: { channelId: 'familia', sound: 'default' } }
  }));
  console.log('avisos enviats', n);
});
