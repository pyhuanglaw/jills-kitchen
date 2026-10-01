#!/usr/bin/env python3
"""v2.4 (2026-10-01): the dialogue portraits for the 怡君 / 《那面牆》 stories, cut as cards (rounded corners, the sheet's
own background kept, nothing redrawn, stretched or recoloured) and packed by tools/portraits.py.

- 怡君, from the player's outside-cast sheet (docs/v24/refs/outside_cast_reference_2026-10-01.png, left column): the
  large panel is her portrait; the two small panels under it are her laugh and her side look (they are small on the
  sheet, so they show softer).
- 怡君's two expressions for 《那面牆》, supplied by the player at 14:29 (sheet_yijun_tones_v24.jpg): 漏水後 (tired)
  and 鬆一口氣 (relieved).
- 王先生's two, supplied by the player at 14:35 (sheet_wang_tones_v24.jpg): 等一下 (lawyer mode, looking up from the
  paper) and 淡淡的笑 (the faint smile).
- Mia's 認真看, supplied by the player at 14:43 (sheet_mia_tone_v24.jpg): looking hard at the photo of the wall.
- 房東 (the Second Floor's landlord, a new person), supplied by the player at 14:50 (sheet_landlord_v24.jpg): his
  portrait, ordinary talk, and the mild surprise of 「整層？」 — cut from the head to the belt like the others' cards.
- 秀琴阿姨's three expressions, supplied by the player at 14:27 (assets/portraits/src/sheet_xiuqin_tones_v24.jpg, the
  labels under each figure are left out): 心神不寧 (worried), 講電話 (phone), 「喔～～」 (oh). Her everyday portrait stays
  st23_xiuqin.
- 許葳 (the Lounge's cleaner, a new person), supplied by the player at 19:11 (sheet_xuwei_v24.jpg): the large face is her
  portrait; the four expressions are 工作中, 淺笑, 覺得好笑, 已經處理好了 (the labels are left out).

  python3 tools/portraits_v24.py && python3 tools/portraits.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'portraits')
WEB = os.path.join(OUT, 'web')
DISPLAY_H = 480
WEBP_Q = 84
RADIUS = 18
YJ = os.path.join(ROOT, 'docs', 'v24', 'refs', 'outside_cast_reference_2026-10-01.png')
XQ = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_xiuqin_tones_v24.jpg')
YT = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_yijun_tones_v24.jpg')   # 2026-10-01 14:29, the player: 怡君 漏水後 / 鬆一口氣
WT = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_wang_tones_v24.jpg')     # 2026-10-01 14:35, the player: 王先生 等一下 / 淡淡的笑
MT = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_mia_tone_v24.jpg')       # 2026-10-01 14:43, the player: Mia 認真看 (the photo of the wall on her phone)
LT = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_landlord_v24.jpg')       # 2026-10-01 14:50, the player: 房東 (for the Second Floor) — 房東 / 平常 / 整層？
XW = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_xuwei_v24.jpg')          # 2026-10-01 19:11, the player: 許葳, the Lounge's cleaner — the large face, and four expressions
# (id, sheet, box, who / tone) — boxes in sheet px, found by the sheets' separators / the figures' ink
CARDS = [
    ('v24_yj', YJ, (0, 0, 436, 572), '怡君'),
    ('v24_yj_laugh', YJ, (0, 583, 219, 859), '怡君 laugh'),
    ('v24_yj_side', YJ, (227, 583, 436, 859), '怡君 side'),
    ('v24_xiuqin_worried', XQ, (203, 26, 1093, 1004), '秀琴阿姨 心神不寧'),
    ('v24_xiuqin_phone', XQ, (1309, 26, 2193, 1004), '秀琴阿姨 講電話'),
    ('v24_xiuqin_oh', XQ, (2429, 26, 3319, 1004), '秀琴阿姨 喔～～'),
    ('v24_yj_tired', YT, (76, 26, 1300, 1374), '怡君 漏水後'),
    ('v24_yj_relieved', YT, (1372, 26, 2584, 1374), '怡君 鬆一口氣'),
    ('v24_wang_wait', WT, (26, 86, 1366, 1404), '王先生 等一下'),
    ('v24_wang_smile', WT, (1410, 86, 2726, 1404), '王先生 淡淡的笑'),
    ('v24_mia_thinking', MT, (16, 36, 1648, 2284), 'Mia 認真看'),
    ('v24_landlord', LT, (133, 110, 900, 1150), '房東'),
    ('v24_landlord_talk', LT, (1018, 110, 1784, 1150), '房東 平常'),
    ('v24_landlord_surprised', LT, (1914, 107, 2680, 1150), '房東 整層？'),
    ('v24_xuwei', XW, (420, 108, 690, 548), '許葳 (Neutral, focused, 敏銳)'),
    ('v24_xuwei_work', XW, (708, 36, 966, 324), '許葳 Neutral/Working'),
    ('v24_xuwei_smile', XW, (984, 36, 1244, 324), '許葳 Small Smile'),
    ('v24_xuwei_amused', XW, (708, 352, 966, 640), '許葳 Mildly Amused'),
    ('v24_xuwei_done', XW, (984, 352, 1244, 640), '許葳 Deadpan/Already Done'),
]


def card(pid, sheet, box, name):
    c = Image.open(sheet).convert('RGBA').crop(box)
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
    for pid, sheet, box, name in CARDS:
        card(pid, sheet, box, name)


if __name__ == '__main__':
    main()
