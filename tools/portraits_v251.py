#!/usr/bin/env python3
"""2026-10-10 (the user, after v2.5.1, docs/v24/waiters_8_9_2026-10-10.txt): the eighth and ninth waiters' card portraits, from
the user's own pictures — 「收到圖片後，以我提供的圖片作為最高優先級外觀參考，不得擅自重新生成或大幅修改人物外型」. Cut as cards like
the other staff (tools/portraits_staff_v23.py, tools/portraits_v24.py): a box chosen by eye, rounded corners, the sheet's own
background kept; nothing redrawn, stretched or recoloured. Packed by tools/portraits.py.

- 小夏 (sheet_xia_v251.png, supplied 2026-10-10 11:20 UTC): the sheet has three panels — standing, a smiling bust facing
  us, a three-quarter bust; the card is the middle one (her hair, the clip and her smile all show), from the top of the
  sheet to the panel's own lower edge.

  python3 tools/portraits_v251.py && python3 tools/portraits.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'portraits', 'src')
OUT = os.path.join(ROOT, 'assets', 'portraits')
WEB = os.path.join(OUT, 'web')
DISPLAY_H = 480
WEBP_Q = 84
RADIUS = 18
# (id, sheet, box in sheet px, name)
CARDS = [
    ('st251_xia', 'sheet_xia_v251.png', (368, 0, 945, 905), '小夏'),
]


def card(pid, sheet, box, name):
    c = Image.open(os.path.join(SRC, sheet)).convert('RGBA').crop(box)
    m = Image.new('L', c.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, c.size[0] - 1, c.size[1] - 1), radius=RADIUS, fill=255)
    c.putalpha(m)
    c.save(os.path.join(OUT, pid + '.png'), optimize=True)
    w, h = c.size
    if h > DISPLAY_H: c = c.resize((round(w * DISPLAY_H / h), DISPLAY_H), Image.LANCZOS)
    c.save(os.path.join(WEB, pid + '.webp'), 'WEBP', quality=WEBP_Q, method=6)
    print(pid, name, c.size)


if __name__ == '__main__':
    for pid, sheet, box, name in CARDS:
        card(pid, sheet, box, name)
