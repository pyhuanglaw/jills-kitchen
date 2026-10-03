"""Story Photo art (and the v2.4 story illustrations): crops of the approved concept sheets (docs/v23/story_photos_*.png), by stable key, packed as
js/story_art.js (window.STORY_ART). Panels are cut inside their frames so no sheet caption ends up in the picture;
the album carries the title. 720x540 WebP (the album shows 360x270)."""
import base64, io, os, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAL = os.path.join(ROOT, 'docs/v23/story_photo_jill_dylan_valentine.png')   # 2026-10-01, supplied by the player: Dylan × Jill, Valentine's
WANG = os.path.join(ROOT, 'docs/v23/story_photo_wang_anniv.jpg')             # 2026-10-01, supplied by the player: 王先生 × 王太太, the anniversary
MEAL = os.path.join(ROOT, 'docs/v23/story_photo_staff_meal.png')             # 2026-10-01, supplied by the player (second version, made to the spec): the staff meal
QT = os.path.join(ROOT, 'docs/v23/story_photo_qing_tuo.png')                 # 2026-10-01, supplied by the player: 「多的」 as a full picture (was a small panel of the concept sheet)
QTL = os.path.join(ROOT, 'docs/v23/story_photo_qing_tuo_late.png')           # 2026-10-01, supplied by the player: 「有你在的晚班」 as a full picture (was a small panel of the concept sheet)
SML = os.path.join(ROOT, 'docs/v23/story_photo_sophie_mia_leave.png')       # 2026-10-01, supplied by the player: Sophie × Mia 「一起回家」 as a full picture (was a small panel of the concept sheet)
KDS = os.path.join(ROOT, 'docs/v23/story_photo_ken_du_seat.png')            # 2026-10-01, supplied by the player: Ken × 杜 「固定的位置」 as a full picture (was a small panel of the concept sheet)
KDA = os.path.join(ROOT, 'docs/v23/story_photo_ken_du.png')                 # 2026-10-01, supplied by the player: Ken × 杜 「還是沒有同意」 as a full picture (was a small panel of the concept sheet)
SMA = os.path.join(ROOT, 'docs/v23/story_photo_sophie_mia_arrive.png')      # 2026-10-01, supplied by the player: Sophie × Mia 「今天一起來」, illustrated like 「一起回家」 (was the concept sheet's top banner)
# v2.4 story illustrations (STORY_ILLUS in game.js): event pictures shown with a scene, not album photos
YJI = os.path.join(ROOT, 'docs/v24/art/illus_yj_intro_2026-10-01.png')        # 2026-10-01 13:53, supplied by the player: 怡君 eating, 秀琴阿姨 at her table with the spray bottle and cloth
YJK = os.path.join(ROOT, 'docs/v24/art/illus_yj_key_2026-10-01.png')          # 2026-10-01 13:57, supplied by the player: 怡君's new flat, the spare key — the room 《那面牆》 returns to
WLK = os.path.join(ROOT, 'docs/v24/art/illus_wall_leak_2026-10-01.png')       # 2026-10-01 14:14, supplied by the player (second version: Sophie as she looks, hair down, black jacket): the same room after the rain — the stained corner, Mia with the light, Sophie with the photos
WST = os.path.join(ROOT, 'docs/v24/art/illus_wall_settled_2026-10-01.png')    # 2026-10-01 14:13, supplied by the player: after the mediation — 怡君 and 王先生 in the corridor, restrained
UPC = os.path.join(ROOT, 'docs/v24/art/illus_up_cats_2026-10-02_0841.png')    # 2026-10-02 08:41, supplied by the player (「去二樓發現貓的圖 修改成這一張」, replacing the 08:15 picture): the night of the missing cats — the empty floor at night from above, the two street windows with the city, the orange cat on the sill, Jill bending to the tabby, the column, the boxes and the ladder, two of the crew at the stairs (a portrait picture: kept whole, not cut to 4:3)
KT1 = os.path.join(ROOT, 'docs/v24/art/illus_ken_t1_2026-10-02_1619.png')    # 2026-10-02 16:19, supplied by the player: Ken's first tasting — Ken behind the bar with a glass, the bottles and the decanter, guests on the stools
KWN = os.path.join(ROOT, 'docs/v24/art/illus_ken_wine_2026-10-02_1625.png')  # 2026-10-02 16:25, supplied by the player: the collaboration wine — the bottle, its label 「晚餐之後」 JILL'S KITCHEN × KEN, a glass poured
DWN = os.path.join(ROOT, 'docs/v24/art/illus_du_wine_2026-10-02_1632.png')   # 2026-10-02 16:32, supplied by the player: 杜先生 tasting 「晚餐之後」 at the bar, Ken beside him, quiet
YAT = os.path.join(ROOT, 'docs/v24/art/illus_ya_trial_2026-10-02_1654.png')  # 2026-10-02 16:54, supplied by the player: 予安's trial — the piece just ended, 王太太 at the piano 「彈得真好。」, 王先生 smiling behind, a few tables clapping, Jill at the bar
YAF = os.path.join(ROOT, 'docs/v24/art/illus_ya_first_2026-10-02_1657.png')  # 2026-10-02 16:57, supplied by the player: 予安's first evening as a guest — a small table, a glass of red, her eyes on the piano nobody plays
YAJ = os.path.join(ROOT, 'docs/v24/art/illus_ya_join_2026-10-02_1659.png')   # 2026-10-02 16:59, supplied by the player: after the trial, the room thinner — Jill and 予安 at the bar, 「下週還有空嗎？」
LHI = os.path.join(ROOT, 'docs/v24/art/illus_lin_hello_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《隔壁》 — Day 1 at the door, Madame Lin handing Jill the small box
DBK = os.path.join(ROOT, 'docs/v24/art/illus_dylan_book_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《一本不一樣的書》 — Dylan from behind at his desk (hoodie, headphones), the dark bar-design book among the exam books, Jill looking at it
LVW = os.path.join(ROOT, 'docs/v24/art/illus_lin_viewing_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《看看》 — Madame Lin's own bar before opening (terrazzo, the old bar, red stools, the turntable), Madame Lin showing Jill in, Evan polishing a glass behind the bar
LSG = os.path.join(ROOT, 'docs/v24/art/illus_lin_sign_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《簽約》 — the same bar, closed, in the morning: the contract, the pen and the keys on the bar top, Jill signing, Madame Lin beside her, Evan, Dylan from behind
LGU = os.path.join(ROOT, 'docs/v24/art/illus_lin_guest_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《你選》 — Madame Lin on the guest side of The Lounge's bar for the first time, the drinks list open, Evan behind the bar waiting
QTF = os.path.join(ROOT, 'docs/v24/art/illus_qt_first_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《今天喝？》 — Dylan's first drink at The Lounge's bar, a glass in front of him, Evan behind the bar polishing a glass
QTM = os.path.join(ROOT, 'docs/v24/art/illus_qt_more_2026-10-03.webp')   # 2026-10-03, supplied by the player: 《最近比較常》 — the bar after closing: 阿拓 pours for 沈晴, 予安 beside them, Evan behind the bar, Dylan with his glass
QTL2 = os.path.join(ROOT, 'docs/v24/art/illus_qt_lesson_2026-10-03.webp')  # 2026-10-03, supplied by the player: 《你喜歡予安？》 — 予安 beside 阿拓 at the black grand piano, one finger each on the keys; Dylan and Evan at the bar with their glasses, watching; 沈晴 away
QTP = os.path.join(ROOT, 'docs/v24/art/illus_qt_play_2026-10-03.webp')    # 2026-10-03, supplied by the player: 《講完》 — 阿拓 at the piano, one finger on a key; 沈晴 leaning on the piano, looking at him; Evan, 予安 and Dylan far back at the bar
QTA = os.path.join(ROOT, 'docs/v24/art/illus_qt_alone_2026-10-03.webp')   # 2026-10-03, supplied by the player: 《難怪》 — the empty Lounge from afar, the door shut, part of it dark; 阿拓 on the piano bench, 沈晴 standing by the piano
# key -> (sheet, box). Boxes chosen by eye on the sheets; 4:3 is enforced by a centered crop of the box.
ART = {
    'sophie_mia_leave':  (SML, (15, 0, 1380, 1024)),    # 《一起回家》 — Sophie and Mia arm in arm on the way out, the cat on the counter behind them (the player's full picture, 2026-10-01)
    'sophie_mia_arrive': (SMA, (171, 0, 1536, 1024)),   # 《今天一起來》 — Sophie and Mia coming in together, a server and the cat on the counter behind them (the player's picture, 2026-10-01)
    'ken_du':            (KDA, (120, 0, 1485, 1024)),   # 《還是沒有同意》 — Ken making his case with his hands, 杜 unconvinced, chin in hand (the player's full picture, 2026-10-01)
    'ken_du_seat':       (KDS, (120, 0, 1485, 1024)),   # 《固定的位置》 — Ken and 杜 side by side at the bar, wine and small plates (the player's full picture, 2026-10-01)
    'qing_tuo':          (QT, (60, 0, 1425, 1024)),     # 《多的》 — 阿拓 sets the small plate down beside 晴 (the player's full picture, 2026-10-01)
    'qing_tuo_late':     (QTL, (100, 0, 1465, 1024)),   # 《有你在的晚班》 — 阿拓 plating at the bar, 晴 stirring a drink and smiling up at him (the player's full picture, 2026-10-01)
    'jill_dylan_valentine': (VAL, (150, 0, 1515, 1024)), # 《情人節，還在追》 — both of them, the cake, the cat asleep on the counter
    'wang_anniv':        (WANG, (0, 70, 1093, 890)),     # 《今年也在這裡》 — the gift, both faces, the anniversary box
    'staff_meal':        (MEAL, (120, 0, 1485, 1024)),   # 《開店前》 — the player's second version (to spec): the whole crew, the two cats, the room; every face kept whole
    'yj_intro':          (YJI, (0, 0, 1448, 1086)),      # v2.4 illustration 《吃飯啊》 — 怡君 at her table, 秀琴阿姨 leaning on the chair beside her (the player's picture, whole)
    'yj_key':            (YJK, (0, 0, 1448, 1086)),      # v2.4 illustration 《備用鑰匙》 — the key handed over in the half-unpacked flat (the player's picture, whole)
    'wall_leak':         (WLK, (0, 0, 1448, 1086)),      # v2.4 illustration 《那面牆》 — the same room and wall weeks later, after the rain (the player's picture, whole)
    'wall_settled':      (WST, (0, 0, 1448, 1086)),      # v2.4 illustration 《調解之後》 — 怡君 and 王先生 walking out of the mediation, files under their arms (the player's picture, whole)
    'up_cats':           (UPC, (18, 16, 1106, 1386)),    # v2.4 illustration 《樓上》 — the night the two cats were found upstairs (the player's 08:41 picture, whole, portrait; the white margin and the sliver of the next panel left out)
    'ken_t1':            (KT1, (0, 0, 1448, 1086)),      # rc7 illustration 《Ken 的品酒夜》 — the first tasting, Ken hosting from behind the bar (the player's picture, whole)
    'ken_wine':          (KWN, (0, 0, 1448, 1086)),      # rc7 illustration 《晚餐之後》 — the collaboration wine on the bar (the player's picture, whole)
    'du_wine':           (DWN, (0, 0, 1448, 1086)),      # rc7 illustration 《可是它很好》 — 杜先生 with the glass, Ken watching him, the bottle between them (the player's picture, whole)
    'ya_trial':          (YAT, (0, 0, 1448, 1086)),      # rc7 illustration 《彈得真好》 — the trial at the Lounge's piano (the player's picture, whole)
    'ya_first':          (YAF, (0, 0, 1448, 1086)),      # rc7 illustration 《那台鋼琴》 — 予安 at a small table, looking at the piano (the player's picture, whole)
    'ya_join':           (YAJ, (0, 0, 1448, 1086)),      # rc7 illustration 《星期幾？》 — Jill and 予安 at the bar after the trial (the player's picture, whole)
    'lin_hello':         (LHI, (0, 0, 1448, 1086)),      # rc8 illustration 《隔壁》 — Madame Lin's present at the door, Day 1 (the player's picture, whole)
    'dylan_book':        (DBK, (0, 0, 1448, 1086)),      # rc8 illustration 《一本不一樣的書》 — the book on the exam books; Dylan's face never shown (the player's picture, whole)
    'lin_viewing':       (LVW, (0, 0, 1448, 1086)),      # rc8 illustration 《看看》 — her bar, Evan behind it (the player's picture, whole)
    'lin_sign':          (LSG, (0, 0, 1448, 1086)),      # rc8 illustration 《簽約》 — the contract, the pen, the keys; Dylan's face never shown (the player's picture, whole)
    'lin_guest':         (LGU, (0, 0, 1448, 1086)),      # rc8 illustration 《你選》 — Madame Lin at The Lounge's bar with the list, Evan waiting (the player's picture, whole)
    'qt_first':          (QTF, (0, 0, 1448, 1086)),      # rc8 illustration 《今天喝？》 — Dylan at The Lounge's bar, Evan behind it (the player's picture, whole)
    'qt_more':           (QTM, (0, 0, 1448, 1086)),      # rc8 illustration 《最近比較常》 — 阿拓 pours for 沈晴 after closing (the player's picture, whole)
    'qt_lesson':         (QTL2, (0, 0, 1448, 1086)),     # rc8 illustration 《你喜歡予安？》 — 予安 shows 阿拓 the five notes (the player's picture, whole)
    'qt_play':           (QTP, (0, 0, 1448, 1086)),      # rc8 illustration 《講完》 — 阿拓 plays them for 沈晴 (the player's picture, whole)
    'qt_alone':          (QTA, (0, 0, 1448, 1086)),      # rc8 illustration 《難怪》 — the two of them left in the Lounge (the player's picture, whole)
}
KEEP = {'up_cats': 760}   # pictures kept whole at their own proportions (height in px); the dialog shows them contained
def crop43(im, box):
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    if w / h > 4 / 3: nw = int(h * 4 / 3); x0 += (w - nw) // 2; x1 = x0 + nw
    else: nh = int(w * 3 / 4); y0 += (h - nh) // 2; y1 = y0 + nh
    return im.crop((x0, y0, x1, y1)).resize((720, 540), Image.LANCZOS)
def main():
    out = {}
    for k, (sheet, box) in ART.items():
        im = Image.open(sheet).convert('RGB')
        if k in KEEP: im = im.crop(box) if box else im; h = KEEP[k]; c = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        else: c = crop43(im, box)
        buf = io.BytesIO(); c.save(buf, 'WEBP', quality=82, method=6)
        out[k] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
        if '--png' in sys.argv:
            os.makedirs(os.path.join(ROOT, 'docs/evidence/v23/story_art'), exist_ok=True)
            c.save(os.path.join(ROOT, 'docs/evidence/v23/story_art', k + '.png'))
    js = '/* generated by tools/story_art.py — Story Photo art cut from the approved concept sheets, by stable key */\nwindow.STORY_ART=' + __import__('json').dumps(out, ensure_ascii=False) + ';\n'
    open(os.path.join(ROOT, 'js/story_art.js'), 'w', encoding='utf-8').write(js)
    print('story_art.js', len(js) // 1024, 'KB,', len(out), 'pictures')
if __name__ == '__main__': main()
