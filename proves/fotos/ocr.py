# Reads every photo with an on-device-style text recogniser (RapidOCR, PP-OCR models) and writes the result
# in the same shape as ML Kit's TextRecognition.processImage: { text, blocks: [{ lines: [{ elements: [{ text, boundingBox }] }] }] }.
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np

D = sys.argv[1]
eng = None


def words_of(box, text):
    """Splits a recognised line into words, sharing the line box by character count (ML Kit gives words)."""
    p = np.array(box, np.float32)
    x0, y0 = p[0]; x1, y1 = p[1]; x3, y3 = p[3]
    parts, out, pos = text.split(' '), [], 0
    n = max(1, len(text))
    for w in parts:
        if w:
            a, b = pos / n, (pos + len(w)) / n
            ax, ay = x0 + (x1 - x0) * a, y0 + (y1 - y0) * a
            bx, by = x0 + (x1 - x0) * b, y0 + (y1 - y0) * b
            dx, dy = x3 - x0, y3 - y0
            xs = [ax, bx, ax + dx, bx + dx]; ys = [ay, by, ay + dy, by + dy]
            out.append({'text': w, 'boundingBox': {'left': float(min(xs)), 'top': float(min(ys)), 'right': float(max(xs)), 'bottom': float(max(ys))}})
        pos += len(w) + 1
    return out


def one(name):
    global eng
    if eng is None:
        from rapidocr_onnxruntime import RapidOCR
        eng = RapidOCR()
    res, _ = eng(os.path.join(D, name))
    blocks, txt = [], []
    for box, text, score in res or []:
        blocks.append({'text': text, 'lines': [{'text': text, 'elements': words_of(box, text)}]})
        txt.append(text)
    r = {'text': '\n'.join(txt), 'blocks': blocks}
    json.dump(r, open(os.path.join(D, name.replace('.jpg', '.ocr.json')), 'w'), ensure_ascii=False)
    return name, len(blocks)


if __name__ == '__main__':
    names = sorted(n for n in os.listdir(D) if n.endswith('.jpg') and not os.path.exists(os.path.join(D, n.replace('.jpg', '.ocr.json'))))
    with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
        for i, (n, k) in enumerate(ex.map(one, names)):
            if i % 20 == 0: print(i, n, k, flush=True)
    print('fet')
