# Jill's Kitchen：程式結構與擴充守則

這份文件給「之後要繼續加東西的人」（包括未來的 Claude）。先讀這份，再動 `js/game.js`。

## 1. 檔案

| 檔案 | 用途 |
|---|---|
| `index.html` / `css/style.css` / `js/game.js` | 遊戲本體（唯一需要手改的三個檔案） |
| `jills-kitchen-single-file.html` | **自動產生**，改完上面三個檔案後執行 `python3 tools/build_single.py` |
| `tests/run_tests.py` | 回歸測試（見第 6 節） |
| `tests/fixtures/*.json` | 舊存檔樣本，每次存檔格式改變都要新增一份 |
| `tests/golden/` | 目前版本的「標準答案」：遊戲數值、每幀畫面雜湊、10 張截圖 |
| `tools/analyze.js`、`tools/lint.mjs` | 靜態分析（未使用的程式、共用變數、計時器、事件監聽） |

`game.js` 是一個 IIFE，依區塊註解分段（搜尋 `/* ====`）。目前規模刻意**不拆檔**，原因寫在 `REFACTOR_REPORT.md`。

## 2. 全域狀態（最容易出錯的地方）

| 變數 | 意義 | 誰可以改 |
|---|---|---|
| `S` | 存檔內容（進度、金錢、菜單、照片…）。**只有這個會被存起來** | 任何地方，改完呼叫 `save()` |
| `R` | 今天營業中的一切（客人、訂單、爐台、Jill）。**只在 `phase==='service'` 時存在** | `startService` 建立，`endDay`、`showTitle`、`showPrep`、`showShop` 清掉 |
| `IDLE` | 不營業時畫面上的假店面（桌子、Jill） | `layoutAll`、`applyDY` 與各 `showX` 重建 |
| `phase` | `title` / `prep` / `service` / `summary` / `shop` | 只由 `showTitle`、`showPrep`、`startService`、`showSummary`、`showShop`、`endDay` 設定 |
| `mainScreen` / `sub` | 目前主畫面 / 疊在上面的子畫面（`book`、`guide`、`settings`、`pause`…） | `showX`、`openSub`、`closeSub`、`hideScreen` |
| `paused` | 營業中暫停 | `hPause`、`resume`、`closeEarly`、`closeNow` |
| `CATS` | 五隻貓的即時狀態（不存檔；`applyDY` 會把它清成 `null`，下一幀重新產生） | 貓咪 AI |
| `OCC` / `SIDE` / `perchOcc` | 貓咪「佔位表」：貓抓板、山洞、軟墊、玩具、Jill 左右、跳台各層 | `catGo`、`goJill`、跳台相關函式；**離開時一律透過 `releaseSpots(c)` / `leavePerch`** |
| `bg` / `bgKey` | 背景快取，改等級、裝潢、菜單、尺寸時自動重畫；要強制重畫就設 `bg=null` |

測試會檢查的不變條件（`tests/run_tests.py` 的 `INV` 與 `cat_ai_keeps_running`）：

- `R` 存在 ⇔ `phase==='service'`
- `paused` 只會在營業中，而且一定有選單開著
- 營業中且沒暫停時，選單畫面是隱藏的
- 一隻貓同時最多佔一個位置；佔位時不會同時在跳台上或 Jill 旁邊；軟墊最多兩隻、不重複
- 貓的座標永遠是有限數字，也不會跑出房間

新增畫面或新的貓咪行為時，這些條件必須繼續成立。

## 3. 主迴圈

`frame(now)` 每幀只做這些事，且全遊戲只有一個 `requestAnimationFrame` 鏈：

1. `updateCats(dt)`（營業中暫停時不跑）
2. 營業中：`update(dt)`，每 0.12 秒刷新一次訂單、任務、HUD
3. `drawScene()` → `flushMem()`（拍回憶照片）→ 需要時 `drawTray()`

實測成本：模擬、貓咪 AI、DOM 刷新合計不到 0.02 ms/幀；幾乎所有時間都花在 `drawScene`（約 2000 次 canvas 呼叫、4 次全螢幕繪製）。**新增全螢幕特效是最花手機效能的事**，其他邏輯都很便宜。

計時器：`setInterval` 只有音樂排程一個；`setTimeout` 只用在一次性的提示、橫幅、音效。事件監聽全部在啟動時註冊一次。畫面切換用 `innerHTML` 重畫，靠 `screenEl` 上的單一事件代理處理按鈕，所以**不要在 `showX` 裡對新元素 `addEventListener`**，改用 `data-act` 加到 `screenEl` 的 `switch` 裡。

## 4. 常見擴充怎麼做

### 新增料理
1. `DISHES` 加一筆：`{n, cat, st, v, price, cost, diff, pop, lv, rd, steps:[...]}`，步驟用 `sA`（加料）、`sT`（連點）、`sW`（等待）、`sZ`（抓時機）、`sH`（長按）、`sD`（份量）。
2. 用到新食材 → `ING` 加一筆。
3. 成品圖 → `VESSEL` 與 `paintFood` 加分支；鍋中畫面 → `drawContents` / `drawTopLayers`。
4. 執行測試。`cooking_every_recipe` 會自動把新料理從頭做到完，確認完美操作能拿到 PERFECT。
5. **料理 id 一旦發佈就不要改名或刪除**：存檔的 `menu`、`unlocked`、`stock`、`xp`、`price`、`rstar` 都用 id 記錄。真的要改，寫 migration（第 5 節）。

### 新增貓咪行為
1. 在 `catDecide` 用 `add('新行為', 權重)` 加入候選；權重依個性（`id`）決定。
2. 在同一個 `switch(ch)` 加 `case`，設定 `c.st` / `c.pose` / `c.t`，要移動就用 `catWalk`。
3. 在 `updateCats` 的狀態 `switch(c.st)` 處理每幀行為，結束時呼叫 `catDecide(c)`。
4. 會佔用家具就走 `catGo` / `OCC`，並確保每條離開路徑都經過 `releaseSpots(c)`。
5. 遵守貓咪世界規則：五隻都在，不寫離開、死亡、懷念類內容。
6. 每多一次 `Math.random()` 都會讓之後所有隨機結果改變，所以 golden 測試**一定會**失敗，這是正常的。確認截圖差異是預期的，再重新錄製（第 6 節）。

### 新增可以點的家具
- 貓咪相關：`SPOT` 加座標、`hitSpot` 加判斷、`tapSpot` 加反應，繪製放在 `drawScene` 對應的區塊。
- 廚房用品：`kitchenItems()` 加一筆（繪製和點擊判斷共用同一份座標），`tapKItem` 加 `case`。
- 房間深度會隨螢幕高度調整（`applyDY`），會跟著地板移動的 y 座標請比照 `SPOT.scr` 寫在 `applyDY` 裡。

### 新增存檔欄位
- **只要在 `newState()` 加上預設值**。舊存檔讀進來時缺少的頂層欄位會自動補上。
- 如果是放在 `eq`、`decor`、`staff`、`stats` 這四個物件裡的新鍵，也會自動補上（`fillDefaults` 會逐鍵合併）。
- 其他巢狀物件裡的新鍵**不會**自動補，要在讀取處加 `||預設值`，或寫 migration。

## 5. 存檔格式改變（migration）

`load()` 的流程：讀取 → 解析 → 檢查版本 → 依序跑 `MIGRATE` → `fillDefaults` → `legacyCrew`。

要改變既有資料時（改欄位名稱、改格式、改 id）：

```js
const SAVE_V=2;                       // 原本是 1
const MIGRATE={
  1:o=>{ o.menu=o.menu.map(d=>d==='oldId'?'newId':d); /* …其他欄位 */ },
};
```

- 每一步只負責「版本 n → n+1」，`load()` 會自動把版本號加一。
- 發佈前把現在的存檔存成新的 `tests/fixtures/vN_*.json`，並確認 `old_saves_load` 通過。
- 讀不懂的存檔（壞掉、版本比程式新）會先複製到 `localStorage['jills-kitchen-save-v1-unreadable']`，再開始新遊戲，所以不會被下一次 `save()` 蓋掉。
- 存檔失敗（例如容量滿）會在 console 印一次警告，遊戲畫面不變。

照片（`S.mem`）目前每種回憶最多一張，共 10 張、每張約 5 KB。如果以後要讓照片數量無上限或提高解析度，先把照片搬到 IndexedDB 或獨立的 localStorage key，再用 migration 把舊照片搬過去。做法見 `REFACTOR_REPORT.md`。

## 6. 測試

```bash
pip install playwright        # 第一次才需要；本機要有 Chromium（playwright install chromium）
python3 tests/run_tests.py                  # 多檔版（index.html）
python3 tests/run_tests.py --target single  # 單檔版
python3 tests/run_tests.py -k cats          # 只跑名稱含 cats 的測試
```

- 測試不會修改遊戲檔案。它在瀏覽器載入時注入一個小鉤子讀取內部狀態，並固定亂數種子。
- `golden_frames` 以虛擬時間逐幀執行**真正的主迴圈**兩天，比對：
  - 每秒一次的畫面像素雜湊、DOM、貓咪狀態；
  - 拍下的回憶照片；
  - 10 張全畫面截圖（像素完全一致）。

  只要畫面、動畫、貓咪行為或數值有任何變化，它就會失敗。截圖比對只容許文字反鋸齒的微小雜訊：最多 16 個像素、每個像素的亮度差最多 4。不一致時，實際截圖與差異圖會存到 `tests/artifacts/`。
- **有意改變**遊戲內容後：先看 `tests/artifacts/` 的差異確認是預期的，再執行 `python3 tests/run_tests.py --record` 重新錄製標準答案，並把 `tests/golden/` 一起 commit。
- 截圖與像素雜湊跟機器和 Chromium 版本有關。換一台電腦時，先在舊版本（`git checkout baseline-v13` 或最近一次通過的 commit）用 `--record` 重錄，再切回來比對。
- `JK_GAME_JS=/path/to/game.js python3 tests/run_tests.py` 可以拿任何一版 game.js 跑同一套測試。
