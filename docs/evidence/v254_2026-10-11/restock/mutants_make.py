import sys, os
src = open('/home/user/jills-kitchen/js/game.js', encoding='utf-8').read()
M = {
 'no_return': ("function returnOffMenu(){const out={n:0,rf:0};if(R)return out;", "function returnOffMenu(){const out={n:0,rf:0};return out;"),
 'refund_at_todays_price': ("function stockRefund(d,n){return Math.floor(n*stockUnit(d)+1e-6)}", "function stockRefund(d,n){return n*costOf(d)}"),
 'refund_rounds_up': ("function stockRefund(d,n){return Math.floor(n*stockUnit(d)+1e-6)}", "function stockRefund(d,n){return Math.ceil(n*stockUnit(d)-1e-6)}"),
 'buy_not_recorded': ("S.todayCost+=q.n*q.c;stockIn(d,q.n,q.c);", "S.todayCost+=q.n*q.c;S.stock[d]=cur+q.n;"),
 'free_delivery_at_cost': ("const d=pick(ms);stockIn(d,2,0);", "const d=pick(ms);S.stock[d]=(S.stock[d]||0)+2;"),
 'return_during_evening': ("function returnOffMenu(){const out={n:0,rf:0};if(R)return out;", "function returnOffMenu(){const out={n:0,rf:0};"),
 'return_on_toggle': ("S.menu=S.menu.filter(x=>x!==d)}else{", "S.menu=S.menu.filter(x=>x!==d);returnOffMenu()}else{"),
 'old_toast_v253': ("else if(much.length){", "else if(short.length){"),
 'no_summary': ("else if(said)toast(`${said}，並完成補貨。`);", ";"),
 'menu_order_buying': ("const m0=S.money;const back=returnOffMenu();const sug=suggestStock(),plan=restockPlan();", "const m0=S.money;const back=returnOffMenu();const sug=suggestStock(),plan=(()=>{const s=suggestStock(),o={};for(const d of menuList())if(s[d]>(S.stock[d]||0))o[d]=s[d]-(S.stock[d]||0);return o})();"),
}
for k, (a, b) in M.items():
    assert src.count(a) == 1, (k, src.count(a))
    open(os.path.join(sys.argv[1], k + '.js'), 'w', encoding='utf-8').write(src.replace(a, b))
print(' '.join(M))
