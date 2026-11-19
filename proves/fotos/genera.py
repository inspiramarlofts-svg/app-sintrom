# Genera 200 usuaris ficticis amb fulls de pauta sintètics i fotos degradades.
# Tot és inventat: noms, dates, dosis. Cap dada real de pacients.
import json, math, os, random, sys
from datetime import date, timedelta
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
os.makedirs(OUT, exist_ok=True)
rng = random.Random(20261119)

MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
MONOB = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANSB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
F = lambda p, s: ImageFont.truetype(p, s)

MES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
MESL = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DIAS = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
DIASL = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
NOMS = ['Amparo', 'Vicent', 'Pepa', 'Josep', 'Rosa', 'Manuel', 'Carmen', 'Joan', 'Dolores', 'Francesc', 'Remei', 'Salvador', 'Encarna', 'Bautista', 'Consuelo', 'Rafael', 'Milagros', 'Andreu', 'Pilar', 'Tomàs']
COGNOMS = ['Ferrer', 'Llopis', 'Soler', 'Martí', 'Climent', 'Peris', 'Bosch', 'Navarro', 'Mollà', 'Sanchis', 'Ribes', 'Gimeno', 'Vidal', 'Cervera', 'Puig', 'Esteve', 'Alcover', 'Benet']
DOSIS = ['1/4', '1/2', '3/4', '1', '1 1/4', '1/2', '1/4', '3/4']

DEGS = ['neta', 'foto_mesa', 'doblegada', 'arrugada', 'fosca', 'molt_fosca', 'desenfocada', 'moguda', 'girada', 'girada_90',
        'perspectiva', 'reflex', 'ombra', 'tallada', 'baixa_qualitat', 'combinada']


def user(i):
    fmt = 'gva' if i % 10 < 7 else ('galicia' if i % 10 < 9 else 'arago')
    hoy = date(2026, 11, 19)
    visita = hoy - timedelta(days=rng.randint(0, 3))
    dur = rng.choice([14, 21, 28, 28, 35, 42])
    control = visita + timedelta(days=dur)
    dies = []
    d = visita
    while d < control:
        dies.append({'date': d.isoformat(), 'dosi': '0' if rng.random() < 0.12 else rng.choice(DOSIS)})
        d += timedelta(days=1)
    return {
        'id': 'u%03d' % (i + 1), 'nom': rng.choice(NOMS) + ' ' + rng.choice(COGNOMS) + ' ' + rng.choice(COGNOMS),
        'format': fmt, 'hoy': hoy.isoformat(), 'visita': visita.isoformat(), 'hora_visita': '%02d:%02d' % (rng.randint(8, 13), rng.randint(0, 59)),
        'control': control.isoformat(), 'turno': rng.choice(['Mañanas', 'Tardes']), 'num': rng.randint(1, 40),
        'inr': '%d,%d' % (rng.randint(1, 3), rng.randint(0, 9)), 'dies': dies, 'deg': DEGS[i % len(DEGS)],
        'hospital': rng.choice(['HOSPITAL COMARCAL DE VINARÒS', 'HOSPITAL DE SAGUNT', 'HOSPITAL GENERAL D\'ELDA', 'HOSPITAL DE LA RIBERA', 'HOSPITAL LLUÍS ALCANYÍS'])
    }


def pill(dr, x, y, s, dosi):
    """Draws the tablet split into quarters, the filled part dark."""
    if dosi == '0':
        return
    r = s // 2
    dr.ellipse([x, y, x + s, y + s], outline=(40, 40, 40), width=2)
    frac = {'1/4': 1, '1/2': 2, '3/4': 3, '1': 4, '1 1/4': 4}[dosi]
    dr.pieslice([x, y, x + s, y + s], start=-90, end=-90 + 90 * frac, fill=(90, 90, 90))
    if dosi == '1 1/4':
        dr.pieslice([x + s + 6, y, x + 2 * s + 6, y + s], start=-90, end=0, fill=(90, 90, 90), outline=(40, 40, 40))


def full(u):
    W, H = 1700, 2400
    im = Image.new('RGB', (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    v = date.fromisoformat(u['visita']); c = date.fromisoformat(u['control'])
    mono, monob = F(MONO, 26), F(MONOB, 28)
    blue = (40, 40, 140)
    if u['format'] == 'arago':
        dr.text((120, 90), 'salud', font=F(SANSB, 64), fill=(0, 110, 60))
        dr.text((420, 110), 'Servicio Aragonés de Salud · Hematología', font=F(SANS, 30), fill=(0, 0, 0))
        dr.text((120, 220), 'CALENDARIO DE DOSIFICACIÓN', font=F(SANSB, 40), fill=(0, 0, 0))
        dr.text((120, 300), 'Paciente: ' + u['nom'], font=F(SANS, 30), fill=(0, 0, 0))
        dr.text((120, 350), 'Fecha: %s   INR leído %s   DTS Nueva %d.0' % (v.strftime('%d/%m/%Y'), u['inr'].replace(',', '.'), rng.randint(6, 14)), font=F(SANS, 30), fill=(0, 0, 0))
        top = 460
    else:
        y = 70
        org = 'SERVICIO GALLEGO DE SALUD' if u['format'] == 'galicia' else 'CONSELLERIA DE SANIDAD'
        for t in [org, u['hospital'] if u['format'] == 'gva' else 'CENTRO SAUDE', 'SERVICIO DE HEMATOLOGIA', 'CONTROL DE TRATAMIENTO ANTICOAGULANTE']:
            w = dr.textlength(t, font=monob); dr.text(((W - w) / 2, y), t, font=monob, fill=(0, 0, 0)); y += 36
        y += 20
        dr.text((120, y), 'DATOS DEL PACIENTE', font=F(SANS, 30), fill=(0, 0, 0)); y += 44
        for k, val in [('Nombre.......:', u['nom']), ('Tratamiento..:', 'Sintrom 4 mg'), ('Test/Márgenes:', 'INR 2-3 (2,5)'), ('Diagnóstico..:', 'FA NO VALVULAR')]:
            dr.text((120, y), k, font=mono, fill=(0, 0, 0)); dr.text((360, y), val, font=monob, fill=blue); y += 34
        y += 16
        dr.text((120, y), 'RESUMEN DE LAS ULTIMAS VISITAS', font=F(SANS, 28), fill=(0, 0, 0)); y += 40
        dr.text((120, y), 'Fecha        INR  Fármaco AVK     Dosis    Próx. Visita', font=F(SERIF, 22), fill=(0, 0, 0)); y += 30
        pv = v
        for k in range(4):
            prev = pv - timedelta(days=28 + 7 * (k % 2))
            dr.text((120, y), '%s   %d,%d  Sintrom 4 mg    %s mg    %s' % (prev.strftime('%d/%m/%Y'), rng.randint(1, 3), rng.randint(0, 9), rng.choice(['6,5', '7', '8']), pv.strftime('%d/%m/%Y')), font=F(SERIF, 22), fill=(0, 0, 0)); y += 28
            pv = prev
        y += 16
        dr.text((120, y), 'DATOS DE LA VISITA', font=F(SANS, 28), fill=(0, 0, 0)); y += 42
        dr.text((120, y), 'Fecha........:', font=mono, fill=(0, 0, 0)); dr.text((360, y), '%s %s' % (v.strftime('%d/%m/%Y'), u['hora_visita']), font=monob, fill=blue); y += 34
        dr.text((120, y), 'INR..........:', font=mono, fill=(0, 0, 0)); dr.text((360, y), u['inr'], font=monob, fill=blue); y += 34
        dr.text((120, y), 'Fármaco oral.:', font=mono, fill=(0, 0, 0)); dr.text((360, y), 'Sintrom 4 mg', font=monob, fill=blue); y += 50
        dr.text((120, y), 'DOSIS DIARIA DE ANTICOAGULANTE', font=F(SANS, 40), fill=(0, 0, 0)); y += 56
        top = y
    # grid
    x0, x1 = 110, W - 110
    cw = (x1 - x0) / 7
    hh = 44
    for k, dname in enumerate(DIAS if u['format'] != 'arago' else ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']):
        cx = x0 + k * cw
        dr.rectangle([cx, top, cx + cw, top + hh], outline=(0, 0, 0), width=2, fill=(235, 235, 245))
        f = F(SERIF, 24); w = dr.textlength(dname, font=f); dr.text((cx + (cw - w) / 2, top + 9), dname, font=f, fill=(0, 0, 0))
    lunes = v - timedelta(days=v.weekday())
    rows = (c - lunes).days // 7 + 1
    ch = min(190, int((H - 260 - top - hh) / rows))
    gy = top + hh
    cells = {}
    dosis = {d['date']: d['dosi'] for d in u['dies']}
    for r in range(rows):
        for k in range(7):
            d = lunes + timedelta(days=r * 7 + k)
            bx, by = x0 + k * cw, gy + r * ch
            fill = None
            inside = v <= d < c
            if d == c:
                fill = (150, 150, 150)
            elif u['format'] == 'arago' and not inside and d > lunes:
                fill = (205, 205, 205)
            dr.rectangle([bx, by, bx + cw, by + ch], outline=(0, 0, 0), width=2, fill=fill)
            if d == c and u['format'] != 'arago':
                f = F(MONOB, 28)
                dr.text((bx + 30, by + ch / 2 - 34), 'CONTROL', font=f, fill=(0, 0, 0))
                dr.text((bx + 40, by + ch / 2 + 2), '%02d %s' % (d.day, MES[d.month - 1]), font=f, fill=(0, 0, 0))
                continue
            if u['format'] == 'arago':
                if inside or d < v and d >= lunes:
                    dr.text((bx + 8, by + 6), d.strftime('%d/%m/%Y'), font=F(SANS, 22), fill=(0, 0, 0))
                if inside:
                    cells[d.isoformat()] = [bx, by, bx + cw, by + ch]
                    pill(dr, int(bx + cw / 2 - 30), int(by + 50), 60, dosis[d.isoformat()])
                continue
            if not inside:
                continue
            cells[d.isoformat()] = [bx, by, bx + cw, by + ch]
            ds = dosis[d.isoformat()]
            if u['format'] == 'galicia':
                dr.text((bx + 8, by + 6), '%02d' % d.day, font=F(SERIF, 26), fill=(0, 0, 0))
                dr.text((bx + 8, by + 36), MES[d.month - 1], font=F(SERIF, 26), fill=(0, 0, 0))
            else:
                dr.text((bx + 8, by + 6), '%02d%s' % (d.day, MES[d.month - 1]), font=F(MONOB, 28), fill=(0, 0, 0))
            dr.text((bx + cw - 70, by + 8), ds if ds != '0' else '0', font=F(SERIF, 26), fill=(0, 0, 0))
            if ds == '0':
                dr.text((bx + 20, by + ch - 50), 'NO TOMAR', font=F(MONO, 26), fill=(0, 0, 0))
            else:
                pill(dr, int(bx + 14), int(by + ch - 70), 50, ds)
    y = gy + rows * ch + 20
    if u['format'] == 'arago':
        dr.rectangle([110, y, 900, y + 70], outline=(0, 0, 0), width=2)
        dr.text((130, y + 18), 'Próxima Visita: %d de %s de %d' % (c.day, MESL[c.month - 1].capitalize(), c.year), font=F(SANSB, 30), fill=(0, 0, 0))
        ctrl = {'fecha': c.isoformat(), 'hora': '', 'turno': ''}
    else:
        dr.text((110, y), 'Próxima Visita: %s, %s Turno: %s - Num: %d' % (DIASL[c.weekday()], c.strftime('%d/%m/%Y'), u['turno'], u['num']), font=F(MONO, 26), fill=(0, 0, 0)); y += 36
        dr.text((110, y), 'Centro visita: C.S. %s' % rng.choice(['BENICARLÓ', 'SAGUNT', 'ELDA', 'ALZIRA', 'XÀTIVA']), font=F(MONO, 26), fill=(0, 0, 0))
        ctrl = {'fecha': c.isoformat(), 'turno': '%s, nº %d' % (u['turno'], u['num'])}
    dr.text((110, H - 120), 'NO OLVIDE SEGUIR LAS INDICACIONES MÉDICAS Y TOMAR LA DOSIS SIEMPRE A LA MISMA HORA.', font=F(SANS, 24), fill=(0, 0, 0))
    return im, cells, ctrl


# ---------- degradations; each returns image and a function mapping sheet points to photo points ----------
def warp_persp(img, M, size, bg=None):
    out = cv2.warpPerspective(img, M, size, borderMode=cv2.BORDER_CONSTANT, borderValue=bg or (255, 255, 255))
    f = lambda p: tuple(cv2.perspectiveTransform(np.array([[p]], np.float32), M)[0, 0])
    return out, f


def table_bg(w, h):
    base = np.array([rng.randint(90, 160), rng.randint(70, 130), rng.randint(40, 90)], np.float32)
    n = cv2.GaussianBlur(np.random.default_rng(rng.randint(0, 9999)).normal(0, 25, (h, w)).astype(np.float32), (0, 0), 6)[..., None]
    return np.clip(base + n, 0, 255).astype(np.uint8)


def on_table(img, angle, persp=0.0, scale=0.82):
    h, w = img.shape[:2]
    W, H = int(w * 1.15), int(h * 1.12)
    bg = table_bg(W, H)
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    cx, cy = W / 2, H / 2
    hw, hh = w * scale / 2, h * scale / 2
    pts = np.float32([[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]])
    pts[0, 0] += persp * hw; pts[1, 0] -= persp * hw  # top narrower: keystone
    a = math.radians(angle)
    R = np.float32([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    dst = (pts @ R.T) + np.float32([cx, cy])
    M = cv2.getPerspectiveTransform(src, dst.astype(np.float32))
    sheet = cv2.warpPerspective(img, M, (W, H), borderValue=(0, 0, 0))
    mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), M, (W, H))
    out = np.where(mask[..., None] > 0, sheet, bg)
    f = lambda p: tuple(cv2.perspectiveTransform(np.array([[p]], np.float32), M)[0, 0])
    return out, f


def remap(img, dx, dy):
    h, w = img.shape[:2]
    X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    out = cv2.remap(img, X - dx, Y - dy, cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    f = lambda p: (p[0] + float(dx[int(min(h - 1, max(0, p[1]))), int(min(w - 1, max(0, p[0])))]), p[1] + float(dy[int(min(h - 1, max(0, p[1]))), int(min(w - 1, max(0, p[0])))]))
    return out, f


def shade(img, s):
    return np.clip(img.astype(np.float32) * s[..., None], 0, 255).astype(np.uint8)


def noise(img, sd):
    return np.clip(img.astype(np.float32) + np.random.default_rng(rng.randint(0, 9999)).normal(0, sd, img.shape), 0, 255).astype(np.uint8)


def degrade(img, kind):
    h, w = img.shape[:2]
    ident = lambda p: p
    X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    if kind == 'neta':
        return img, ident
    if kind == 'foto_mesa':
        return on_table(noise(img, 4), rng.uniform(-4, 4), rng.uniform(0, 0.04))
    if kind == 'doblegada':  # folded in four and opened: two creases with a small step and shadow
        fy, fx = h * rng.uniform(0.4, 0.6), w * rng.uniform(0.4, 0.6)
        dy = (np.tanh((Y - fy) / 30) * rng.uniform(4, 12)).astype(np.float32)
        dx = (np.tanh((X - fx) / 30) * rng.uniform(3, 10)).astype(np.float32)
        out, f = remap(img, dx, dy)
        s = 1 - 0.35 * np.exp(-((Y - fy) / 14) ** 2) - 0.3 * np.exp(-((X - fx) / 14) ** 2)
        s = s * np.where(Y > fy, rng.uniform(0.8, 0.95), 1.0) * np.where(X > fx, rng.uniform(0.85, 1.0), 1.0)
        return shade(out, s.astype(np.float32)), f
    if kind == 'arrugada':
        g = np.random.default_rng(rng.randint(0, 9999))
        dx = cv2.GaussianBlur(g.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 60); dx *= 9 / (np.abs(dx).max() + 1e-6)
        dy = cv2.GaussianBlur(g.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 60); dy *= 9 / (np.abs(dy).max() + 1e-6)
        out, f = remap(img, dx, dy)
        s = cv2.GaussianBlur(g.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 25); s = 1 - 0.25 * (s - s.min()) / (s.max() - s.min() + 1e-6)
        return shade(out, s.astype(np.float32)), f
    if kind == 'fosca':
        o = (255 * (img / 255.0) ** 1.0 * rng.uniform(0.35, 0.5)).astype(np.uint8)
        return noise(o, 6), ident
    if kind == 'molt_fosca':
        o = (img * rng.uniform(0.15, 0.22)).astype(np.uint8)
        return noise(o, 5), ident
    if kind == 'desenfocada':
        return cv2.GaussianBlur(img, (0, 0), rng.uniform(2.0, 4.0)), ident
    if kind == 'moguda':
        k = rng.randint(11, 25); ker = np.zeros((k, k), np.float32)
        a = rng.uniform(0, math.pi); c0 = k // 2
        cv2.line(ker, (int(c0 - math.cos(a) * c0), int(c0 - math.sin(a) * c0)), (int(c0 + math.cos(a) * c0), int(c0 + math.sin(a) * c0)), 1, 1)
        return cv2.filter2D(img, -1, ker / ker.sum()), ident
    if kind == 'girada':
        return on_table(img, rng.choice([-1, 1]) * rng.uniform(6, 25), 0, 0.78)
    if kind == 'girada_90':
        ang = rng.choice([90, -90, 180])
        if ang == 180:
            return cv2.rotate(img, cv2.ROTATE_180), lambda p: (w - p[0], h - p[1])
        if ang == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE), lambda p: (h - p[1], p[0])
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE), lambda p: (p[1], w - p[0])
    if kind == 'perspectiva':
        return on_table(img, rng.uniform(-6, 6), rng.uniform(0.12, 0.22), 0.85)
    if kind == 'reflex':  # flash glare over part of the grid
        cx, cy = w * rng.uniform(0.25, 0.75), h * rng.uniform(0.55, 0.8)
        r = w * rng.uniform(0.08, 0.16)
        m = np.exp(-(((X - cx) ** 2 + (Y - cy) ** 2) / (2 * r * r)))
        o = img.astype(np.float32) + m[..., None] * 255 * 1.2
        return np.clip(o, 0, 255).astype(np.uint8), ident
    if kind == 'ombra':  # shadow of the phone/hand over a side
        a = rng.uniform(0, math.pi * 2)
        t = (np.cos(a) * (X - w / 2) + np.sin(a) * (Y - h / 2)) / max(w, h)
        s = np.where(t > rng.uniform(-0.1, 0.15), rng.uniform(0.3, 0.45), 1.0).astype(np.float32)
        s = cv2.GaussianBlur(s, (0, 0), 25)
        return noise(shade(img, s), 4), ident
    if kind == 'tallada':  # photo misses a part of the sheet
        side = rng.choice(['dreta', 'baix', 'esquerra'])
        if side == 'dreta':
            cut = int(w * rng.uniform(0.80, 0.9)); return img[:, :cut].copy(), ident
        if side == 'esquerra':
            cut = int(w * rng.uniform(0.1, 0.2)); return img[:, cut:].copy(), lambda p: (p[0] - cut, p[1])
        cut = int(h * rng.uniform(0.78, 0.88)); return img[:cut].copy(), ident
    if kind == 'baixa_qualitat':
        s = rng.uniform(0.33, 0.45)
        small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, rng.randint(15, 30)])
        return cv2.imdecode(buf, 1), lambda p: (p[0] * s, p[1] * s)
    if kind == 'combinada':
        o, f = on_table(img, rng.choice([-1, 1]) * rng.uniform(4, 12), rng.uniform(0.03, 0.08), 0.84)
        o = cv2.GaussianBlur(o, (0, 0), 1.6)
        o = noise((o * rng.uniform(0.45, 0.6)).astype(np.uint8), 6)
        return o, f
    raise ValueError(kind)


users = []
for i in range(N):
    u = user(i)
    im, cells, ctrl = full(u)
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    out, f = degrade(arr, u['deg'])
    ok, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    open(os.path.join(OUT, u['id'] + '.jpg'), 'wb').write(buf.tobytes())
    u['W'], u['H'] = out.shape[1], out.shape[0]
    # each day's box as a polygon in photo pixels, for checking the crops
    u['caselles'] = {d: [list(map(float, f((b[0], b[1])))), list(map(float, f((b[2], b[1])))), list(map(float, f((b[2], b[3])))), list(map(float, f((b[0], b[3]))))] for d, b in cells.items()}
    u['control_esperat'] = ctrl
    users.append(u)
    if i < 3 or i % 50 == 0:
        print(u['id'], u['format'], u['deg'], len(cells), 'dies', file=sys.stderr)
json.dump(users, open(os.path.join(OUT, 'usuaris.json'), 'w'), ensure_ascii=False, indent=1)
print('fet', len(users))
