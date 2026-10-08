# JILL'S KITCHEN v2.4 rc8.8 — 發布報告（2026-10-08）

rc8.8 建立在 rc8.7（Version 9）之上，只多一件事：`feature/dylan-room` 已經做好的「Dylan 在房間裡的名字」。

使用者 2026-10-07 的指示：

> 把 feature/dylan-room 已完成的玩家可見修改，乾淨地帶到目前最新 main：Dylan 揭曉後，房間名牌顯示 Dylan；房間分頁顯示「Jill 和 Dylan 的房間」；保留原本這個 branch 已經寫好的相關測試與行為

使用者同時說：「如果完整回歸無阻斷，直接走發布流程，不需要再停下來問我要不要發布。」

原話收在 `docs/v24/cooking_overnight_orders_2026-10-07.txt`（`feature/cooking-gameplay` branch）。

**怎麼報告**（`docs/RELEASE_CHECKLIST.md` §3）：分四層——程式寫了／測試確認了／正常遊玩看得到／使用者在 iPhone 上確認了。這份
報告裡沒有任何一項是使用者在 iPhone 上確認過的。

- Branch `main`，tag `v2.4-rc8.8` ＝ commit `9253fae`（`feature/dylan-room-rc88` 快轉合回 `main`）。
- 發布到正式網址：https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA ——**Version 10（version id `1791419491-01ae`）**。

## 1. 玩家會看到什麼

使用者 2026-10-05 的原話：「Dylan已經揭露但在房間還是沒寫Dylan」（`docs/v24/dylan_room_name_2026-10-05.txt`）。

| 你會看到的 | 什麼時候、在哪裡 |
|---|---|
| Dylan 揭曉之後，在房間裡他頭上的名牌寫「Dylan」 | 營業中或打烊後，切到最後一個分頁「房間」。他在書桌前、沙發上、或在房間裡走動時都一樣。揭曉之前還是寫「先生」 |
| 選到房間分頁時，分頁寫「Jill 和 Dylan 的房間」 | 揭曉之後才這樣寫；揭曉之前寫「Jill 的房間」。沒選到的時候，分頁跟以前一樣只寫「房間」 |
| 分頁放不下全名時寫「Jill & Dylan」；連這樣也放不下時寫「房間」 | **你的 Day 92 存檔**在 iPhone 寬度（390）有 8 個分頁，全名放不下，所以你會看到「Jill & Dylan」。分頁少的時候（例如還沒有 Lounge、二樓）才看得到全名 |
| 分頁那一排不會超出畫面 | 有 8 個分頁時，每個分頁窄一點點 |
| 帽子一直戴著 | 跟以前一樣，揭曉前後都戴著（使用者 2026-10-03 07:44：「在房間Dylan就穿帽T一直戴著帽T帽子吧」） |

做法沿用 `feature/dylan-room` 原本做好、確認過的版本（09f3312，做在 rc8.5 上），沒有重新設計。跟原本不一樣的只有兩處：

- 手冊不用改：rc8.6 手冊重寫後，「怎麼進去」只寫「房間分頁的最後一個」，不寫分頁的名字。
- 截圖重拍：原本的截圖放在 rc8.6 的資料夾，這一版重拍，放在 `docs/evidence/v24_rc8_8/dylan_room/`。

**沒有在這一版的**

| 項目 | 狀態 | 為什麼 |
|---|---|---|
| 料理系統（`feature/cooking-gameplay`） | 開發中，不發布 | 使用者 10/7：不要在睡覺期間把料理系統發布到玩家版 |
| `proto/cooking-flow`（料理流程試玩） | 不合併 | 使用者 10/7 |
| 太太的手機不用登入就能匯出存檔 | **還沒解決** | 需要使用者用手機實測；這一版沒有改存檔匯出 |
| `docs/audit/2026-10-06/DECISIONS.md` 的問題 | 等使用者決定 | 創作與設計的問題 |

## 2. 店主手冊（MANUAL AUDIT）

- 檢查了「Jill 的房間」那張卡，以及所有提到房間分頁的句子。
- **不用改**：rc8.6 重寫後，「怎麼進去」只寫「房間分頁的最後一個」，不寫分頁的名字，所以分頁改名不影響手冊。其他卡也沒有一句寫到
  分頁名字或 Dylan 的名牌。
- 戳記改成 `last: v2.4 rc8.8, 2026-10-07`（commit fbbfca5）。
- 手冊的測試都過，包括 `followup_the_manual_describes_the_current_game`、`rc8_the_manual_shows_a_space_once_the_shop_has_it`。

## 3. 文字

繁體掃描（`tools/hans_scan.py js/game.js index.html docs/v24/dylan_room_name_2026-10-05.txt`）：只有預期的合法字形（干貝、沉、宿舍），
跟 rc8.7 一樣。

## 4. 測試與存檔

- **完整回歸**：在 **`9253fae`（就是發布的這個 commit）上跑，306 個全部通過**；0 個失敗，0 個已知未修。
  - 其中 50 個是例行 QA，5 個是模擬玩家自己的測試。
  - 從固定在這個 commit 的獨立 worktree 分三份同時跑：102＋101＋103，共 37 分鐘（2026-10-07 23:53 → 10-08 00:31 UTC）。
  - 紀錄：`docs/evidence/v24_rc8_8/regression/full_regression_9253fae_shard*.log`。
- **舊存檔，揭曉前／揭曉後**（使用者 HARD RULE 7）：
  - **揭曉前**：玩家的 Day 68 存檔（`player_day68_1033.json`，還沒揭曉）。房間分頁寫「Jill 的房間」，書桌前的名牌寫「先生」；
    整天玩完、結算、Day 69 開店前，重新整理後標題是 DAY 69，頁面錯誤 0。截圖 `04_before_day68_room.png`。
  - **揭曉後**：玩家的 Day 92 存檔（`player_day92_2105.json`）。名牌寫「Dylan」，選到的房間分頁寫「Jill & Dylan」（8 個分頁、
    分頁列寬 382，沒有超出 390 的畫面）；整天玩完、結算、Day 94 開店前，重新整理後標題是 DAY 94，頁面錯誤 0。截圖
    `05_after_day92_room.png`。
  - 新遊戲（揭曉前）：「先生」、「Jill 的房間」，截圖 `03_before_desk.png`。玩家的 Day 89 存檔（揭曉後）：書桌前和打烊後，截圖
    `01_out_desk.png`、`02_out_evening.png`。
  - 紀錄：`docs/evidence/v24_rc8_8/dylan_room/saves_before_after.txt`、`dylan_room.txt`。
- 這一版沒有改存檔格式，也沒有新的 migration：名字和分頁都是從現有的 `S.dylan` 與 `dylanOut()` 算出來的。
- 測試：`rc86_dylan_is_named_in_their_room`（原 branch 的測試，原樣帶過來）。
- **單檔版同步**（使用者 HARD RULE 8）：`single_file_in_sync` 通過。在發布的 commit 上重建單檔版，跟 commit 裡的一個字不差。
- 發布前確認：
  - `main` 是快轉合回（6589e89 → 9253fae），`main` 本身沒有被改寫。
  - 發布的頁面裡沒有 `prototype/`，也沒有料理系統的程式（料理系統在另一條 branch）。
- **發布後檢查**（`tools/sims/live_check.py`，紀錄在 `docs/evidence/v24_rc8_8/live/`）：
  - 從 tag 建的頁面（6,855,053 bytes）一個字不差地在線上頁面裡（6,855,605 bytes），主機只加了 552 bytes 的外框。
  - 用玩家 Day 92 存檔（打烊後存的）走完一輪：升級餐廳 → Day 93 開店前 → 玩完 Day 93（主廳、側廳、門口、Lounge、廚房、
    房間）→ 結算 → 員工頁 → Day 94 開店前 → 重新整理後標題還是 DAY 94。
  - 頁面錯誤 0。
  - 房間那張截圖（`07b_home.png`）：選到的房間分頁寫「Jill & Dylan」，8 個分頁都在畫面裡。

## 5. 四層

- **程式寫了**：上面全部。
- **測試／模擬確認了**：上面全部（`rc86_dylan_is_named_in_their_room`；揭曉前、揭曉後的存檔各玩完一天）。
- **正常遊玩看得到**：
  - 揭曉之後每天都看得到，只要切到房間分頁。你的 Day 92 存檔已經揭曉了，讀進來就看得到。
  - 在 iPhone 寬度、8 個分頁時，分頁寫的是「Jill & Dylan」，不是全名。
- **使用者在 iPhone 上確認**：還沒有。

## 6. 已知、還沒解決的

- **太太的手機不用登入就能匯出／備份存檔**：還沒解決，需要用手機實測。這一版沒有碰。
- Tag `v2.4-rc8.8` 只在本機：推 tag 到 GitHub 時連線會被中斷，跟 rc8.6、rc8.7 一樣。
