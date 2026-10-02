"""golden proof (rc6): take the current game.js and put back ONLY the two things that legitimately move golden_scenario —
the p21 dialogue changes (09:39: a guest's line once a day, more ways of answering, the VIPs' and the named guests' own
order lines, the extra cat questions) and the novelty seat pools (09:39: new things talked about, replacing the old
'decor' pool). If the old golden then passes, nothing else in rc6 moved it. Usage: proof_revert.py GAME_JS"""
import sys, re
P = sys.argv[1]
s = open(P, encoding='utf-8').read()
OLD = open('/tmp/claude-0/-home-claude/3e92becc-ea59-5b58-92f6-ca1d4bdefb76/scratchpad/rc6/wt_head/js/game.js', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    k = s.count(old)
    if k != cnt:
        sys.exit(f'anchor count {k} != {cnt}: {old[:100]}')
    s = s.replace(old, new)

# 1. quote: said every time again (the old function's behaviour)
i = s.find('function quote(g,txt,o){'); j = s.find('\n', i)
s = s[:i] + 'function quote(g,txt,o){quote0(g,txt,o);return true}' + s[j:]
# 2. the cat question's old lines
rep("const asked=quote(g,pickT(['這隻貓叫什麼名字？','牠是店裡的貓嗎？','可以摸嗎？','牠都不怕人耶。','那隻貓好可愛。','牠平常都睡哪裡？']));if(asked&&free&&J.calm>1)setTimeout(",
    "quote(g,pickT(['這隻貓叫什麼名字？','牠是店裡的貓嗎？','可以摸嗎？','牠都不怕人耶。']));if(free&&J.calm>1)setTimeout(")
# 3. the old answers to 「還可以嗎？」
rep("quote(g,q==='P'?pick(['很好吃。','太好吃了。','這個我喜歡。','好吃，真的。','下次還要點這個。','比想像中還好吃。','剛剛好，謝謝。']):q==='O'?pick(['還可以。','有一點鹹。','普通。','嗯……還好。','跟上次不太一樣。']):q==='B'?pick(['有點焦…','下次再來試試。','今天好像有點焦。']):pick(['不錯。','好吃。','嗯，可以。','還不錯喔。','味道很好。','可以，謝謝。']))",
    "quote(g,q==='P'?pick(['很好吃。','太好吃了。','這個我喜歡。']):q==='O'?pick(['還可以。','有一點鹹。','普通。']):q==='B'?pick(['有點焦…','下次再來試試。']):pick(['不錯。','好吃。','嗯，可以。']))")
# 4. the VIPs and the order lines
rep("else if(g.type==='vip')quote(g,pickH(VIP_ORDER,'vip|'+S.day+'|'+g.id));else if(Math.random()<.12)quote(g,pickT(namedId(g)?ORDER_KNOWN:ORDER_NEW));",
    "else if(g.type==='vip')quote(g,'把你們最好的端上來吧。');else if(Math.random()<.12)quote(g,pickT(['今天想吃點好的。','聽說這裡的東西都是 Jill 親手做的？','有推薦的嗎？算了，都點吧。']));")
# 5. seatLine: the old function, whole (the old 'decor' pool, no novelty pools, no SEAT_KNOWN)
def fn(src, name):
    i = src.find('function ' + name + '(')
    j = src.find('\n/* now and then someone in the room says something', i)
    return src[i:j]
rep(fn(s, 'seatLine'), fn(OLD, 'seatLine'))
open(P, 'w', encoding='utf-8').write(s)
print('reverted', P)
