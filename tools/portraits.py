#!/usr/bin/env python3
"""Cuts the supplied portrait sheets into individual transparent portraits and packs the display versions for the game.

  python3 tools/portraits.py            # writes assets/portraits/<id>.png (full-res crops, alpha kept),
                                        #        assets/portraits/web/<id>.webp (display size, max 640 px tall)
                                        #        js/portraits.js (window.PORTRAIT_DATA = {id: data-URI})

The sheets are kept untouched under assets/portraits/src/. The figures on a sheet overlap their neighbours at the
shoulders, so each portrait is a *display crop* chosen by hand (head and upper body, the neighbour's parts left out)
with a short alpha feather on the sides that were cut through the drawing. Nothing is redrawn, stretched or
recoloured; the crops keep the sheet's pixels and alpha. Identities: the sheet order given with the assets — regulars
陳伯伯, Mia, Sophie, Leo, 小林, 王先生, 王太太 (the third and fifth figures: Sophie and 小林, confirmed by the author in v2.2.1); the six staff designs are staff_1..staff_6 and the game maps them to its
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
    # v2.2.1 (#11): the four Jill poses overlap on the sheet — hair over a neighbour's shoulder, two white sleeves
    # touching — so a rectangle always carried part of the next figure (a stranger's hair down the left side of
    # jill_cheerful on the phone). Each crop now also has a separator polyline (sheet px) per side that runs through
    # the seam between the two figures; everything on the neighbour's side of it is made transparent (4 px feather).
    # The crops are widened to the seam so each figure keeps her own hair and shoulder.
    ('sheet_jill_dylan_8.png', 'jill_warm', (15, 15, 362, 470),
        {'right': [(356, 15), (358, 120), (352, 200), (348, 270), (346, 290), (344, 320), (350, 345), (352, 420), (350, 470)]}),
    ('sheet_jill_dylan_8.png', 'jill_cheerful', (296, 15, 700, 490),
        {'left': [(358, 15), (360, 120), (353, 200), (349, 270), (347, 290), (345, 320), (351, 345), (353, 420), (351, 490)],
         'right': [(660, 15), (662, 150), (660, 330), (658, 490)]}),
    ('sheet_jill_dylan_8.png', 'jill_teasing', (642, 15, 962, 480),
        {'left': [(665, 15), (668, 100), (665, 300), (665, 340), (662, 480)],
         'right': [(945, 15), (945, 300), (958, 380), (960, 480)]}),
    ('sheet_jill_dylan_8.png', 'jill_gentle', (940, 15, 1262, 480),
        {'left': [(950, 15), (950, 300), (961, 380), (964, 480)]}),
    # the Jill row's sleeves and aprons end 5–18 px below y=650, touching the Dylan heads: a 'top' separator per crop
    ('sheet_jill_dylan_8.png', 'dylan_default', (10, 650, 305, 1050),
        {'top': [(10, 651), (60, 654), (150, 658), (230, 662), (305, 667)]}),
    ('sheet_jill_dylan_8.png', 'dylan_friendly', (318, 650, 618, 1090),
        {'top': [(318, 663), (618, 663)]}),
    ('sheet_jill_dylan_8.png', 'dylan_playful', (641, 650, 928, 1080),
        {'top': [(641, 669), (772, 669), (782, 654), (905, 654), (915, 663), (928, 663)]}),
    ('sheet_jill_dylan_8.png', 'dylan_gentle', (952, 650, 1262, 1080),
        {'top': [(952, 673), (1030, 673), (1045, 661), (1200, 661), (1215, 653), (1262, 653)]}),
    ('sheet_regulars_staff_13.png', 'chen', (5, 10, 250, 400)),
    ('sheet_regulars_staff_13.png', 'mia', (262, 10, 500, 400)),
    ('sheet_regulars_staff_13.png', 'sophie', (515, 10, 750, 410), {'left': [(526, 10), (526, 410)]}),    # v2.2.1: the author confirmed the third figure is Sophie; Mia's hair tips masked
    ('sheet_regulars_staff_13.png', 'leo', (765, 10, 1016, 400)),
    ('sheet_regulars_staff_13.png', 'xiaolin', (1018, 10, 1295, 400), {'left': [(1040, 10), (1040, 200), (1026, 240), (1026, 400)]}),  # v2.2.1: ...and the fifth is 小林 (the two were swapped in v2.2); Leo's hair tips masked, his own hair kept
    ('sheet_regulars_staff_13.png', 'mr_wang', (1272, 10, 1512, 410), {'left': [(1292, 10), (1292, 210), (1279, 250), (1279, 410)]}),
    ('sheet_regulars_staff_13.png', 'mrs_wang', (1525, 10, 1770, 400)),
    ('sheet_regulars_staff_13.png', 'staff_1', (0, 445, 313, 860)),
    ('sheet_regulars_staff_13.png', 'staff_2', (300, 445, 585, 860), {'left': [(316, 445), (316, 570), (304, 600), (304, 860)]}),
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


SEP_FEATHER = 4

def separate(im, box, seps):
    """Make the neighbour's side of each separator polyline transparent. seps = {'left': [(x,y),...]} keeps what is
    right of the line, {'right': [...]} keeps what is left of it, {'top': [...]} keeps what is below it; the line is interpolated per row (sheet px) and the
    cut is feathered over SEP_FEATHER px so no hard edge appears where two figures touched."""
    import numpy as np
    x0, y0, x1, y1 = box
    rgba = np.asarray(im).copy()
    h, w = rgba.shape[:2]
    ys = np.arange(h) + y0
    xs = np.arange(w) + x0
    for side, pts in seps.items():
        if side == 'top':                                                      # keep what is below the line
            pts = sorted(pts, key=lambda p: p[0])
            py = np.interp(xs, [p[0] for p in pts], [p[1] for p in pts])      # separator y per column
            d = ys[:, None] - py[None, :]                                      # + = below the line
            f = np.clip(d / SEP_FEATHER + .5, 0, 1)
        else:
            pts = sorted(pts, key=lambda p: p[1])
            px = np.interp(ys, [p[1] for p in pts], [p[0] for p in pts])      # separator x per row
            d = xs[None, :] - px[:, None]                                      # + = right of the line
            if side == 'left': f = np.clip(d / SEP_FEATHER + .5, 0, 1)         # keep the right side
            else: f = np.clip(-d / SEP_FEATHER + .5, 0, 1)                     # keep the left side
        rgba[:, :, 3] = (rgba[:, :, 3].astype(np.float32) * f).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def trim(im):
    bb = im.getchannel('A').getbbox()
    return im.crop(bb) if bb else im


HOLE_MAX = 300   # a keyed-out region bigger than this is real background enclosed by the drawing (the gap between the ladle and the shoulder), not a pinhole

def solid_inside(im):
    """The supplied sheets have alpha holes inside the figures (dark hair and clothes were partly keyed out with the
    background). The outline stays as drawn; every small hole enclosed by the figure becomes opaque again and takes
    the colour of the nearest drawn pixel (the RGB stored under a keyed-out pixel is noise — v2.2 revealed it as
    coloured speckles on the ladle), so a face never shows what is behind it. A large enclosed region is background
    the drawing happens to surround and stays transparent. Nothing else changes."""
    import numpy as np
    from scipy import ndimage
    rgba = np.asarray(im).copy()
    a = rgba[:, :, 3]
    figure = a > 8
    outside = ~figure
    lab, n = ndimage.label(outside)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))          # the background: transparent regions touching the edge of the image
    holes = (~bg) & outside                   # keyed-out pixels enclosed by the figure
    hl, hn = ndimage.label(holes)
    if hn:
        sizes = ndimage.sum(holes, hl, range(1, hn + 1))
        big = np.isin(hl, [k + 1 for k, sz in enumerate(sizes) if sz > HOLE_MAX])
        holes = holes & ~big
    inside = figure | holes
    core = ndimage.binary_erosion(inside, iterations=3)   # keep the antialiased rim as drawn
    fill = holes & core
    if fill.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~(a > 96), return_indices=True)   # nearest solidly drawn pixel
        rgba[fill, :3] = rgba[iy[fill], ix[fill], :3]
    a2 = a.copy(); a2[core] = 255
    rgba[:, :, 3] = a2
    return Image.fromarray(rgba, 'RGBA')


def main():
    os.makedirs(WEB, exist_ok=True)
    data = {}
    sheets = {}
    for entry in CROPS:
        sheet, pid, box = entry[:3]
        seps = entry[3] if len(entry) > 3 else None
        if sheet not in sheets: sheets[sheet] = Image.open(os.path.join(SRC, sheet)).convert('RGBA')
        sh = sheets[sheet]
        im = solid_inside(sh.crop(box))
        if seps: im = separate(im, box, seps)
        im = trim(feather(im, box, sh.size))
        im.save(os.path.join(OUT, pid + '.png'), optimize=True)
        data[pid] = pack(im, pid)
    for fn, pid in STANDALONE:
        im = trim(solid_inside(Image.open(os.path.join(OUT, fn)).convert('RGBA')))
        data[pid] = pack(im, pid)
    # v2.2.1 H2: the named guests' and staff's card portraits (cut by tools/portraits_named.py, used as they are)
    import importlib.util
    spec = importlib.util.spec_from_file_location('portraits_named', os.path.join(ROOT, 'tools', 'portraits_named.py'))
    pn = importlib.util.module_from_spec(spec); spec.loader.exec_module(pn)
    for pid, _box in pn.CARDS:
        fp = os.path.join(OUT, pid + '.png')
        if os.path.exists(fp): data[pid] = pack(Image.open(fp).convert('RGBA'), pid)
    # v2.3: the Lounge staff's card portraits (tools/portraits_lounge.py)
    spec2 = importlib.util.spec_from_file_location('portraits_lounge', os.path.join(ROOT, 'tools', 'portraits_lounge.py'))
    pl = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(pl)
    for pid, _src, _box in pl.CARDS:
        fp = os.path.join(OUT, pid + '.png')
        if os.path.exists(fp): data[pid] = pack(Image.open(fp).convert('RGBA'), pid)
    # v2.3 follow-up: the staff portraits the player redrew (tools/portraits_staff_v23.py)
    spec3 = importlib.util.spec_from_file_location('portraits_staff_v23', os.path.join(ROOT, 'tools', 'portraits_staff_v23.py'))
    ps = importlib.util.module_from_spec(spec3); spec3.loader.exec_module(ps)
    for pid in [c[0] for c in ps.CARDS] + [c[0] for c in ps.CARDS8]:
        fp = os.path.join(OUT, pid + '.png')
        if os.path.exists(fp): data[pid] = pack(Image.open(fp).convert('RGBA'), pid)
    # v2.3 follow-up: the regulars' portraits the player supplied (tools/portraits_regulars_v23.py)
    spec4 = importlib.util.spec_from_file_location('portraits_regulars_v23', os.path.join(ROOT, 'tools', 'portraits_regulars_v23.py'))
    pr = importlib.util.module_from_spec(spec4); spec4.loader.exec_module(pr)
    for pid in [c[0] for c in pr.CARDS]:
        fp = os.path.join(OUT, pid + '.png')
        if os.path.exists(fp): data[pid] = pack(Image.open(fp).convert('RGBA'), pid)
    # v2.4: 怡君 and 秀琴阿姨's expressions (tools/portraits_v24.py)
    spec5 = importlib.util.spec_from_file_location('portraits_v24', os.path.join(ROOT, 'tools', 'portraits_v24.py'))
    p24 = importlib.util.module_from_spec(spec5); spec5.loader.exec_module(p24)
    for pid in [c[0] for c in p24.CARDS]:
        fp = os.path.join(OUT, pid + '.png')
        if os.path.exists(fp): data[pid] = pack(Image.open(fp).convert('RGBA'), pid)
    # v2.4 rc7.1 (the player, 20:50–20:56: the page got slow to open on a phone): portraits the game never shows stay out of
    # the page — kept as files in assets/portraits — the seven outside-cast cards of P5 (paused, 18:38) and the 2.2.1 staff
    # cards the player redrew as st23_* in 2.3. rc7.7: and Sophie's and Mia's first cards (sophie, mia), redrawn as reg23_*
    # in v2.3 — the game asks PORTRAIT_DATA only for the keys in PORTRAITS, STAFF_PORTRAITS, PORTRAIT_TONES and NAMED
    import re as _re
    for pid in [k for k in data if _re.match(r'^(v24_(xtm|shan|gx|lin|kevin|yx|xtf)(_[a-z]+)?|staff_([1-6]|xiaotong|momo|nina|yuki|azhu|hugo|azhe|aming)|sophie|mia)$', k)]:
        del data[pid]
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
