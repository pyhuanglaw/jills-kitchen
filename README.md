# Jill's Kitchen

A Restaurant by Chef Jill — 手機優先的餐廳經營遊戲。純 HTML / CSS / JavaScript，不需要安裝任何套件或建置工具。

## 專案結構

```
jills-kitchen-project/
├── index.html                      進入點：頁面結構，載入 CSS 與 JS
├── css/
│   └── style.css                   所有介面樣式（HUD、訂單、選單、商店、說明書…）
├── js/
│   └── game.js                     全部遊戲邏輯（見下方模組說明）
├── jills-kitchen-single-file.html  單檔版本（由建置腳本產生，直接開就能玩）
├── docs/
│   ├── ARCHITECTURE.md             程式結構、全域狀態、擴充守則、存檔 migration、測試流程
│   ├── V16_CHANGES.md              V16：做菜流程、Dylan 的戲、等候長椅、備份存檔
│   ├── LIFE_SYSTEM.md              打烊後的生活系統：沙發、閨蜜機、Jill、五隻貓、Dylan（含劇情，會爆雷）
│   └── REFACTOR_REPORT.md          安全網與重構報告（分析、風險、做了什麼、沒做什麼）
├── tests/                          回歸測試、舊存檔樣本、畫面標準答案
├── tools/                          單檔建置、靜態分析、lint
├── backups/v13-before-refactor/    重構前的原始檔案（可直接換回去）
└── README.md
```

> 手動修改的只有 `index.html`、`css/style.css`、`js/game.js`。改完執行 `python3 tools/build_single.py` 更新單檔版。

遊戲裡所有圖像（Jill、客人、五隻貓、料理、家具、廚房設備）都是用 Canvas 程式即時畫出來的，所以沒有圖片素材資料夾；音樂與音效也是用 Web Audio 即時合成。唯一的外部資源是 Google Fonts 字型（Young Serif、Figtree），離線時會自動改用系統字型。

## 怎麼執行

- **最簡單**：直接用瀏覽器打開 `index.html`（或 `jills-kitchen-single-file.html`）。
- **用本機伺服器**（建議，手機測試也方便）：

  ```bash
  cd jills-kitchen-project
  python3 -m http.server 8000
  ```

  然後打開 `http://localhost:8000`。同一個 Wi‑Fi 下的手機可以用電腦的 IP 連進來。

- **放上網路**：把整個資料夾上傳到任何靜態網站服務即可（GitHub Pages、Netlify、Vercel、Cloudflare Pages 等），不需要後端。

## 存檔

- 存檔使用瀏覽器的 `localStorage`，鍵名是 `jills-kitchen-save-v1`。
- 存檔只存在「那個瀏覽器 + 那個網址」底下。所以：
  - Claude 上的遊戲頁面、你本機打開的檔案、你自己架的網站，三者的存檔互相獨立。
  - 換手機、換瀏覽器、清除網站資料，存檔都不會跟著走。
- 遊戲內「設定・存檔」可以手動存檔、回到上次存檔、重置（重置需要按兩次確認）。
- **備份存檔**：把進度存成一個 `JillsKitchen_Save_日期_時間_DayN.json`；**讀取存檔**：選那個檔案，確認後取代目前進度。不是 Jill's Kitchen 的檔案、壞掉的檔案、比較新的版本都會被拒絕，目前的進度不會動。換手機、換瀏覽器就靠這個。
- 如果存檔讀不懂（檔案壞掉，或是用舊版程式打開新版存檔），遊戲會先把它原封不動複製到 `jills-kitchen-save-v1-unreadable`，再開始新遊戲，不會把它蓋掉。
- 新增存檔欄位、改存檔格式的規則見 `docs/ARCHITECTURE.md` 第 4、5 節。

## game.js 模組導覽

`game.js` 是一個立即執行函式（IIFE），依照區塊註解分段，搜尋 `/* ====` 可以快速跳轉：

| 區塊 | 內容 |
|---|---|
| utilities | 共用數學、繪圖小工具、亂數 |
| game data | 料理與食譜步驟（`DISHES`）、食材（`ING`）、客人類型、熟客、擴建等級、裝潢、成就、評論 |
| save / state | 存檔格式 `newState()`；`load()`＝版本檢查 → `MIGRATE` → `fillDefaults` → `legacyCrew`；讀不懂的存檔會被保留；`save()` |
| derived / layout of the room | 售價、熟練度等計算值；桌位與座位配置 |
| food art / people art / icons | 料理、人物、家具與圖示的 Canvas 繪製 |
| audio | 背景音樂（bossa nova 風格即時合成）與所有音效 |
| planning a day | 天氣、事件、每日任務、建議進貨 |
| service | 營業流程：客人生成、帶位、點餐、步驟式烹飪與計分、出餐、結帳、評論、打烊 |
| effects / HUD & tickets | 橫幅、提示、COMBO、上方狀態列與訂單單據 |
| layout / scene render | 依螢幕大小調整餐廳深度；餐廳、牆面、燈光的繪製 |
| kitchen render | 料理台彈窗、開放式廚房檯面與設備 |
| cats | 貓跳台、牆上貓爬架、貓咪外觀與動作繪製 |
| five cats: personality AI | 五隻貓的個性、關係、Jill 身邊座位競爭、埋伏、賽跑、怕生、打烊後模式、回憶照片 |
| life | 大沙發與位子計算、閨蜜機、Jill 打烊後的自主休息、Dylan（營業中的行為、留下來的晚上、隱藏進度） |
| crew / incidents / emergency stock | 員工；突發事件；缺料時的緊急叫貨 |
| stars & lab | 食譜星級、試做實驗室 |
| Jill's bag cabinet / guide | 包包收藏櫃；遊戲說明內容 |
| input / screens | 觸控操作；標題、開店前、結算、商店、餐廳手冊、設定 |
| loop / boot | 主迴圈與啟動 |

## 常改的地方

- **料理與食譜**：`const DISHES={...}`，每道菜的 `steps` 決定料理台的操作步驟。
- **貓咪名字與外觀**：`const CAT_DEF=[...]`（樾樾、小齁、包包、柔柔、寶寶）。
- **貓咪行為權重**：`function catDecide(c)`。
- **一天營業長度**：`function dayDur(D)`。
- **客人數量**：`function expected(weather,event)`。
- **加東西之前**：先讀 `docs/ARCHITECTURE.md`，裡面有新增料理、貓咪行為、家具、存檔欄位的步驟與注意事項。

## 測試

```bash
pip install playwright && playwright install chromium   # 第一次才需要
python3 tests/run_tests.py                  # 測多檔版
python3 tests/run_tests.py --target single  # 測單檔版
python3 tests/run_tests.py --record         # 刻意改變遊戲內容後，重新錄製標準答案
```

29 項測試涵蓋：
- 新遊戲、舊存檔、存讀檔、備份檔匯出／匯入（含壞檔案被拒絕）、開店、打烊；
- 客人完整流程、每道料理（每道 2–5 次操作、五種料理家族的形狀、寬容度）、廚房員工的能力階梯、服務生送餐、門口長椅的等候流程、Dylan 的付款／收桌／不是員工、經濟數值；
- 五隻貓的初始化、個性 AI 與個性指紋；
- 打烊後的生活：沙發位子幾何、Jill 的晚上、五隻貓怎麼用沙發、Dylan 的前期與揭露；
- UI 與觸控操作、主迴圈只有一份、長時間遊玩不累積；
- 逐像素比對畫面的黃金基準。

詳細說明見 `docs/ARCHITECTURE.md` 第 6 節。
