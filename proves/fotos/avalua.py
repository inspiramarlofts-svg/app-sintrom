# Compares what the app saved with the truth of each fictitious sheet.
# For each day: is the date there, and does the crop the app will show really cover that day's box?
import json, math, sys, unicodedata
norm = lambda t: unicodedata.normalize('NFD', t or '').encode('ascii', 'ignore').decode().lower()
from collections import defaultdict
import numpy as np, cv2

D, RES = sys.argv[1], sys.argv[2]
users = {u['id']: u for u in json.load(open(D + '/usuaris.json'))}
res = json.load(open(RES))


def inside(poly, p):
    return cv2.pointPolygonTest(np.array(poly, np.float32), (float(p[0]), float(p[1])), False) >= 0


def crop_center(d, W, H):
    x, y, w, h = d['x'] * W / 100, d['y'] * H / 100, d['w'] * W / 100, d['h'] * H / 100
    if d['rot']:
        r = d['rot']; cx, cy = w / 2, h / 2
        return (x + cx * math.cos(r) - cy * math.sin(r), y + cx * math.sin(r) + cy * math.cos(r))
    return (x + w / 2, y + h / 2)


rows = []
for r in res:
    u = users[r['id']]
    truth = set(u['caselles'])
    o = {'id': r['id'], 'deg': u['deg'], 'format': u['format'], 'dies': len(truth)}
    if not r.get('llegida'):
        o.update(estat='rebutjada', motiu=r.get('missatge') or r.get('excepcio', ''))
        rows.append(o); continue
    # the image the app stored may be downscaled: map back to the photo's pixels
    W, H = u['W'], u['H']
    g = r.get('gir') or 0
    if g:  # the app turned the photo before reading it: turn the true boxes the same way
        fp = {90: lambda p: [H - p[1], p[0]], 270: lambda p: [p[1], W - p[0]], 180: lambda p: [W - p[0], H - p[1]]}[g]
        u['caselles'] = {k: [fp(p) for p in v] for k, v in u['caselles'].items()}
        if g != 180: W, H = H, W
    got = {d['date']: d for d in r['days']}
    falten = sorted(truth - set(got)); sobren = sorted(set(got) - truth)
    mal = []  # days whose crop shows a different box: the dangerous case
    for k, d in got.items():
        if k not in truth: continue
        c = crop_center(d, W, H)
        if not inside(u['caselles'][k], c):
            mal.append(k)
    # extra days the app added that fall on the sheet: does their crop at least show a real box?
    ce = u['control_esperat']; cg = r.get('control') or {}
    o.update(falten=falten, sobren=sobren, mal=mal,
             control_ok=cg.get('fecha') == ce['fecha'], turno_ok=('turno' not in ce) or norm(cg.get('turno')) == norm(ce['turno']),
             inr_ok=any(x.get('valor') == u['inr'] for x in (r.get('inr') or [])) if u['format'] != 'arago' else None,
             persistida=r.get('persistida'), confirmada=r.get('confirmada'), hoyCrop=r.get('hoyCrop'), bytes=r.get('bytes'), errors=r.get('errors'))
    if mal or sobren:
        o['estat'] = 'PERILL'  # shows a wrong box or a day that is not in the sheet
    elif falten:
        o['estat'] = 'incompleta'
    else:
        o['estat'] = 'perfecta'
    rows.append(o)

json.dump(rows, open(RES.replace('.json', '-aval.json'), 'w'), ensure_ascii=False, indent=1)
per = defaultdict(lambda: defaultdict(int))
for o in rows:
    per[o['deg']][o['estat']] += 1; per[o['deg']]['n'] += 1
    per['TOTAL'][o['estat']] += 1; per['TOTAL']['n'] += 1
print('%-15s %4s %9s %10s %9s %7s' % ('tipus', 'n', 'perfecta', 'incompleta', 'rebutjada', 'PERILL'))
for k, v in per.items():
    print('%-15s %4d %9d %10d %9d %7d' % (k, v['n'], v['perfecta'], v['incompleta'], v['rebutjada'], v['PERILL']))
ok = [o for o in rows if o['estat'] in ('perfecta', 'incompleta', 'PERILL')]
print('control ok', sum(o['control_ok'] for o in ok), '/', len(ok), ' turno ok', sum(o['turno_ok'] for o in ok),
      ' inr ok', sum(1 for o in ok if o['inr_ok']), '/', sum(1 for o in ok if o['inr_ok'] is not None),
      ' persistida', sum(1 for o in ok if o['persistida']), ' confirmada', sum(1 for o in ok if o['confirmada']), ' hoyCrop', sum(1 for o in ok if o['hoyCrop']),
      ' max bytes', max([o['bytes'] or 0 for o in ok] or [0]), ' errors js', sum(len(o['errors'] or []) for o in ok))
for o in rows:
    if o['estat'] != 'perfecta':
        print(o['id'], o['deg'], o['format'], o['estat'], 'falten', len(o.get('falten', [])), o.get('falten', [])[:3], 'sobren', o.get('sobren', [])[:4], 'mal', o.get('mal', [])[:4], o.get('motiu', '')[:50])
