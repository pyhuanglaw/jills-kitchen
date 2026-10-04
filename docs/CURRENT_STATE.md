# Jill's Kitchen — 目前狀態（暫時的，會一直更新）

這份只放「現在」的狀態：branch、版本、待辦、待確認。永久的設計規則在 `docs/PROJECT_MEMORY.md`，不要寫到這裡；這裡的內容過時了就
直接改掉或刪掉。最後更新：2026-10-03，v2.4 rc8 發布之後。

## Repo 與 branch

- GitHub：`pyhuanglaw/jills-kitchen`。**開發 branch：`wip/lin`**（目前所有最新的工作都在這裡）。
- `main`：只有一個 commit（d0947ea），是 2026-10-03 把 rc7.6 的 12 個 zip 匯入 GitHub 時建的，已被 `wip/lin` 取代，沒有合併。
- `claude/jills-kitchen-github-setup-4x7483`：網址改到新 artifact 的那個 commit（8ca784b），已 cherry-pick 進 `wip/lin`（ec985d1）。
- 本機的 `bundle` remote 是原開發 session 的備份 bundle，只是還原來源，不推送。
- 舊版本（玩家 2026-10-03 給的 v2.2.1、v2.4 rc4，以及其他每一版）怎麼查：`docs/OLD_VERSIONS.md`。

## 已發布

- **v2.4 rc8.3**，2026-10-03，發布到 **https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA**（**Version 5**，id 1791055230-dd7a）。
  遊戲內容＝ commit e797665（tag `v2.4-rc8.3`，只在本機）。報告：`docs/V24_RC8_3_REPORT.md`。Gate：e797665 上 242/242；讀回與
  live_check 通過（`docs/evidence/v24_rc8_3/`）。內容：候位到店門口、三種披薩、房間的貓砂盆與碗架、寶寶靠著 Jill／柔柔睡腳上、
  拿掉 PERFECT 橫幅、Sophie 和 Mia 坐隔壁桌、杯墊那段的旁白、香煎鴨胸 6 天說一次、Ken 品酒夜的分帳與開場、猜酒、新空間的照片、
  特別的晚上「繼續營業」接得回來。
- v2.4 rc8.2（Version 4，b443ab5；報告 `docs/V24_RC8_2_REPORT.md`）。
- 前一版 v2.4 rc8.1（version 3，df8a95b）；再前一版 v2.4 rc8（version 2，252ff1c；報告 `docs/V24_RC8_REPORT.md`）。
- 玩家在 2026-10-03 選擇以後都發布到這個新網址。舊網址 https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps 停在 rc7.6（version
  49），不再更新。舊網址的存檔要用遊戲裡的「設定・存檔」備份後搬過來。
- 新網址的分享設定由玩家在頁面的分享選單決定（目前是「知道連結的人都能看」）。

## 已做、還沒發布

- 沒有。

## 測試

- 237 個測試（`python3 tests/run_tests.py`；`-k a,b,c` 跑指定的）。rc8 的 gate：252ff1c 上 231 過、2 個失敗都是測試本身，已在
  8f7d6b2 修好並重跑通過。
- 已知會在單一 seed 上偶爾落差的機率性測試，都在測試註解裡寫了量過的分布（例：`lounge_i_content_bar_food…`、
  `v24_rc6_new_things_are_talked_about`）。

## 待辦／待確認

- ~~營業中存檔、「繼續營業」在特別的晚上會變成空店~~：rc8.3 已修（`rc83_a_special_evening_comes_back_with_its_room`）。原本的說明：存檔時有人在
  `piano`（予安彈琴）、`toHost`／`host`（Ken 主持品酒夜）這些狀態，`restoreService` 的 `G_STATES` 不認得，整個還原失敗，
  退回「同一時間、店是空的」；主廚之夜的 `R.cn`、品酒夜的 `R.kt`、予安的 `R.ya` 也不會還原。存檔本身沒有壞，只是那一晚
  的客人不見。修法：還原時接受這些狀態，並重建 `R.ya`／`R.kt`／`R.cn`（玩家 Day 87 存檔可以重現：19:19 的 29 組客人變 0）。
- **太太的手機不用登入就能匯出／備份存檔**：還沒解決，需要玩家用手機實測。不要用「文字框複製」的方式（會讓 iPhone 當機）。
- `docs/evidence/v24_rc8/release/qing_tuo/` 的重拍截圖缺《講完》那一組（截圖腳本逾時）；原本的 q5 在 `docs/evidence/v24_rc8/qing_tuo/`。

## 等玩家的圖

- Ken 前三次品酒夜的三張圖（玩家 2026-10-04 選 B，三張各自不同；`docs/v24/ken_tasting_pictures_2026-10-04.txt`）。程式已接好
  （還沒發布）：第二、第三次開場有自己的插圖（現在是「插圖待補」），故事頁三段各有「看插圖」；相簿的三張照片等在 slot，圖來了就照
  那一晚的日子補進去（玩家的存檔：Day 78、83、88）。圖來了要做的：三張放進 STORY_ART 的 ken_night1–3，ken_t1 的插圖改用
  ken_night1（舊的 ken_t1 那張移除），依新的第一張改 ken_t1 的說明文字（現在寫「吧台前坐滿了」，新設計是客人不多），然後發布。

## 玩家回報、下一批

- 玩家 2026-10-03 晚上 Day 83–89 的回報都在 rc8.3 做完了（`docs/V24_RC8_3_REPORT.md`），只剩品酒會插圖等玩家決定。
- 長期方向（PROJECT_MEMORY §3）：Jill 的房間是一層「生活」，之後繼續加。

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
1. 在 cb3470f 跑的完整回歸已跑完：233 過、4 個失敗。其中三個已處理：`cats_use_sofa_by_personality`（147165d 修好，
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
