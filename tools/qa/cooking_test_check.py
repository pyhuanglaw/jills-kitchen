"""Smoke check of the private test page built by tools/qa/cooking_test_build.py (before publishing it): the page opens with
no script error, the test panel loads the Day 30 save through the game's own import, the restaurant opens. Screenshots
next to the page (title.png, after_tap.png, after_open.png).
  python3 tools/qa/cooking_test_build.py OUT/cooking-test.html && python3 tools/qa/cooking_test_check.py OUT/cooking-test.html"""
import sys, os, http.server, threading, functools
page_path = os.path.abspath(sys.argv[1]); D = os.path.dirname(page_path)
page = open(page_path, encoding='utf-8').read()
html = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + page + '</body></html>')
open(os.path.join(D, 'wrapped.html'), 'w', encoding='utf-8').write(html)
from playwright.sync_api import sync_playwright
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=D)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/wrapped.html'); pg.wait_for_timeout(2500)
    pg.screenshot(path=os.path.join(D, 'title.png'))
    pg.click('#tbBtn'); pg.wait_for_timeout(1500)
    acts = pg.evaluate("[...document.querySelectorAll('#screen [data-act]')].map(e=>e.dataset.act+':'+e.textContent.trim().slice(0,14))")
    print('after tap, buttons:', acts[:14])
    pg.screenshot(path=os.path.join(D, 'after_tap.png'))
    ok = [a for a in acts if a.split(':')[0] in ('importConfirm', 'importOk', 'impYes', 'importYes')]
    print('confirm:', ok)
    if ok:
        pg.click(f"#screen [data-act={ok[0].split(':')[0]}]"); pg.wait_for_timeout(1500)
        print('title now:', pg.evaluate("(document.querySelector('#screen .title .cont')||{}).textContent"))
        pg.click('[data-act=open]'); pg.wait_for_timeout(2500)
        print('after open:', pg.evaluate("document.querySelector('#screen')?document.querySelector('#screen').innerText.slice(0,120):''").replace('\n', ' | '))
        pg.screenshot(path=os.path.join(D, 'after_open.png'))
    print('errors:', errs[:3])
    b.close()
srv.shutdown()
