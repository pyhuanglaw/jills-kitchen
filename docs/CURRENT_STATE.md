# Jill's Kitchen — 目前狀態（暫時的，會一直更新）

這份只放「現在」的狀態：branch、版本、待辦、待確認。永久的設計規則在 `docs/PROJECT_MEMORY.md`，不要寫到這裡；這裡的內容過時了就
直接改掉或刪掉。最後更新：2026-10-03，v2.4 rc8 發布之後。

## Repo 與 branch

- GitHub：`pyhuanglaw/jills-kitchen`。**開發 branch：`wip/lin`**（目前所有最新的工作都在這裡）。
- `main`：只有一個 commit（d0947ea），是 2026-10-03 把 rc7.6 的 12 個 zip 匯入 GitHub 時建的，已被 `wip/lin` 取代，沒有合併。
- `claude/jills-kitchen-github-setup-4x7483`：網址改到新 artifact 的那個 commit（8ca784b），已 cherry-pick 進 `wip/lin`（ec985d1）。
- 本機的 `bundle` remote 是原開發 session 的備份 bundle，只是還原來源，不推送。

## 已發布

- **v2.4 rc8.1**（緊急更新），2026-10-03，發布到 **https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA**（version 3，id
  1791037558-a88f）。遊戲內容＝ commit df8a95b（tag `v2.4-rc8.1`，只在本機：推 tag 時 GitHub 端斷線，branch 已推）。
  內容：教學提示 9 秒後自己收起（「這一段開店很久都不消失！」）、Day 1 揭曉前 Dylan 寫「Jill 先生」不露臉、店主手冊一行一點變短。
  Gate：db8dd56 上完整回歸 232/233，唯一失敗是手冊少一句玩法規則，df8a95b 補回，讀手冊的測試全部重跑通過；讀回與
  live_check 通過（`docs/evidence/v24_rc8_1/`）。
- 前一版 v2.4 rc8（version 2，252ff1c；報告 `docs/V24_RC8_REPORT.md`）。
- 玩家在 2026-10-03 選擇以後都發布到這個新網址。舊網址 https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps 停在 rc7.6（version
  49），不再更新。舊網址的存檔要用遊戲裡的「設定・存檔」備份後搬過來。
- 新網址的分享設定由玩家在頁面的分享選單決定（目前是「知道連結的人都能看」）。

## 已做、還沒發布

- b6be7c2：《今天喝？》之前 Dylan 不會坐進 Lounge（Day 81 存檔：「他第一次去酒吧的故事都還沒開始前他不能去酒吧」）。原因是客滿時
  一兩位的客人會先到 Lounge 吧台等位子，Dylan 也被帶過去。存檔放在 `tests/saves/player_day81_2206.json`。
- 店主手冊只寫店裡已經有的空間（「每個空間等他出現才出現在說明書吧」）：`GUIDE_WHEN`。新遊戲的手冊是 14 節 101 項，沒有 Lounge、
  二樓、側廳、露天；Day 81 存檔有 Lounge、沒有二樓（她還沒租）。「VIP 卡」搬到「招待與熟客」、「配菜的酒」搬到「開店與料理」。
  截圖：`docs/evidence/v24_rc8_next/guide_gate_*.png`。新測試 `rc8_the_manual_shows_a_space_once_the_shop_has_it`。
- Jill 在房間自己找事做（電視、手遊、跟先生聊天、看他在忙什麼、傳訊息、叫貓）：營業中的休息和打烊後都有。順手修了電視推過去時
  會被主廳的貓「擋住」的舊 bug（主廳的貓跟房間共用座標）。截圖 `docs/evidence/v24_rc8_next/room_*.png`；新測試
  `rc8_jill_has_things_to_do_in_her_room`。手冊「Jill 的空檔」「Jill 在房間」已更新。
- 二樓 hard canon（玩家 2026-10-03）：租下二樓時員工休息室就在。《大家待的地方》移到租下之前，變成打給房東的理由；租二樓
  $510,000（原本整層 $350,000＋休息室第一階段 $160,000）；包廂 era 租下後 12 天才開。舊存檔租了空二樓的，讀檔時休息室就在
  （算租下那天蓋的，`srLeaseMig`）——玩家的 Day 87、Day 89 存檔都是這種。截圖 `docs/evidence/v24_rc8_next/lease_*.png`。
  二樓相關 30 個測試全過（4 個測試改成新 canon）。
- 主廚之夜／予安試彈撞在同一晚（玩家 Day 87）：順延的主廚之夜在排客人時就算今晚；包場夜不讓予安來試彈；試彈改在晚餐後
  （王先生王太太 40%、予安 46%），拍手等 Lounge 有人，插圖只在 Lounge 坐滿、王太太在場時出現。Ken 的品酒夜本來就這樣算，
  沒有同樣的問題。測試 `rc8_a_booked_out_lounge_never_shares_its_evening_with_the_trial`。
- 「多的」不用圖：「從工作開始」不再拍照（已經有這張照片的存檔照片留著）。測試 `rc8_duode_has_no_picture`。

## 測試

- 237 個測試（`python3 tests/run_tests.py`；`-k a,b,c` 跑指定的）。rc8 的 gate：252ff1c 上 231 過、2 個失敗都是測試本身，已在
  8f7d6b2 修好並重跑通過。
- 已知會在單一 seed 上偶爾落差的機率性測試，都在測試註解裡寫了量過的分布（例：`lounge_i_content_bar_food…`、
  `v24_rc6_new_things_are_talked_about`）。

## 待辦／待確認

- **營業中存檔、「繼續營業」在特別的晚上會變成空店**（rc8.2 發布前找到，舊版本也一樣，這一版沒修）：存檔時有人在
  `piano`（予安彈琴）、`toHost`／`host`（Ken 主持品酒夜）這些狀態，`restoreService` 的 `G_STATES` 不認得，整個還原失敗，
  退回「同一時間、店是空的」；主廚之夜的 `R.cn`、品酒夜的 `R.kt`、予安的 `R.ya` 也不會還原。存檔本身沒有壞，只是那一晚
  的客人不見。修法：還原時接受這些狀態，並重建 `R.ya`／`R.kt`／`R.cn`（玩家 Day 87 存檔可以重現：19:19 的 29 組客人變 0）。
- **太太的手機不用登入就能匯出／備份存檔**：還沒解決，需要玩家用手機實測。不要用「文字框複製」的方式（會讓 iPhone 當機）。
- `docs/evidence/v24_rc8/release/qing_tuo/` 的重拍截圖缺《講完》那一組（截圖腳本逾時）；原本的 q5 在 `docs/evidence/v24_rc8/qing_tuo/`。

## 玩家回報、下一批（不在 rc8.2）

玩家 2026-10-03 晚上玩 Day 87–89 的回報，這一批沒有做（玩家把這一批限定在上面那幾項）：
- 「lounge根本沒人點披薩」（酒吧披薩）。
- 「品酒會的對話猜 怎麼是猜什麼干貝」（品酒夜的猜題）。
- 「寶寶偶爾也會靠著jill 柔柔也會在jill腳上睡覺」（沙發上的貓）。
- 「可以不要一直跳出perfect擋住選區嗎」。
- 「sophie mia根本沒有坐在一起 我要找他們在哪也超難找」（存檔 `tests/saves/player_day89_2320.json`）。
- 「這段對話沒頭沒尾欸」：`kd_coaster`（Evan 多放一個杯墊；Ken「他今天沒來。」Evan「我沒問。」）。話語紀錄裡兩句隔了三分鐘、
  中間夾著 Jill 的話，「他」是誰也看不出來（是杜）。
- 「披薩只有一種嗎」（酒吧披薩只有一種）。
- 「房間要有至少兩個貓砂盆啊 貓咪碗架啊 水盆」（Jill 的房間的貓用品）。
- 「排隊的人可不可以改到店門口啊 在主廳好礙事」（候位的客人）。
- 「為什麼品酒師Ken 突然給錢說是我自己要辦的 我甚至看不出來他辦了什麼」「而且我明明給了品酒會的照片」：Ken 自己排的品酒夜
  （`ken_t2`，Day 83，存檔 `tests/saves/player_day83_2218.json`）看不出在辦什麼，玩家給的品酒會插圖沒有出現。
- 「新增房間之後要有拍照時刻是設計給房間的吧」（新的房間蓋好後的照片時刻）。
- 「Sophie連續兩天說沒有香煎鴨胸很白癡」：最愛的菜不在菜單上時（`LOVE_MISS`），每次來都有 35% 會講，沒有冷卻；常客幾乎天天講。

## 美術

- 玩家要的十張插圖（Madame Lin 線 5 張、晴 × 阿拓 5 張）都已放進遊戲。目前沒有缺圖。

## 需要玩家正常遊玩才能確認的（O）

- 員工滿編時 Jill 大半個營業時間在房間休息，看起來是否自然；廚師去別站幫忙會不會讓雇人變得不重要。
- 晴 × 阿拓的節奏：從 Day 74 存檔大約 13 天走完五幕（Day 82 / 84 / 88 / 90 / 95）。
- 十張圖在手機上的樣子。
- Madame Lin 線從新遊戲 Day 1 開始的節奏（模擬是從 Day 30、Day 52 的存檔跑的）。
- 樾樾打烊後出來等 Jill、Jill 在開店和快打烊時在主廳。

## 接手：v2.4 rc8.2 還沒發布（2026-10-03 22:30，玩家的用量到上限，週二 16:00 重置）

這一批（玩家定義的 A–K）程式都做完、推上 `wip/lin` 了，只差發布 gate：
1. 在 cb3470f 跑的完整回歸做到一半（約 80/237）。到那時為止三個失敗都已處理：`cats_use_sofa_by_personality`（147165d 修好，
   單獨重跑過）、`phase7_the_arcs_run_on_real_history_and_leave_it_changed`（659fc4f 改成「多的不用圖」，重跑過）、
   `golden_frames`（Jill 的房間生活改了第 1 天晚上，**要重錄**：`python3 tests/run_tests.py --record -k golden_frames`，也看一下
   `golden_scenario`、`cat_personality_fingerprint` 要不要一起重錄，並在報告寫原因）。
   第四個失敗（還沒查）：`v24_rc8_the_bar_next_door_from_kens_question_to_jills_decision`——`pairing_start` 的 held scene
   （「Jill：今晚那幾支，可以再幫我進嗎？」）沒有演，只出現 note 版（「收店的時候，Jill 把今晚那幾支酒的名字抄下來……」）。
   rc8.1 的 gate 是過的，先在 abc9d38（房間生活之前）和 ec17365（之後）各跑一次這個測試，看是哪一批造成的。
2. 重錄後，在**最後要發布的那個 commit** 上跑完整回歸（全部 237 個，不能跳），全過才發布。
3. `build_single.py`、`build_artifact.py` → 發布到 https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA → 讀回 → `live_check.py` → 報告
   （I／T／O 分開）。不打 zip。
4. 發布後確認玩家最新存檔（Day 89）還能「繼續營業」，Day 86 存檔讀檔時二樓有員工休息室（發布前已在本機確認過兩者）。

## 下次發布前

照 `docs/RELEASE_CHECKLIST.md`：這一批要求做完 → 完整回歸（在要發布的 commit 上）→ 手冊檢查與 GUIDE 戳記 → 繁體掃描 →
`build_single.py`、`build_artifact.py` → 發布到上面的新網址 → 讀回、`live_check.py` → 報告。一般發布不打 zip。
