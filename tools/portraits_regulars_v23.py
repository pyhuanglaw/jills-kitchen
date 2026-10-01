#!/usr/bin/env python3
"""v2.3 follow-up (2026-10-01): Sophie's and Mia's portraits, from the illustrated Sophie × Mia sheet the player
supplied (assets/portraits/src/sophie_mia_sheet_anime_v23.png, white background) — each one's main panel. They now
match their story photos: Sophie with long dark hair and a black jacket, Mia with a messy ponytail, a cream shirt
and an apron. The other regulars keep their portraits (the player compared a new sheet with them: 陳伯伯, 王先生,
王太太 are the same people as before, and 小林 / Leo stay as they were).

Each figure is cut as a card: a box chosen by eye; the sheet's name label painted out with the sheet's white;
rounded corners; nothing keyed out. tools/portraits.py packs the result.

  python3 tools/portraits_regulars_v23.py && python3 tools/portraits.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SM = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sophie_mia_sheet_anime_v23.png')
OUT = os.path.join(ROOT, 'assets', 'portraits')
WEB = os.path.join(OUT, 'web')
DISPLAY_H = 480
WEBP_Q = 86
RADIUS = 16
# (id, regular, box, paint-outs) — sheet px
CARDS = [
    ('reg23_sophie', 'sophie', (125, 0, 432, 392), [(125, 20, 192, 100)]),   # the main Sophie panel; the name label painted out
    ('reg23_mia', 'mia', (800, 0, 1062, 402), []),                             # the main Mia panel
]


def main():
    os.makedirs(WEB, exist_ok=True)
    sheet = Image.open(SM).convert('RGBA')
    for pid, reg, box, outs in CARDS:
        sh = sheet.copy()
        paint = ImageDraw.Draw(sh)
        for r in outs:
            paint.rectangle(r, fill=(255, 255, 255, 255))
        c = sh.crop(box)
        m = Image.new('L', c.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, c.size[0] - 1, c.size[1] - 1), radius=RADIUS, fill=255)
        c.putalpha(m)
        c.save(os.path.join(OUT, pid + '.png'), optimize=True)
        w, h = c.size
        if h > DISPLAY_H:
            c = c.resize((round(w * DISPLAY_H / h), DISPLAY_H), Image.LANCZOS)
        c.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
        print(pid, reg, c.size)


if __name__ == '__main__':
    main()
