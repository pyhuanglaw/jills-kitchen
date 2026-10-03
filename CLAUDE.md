# CLAUDE.md — 開工前先讀

這是《Jill's Kitchen》：手機優先的單檔 HTML 餐廳遊戲，但它不是一般的餐廳數值遊戲。玩家想看的是 Jill、五隻貓、員工、熟客慢慢
生活下去。在動任何東西之前：

1. **`docs/PROJECT_MEMORY.md`**：設計 canon，以及每條規則的原因。看到程式和它不一樣，先想是不是 regression，不要把它改回舊規則。
2. **`docs/CURRENT_STATE.md`**：現在的 branch、已發布版本與網址、待辦、待確認。
3. **`docs/ARCHITECTURE.md`**：程式結構、全域狀態、存檔 migration、測試怎麼跑。
4. 要發布時：**`docs/RELEASE_CHECKLIST.md`**（唯一的發布流程）。

最重要的幾條（細節與原因都在 PROJECT_MEMORY §0）：

- **只用繁體中文**：遊戲、文件、回覆都一樣。
- **Canon 衝突就停下來問玩家**，用 `CONFLICT FOUND` 的格式。不要用測試、模擬、換 seed、程式現況替玩家決定產品設計。
- **運算是付費的**：完整回歸只用在 release gate 和高風險修改；先想清楚這次執行要回答什麼問題。
- **Commit ≠ Push ≠ Publish**：開發中隨時 commit、push 到開發 branch；玩家說「發布」才發布。
- **I / T / O 分開報告**：測試通過不等於玩家在 iPhone 上看得到。
- **報告 ≠ 停下**：回報後繼續已定義的工作，除非遇到 canon 衝突、存檔風險，或需要玩家做的產品決策。
- 玩家說「這個是 hard canon，寫進 project memory」時，更新 `docs/PROJECT_MEMORY.md` 對應的段落，附上日期和原話，然後 commit。

文件記住不能忘的規則；你讀 code 時仍然保留第一次看的眼睛：抓 bug、質疑既有實作都可以，只是不要在不知道原因的情況下把刻意改過的設計改回去。
