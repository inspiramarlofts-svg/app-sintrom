// Local test server: the same API in memory on http://localhost:8790, for trying the app without Firebase.
// node functions/local.js   ·   POST /revisar?ara=<ms> runs the overdue check and prints the pushes.
'use strict';
const http = require('node:http');
const api = require('./api')(require('./memoria')());
http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'content-type');
  if (req.method === 'OPTIONS') { res.end(); return; }
  let cos = ''; for await (const c of req) cos += c;
  const url = new URL(req.url, 'http://x');
  try {
    let r;
    if (url.pathname === '/revisar') {
      const enviats = [];
      await api.revisar(Number(url.searchParams.get('ara')) || Date.now(), async (token, n) => enviats.push({ token, ...n }));
      r = { enviats };
    } else r = await api.atendre(url.pathname.slice(1), cos ? JSON.parse(cos) : {});
    res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(r));
  } catch (e) { res.statusCode = e.codi || 500; res.end(JSON.stringify({ error: e.message })); }
}).listen(Number(process.env.PORT) || 8790, () => console.log('PautApp familia local: http://localhost:' + (Number(process.env.PORT) || 8790)));
