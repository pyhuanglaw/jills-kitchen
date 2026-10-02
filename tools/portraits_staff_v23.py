#!/usr/bin/env python3
"""v2.3 follow-up (2026-10-01): the staff portraits redrawn by the player — a sheet of twelve (two rows of six) and a
sheet of the other eight (scattered), on a white background, each with a name label under it
(assets/portraits/src/sheet_staff_12_v23.png, sheet_staff_8_v23.png).

Used as card portraits, like tools/portraits_named.py: each figure is cut by its column (the sheet is a regular grid),
from the top of the head down to just above its label (on the scattered sheet, a box chosen by eye; where a
neighbour's label pokes into the box it is painted out with the sheet's own white), given rounded corners, and
packed by tools/portraits.py. No
background keying: the chef whites would be keyed out with the white background. The Lounge four (Evan, 沈晴, 安安,
阿拓) keep their own portraits (tools/portraits_lounge.py), as the player asked.

  python3 tools/portraits_staff_v23.py && python3 tools/portraits.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_staff_12_v23.png')
SRC8 = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_staff_8_v23.png')
OUT = os.path.join(ROOT, 'assets', 'portraits')
WEB = os.path.join(OUT, 'web')
DISPLAY_H = 480
WEBP_Q = 84
RADIUS = 18
COL = 1683 / 6                      # six equal columns
ROWS = [(18, 392), (466, 838)]      # head top → just above the name label
# (id, row, column, name) — the names are the labels on the sheet
CARDS = [
    ('st23_ade', 0, 0, '阿德師傅'), ('st23_marco', 0, 1, 'Marco'), ('st23_xiaolin', 0, 2, '小林師傅'),
    ('st23_azhu', 0, 3, '阿珠姐'), ('st23_hugo', 0, 4, 'Hugo'), ('st23_ayong', 0, 5, '阿勇'),
    ('st23_xiaomo', 1, 0, '小茉'), ('st23_kai', 1, 1, 'Kai'), ('st23_nina', 1, 2, 'Nina'),
    ('st23_azhe', 1, 3, '阿哲'), ('st23_xiuqin', 1, 4, '秀琴阿姨'), ('st23_xiaotong', 1, 5, '小彤'),
]
# the scattered sheet: (id, box, name, white-outs) — boxes and white-outs in sheet px
CARDS8 = [
    ('st23_laozhou', (475, 3, 812, 245), '老周師傅', []),
    ('st23_wei', (874, 9, 1300, 250), '小魏', []),
    ('st23_momo', (212, 265, 570, 526), 'Momo', [(541, 265, 570, 312)]),        # 老周師傅's label
    ('st23_xiaowei', (745, 279, 1054, 528), '小威', [(985, 279, 1054, 312)]),   # 小魏's label
    ('st23_afang', (1245, 284, 1594, 524), '阿芳', []),
    ('st23_aming', (182, 599, 502, 810), '阿明', []),
    ('st23_yuki', (740, 594, 1010, 814), 'Yuki', []),
    ('st23_agui', (1349, 602, 1637, 812), '阿桂', []),
]


def box(row, col):
    y0, y1 = ROWS[row]
    return (round(col * COL) + 2, y0, round((col + 1) * COL) - 2, y1)


def card(sheet, b, pid, name):
    c = sheet.crop(b)
    m = Image.new('L', c.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, c.size[0] - 1, c.size[1] - 1), radius=RADIUS, fill=255)
    c.putalpha(m)
    c.save(os.path.join(OUT, pid + '.png'), optimize=True)
    w, h = c.size
    if h > DISPLAY_H: c = c.resize((round(w * DISPLAY_H / h), DISPLAY_H), Image.LANCZOS)
    c.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
    print(pid, name, c.size)


# v2.4 rc6 (the player, 2026-10-02 09:45 and 09:47): the sheet is not a clean grid — an elbow, a sleeve, a wok, a pot, a
# tray or a glass crosses into the next column — so each of the twelve has a box of its own, chosen by eye (it cuts the
# person's own arm or pan where a neighbour touches them, never the other way), and inside it everything that is not
# connected to that person's drawing (a neighbour's sleeve, hand or tray standing apart) is painted with the sheet's
# white; the person's own outline and its soft edge stay.
BOXES = {'st23_ade': (0, 18, 300, 392), 'st23_marco': (245, 18, 585, 392), 'st23_xiaolin': (560, 18, 822, 392),
         'st23_azhu': (828, 18, 1094, 392), 'st23_hugo': (1132, 18, 1342, 392), 'st23_ayong': (1404, 18, 1683, 392),
         'st23_xiaomo': (0, 466, 275, 838), 'st23_kai': (275, 466, 570, 838), 'st23_nina': (570, 466, 870, 838),
         'st23_azhe': (841, 466, 1160, 838), 'st23_xiuqin': (1150, 466, 1430, 838), 'st23_xiaotong': (1425, 466, 1683, 838)}
SEEDS = {'st23_ade': (150, 150), 'st23_marco': (440, 120), 'st23_xiaolin': (720, 140), 'st23_azhu': (991, 120),
         'st23_hugo': (1261, 140), 'st23_ayong': (1561, 120), 'st23_xiaomo': (150, 600), 'st23_kai': (460, 580),
         'st23_nina': (700, 620), 'st23_azhe': (1011, 590), 'st23_xiuqin': (1311, 600), 'st23_xiaotong': (1561, 620)}


def only_them(sheet, b, seed):
    """the box, with whatever does not touch the person's own drawing painted white"""
    import numpy as np
    import scipy.ndimage as nd
    A = np.asarray(sheet.crop(b)).copy()
    rgb = A[..., :3].astype(int)
    fg = ~((rgb.min(axis=2) >= 238) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 14))
    lab, _ = nd.label(fg, structure=np.ones((3, 3)))
    if seed is None:   # the person is the largest drawing in their box
        sizes = np.bincount(lab.ravel()); sizes[0] = 0; k = int(sizes.argmax())
    else:
        sx, sy = seed[0] - b[0], seed[1] - b[1]
        k = lab[sy, sx]
        if k == 0:
            ys, xs = np.nonzero(lab); d = (ys - sy) ** 2 + (xs - sx) ** 2; k = lab[ys[d.argmin()], xs[d.argmin()]]
    keep = nd.binary_dilation(lab == k, iterations=2)
    A[~keep, :3] = 255
    return Image.fromarray(A)


def card_img(c, pid, name):
    m = Image.new('L', c.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, c.size[0] - 1, c.size[1] - 1), radius=RADIUS, fill=255)
    c.putalpha(m)
    c.save(os.path.join(OUT, pid + '.png'), optimize=True)
    w, h = c.size
    if h > DISPLAY_H: c = c.resize((round(w * DISPLAY_H / h), DISPLAY_H), Image.LANCZOS)
    c.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
    print(pid, name, c.size)


def main():
    os.makedirs(WEB, exist_ok=True)
    sheet = Image.open(SRC).convert('RGBA')
    for pid, row, col, name in CARDS:
        card_img(only_them(sheet, BOXES[pid], SEEDS[pid]), pid, name)
    s8 = Image.open(SRC8).convert('RGBA')
    paint = ImageDraw.Draw(s8)
    for pid, b, name, outs in CARDS8:
        for r in outs: paint.rectangle(r, fill=(255, 255, 255, 255))
    # v2.4 rc6 (the full release check, 2026-10-02 13:40): the scattered sheet too — Momo's box still held a corner of
    # 老周師傅's tray and 小威's a piece of 小魏's sleeve; everything that does not touch the person's own drawing (the
    # largest drawing in the box) is painted with the sheet's white, as for the twelve
    for pid, b, name, outs in CARDS8:
        card_img(only_them(s8, b, None), pid, name)


if __name__ == '__main__':
    main()
