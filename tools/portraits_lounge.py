#!/usr/bin/env python3
"""v2.3: the four Lounge staff (Evan, 沈晴, 阿拓, 安安) as card portraits, cut from the approved concept sheets in docs/v23
(docs/v23/lounge_cast_concept.png and qing_tuo_ken_du_concept.png). Rectangular head-and-shoulders crops with rounded
corners, like the named guests' cards (tools/portraits_named.py); nothing redrawn or recoloured. Identity is by name
(STAFF_PORTRAITS in js/game.js), never by order. Transparent-background versions are pending from the author.

  python3 tools/portraits_lounge.py   # writes assets/portraits/<id>.png + web/<id>.webp; then run tools/portraits.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'portraits'); WEB = os.path.join(OUT, 'web')
DISPLAY_H = 480; WEBP_Q = 84; RADIUS = 18
A = os.path.join(ROOT, 'docs', 'v23', 'lounge_cast_concept.png')
B = os.path.join(ROOT, 'docs', 'v23', 'qing_tuo_ken_du_concept.png')
# v2.4 rc6 (the player, 2026-10-02 09:33): 阿拓 is the short-haired cook in the white chef's jacket of the Lounge cast sheet
# (and of the two 晴 × 阿拓 pictures) — the crop from the second sheet showed someone with Evan's wavy hair
CARDS = [('staff_evan', A, (215, 70, 384, 300)), ('staff_qing', B, (275, 10, 545, 340)), ('staff_tuo', A, (972, 60, 1158, 340)), ('staff_anan', A, (1360, 90, 1536, 300))]


def main():
    os.makedirs(WEB, exist_ok=True)
    for pid, src, box in CARDS:
        c = Image.open(src).convert('RGBA').crop(box)
        m = Image.new('L', c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.size[0] - 1, c.size[1] - 1), radius=RADIUS, fill=255); c.putalpha(m)
        c.save(os.path.join(OUT, pid + '.png'), optimize=True)
        w = c if c.size[1] <= DISPLAY_H else c.resize((round(c.size[0] * DISPLAY_H / c.size[1]), DISPLAY_H), Image.LANCZOS)
        w.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
        print(pid, c.size, '->', w.size)


if __name__ == '__main__':
    main()
