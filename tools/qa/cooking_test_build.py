#!/usr/bin/env python3
"""料理測試版 — the private test page of the cooking branch (never the player's live URL; docs/RELEASE_CHECKLIST.md is for
releases, this is not one).

It is the artifact page tools/build_artifact.py writes, with two differences, both outside the game:
  - its name is 「Jill's Kitchen 料理測試版」, so it is never mistaken for the game the player plays;
  - the title screen has one panel, labelled 「測試用 · 只在料理測試版」, that loads the player's Day 30 save
    (tests/saves/player_day30.json: five cooks, the cold station, the oven, the coffee machine) through the game's own
    import (it opens 設定・存檔, pastes the backup and presses 恢復; the game asks to confirm, as always), so the new
    kitchen can be seen mid-game on a phone without moving a save between URLs. Saves live with each URL: the player's
    game on the live URL is untouched.
Nothing in js/ knows about the panel.

  python3 tools/qa/cooking_test_build.py OUT.html
"""
import os, sys, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1]
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_artifact.py'), OUT], check=True)
page = open(OUT, encoding='utf-8').read()
name = "<title>Jill's Kitchen</title>"
assert page.count(name) == 1, 'the page has its title once'
page = page.replace(name, "<title>Jill's Kitchen 料理測試版</title>", 1)
save_text = open(os.path.join(ROOT, 'tests', 'saves', 'player_day30.json'), encoding='utf-8').read()
json.loads(save_text)   # a real save file, or stop here
PANEL = r"""
<script>/* 料理測試版 only (tools/qa/cooking_test_build.py) — not part of the game */
(function(){var SAVE=%s;
 function put(){var t=document.querySelector('#screen .title');if(!t||t.querySelector('#tbLoad'))return;
  var d=document.createElement('div');d.id='tbLoad';
  d.style.cssText='margin:16px auto 0;max-width:300px;padding:9px 12px 10px;border:1.5px dashed rgba(46,32,25,.35);border-radius:12px;background:rgba(255,248,236,.92);color:#2E2019;font-size:12px;line-height:1.55;text-align:left';
  d.innerHTML='<div style="font-weight:800;letter-spacing:.04em;color:#8E6422">測試用 · 只在料理測試版</div>'+
   '<div>載入你的第 30 天存檔（五位廚師、冷盤台、烤箱、咖啡機），直接看新廚房。只換掉這個測試版裡的進度，正式版的存檔不受影響。</div>'+
   '<button class="btn sm" id="tbBtn" style="margin-top:7px">載入第 30 天存檔</button>';
  t.appendChild(d);
  /* the game's own way in (設定・存檔 → 貼上以前的備份文字恢復 → 恢復), so its own confirmation comes up */
  var q=function(sel){return document.querySelector(sel)},b=d.querySelector('#tbBtn');
  b.addEventListener('click',function(e){e.stopPropagation();var s=q('[data-act=settings]');if(!s){b.textContent='找不到設定・存檔';return}s.click();
   setTimeout(function(){var p=q('[data-act=pasteBackup]');if(!p)return;p.click();
    setTimeout(function(){var a=q('#pasteArea'),g=q('[data-act=pasteGo]');if(!a||!g)return;a.value=JSON.stringify(SAVE);g.click()},150)},150)})}
 setInterval(put,600)})();
</script>
""" % save_text
page = page.rstrip() + '\n' + PANEL
open(OUT, 'w', encoding='utf-8').write(page)
print(f'wrote {OUT} ({len(page.encode("utf-8")) / 1e6:.1f} MB)')
