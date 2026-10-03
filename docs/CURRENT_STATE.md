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

- 目前沒有（rc8.1 之後）。

## 測試

- 233 個測試（`python3 tests/run_tests.py`；`-k a,b,c` 跑指定的）。rc8 的 gate：252ff1c 上 231 過、2 個失敗都是測試本身，已在
  8f7d6b2 修好並重跑通過。
- 已知會在單一 seed 上偶爾落差的機率性測試，都在測試註解裡寫了量過的分布（例：`lounge_i_content_bar_food…`、
  `v24_rc6_new_things_are_talked_about`）。

## 待辦／待確認

- **太太的手機不用登入就能匯出／備份存檔**：還沒解決，需要玩家用手機實測。不要用「文字框複製」的方式（會讓 iPhone 當機）。
- 《晚點回去》的四句工作閒聊（「今天沙發那四個，炸雞點了三次。」……）是開發 session 寫的，玩家可以換。
- `docs/evidence/v24_rc8/release/qing_tuo/` 的重拍截圖缺《講完》那一組（截圖腳本逾時）；原本的 q5 在 `docs/evidence/v24_rc8/qing_tuo/`。

## 美術

- 玩家要的十張插圖（Madame Lin 線 5 張、晴 × 阿拓 5 張）都已放進遊戲。目前沒有缺圖。

## 需要玩家正常遊玩才能確認的（O）

- 員工滿編時 Jill 大半個營業時間在房間休息，看起來是否自然；廚師去別站幫忙會不會讓雇人變得不重要。
- 晴 × 阿拓的節奏：從 Day 74 存檔大約 13 天走完五幕（Day 82 / 84 / 88 / 90 / 95）。
- 十張圖在手機上的樣子。
- Madame Lin 線從新遊戲 Day 1 開始的節奏（模擬是從 Day 30、Day 52 的存檔跑的）。
- 樾樾打烊後出來等 Jill、Jill 在開店和快打烊時在主廳。

## 下次發布前

照 `docs/RELEASE_CHECKLIST.md`：這一批要求做完 → 完整回歸（在要發布的 commit 上）→ 手冊檢查與 GUIDE 戳記 → 繁體掃描 →
`build_single.py`、`build_artifact.py` → 發布到上面的新網址 → 讀回、`live_check.py` → 報告。一般發布不打 zip。
