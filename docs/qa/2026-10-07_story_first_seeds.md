# 故事優先（版本 A，最終 canon）：正常玩家三個 seed（2026-10-07）

程式：branch `feature/lounge-decided`，從固定在 090b6b4 的 worktree 跑（遊戲內容＝ f5375d6）。
`tools/qa/new_game_timeline.py --seed N --policy normal --service human --days 115 --after-opening 999 --probe tools/qa/probes/story_first_waits.json`；
分析：`tools/qa/story_waits.py`（每一段：條件成立 → 發生；project 出現 → 第一次付得起；付得起 → 實際買）。
三個 seed 都在包廂 I 動工的隔天收店時，出現模擬玩家不認得的畫面而停下（Day 88／93／94）；頁面錯誤 0。這個畫面是模擬器
不會處理還是遊戲的問題，還沒查。

完整 timeline 和每一段的等待：`docs/qa/data/2026-10-07_story_first_waits.md`；每天的決定：`docs/qa/data/2026-10-07_story_first_seed30x_decisions.txt`。

## 重點

- 故事本身不再卡：試酒之夜、Madame Lin 退休、《看看》、二樓的故事、《大家待的地方》、打給房東，條件成立後 0–3 天就發生；
  多的幾天是在等人來（Madame Lin、予安、Dylan 晚上去 Lounge 是機率）、包場的晚上，或那天已經有兩個 major。
- 長的等待都在「錢夠了 → 玩家還沒買」：Lounge I 7–21 天、鋼琴 12–24 天。模擬玩家的理由（決策紀錄）：
  - Lounge I：每天晚上先買菜單研發、廚房設備，輪到 Lounge 卡片時錢已經不夠；另外它不會花到遊戲顯示的「建議保留」以下，
    這個數字從約 $2 萬長到約 $5 萬。期間錢花在廚房擴建 $45,000、側廳 $60,000、Fine Dining $40,000、卡座、菜單研發和每天的備料。
  - 鋼琴：它把 Lounge II、III、二樓工程當成「故事的工程」排在前面，鋼琴當成一般空間工程排最後（「在存 Lounge III……空間的工程
    等故事的工程之後」）；鋼琴卡片上還寫著「遠程」。
- 錢不是後期的瓶頸：每天淨利 Day 30–39 約 $1.8–2.4 萬，Day 50–59 約 $3.2–4.9 萬，Day 60 以後約 $5.6–7 萬；Lounge II、III、
  披薩烤爐、二樓工程、包廂 I 都在付得起之後幾天內就買了。
