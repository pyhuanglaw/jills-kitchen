"""The dishes' frames from tools/qa/dish_frames.py as one sheet to look at on a phone: a row per dish, each frame cropped
close around the food (the plating frames whole, the plates being beside it), labelled with the place and the beat in the
user's words. What the user's choreography spec asks to see (docs/v24/cooking_choreography_2026-10-08.txt §I): the dish
at the start of its place, each visible change, done, plated.
  python3 tools/qa/dish_sheet.py FRAMES_DIR OUT.png DISH [DISH ...]"""
import sys, os, re, html as H
from playwright.sync_api import sync_playwright
from PIL import Image
src, out, DISHES = sys.argv[1], sys.argv[2], sys.argv[3:]
NAMES = {'friedrice': '黃金蛋炒飯', 'coffee': '拿鐵咖啡', 'blacktea': '錫蘭檸檬紅茶', 'sparkling': '檸檬氣泡水', 'salad': '田園沙拉', 'pasta': '番茄義大利麵', 'soup': '南瓜濃湯',
         'burger': '經典牛肉漢堡', 'pudding': '焦糖布丁', 'fries': '松露薯條', 'fruitsoda': '莓果蘇打', 'veg': '香料烤蔬菜',
         'tiramisu': '提拉米蘇', 'chicken': '香草烤雞', 'steak': '炙烤肋眼牛排', 'basque': '巴斯克乳酪蛋糕', 'prosciutto': '生火腿沙拉',
         'salmon': '香烤鮭魚', 'seafood': '海鮮義大利麵', 'duck': '香煎鴨胸', 'risotto': '松露燉飯', 'souffle': '舒芙蕾',
         'bites': '炸雞塊', 'croquette': '起司可樂餅', 'cheeseplate': '起司拼盤', 'mushroom': '蒜香蘑菇', 'wings': '水牛城雞翅', 'cheesestick': '起司條',
         'oyster': '生蠔', 'knuckle': '德國豬腳', 'pizza': '酒吧披薩', 'pzmarg': '瑪格麗特披薩', 'pzfungi': '蘑菇白醬披薩'}
tmp = os.path.join(src, '_sheet'); os.makedirs(tmp, exist_ok=True)
rows = []
for d in DISHES:
    page = open(os.path.join(src, f'{d}_strip.html'), encoding='utf-8').read()
    figs = re.findall(r'<figcaption>(.*?)</figcaption><img src="file://(.*?)">', page)
    cells = []
    for i, (cap, fn) in enumerate(figs):
        im = Image.open(fn); w, h = im.size
        whole = '裝盤' in cap or '端' in cap
        c = im if whole else im.crop((w // 2 - 130, int(h * .62) - 150, w // 2 + 130, int(h * .62) + 60))
        p = os.path.join(tmp, f'{d}_{i}.png'); c.save(p)
        cap = H.unescape(cap).replace('drink', '飲料').replace('prep', '備料').replace('hot', '熱區').replace('oven', '烤箱')
        cells.append(f'<figure><img src="file://{p}"><figcaption>{H.escape(cap)}</figcaption></figure>')
    rows.append(f'<h2>{H.escape(NAMES.get(d, d))}</h2><div class=row>{"".join(cells)}</div>')
doc = f"""<!doctype html><meta charset=utf-8><style>body{{margin:0;padding:8px 0 12px;background:#FAF6EE;font-family:'Noto Sans TC','PingFang TC',sans-serif;color:#2E2019;width:1180px}}
h2{{font-size:26px;margin:14px 16px 6px}}.row{{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px}}figure{{margin:0;width:180px}}img{{display:block;width:180px;height:146px;object-fit:cover;border-radius:8px}}
figcaption{{font-size:14px;font-weight:700;color:#7A5226;margin:3px 2px 6px;line-height:1.3}}</style>{''.join(rows)}"""
hp = os.path.join(tmp, 'sheet.html'); open(hp, 'w', encoding='utf-8').write(doc)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1180, 'height': 600}, device_scale_factor=1)
    pg.goto('file://' + hp); pg.wait_for_timeout(300); pg.screenshot(path=out, full_page=True); b.close()
print(out)
