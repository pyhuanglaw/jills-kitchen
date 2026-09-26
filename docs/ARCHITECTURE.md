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
| `docs/V16_CHANGES.md` | V16（做菜流程、Dylan 的戲、等候長椅、備份存檔）改了什麼、為什麼 |
| `docs/V18_CHANGES.md` | V18（跨日變暗與音樂的根因、營業中 checkpoint、Jill 的休息與互動、料理研發、相簿／日誌）改了什麼、為什麼 |
| `docs/V17_CHANGES.md` | V17（Dylan 出場頻率、視覺打磨）改了什麼；第 5 天畫面消失的根因 |
| `docs/LIFE_SYSTEM.md` | 沙發、閨蜜機、Jill 的晚上、五隻貓的沙發行為、Dylan 隱藏線的規則與測試 |
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
| `LIFE` | 當晚的生活狀態（Jill 在沙發上的位置與活動、閨蜜機、留下來的 Dylan、對話泡泡）。不存檔；每天開店與回到標題時 `lifeReset()`。晚上由 `lifeUpd` 更新；**營業中 Jill 休息時**（`R.jill.rest==='sit'`）`LIFE.jill` 也會 `on`，由 `restTick` 更新，`endRest()` 清掉 | `lifeUpd`（每幀）、`startClosing`、`dylanLinger`、`startRest`／`restTick`／`endRest` |
| `S.checkpoint` | 營業中的快照（`snapshotService()` 的純資料），每 20 秒、暫停、切到背景時更新；`endDay`／`nextDay`／開店時清掉。標題畫面用它顯示「繼續營業 · 19:42」 | `checkpointSave`、`clearCheckpoint`、`resumeCheckpoint` |
| `c.sofa` / `c.sofaOn` | 貓在沙發上的位子（預約時就設定，跳上去後 `sofaOn=true`）；`releaseSpots(c)` 會一併清掉 | `goSofaSlot`、`leaveSofa` |

測試會檢查的不變條件（`tests/run_tests.py` 的 `INV` 與 `cat_ai_keeps_running`）：

- `R` 存在 ⇔ `phase==='service'`
- `paused` 只會在營業中，而且一定有選單開著
- 營業中且沒暫停時，選單畫面是隱藏的
- 一隻貓同時最多佔一個位置；佔位時不會同時在跳台上或 Jill 旁邊；軟墊最多兩隻、不重複
- 貓的座標永遠是有限數字，也不會跑出房間
- 沙發：一個位子一隻貓、Jill 腿上最多一隻、座墊上的區間（Jill 身體、她的腿、Dylan、每隻貓）互不重疊、閨蜜機移動時不會撞到貓（詳見 `docs/LIFE_SYSTEM.md`）

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
1. `DISHES` 加一筆：`{n, cat, st, v, price, cost, diff, pop, lv, rd, steps:[...], fin:[...]}`，步驟用 `sA`（加料，玩家點）、`sK`（Jill 自己做的手工：切菜、打發，開始後不用管）、`sW`（等待；第 4 個參數 `'stir'` 會讓 Jill 在鍋邊翻炒）、`sZ`（抓時機：翻面、起鍋、出爐）、`sH`（長按量表，飲料）、`sD`（撒幾下）。`fin` 是上桌時自動擺上的配料（不是步驟）。V16 起**沒有連點步驟**（`sT` 已移除）。
   - 一道普通菜控制在 2–5 次玩家操作，測試 `cooking_flow_families` 會數。
   - 五種家族的形狀：煎（放料 → 等 → 翻面 → 等 → 起鍋）、燉煮（快速備料 → 長時間等 → 回來加一次 → 完成）、冷盤（幾秒手工 → 擺盤 → 淋醬）、快炒（照順序放料 → 短暫翻炒 → 一次調味）、烤箱（備料 → 長時間等 → 出爐）、飲料（量表，沒變）。
   - 寬容度：`sZ` 的目標區 ±w 是 PERFECT、±(w+.12) 是 GOOD，1.0–1.22 之間「有點過」但只扣分，超過 1.22 才焦；`sW` 的 `over` 是超時秒數，超過才扣分，0 表示不扣。
2. 用到新食材 → `ING` 加一筆。
3. 成品圖 → `VESSEL` 與 `paintFood` 加分支；鍋中畫面 → `drawContents` / `drawTopLayers`。
4. 執行測試。`cooking_every_recipe` 會自動把新料理從頭做到完，確認完美操作能拿到 PERFECT。
5. **料理 id 一旦發佈就不要改名或刪除**：存檔的 `menu`、`unlocked`、`stock`、`xp`、`price`、`rstar` 都用 id 記錄。真的要改，寫 migration（第 5 節）。

### 廚房員工能做什麼（`chefCan` / `chefHandles`）
- 廚師只做 Jill 已經做過至少一次的菜（`S.xp[d]>0`），而且難度 ≤ min(3, 等級)：LV1 簡單菜、LV2 一般菜、LV3 起全部（招牌菜永遠除外）。
- LV3 起也會接手 Jill 已經開始的菜（`chefHandles(s)` 對「他自己開始的」或「他有能力做的」都成立）。料理台面板會自動關掉，讓玩家去做別的。
- 服務生 LV2（帶位＋點餐）會把出餐口做好的菜端到桌上（`crewUpd` 的 `serve` 任務；`w.carry` 畫在手上）。
- 員工待命位置：服務生 (84,150) 門邊、清潔 (362,190) 右側，不要放在沙發上（V15 的 (110,136) 就是坐在沙發座墊上）。

### 等候區（門口的長椅）
- `BENCH`：三個座位（`seats`，y 座標）＋兩個站位（`stand`）。座位用「預約」而不是索引：客人 `g.spot={k:'seat'|'stand',i}`、貓 `OCC.bench0..2`。`benchFree(i)`／`standFree(i)`／`pickSpot(g)`／`requeue()` 是唯一的分配邏輯：1–2 人先坐、3 人以上站、沒位子就站；貓離開後站著的人自己坐過去。
- 客人流程（`updGroup`）：進門 → 落地點 `(DOOR.x, DOOR.y+22)` → 有合適空桌就直接走過去（`seatGroup`）→ 沒有就去長椅 → 坐著等（2–4 秒看一次有沒有空桌，先來先坐，坐著時耐心消耗 ×0.7）→ 自己起身走過去。玩家點客人或點空桌可以馬上帶位；服務生的 `seat` 任務也還在。
- 等待時的小動作 `g.wact`：`idle`／`phone`／`look`／`cat`（附近 110px 內有貓就看牠）／`talk`（兩人以上）。純視覺，沒有數值。
- 沒位子而且門口滿了：`spawn` 直接讓他們「看到客滿，失望地走了」（原本就有的 `queueMax()` 也還在）。
- 幾何：長椅在 x 48–76、y 140–250，門口落地點在它上方，沙發從 x=88 開始，跳台最高層在 y=254+DY。測試 `waiting_bench` 檢查它不碰門口、桌子、沙發、跳台、閨蜜機、員工待命點。

### 畫人、畫光、畫影子
- 所有人（客人、員工、Dylan、Jill）都走 `drawPerson(c,x,y,L,o)`。`L`：`skin/hair/hs(0–8)/top/acc/pants`；`o`：`seated/lounge/step/bob/mood/blink/gaze/hold/expr…`。座標系是固定的（頭半徑 9.6、身體寬 17），改外觀不要動這些數字，否則點擊判定和位子會跑掉。Jill 專用的 `expr`（smile/focus/soft/tired/amused）由呼叫端依情境決定。
- 從 `hash()`（無號 32 位元）取索引一律用 `>>>`，不要用 `>>`：有號位移會把一半的值變成負數索引，畫圖時取到 `undefined` 就會讓整個 rAF 迴圈死掉（V17 修過一次，見 `docs/V17_CHANGES.md`）。
- 站在地上的東西用 `softShadow(c,x,y,rx,ry,a)` 畫接觸陰影；整體光線用 `tintFor(dusk)`（開店→傍晚→打烊三段），打烊後另有以沙發為中心的暗角。地板的織紋、暗角在 `makeBg` 快取裡。
- 畫圖的函式裡**不能丟例外**：`drawScene` 跑在 `requestAnimationFrame` 裡，一個例外就是整個遊戲停住而 UI 還活著。`world_stays_visible_across_days` 會抓這種事，但新畫法請先在 `tests/artifacts/` 看截圖。

### 新增貓咪行為
1. 在 `catDecide` 用 `add('新行為', 權重)` 加入候選；權重依個性（`id`）決定。
2. 在同一個 `switch(ch)` 加 `case`，設定 `c.st` / `c.pose` / `c.t`，要移動就用 `catWalk`。
3. 在 `updateCats` 的狀態 `switch(c.st)` 處理每幀行為，結束時呼叫 `catDecide(c)`。
4. 會佔用家具就走 `catGo` / `OCC`，並確保每條離開路徑都經過 `releaseSpots(c)`。
5. 遵守貓咪世界規則：五隻都在，不寫離開、死亡、懷念類內容。
6. 每多一次 `Math.random()` 都會讓之後所有隨機結果改變，所以 golden 測試**一定會**失敗，這是正常的。確認截圖差異是預期的，再重新錄製（第 6 節）。

### 新增打烊後的行為
- Jill：在 `jillDecide` 加一個權重和一個 `act`，在 `jillLife` 處理它的每幀更新與結束。不要加數值需求。
- Dylan：在 `dylanDecide` 加權重與 `case`，在 `dylanArrive` / `dylanUpd` 處理。他的「階段」只能靠 `dylanStageCheck` 的條件推進，不要在 UI 顯示。
- 貓在沙發上的新位子：加到 `sofaSlots`，並在 `pickSofaSlot` 給每隻貓一個權重。位子一定要能用區間表示，不變條件才管得到。
- 新的線索：往 `S.dylan.clues.<名字>` 累加即可，`dylanStageCheck` 數的是「有幾種線索」。

### 新增可以點的家具
- 貓咪相關：`SPOT` 加座標、`hitSpot` 加判斷、`tapSpot` 加反應，繪製放在 `drawScene` 對應的區塊。
- 廚房用品：`kitchenItems()` 加一筆（繪製和點擊判斷共用同一份座標），`tapKItem` 加 `case`。
- 房間深度會隨螢幕高度調整（`applyDY`），會跟著地板移動的 y 座標請比照 `SPOT.scr` 寫在 `applyDY` 裡。

### 新增存檔欄位
- **只要在 `newState()` 加上預設值**。舊存檔讀進來時缺少的頂層欄位會自動補上。
- 如果是放在 `eq`、`decor`、`staff`、`stats` 這四個物件裡的新鍵，也會自動補上（`fillDefaults` 會逐鍵合併）。
- 其他巢狀物件裡的新鍵**不會**自動補，要在讀取處加 `||預設值`，或寫 migration。

## 5. 存檔格式改變（migration）

`parseSave(text)` 是唯一的解析管線：解析 → 是不是我們的存檔（頂層 `v`/`day`/`money`/`unlocked`/`menu`，或是備份檔的外殼 `{app:'jills-kitchen',save:{…}}`）→ 檢查版本 → 依序跑 `MIGRATE` → `fillDefaults` → `legacyCrew` → 基本合理性檢查。回傳 `{o}` 或 `{err}`，**不碰 `S`、不碰 localStorage**。`load()`（瀏覽器自己的那份）和「讀取存檔」（玩家選的檔案）都用它。

備份／讀取（V16）：
- 「備份存檔」`exportSave()`：先 `save()`，再把 `{app,kind,v,exported,save:S}` 存成 `JillsKitchen_Save_YYYY-MM-DD_HHMM_DayN.json` 下載。營業中不能備份。
- 「讀取存檔」`pickImportFile()`：隱藏的 `<input type=file>`（只建一次）→ `FileReader` → `importSaveText()` → `parseSave` → 成功就放進 `pendingImport`，設定畫面顯示「讀取這個備份？DAY n · $m，目前的進度會被取代」→ 玩家按「讀取這個存檔」才 `importConfirm()`：換掉 `S`、`save()`、清快取、`lifeReset()`、回標題。失敗（不是 JSON、不是我們的存檔、版本太新、壞掉）只出一個 toast，`S` 完全不變。
- `S.savedAt`：每次 `save()` 蓋上時間戳，設定畫面顯示「上次存檔」。舊存檔沒有這個欄位也沒關係。

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

照片：`S.album`（V18 起）是一個陣列，每種畫面第一張 `keep:true`（珍藏），一般照片最多 `ALBUM_CAP`=30 張、最舊先出；每張 240×176 JPEG 約 6 KB，全滿約 300 KB。舊的 `S.mem` 在第一次 `albumList()` 時搬進相簿（圖片不再留在 `S.mem`）。要拍新種類的畫面：在 `MEMS` 加標題、`MEM_TXT` 加那句話、在條件成立處呼叫 `memo(id,x,y,info)`——冷卻、每日上限、容量都由 `albumAllows`／`albumAdd` 處理。如果以後要無上限，先搬到 IndexedDB。

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

  只要畫面、動畫、貓咪行為或數值有任何變化，它就會失敗。截圖比對只容許文字反鋸齒的微小雜訊：最多 40 個像素、每個像素的亮度差最多 8。不一致時，實際截圖與差異圖會存到 `tests/artifacts/`。
- **有意改變**遊戲內容後：先看 `tests/artifacts/` 的差異確認是預期的，再執行 `python3 tests/run_tests.py --record` 重新錄製標準答案，並把 `tests/golden/` 一起 commit。
- 截圖與像素雜湊跟機器和 Chromium 版本有關。換一台電腦時，先在舊版本（`git checkout baseline-v13` 或最近一次通過的 commit）用 `--record` 重錄，再切回來比對。
- `JK_GAME_JS=/path/to/game.js python3 tests/run_tests.py` 可以拿任何一版 game.js 跑同一套測試。
