#!/usr/bin/env python3
"""v2.2.1 H2: the supplementary sheet of named guests and staff. The author supplied it as framed cards
(assets/portraits/src/sheet_named_staff_18.png: each portrait painted inside a rounded card with its own background,
a label under it). These are used as *card portraits*: each card is cut by its frame (hand-chosen boxes, the label left
out), inset a few px, given rounded corners, and packed like the other portraits. No background keying — a second
sheet with a painted checkerboard exists in src/ but is not used (see docs/V221_REPORT.md).

  python3 tools/portraits_named.py   # writes assets/portraits/<id>.png + web/<id>.webp; then run tools/portraits.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_named_staff_18.png')
OUT = os.path.join(ROOT, 'assets', 'portraits')
WEB = os.path.join(OUT, 'web')
DISPLAY_H = 480
WEBP_Q = 84
INSET = 5
RADIUS = 18

# id → the card's frame on the sheet (sheet px)
CARDS = [
    ('zhou', (22, 45, 236, 280)), ('madame_lin', (275, 45, 489, 280)), ('mr_hart', (527, 45, 741, 280)),
    ('laotao_li', (780, 45, 994, 280)), ('monsieur_du', (1032, 45, 1246, 280)), ('ken', (1285, 45, 1499, 280)),
    ('critic', (22, 343, 236, 580)), ('xiaoqi', (275, 343, 489, 580)), ('blogger_momo', (549, 343, 801, 580)), ('inspector', (823, 343, 1077, 580)),
    ('staff_azhu', (22, 695, 190, 935)), ('staff_hugo', (210, 695, 378, 935)), ('staff_nina', (399, 695, 567, 935)), ('staff_azhe', (590, 695, 758, 935)),
    ('staff_momo', (780, 695, 948, 935)), ('staff_xiaotong', (970, 695, 1138, 935)), ('staff_aming', (1160, 695, 1328, 935)), ('staff_yuki', (1350, 695, 1518, 935)),
]


def main():
    os.makedirs(WEB, exist_ok=True)
    sheet = Image.open(SRC).convert('RGBA')
    for pid, (x0, y0, x1, y1) in CARDS:
        c = sheet.crop((x0 + INSET, y0 + INSET, x1 - INSET, y1 - INSET))
        m = Image.new('L', c.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, c.size[0] - 1, c.size[1] - 1), radius=RADIUS, fill=255)
        c.putalpha(m)
        c.save(os.path.join(OUT, pid + '.png'), optimize=True)
        w, h = c.size
        if h > DISPLAY_H: c = c.resize((round(w * DISPLAY_H / h), DISPLAY_H), Image.LANCZOS)
        c.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
        print(pid, c.size)


if __name__ == '__main__':
    main()
