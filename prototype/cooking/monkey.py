"""Random taps and drags all over the prototype, every night, checking that nothing breaks: no page error, every thing in
exactly one place, no tray pointing at a thing that is gone, no staff stuck carrying nothing.
  python3 prototype/cooking/monkey.py [--secs 25] [--seed 1]"""
import argparse, os, random, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--secs', type=float, default=25); ap.add_argument('--seed', type=int, default=1); A = ap.parse_args()
CHECK = r"""(()=>{const G=__cook.G;const bad=[];if(!G)return['no game'];const where={};
 for(const st in G.slots)G.slots[st].forEach((id,i)=>{if(!id)return;if(!G.items.has(id))bad.push('slot '+st+i+' -> gone '+id);where[id]=(where[id]||0)+1;const it=G.items.get(id);if(it&&(!it.at||it.at.st!==st||it.at.i!==i))bad.push('slot/item mismatch '+id)});
 for(const tk of G.tickets)tk.fill.forEach((id,j)=>{if(!id)return;if(!G.items.has(id))bad.push('tray '+tk.id+' -> gone '+id);where[id]=(where[id]||0)+1});
 for(const it of G.items.values()){if(it.at&&it.at.carry){where[it.id]=(where[it.id]||0)+1}if(!it.at)bad.push('nowhere '+it.id+' '+it.k);if((where[it.id]||0)>1)bad.push('twice '+it.id)}
 for(const s of G.staff){if((s.state==='carry')&&(!s.it||!G.items.has(s.it.id)))bad.push('staff carrying nothing '+s.n)}
 return bad})()"""
with sync_playwright() as pw:
    b = pw.chromium.launch(); R = random.Random(A.seed)
    for W, H, touch in ((390, 844, True), (1280, 800, False)):
        ctx = b.new_context(viewport={'width': W, 'height': H}, has_touch=touch, is_mobile=touch)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.join(HERE, 'index.html')); pg.wait_for_timeout(300)
        for night in (1, 2, 3, 4, 5):
            pg.evaluate("try{localStorage.clear()}catch(e){}"); pg.reload(); pg.wait_for_timeout(200)
            pg.click(f'[data-go="{night}"]'); pg.wait_for_timeout(150)
            if night == 5: pg.click('#goFree'); pg.wait_for_timeout(150)
            if pg.locator('[data-line]').count(): pg.click('[data-line]'); pg.wait_for_timeout(100)
            pg.evaluate("__cook.setSpeed(4)")
            box = pg.locator('#stage').bounding_box()
            bads = []; acts = 0
            import time; t0 = time.time()
            while time.time() - t0 < A.secs:
                x = box['x'] + R.random() * box['width']; y = box['y'] + R.random() * box['height']
                if R.random() < .25:
                    x2 = box['x'] + R.random() * box['width']; y2 = box['y'] + R.random() * box['height']
                    pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.move(x2, y2, steps=5); pg.mouse.up()
                else:
                    pg.mouse.click(x, y)
                acts += 1
                if acts % 15 == 0:
                    bad = pg.evaluate(CHECK)
                    if bad: bads.append(bad[:3])
                if pg.evaluate("!!(__cook.G&&__cook.G.ended)"): break
            st = pg.evaluate("JSON.stringify({t:Math.round(__cook.G.t),served:__cook.G.st.served,moves:__cook.G.st.moves,items:__cook.G.items.size,ended:__cook.G.ended})")
            print(f'{W}x{H} night {night}: {acts} random acts; {st}; problems: {bads[:2]}; errors: {errs[:2]}')
            errs.clear()
        ctx.close()
    b.close()
