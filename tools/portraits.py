#!/usr/bin/env python3
"""Cuts the supplied portrait sheets into individual transparent portraits and packs the display versions for the game.

  python3 tools/portraits.py            # writes assets/portraits/<id>.png (full-res crops, alpha kept),
                                        #        assets/portraits/web/<id>.webp (display size, max 640 px tall)
                                        #        js/portraits.js (window.PORTRAIT_DATA = {id: data-URI})

The sheets are kept untouched under assets/portraits/src/. The figures on a sheet overlap their neighbours at the
shoulders, so each portrait is a *display crop* chosen by hand (head and upper body, the neighbour's parts left out)
with a short alpha feather on the sides that were cut through the drawing. Nothing is redrawn, stretched or
recoloured; the crops keep the sheet's pixels and alpha. Identities: the sheet order given with the assets — regulars
陳伯伯, Mia, 小林, Leo, Sophie, 王先生, 王太太; the six staff designs are staff_1..staff_6 and the game maps them to its
own staff records by role and hiring order (see STAFF_PORTRAITS in js/game.js), never by appearance.
"""
import base64, io, json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'portraits', 'src')
OUT = os.path.join(ROOT, 'assets', 'portraits')
WEB = os.path.join(OUT, 'web')
JS = os.path.join(ROOT, 'js', 'portraits.js')
DISPLAY_H = 640      # tallest display size a phone needs (≈ 250 css px at 2× and a bit of room)
WEBP_Q = 84
FEATHER = 16

# (sheet, id, box) — boxes in sheet pixels, inspected by eye on a grid
CROPS = [
    ('sheet_jill_dylan_8.png', 'jill_warm', (15, 15, 300, 470)),
    ('sheet_jill_dylan_8.png', 'jill_cheerful', (296, 15, 632, 490)),
    ('sheet_jill_dylan_8.png', 'jill_teasing', (642, 15, 926, 480)),
    ('sheet_jill_dylan_8.png', 'jill_gentle', (952, 15, 1262, 480)),
    ('sheet_jill_dylan_8.png', 'dylan_default', (10, 650, 305, 1050)),
    ('sheet_jill_dylan_8.png', 'dylan_friendly', (318, 650, 618, 1090)),
    ('sheet_jill_dylan_8.png', 'dylan_playful', (641, 650, 928, 1080)),
    ('sheet_jill_dylan_8.png', 'dylan_gentle', (952, 650, 1262, 1080)),
    ('sheet_regulars_staff_13.png', 'chen', (5, 10, 250, 400)),
    ('sheet_regulars_staff_13.png', 'mia', (262, 10, 500, 400)),
    ('sheet_regulars_staff_13.png', 'xiaolin', (515, 10, 750, 410)),
    ('sheet_regulars_staff_13.png', 'leo', (765, 10, 1005, 400)),
    ('sheet_regulars_staff_13.png', 'sophie', (1018, 10, 1258, 400)),
    ('sheet_regulars_staff_13.png', 'mr_wang', (1272, 10, 1512, 410)),
    ('sheet_regulars_staff_13.png', 'mrs_wang', (1525, 10, 1770, 400)),
    ('sheet_regulars_staff_13.png', 'staff_1', (0, 445, 290, 860)),
    ('sheet_regulars_staff_13.png', 'staff_2', (300, 445, 585, 860)),
    ('sheet_regulars_staff_13.png', 'staff_3', (596, 445, 880, 860)),
    ('sheet_regulars_staff_13.png', 'staff_4', (892, 445, 1175, 860)),
    ('sheet_regulars_staff_13.png', 'staff_5', (1188, 445, 1470, 860)),
    ('sheet_regulars_staff_13.png', 'staff_6', (1483, 445, 1770, 860)),
]
# the two stand-alone Jill portraits (supplied as finished files): used whole, only resized for display
STANDALONE = [('jill.png', 'jill_default'), ('jill-relaxed.png', 'jill_relaxed')]


def feather(im, box, sheet_size):
    """Fade the alpha over FEATHER px on every side where the crop cut through the drawing (not at the sheet's edge)."""
    import numpy as np
    w, h = im.size
    x0, y0, x1, y1 = box
    f = np.ones((h, w), dtype=np.float32)
    ramp = (np.arange(FEATHER) + .5) / FEATHER
    rgba = np.asarray(im).copy()
    a = rgba[:, :, 3]
    cuts = lambda edge: (edge > 30).mean() > .05     # the edge runs through the drawing, not through empty sheet
    if x0 > 2 and cuts(a[:, 0]): f[:, :FEATHER] = np.minimum(f[:, :FEATHER], ramp[None, :])
    if x1 < sheet_size[0] - 2 and cuts(a[:, -1]): f[:, w - FEATHER:] = np.minimum(f[:, w - FEATHER:], ramp[::-1][None, :])
    if y0 > 2 and cuts(a[0]): f[:FEATHER, :] = np.minimum(f[:FEATHER, :], ramp[:, None])
    if y1 < sheet_size[1] - 2 and cuts(a[-1]): f[h - FEATHER:, :] = np.minimum(f[h - FEATHER:, :], ramp[::-1][:, None])
    rgba[:, :, 3] = (rgba[:, :, 3].astype(np.float32) * f).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def trim(im):
    bb = im.getchannel('A').getbbox()
    return im.crop(bb) if bb else im


def solid_inside(im):
    """The supplied sheets have alpha holes inside the figures (dark hair and clothes were partly keyed out with the
    background). The outline stays as drawn; every pixel enclosed by the figure becomes opaque again, so a face never
    shows what is behind it. Nothing else changes."""
    import numpy as np
    from scipy import ndimage
    a = np.asarray(im.getchannel('A'))
    figure = a > 8
    outside = ~figure
    lab, n = ndimage.label(outside)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))          # the background: transparent regions touching the edge of the image
    inside = ~bg                              # the figure and every hole enclosed by it
    core = ndimage.binary_erosion(inside, iterations=3)   # keep the antialiased rim as drawn
    a2 = a.copy(); a2[core] = 255
    rgba = np.asarray(im).copy(); rgba[:, :, 3] = a2
    return Image.fromarray(rgba, 'RGBA')


def main():
    os.makedirs(WEB, exist_ok=True)
    data = {}
    sheets = {}
    for sheet, pid, box in CROPS:
        if sheet not in sheets: sheets[sheet] = Image.open(os.path.join(SRC, sheet)).convert('RGBA')
        sh = sheets[sheet]
        im = trim(feather(solid_inside(sh.crop(box)), box, sh.size))
        im.save(os.path.join(OUT, pid + '.png'), optimize=True)
        data[pid] = pack(im, pid)
    for fn, pid in STANDALONE:
        im = trim(solid_inside(Image.open(os.path.join(OUT, fn)).convert('RGBA')))
        data[pid] = pack(im, pid)
    js = '/* generated by tools/portraits.py — the display versions of assets/portraits (WebP with alpha, max %d px tall) */\nwindow.PORTRAIT_DATA=%s;\n' % (DISPLAY_H, json.dumps(data, separators=(',', ':')))
    open(JS, 'w', encoding='utf-8').write(js)
    total = sum(len(v) for v in data.values())
    print('portraits:', len(data), '| js/portraits.js', round(len(js) / 1024), 'KB | data', round(total / 1024), 'KB')


def pack(im, pid):
    w, h = im.size
    if h > DISPLAY_H:
        im = im.resize((round(w * DISPLAY_H / h), DISPLAY_H), Image.LANCZOS)
    im.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=WEBP_Q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


if __name__ == '__main__':
    main()
