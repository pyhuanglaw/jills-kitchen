"""v2.3 follow-up: play a whole lazy day with a campaign running and one without, on the same save and seed, and count
what a player could actually notice — the campaign guests, the lines they said, the promoted dish on tickets,
glasses and Lounge tabs, reviews and posts. Usage:
  python3 tools/sims/campaign_days.py <save.json> <cats|dish|local|side|wine> [seed] [give the save a Lounge: 0/1]"""
import sys, os, json
ROOT = '/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

save = sys.argv[1]; k = sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7; lounge = int(sys.argv[4]) if len(sys.argv) > 4 else 0
raw = json.load(open(save)); raw = raw.get('save', raw)
PHR = ['第一次進來', '一直沒來過', '樓下', '看到介紹', '貓咪的', '貓呢', '照片', '網路上那一道', '看到這個才來', '，就是這個', '不是說有', '賣完了喔', '為了那一道',
       '照片裡那個側廳', '好適合聚餐', '一整桌', '側廳滿了', '有酒？', '酒單呢', '那一杯', '吃完可以坐', '跟照片一樣', '真的有', '還是沒看到貓', '今天貓呢', '牠們今天在哪', '今天賣完了，抱歉']

def open_save(g):
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__fastSay=1")   # lines are spoken ~0.7 s of real time after the moment; the sim runs a whole day in under a second
    if lounge:
        g.ev("S.money+=900000;factSet('lounge_project');buyLounge(1);hideReveal();S.crew.push({id:'cb1',role:'bartender',name:'Evan',lv:2,duty:'lbar'});showPrep()")

def play(g, camp):
    g.ev("if(phase!=='prep'){S.phase='prep';showPrep()}S.money+=60000;S.social=S.social||{};S.social.camp=null")
    if camp:
        d = g.ev("menuList().find(x=>!(DISHES[x]&&DISHES[x].bar)&&x!=='signature'&&x!=='sigdessert'&&stationOk(x)&&DISH(x).cat==='main')")
        if not g.ev("startCampaign(%s,%s)" % (json.dumps(k), json.dumps(d))):
            print('campaign did not start'); return None
    g.ev("autoStock()")
    rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    rt.play_day(g, max_steps=60000)
    for _ in range(400):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    r = json.loads(g.ev("""JSON.stringify({day:S.day,guests:S.lastSummary.guests,camp:S.lastSummary.camp,lg:S.lastSummary.lg,
      glasses:(S.dayLog||[]).length?null:null,log:(S.dayLog||[]).map(l=>l.w+'：'+l.t),rv:S.reviews.filter(r=>r.day===S.day).map(r=>r.txt),
      posts:((S.social&&S.social.posts)||[]).filter(p=>p.day===S.day).map(p=>p.who+'：'+p.txt),dish:S.lastSummary.top})"""))
    r['lines'] = [l for l in r['log'] if any(p in l for p in PHR)]
    del r['log']
    return r

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for camp in (False, True):
        g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
        open_save(g); r = play(g, camp)
        if r is None: g.close(); continue
        print(('== with ' if camp else '== without ') + k, json.dumps({x: r[x] for x in ('day', 'guests', 'camp', 'lg')}, ensure_ascii=False))
        for l in r['lines'][:16]: print('    ', l)
        mention = sum(1 for t in r['rv'] if any(w in t for w in ['貓', '酒', 'Lounge', '側廳', '賣完', '第一次', '沒遇到']))
        print('    campaign lines:', len(r['lines']), '| reviews mentioning cats/wine/side/sold out:', mention, '/', len(r['rv']), '| posts:', len(r['posts']), r['posts'][:3])
        print('    errors', g.errors[:2]); g.close()
    b.close()
