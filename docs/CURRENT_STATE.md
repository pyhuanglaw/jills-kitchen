# Jill's Kitchen — 目前狀態（暫時的，會一直更新）

這份只放「現在」的狀態：branch、版本、待辦、待確認。永久的設計規則在 `docs/PROJECT_MEMORY.md`，不要寫到這裡；這裡的內容過時了就
直接改掉或刪掉。最後更新：2026-10-06，全面 Audit 與例行 QA 合回 `main` 之後（遊戲還是 rc8.5，沒有發布）。

## Repo 與 branch

- GitHub：`pyhuanglaw/jills-kitchen`，預設 branch 是 `main`。
- **`main` ＝ Jill's Kitchen 的正式主線**：目前的、穩定的、發布出去的版本都在這裡。最新正式版是 bded558（v2.4 rc8.5），之後
  `main` 上只有文件與紀錄。從 v2.2.1 起的完整開發歷史都在 `main` 上。
- 還沒做完的遊戲功能，另外開短期的 `feature/…` 或 `wip/…` branch；做完、測試通過才回到 `main`，發布的 commit 一定在 `main` 上。
  文件與紀錄可以直接在 `main`。不要讓工作 branch 跟 `main` 長期並行。
- GitHub 上的 branch：`main`、`archive/rc7.6-import-main`、`feature/fewer-lines`（rc8.5，已合回 `main`，可以在 GitHub 網頁刪掉）、
  `feature/dylan-room`（Dylan 在房間的名字，還沒合回、還沒發布）、`feature/lounge-decided`（《看看》後直接決定接隔壁、Lounge I 的新條件；
  還沒合回、還沒發布）、`qa/audit-2026-10-06`（全面 Audit 與例行 QA；2026-10-06 使用者同意合回 `main`，已合回，可以在 GitHub 網頁刪掉）。
- 已刪除（玩家 2026-10-04 在 GitHub 網頁刪掉）：`feature/ken-tasting-pictures`（81cbe46，rc8.4 已合回 `main`）、`wip/lin`（舊的開發
  branch 名稱；最後指向的 b87b77b 在 `main` 裡）、`claude/jills-kitchen-github-setup-4x7483`（8ca784b，接在舊的匯入 commit 後面改網址；
  同樣的改動在主線的 ec985d1）。三條的內容都已經在 `main` 或不需要了。
- `archive/rc7.6-import-main`（d0947ea）：2026-10-03 把 rc7.6 的 12 個 zip 匯入 GitHub 時建的那一個 commit，原本的 `main`。跟現在的
  `main` 沒有共同祖先，只是保存，不合併。
- 2026-10-04 的整理：`main` 從 d0947ea 強制改指到 b865d3c（舊的保存在 `archive/rc7.6-import-main`）。要復原：
  `git push --force-with-lease=refs/heads/main:<目前的 main> origin d0947ead2c18167ab3955fef51478a9168f5b8fd:refs/heads/main`。
- 本機的 `bundle` remote 是原開發 session 的備份 bundle，只是還原來源，不推送。
- 版本 tag（`v2.4-rc8` 到 `v2.4-rc8.5` 等）只在本機：推 tag 到 GitHub 時連線會被中斷。各版的 commit 寫在它的發布報告裡。
- 舊版本（玩家 2026-10-03 給的 v2.2.1、v2.4 rc4，以及其他每一版）怎麼查：`docs/OLD_VERSIONS.md`。

## 已發布

- **v2.4 rc8.5**，2026-10-04，發布到 **https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA**（**Version 7**，id 1791128420-4d10）。
  遊戲內容＝ commit bded558（tag `v2.4-rc8.5`，只在本機）。報告：`docs/V24_RC8_5_REPORT.md`。Gate：bded558 上 247/247；讀回與
  live_check 通過（`docs/evidence/v24_rc8_5/`）。內容：玩家的圖跳出時店一定停住；營業中員工會上休息室（以前在忙的店裡幾乎不會）；
  二樓房間的訂購／動工按鈕修好（從 rc6 起按了沒反應，包廂也一直蓋不起來）；點單的愛心只給 Sophie 和 Mia；路人閒聊少很多、
  同一句一週不重複、沒頭沒尾的句子改寫（Ken 和杜的「果味」）。
- v2.4 rc8.4（Version 6，922223b；報告 `docs/V24_RC8_4_REPORT.md`）：Ken 前三次品酒之夜各一張圖和相簿照片；名稱改成「品酒之夜」。
- v2.4 rc8.3（Version 5，e797665；報告 `docs/V24_RC8_3_REPORT.md`）：候位到店門口、三種披薩、房間的貓砂盆與碗架、寶寶靠著 Jill／
  柔柔睡腳上、拿掉 PERFECT 橫幅、Sophie 和 Mia 坐隔壁桌、杯墊那段的旁白、香煎鴨胸 6 天說一次、品酒之夜的分帳與開場、猜酒、
  新空間的照片、特別的晚上「繼續營業」接得回來。
- v2.4 rc8.2（Version 4，b443ab5；報告 `docs/V24_RC8_2_REPORT.md`）。
- 前一版 v2.4 rc8.1（version 3，df8a95b）；再前一版 v2.4 rc8（version 2，252ff1c；報告 `docs/V24_RC8_REPORT.md`）。
- 玩家在 2026-10-03 選擇以後都發布到這個新網址。舊網址 https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps 停在 rc7.6（version
  49），不再更新。舊網址的存檔要用遊戲裡的「設定・存檔」備份後搬過來。
- 新網址的分享設定由玩家在頁面的分享選單決定（目前是「知道連結的人都能看」）。

## 尚未發布的工作

### 已完成、尚未發布

- **Dylan 在房間裡的名字**（branch `feature/dylan-room`，還沒合回 `main`、還沒跑完整回歸）：玩家 2026-10-05「Dylan已經揭露但在房間還是沒寫Dylan」。
  揭曉後他頭上的名牌寫 Dylan（揭曉前「先生」）、房間分頁寫「Jill 和 Dylan 的房間」（放不下時「Jill & Dylan」、再放不下「房間」），
  分頁那一排不會再超出畫面；帽子照玩家 10/3 的話一直戴著。相關測試通過（`rc86_dylan_is_named_in_their_room` 等）。玩家說「發布」時：
  合回 `main` → 完整回歸 → 發布。

- **Lounge I：《看看》後 Jill 就決定接；條件是評分 4.0＋$50,000，不等 Madame Lin 的最後一晚**（branch `feature/lounge-decided`，
  還沒合回 `main`、還沒跑完整回歸、沒有發布）：使用者 2026-10-06 的最終規則（PROJECT_MEMORY §6 第 6 條）。玩家會看到：《看看》最後一句
  「隔壁，Jill 決定接下來。簽約和改裝在「升級餐廳 › 店舖工程」。」，沒有「接下隔壁／再想想」；當天店舖工程就有 Lounge I，卡片只寫還缺
  什麼（「需要餐廳評分 4.0（目前 X）」、「還差 $X」），夠了就能按「簽約・開工 $50,000」。她最後一晚之前簽，簽約前一晚就是她的最後一晚；
  沒簽的話她照常做到最後一晚，結束時提醒一次簽約在哪裡。Lounge II／III 不變。舊存檔：「再想想」、卡片沒回答、《看看》和卡片之間存的檔
  都當作已決定（`linDecMig`）；已付 $120,000 的不重收、已開幕的不動。相關 29 個測試通過，含 `v24_lounge_one_after_the_viewing_rating_four_
  and_50000_no_wait_for_her_last_night` 和例行 QA 的 `qa_lounge_one_signs_before_her_last_night`；例行 QA 11 過、17 個已知未修。
  新玩家時間表（`docs/evidence/lounge_decided_2026-10-06/50000/`）：規則照現在，模擬玩家第 32–34 天買側廳後評分掉到 2–3.7、110 天內
  沒開 Lounge；假設評分不擋，第 48–49 天付錢、第 51–52 天開幕，依賴 Lounge 的故事比 $80,000 早 12–17 天。開幕後收銀機停在 $0 的平衡
  問題：方案比較在 `options.md`，等使用者選，正式經濟沒改。評分 4.0 會卡住評分掉下去的玩家：等使用者決定。使用者說「發布」時：合回 `main` → 完整回歸 → 發布。
- **2026-10-06 全面 Audit 與例行 QA**（已合回 `main`，使用者 2026-10-06「Audit 這套 QA 工具和測試我同意合回 main」；沒有改遊戲、沒有發布）：報告 `docs/audit/2026-10-06/README.md`；
  例行 QA `python3 tests/run_tests.py --qa`（`docs/QA.md`）；全面 Audit 的做法 `docs/audit/PLAYBOOK.md`。Audit 找到、還沒修的問題，
  每一條都已經有測試在等（`tests/qa_known_open.json`）。

### 進行中／等待玩家素材

- 沒有。品酒之夜的三張圖已在 rc8.4 發布。

## 測試

- **例行 QA**（2026-10-06 起）：`python3 tests/run_tests.py --qa`，`tests/qa_tests.py` 的 `qa_` 測試，用 `tests/player.py` 真的點畫面、
  故事面板開著。每次改完遊戲跑；完整回歸也包含它們。已知未修的問題列在 `tests/qa_known_open.json`（失敗顯示 OPEN、不算失敗；修好時
  顯示 FIXED，要把那一條拿掉）。
- 247 個測試（`tests/run_tests.py` 95、`tests/v23_tests.py` 30、`tests/v24_tests.py` 122；`feature/lounge-decided` 上 v24 多一個，248；`python3 tests/run_tests.py` 全跑，`-k a,b,c`
  跑指定的）。最近一次完整回歸：rc8.5 的 bded558 上 247/247（`docs/evidence/v24_rc8_5/regression/`）。
- 已知會在單一 seed 上偶爾落差的機率性測試，都在測試註解裡寫了量過的分布（例：`lounge_i_content_bar_food…`、
  `v24_rc6_new_things_are_talked_about`）。

## 待辦／待確認

- **2026-10-06 Audit 的結果**（`docs/audit/2026-10-06/README.md`）：十件最重要的事、接下來最值得做的 3–5 件、以及最後一段「需要使用者決定」
  的 20 個問題，都等使用者看過再動。Audit 本身沒有改遊戲。
- ~~營業中存檔、「繼續營業」在特別的晚上會變成空店~~：rc8.3 已修（`rc83_a_special_evening_comes_back_with_its_room`）。原本的說明：存檔時有人在
  `piano`（予安彈琴）、`toHost`／`host`（Ken 主持品酒夜）這些狀態，`restoreService` 的 `G_STATES` 不認得，整個還原失敗，
  退回「同一時間、店是空的」；主廚之夜的 `R.cn`、品酒夜的 `R.kt`、予安的 `R.ya` 也不會還原。存檔本身沒有壞，只是那一晚
  的客人不見。修法：還原時接受這些狀態，並重建 `R.ya`／`R.kt`／`R.cn`（玩家 Day 87 存檔可以重現：19:19 的 29 組客人變 0）。
- **菜單上「♥ 陳伯伯」這種「熟客最愛的菜」標記要不要也拿掉愛心**：玩家選了「愛心只給 Sophie 和 Mia」（點單已改），菜單的標記另有手冊說明，
  還沒動，等玩家說。
- **太太的手機不用登入就能匯出／備份存檔**：還沒解決，需要玩家用手機實測。不要用「文字框複製」的方式（會讓 iPhone 當機）。
- `docs/evidence/v24_rc8/release/qing_tuo/` 的重拍截圖缺《講完》那一組（截圖腳本逾時）；原本的 q5 在 `docs/evidence/v24_rc8/qing_tuo/`。

## 玩家回報、下一批

- 玩家 2026-10-04 晚上 Day 89–92 的回報都在 rc8.5 做完了（`docs/V24_RC8_5_REPORT.md`）。
- 長期方向（PROJECT_MEMORY §3）：Jill 的房間是一層「生活」，之後繼續加。

## 美術

- 玩家要的十張插圖（Madame Lin 線 5 張、晴 × 阿拓 5 張）都已放進遊戲。
- 缺的圖見上面「進行中／等待玩家素材」。

## 需要玩家正常遊玩才能確認的（O）

- 員工滿編時 Jill 大半個營業時間在房間休息，看起來是否自然；廚師去別站幫忙會不會讓雇人變得不重要。
- 晴 × 阿拓的節奏：從 Day 74 存檔大約 13 天走完五幕（Day 82 / 84 / 88 / 90 / 95）。
- 十張圖在手機上的樣子。
- Madame Lin 線從新遊戲 Day 1 開始的節奏（模擬是從 Day 30、Day 52 的存檔跑的）。
- 樾樾打烊後出來等 Jill、Jill 在開店和快打烊時在主廳。
- rc8.5：營業中切到「休息室」偶爾看到有人；二級休息室和包廂能買；有插圖的故事店會停住；一晚跳出的話少很多、看得懂。

## 下次發布前

照 `docs/RELEASE_CHECKLIST.md`：這一批要求做完、合回 `main` → 完整回歸（在要發布的 commit 上）→ 手冊檢查與 GUIDE 戳記 → 繁體掃描 →
`build_single.py`、`build_artifact.py` → 發布到上面的新網址 → 讀回、`live_check.py` → 報告。一般發布不打 zip。
