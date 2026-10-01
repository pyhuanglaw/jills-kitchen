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


def main():
    os.makedirs(WEB, exist_ok=True)
    sheet = Image.open(SRC).convert('RGBA')
    for pid, row, col, name in CARDS:
        card(sheet, box(row, col), pid, name)
    s8 = Image.open(SRC8).convert('RGBA')
    paint = ImageDraw.Draw(s8)
    for pid, b, name, outs in CARDS8:
        for r in outs: paint.rectangle(r, fill=(255, 255, 255, 255))
    for pid, b, name, outs in CARDS8:
        card(s8, b, pid, name)


if __name__ == '__main__':
    main()
