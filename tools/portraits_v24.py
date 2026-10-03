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
- rc7: Ken's three expressions for his tastings, supplied by the player at 16:21 with his glasses (sheet_ken_tones_v24.png; 16:12's had none): 主持 (talking,
  a hand out, the glass in the other), 乾笑 (the dry smile that knew it), 品酒 (nosing the glass). 杜先生's three, at
  16:14 (sheet_du_tones_v24.png): 品酒 (tasting, saying nothing), 不以為然, 真心稱讚 (restrained, sincere).
- v2.4 P5 (rc7): the rest of the outside cast — Kevin, 珊珊, 宇翔 from the first sheet (its other three columns), and
  小彤's mother, 小彤's father, 老林, 國雄 from the second (docs/v24/refs/outside_cast_2_reference_2026-10-01.png),
  each with the two expressions under the portrait.

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
OC2 = os.path.join(ROOT, 'docs', 'v24', 'refs', 'outside_cast_2_reference_2026-10-01.png')   # 2026-10-01 11:44, the player: 小彤's mother and father, 老林, 國雄
KT = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_ken_tones_v24.png')   # 2026-10-02 16:21, the player: Ken 主持 / 乾笑 / 品酒, with his glasses (replacing 16:12's, which had none); the labels under each are left out
DT = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_du_tones_v24.png')    # 2026-10-02 16:14, the player: 杜先生 品酒 / 不以為然 / 真心稱讚
YA = os.path.join(ROOT, 'assets', 'portraits', 'src', 'sheet_yuan_v24.png')       # 2026-10-02 16:42, the player: 林予安, the Lounge's pianist (docs/v24/pianist_yuan_2026-10-02_1642.txt) — 平常 / 演奏 / 淺笑
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
    ('v24_xuwei', XW, (420, 150, 690, 525), '許葳 (Neutral, focused, 敏銳)'),   # v2.4 rc6 (the player, 09:53): her card showed only the top of her face — less above the head, so a card shows the whole face, as the others' do
    ('v24_xuwei_work', XW, (708, 36, 966, 324), '許葳 Neutral/Working'),
    ('v24_xuwei_smile', XW, (984, 36, 1244, 324), '許葳 Small Smile'),
    ('v24_xuwei_amused', XW, (708, 352, 966, 640), '許葳 Mildly Amused'),
    ('v24_xuwei_done', XW, (984, 352, 1244, 640), '許葳 Deadpan/Already Done'),
    # v2.4 P5 (rc7): the rest of the two outside-cast sheets (2026-10-01 11:42 / 11:44). Each column is one person: the
    # large panel is the portrait, the two small ones under it two expressions. Boxes inside the sheets' light
    # separators (measured: columns 437–443 / 884–888 / 1330–1335 and 442–448 / 883–890 / 1325–1333; the small panels'
    # own at 674–677, 1110–1114, 1566–1569 and 659–663, 1102–1106, 1546–1548), so no neighbour's edge comes along.
    ('v24_kevin', YJ, (445, 0, 883, 572), 'Kevin'),
    ('v24_kevin_laugh', YJ, (445, 583, 673, 859), 'Kevin laugh'),
    ('v24_kevin_side', YJ, (679, 583, 883, 859), 'Kevin side'),
    ('v24_shan', YJ, (890, 0, 1329, 572), '珊珊'),
    ('v24_shan_smile', YJ, (890, 583, 1109, 859), '珊珊 smile'),
    ('v24_shan_down', YJ, (1116, 583, 1329, 859), '珊珊 looking down'),
    ('v24_yx', YJ, (1337, 0, 1774, 572), '宇翔'),
    ('v24_yx_smile', YJ, (1337, 583, 1565, 859), '宇翔 smile'),
    ('v24_yx_side', YJ, (1571, 583, 1774, 859), '宇翔 side'),
    ('v24_xtm', OC2, (0, 17, 441, 572), '小彤的媽媽'),
    ('v24_xtm_smile', OC2, (0, 580, 220, 859), '小彤的媽媽 smile'),
    ('v24_xtm_laugh', OC2, (226, 580, 440, 859), '小彤的媽媽 laugh'),
    ('v24_xtf', OC2, (450, 17, 882, 572), '小彤的爸爸'),
    ('v24_xtf_smile', OC2, (450, 580, 658, 859), '小彤的爸爸 smile'),
    ('v24_xtf_side', OC2, (665, 580, 882, 859), '小彤的爸爸 side'),
    ('v24_lin', OC2, (892, 17, 1324, 572), '老林'),
    ('v24_lin_grin', OC2, (892, 580, 1101, 859), '老林 grin'),
    ('v24_lin_laugh', OC2, (1108, 580, 1324, 859), '老林 laugh'),
    ('v24_gx', OC2, (1334, 17, 1774, 572), '國雄'),
    ('v24_gx_front', OC2, (1334, 580, 1545, 859), '國雄 front'),
    ('v24_gx_side', OC2, (1550, 580, 1774, 859), '國雄 side'),
    # rc7: Ken's three (the 16:21 sheet, with his glasses), the same 630×678 window on each (the figures are cut by a straight line at y 696–697)
    ('v24_ken_talk', KT, (0, 20, 630, 698), 'Ken 主持'),
    ('v24_ken_wry', KT, (631, 20, 1261, 698), 'Ken 乾笑'),
    ('v24_ken_taste', KT, (1290, 20, 1920, 698), 'Ken 品酒'),
    # rc7: 杜先生's three, a 634×676 window on each (cut at y 695)
    ('v24_du_taste', DT, (0, 20, 634, 696), '杜先生 品酒'),
    ('v24_du_doubt', DT, (635, 20, 1269, 696), '杜先生 不以為然'),
    ('v24_du_praise', DT, (1284, 20, 1918, 696), '杜先生 真心稱讚'),
    # rc7: 林予安's three, a 582×686 window on each (the panels are cut by a straight line at y 690)
    ('v24_yuan', YA, (37, 4, 619, 690), '林予安 平常'),
    ('v24_yuan_play', YA, (666, 4, 1248, 690), '林予安 演奏'),
    ('v24_yuan_smile', YA, (1315, 4, 1897, 690), '林予安 淺笑'),
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
