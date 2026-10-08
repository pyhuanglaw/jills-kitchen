# Jill's Kitchen — 目前狀態（暫時的，會一直更新）

這份只放「現在」的狀態：branch、版本、待辦、待確認。永久的設計規則在 `docs/PROJECT_MEMORY.md`，不要寫到這裡；這裡的內容過時了就
直接改掉或刪掉。最後更新：2026-10-08 凌晨，v2.4 rc8.8 發布（Version 10，Dylan 揭曉後房間裡寫他的名字）。

## Repo 與 branch

- GitHub：`pyhuanglaw/jills-kitchen`，預設 branch 是 `main`。
- **`main` ＝ Jill's Kitchen 的正式主線**：目前的、穩定的、發布出去的版本都在這裡。最新正式版是 9253fae（v2.4 rc8.8），之後
  `main` 上只有文件與紀錄。從 v2.2.1 起的完整開發歷史都在 `main` 上。
- 還沒做完的遊戲功能，另外開短期的 `feature/…` 或 `wip/…` branch；做完、測試通過才回到 `main`，發布的 commit 一定在 `main` 上。
  文件與紀錄可以直接在 `main`。不要讓工作 branch 跟 `main` 長期並行。
- GitHub 上的 branch：`main`、`archive/rc7.6-import-main`、`feature/fewer-lines`（rc8.5，已合回 `main`，可以在 GitHub 網頁刪掉）、
  `feature/dylan-room`（Dylan 在房間的名字，做在 rc8.5 上的原版 09f3312；同樣的改動已經帶到 `feature/dylan-room-rc88`，可以在 GitHub 網頁刪掉）、`feature/dylan-room-rc88`（上面那個帶到 rc8.7 的版本；2026-10-08 快轉合回 `main` 並發布成 rc8.8，可以在 GitHub 網頁刪掉）、`feature/cooking-gameplay`（新的料理系統，開發中；使用者 2026-10-07：不發布到玩家版）、`feature/lounge-decided`（故事優先：Lounge、試酒之夜、鋼琴、予安、二樓；
  2026-10-07 快轉合回 `main` 並發布成 rc8.7，可以在 GitHub 網頁刪掉）、`qa/audit-2026-10-06`（全面 Audit 與例行 QA；2026-10-06 使用者同意合回
  `main`，已合回，可以在 GitHub 網頁刪掉）、`fix/audit-narrative-2026-10-06`（Audit 之後的修正；2026-10-07 快轉合回 `main` 並發布成
  rc8.6，可以在 GitHub 網頁刪掉）、`proto/cooking-flow`（料理流程的獨立試玩頁 `prototype/cooking/`，不動遊戲本體；使用者 2026-10-07：
  不合併、不發布、現在不做）。
- 已刪除（玩家 2026-10-04 在 GitHub 網頁刪掉）：`feature/ken-tasting-pictures`（81cbe46，rc8.4 已合回 `main`）、`wip/lin`（舊的開發
  branch 名稱；最後指向的 b87b77b 在 `main` 裡）、`claude/jills-kitchen-github-setup-4x7483`（8ca784b，接在舊的匯入 commit 後面改網址；
  同樣的改動在主線的 ec985d1）。三條的內容都已經在 `main` 或不需要了。
- `archive/rc7.6-import-main`（d0947ea）：2026-10-03 把 rc7.6 的 12 個 zip 匯入 GitHub 時建的那一個 commit，原本的 `main`。跟現在的
  `main` 沒有共同祖先，只是保存，不合併。
- 2026-10-04 的整理：`main` 從 d0947ea 強制改指到 b865d3c（舊的保存在 `archive/rc7.6-import-main`）。要復原：
  `git push --force-with-lease=refs/heads/main:<目前的 main> origin d0947ead2c18167ab3955fef51478a9168f5b8fd:refs/heads/main`。
- 本機的 `bundle` remote 是原開發 session 的備份 bundle，只是還原來源，不推送。
- 版本 tag（`v2.4-rc8` 到 `v2.4-rc8.8` 等）只在本機：推 tag 到 GitHub 時連線會被中斷（2026-10-07 rc8.6、rc8.7 再試，一樣）。各版的 commit 寫在它的發布報告裡。
- 舊版本（玩家 2026-10-03 給的 v2.2.1、v2.4 rc4，以及其他每一版）怎麼查：`docs/OLD_VERSIONS.md`。

## 已發布

- **v2.4 rc8.8**，2026-10-08 凌晨，發布到 **https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA**（**Version 10**，id 1791419491-01ae）。
  遊戲內容＝ commit 9253fae（tag `v2.4-rc8.8`）。報告：`docs/V24_RC8_8_REPORT.md`。Gate：9253fae 上完整回歸 306/306；讀回與
  live_check 通過（`docs/evidence/v24_rc8_8/`）。內容：玩家 2026-10-05「Dylan已經揭露但在房間還是沒寫Dylan」——揭曉後房間裡他頭上
  的名牌寫 Dylan、選到的房間分頁寫「Jill 和 Dylan 的房間」（放不下時「Jill & Dylan」，你的 Day 92 存檔在 iPhone 寬度就是這個）。
  `feature/dylan-room` 原本做好的版本，沒有重新設計。
- v2.4 rc8.7（Version 9，24ecf98；報告 `docs/V24_RC8_7_REPORT.md`），2026-10-07 晚上。
  Gate：24ecf98 上完整回歸 305/305。內容：使用者 2026-10-07 的「故事優先」（`docs/v24/story_first_canon_2026-10-07.txt`、
  PROJECT_MEMORY §1、§5、§6、§7）——《看看》後 Lounge I $50,000、試酒之夜只看 Ken 的故事、Lounge II $80,000／III $150,000 沒有等級、
  阿拓在 Lounge I、鋼琴 $100,000 在店舖工程的 Lounge 那一段（沒有「遠程」）、二樓的故事不等 JILL 或錢、二樓工程 $160,000＋租金
  $4,000／日；手冊「Lounge 的人」。
- v2.4 rc8.6（Version 8，023b17c；報告 `docs/V24_RC8_6_REPORT.md`）：2026-10-06 Audit 之後的修正——電腦版分頁、對話一次一組、
  存檔與「繼續營業」、日誌長場景、手冊重寫、備料規則一種說法、拿掉「複製備份文字」。
- v2.4 rc8.5（Version 7，bded558；報告 `docs/V24_RC8_5_REPORT.md`）：玩家的圖跳出時店一定停住；營業中員工會上休息室；二樓房間的
  訂購／動工按鈕修好；點單的愛心只給 Sophie 和 Mia；路人閒聊少很多。
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

- **料理流程 prototype**（branch `proto/cooking-flow`，`prototype/cooking/`）：獨立試玩頁，不是遊戲本體。使用者 2026-10-07：不合併、
  不發布、現在不要再做；之後重新開始時，以正式遊戲原本的廚房畫面為底，不重新設計美術。私人連結 https://claude.ai/artifact/EBzi6qETraguAApvettBFe 。

- **新的料理系統＋Restaurant Workflow**（branch `feature/cooking-gameplay`）：使用者 2026-10-07、10-08 的規格（`docs/v24/cooking_*.txt`、
  `docs/v24/restaurant_workflow_b_2026-10-08.txt`，在那條 branch 上）。**HARD RULE（2026-10-08）：使用者說「可以進 main」以前，不 merge
  main、不發布到正式玩家版；只更新私人測試版**（PROJECT_MEMORY §10）。開發中；做到哪裡寫在那條 branch 的 `docs/cooking/ARCHITECTURE.md`，2026-10-08 早上的報告
  `docs/cooking/MORNING_REPORT_2026-10-08.md`。私人測試版（不是正式版，存檔分開）https://claude.ai/artifact/TQpEqEFgqUW6jUm2Gfnhbg ，
  用 `tools/qa/cooking_test_build.py` 建、發布到同一個網址。
  2026-10-08 晚上：Restaurant Workflow B（服務生一次端多盤、出菜口有上限、髒盤子拿回廚房洗、秀琴阿姨第一天幫忙；報告
  `docs/cooking/WORKFLOW_B_REPORT_2026-10-08.md`、設計 `docs/cooking/WORKFLOW_B.md`）和前三天的 onboarding（炒飯／咖啡／沙拉、
  起始現金 $1,200；`docs/cooking/ARCHITECTURE.md`「前三天」）都在私人測試版第 9 版。**等使用者決定**：商用洗碗機做什麼、
  中期的店少四分之一客人是否可以、兩個 Jill、主廚之夜一次端、秀琴阿姨第一天的字、燒焦的舊程式三件事。炒飯／裝盤等使用者
  在 iPhone 上確認後，才做其他 34 道菜。

- **2026-10-06 全面 Audit 與例行 QA**（已合回 `main`，使用者 2026-10-06「Audit 這套 QA 工具和測試我同意合回 main」；沒有改遊戲、沒有發布）：報告 `docs/audit/2026-10-06/README.md`；
  例行 QA `python3 tests/run_tests.py --qa`（`docs/QA.md`）；全面 Audit 的做法 `docs/audit/PLAYBOOK.md`。Audit 找到、還沒修的問題，
  每一條都已經有測試在等（`tests/qa_known_open.json`）。

### 進行中／等待玩家素材

- 品酒之夜的三張圖已在 rc8.4 發布。

## 測試

- **例行 QA**（2026-10-06 起）：`python3 tests/run_tests.py --qa`，`tests/qa_tests.py` 的 `qa_` 測試，用 `tests/player.py` 真的點畫面、
  故事面板開著。每次改完遊戲跑；完整回歸也包含它們。已知未修的問題列在 `tests/qa_known_open.json`（失敗顯示 OPEN、不算失敗；修好時
  顯示 FIXED，要把那一條拿掉）。
- 306 個測試（其中 50 個是例行 QA 的 `qa_` 測試，5 個是模擬玩家的 `sim_player_` 測試；`python3 tests/run_tests.py` 全跑，
  `-k a,b,c` 跑指定的）。最近一次完整回歸：rc8.8 的 9253fae 上 306/306（2026-10-08，在固定在那個 commit 的另一個 worktree 分三份跑，
  37 分鐘；`docs/evidence/v24_rc8_8/regression/`）。再前一次：rc8.7 的 24ecf98 上 305/305。這一批中途：合併 commit c614255 的完整回歸開跑後停掉（手冊一句話的出現條件漏改，
  a0ee007 修好）；a0ee007 上合併影響到的 96 個 94 過，2 個是測試還照舊規則寫，24ecf98 改了測試。
- 這一批的私人測試版（https://claude.ai/artifact/BzGu1nFBVEqDt72Fad1sHP ，Version 3，0e41527）已經被正式版 rc8.6 取代，不用再開。
- 已知會在單一 seed 上偶爾落差的機率性測試，都在測試註解裡寫了量過的分布（例：`lounge_i_content_bar_food…`、
  `v24_rc6_new_things_are_talked_about`）。

## 待辦／待確認

- **2026-10-06 Audit 的結果**（`docs/audit/2026-10-06/README.md`）：十件最重要的事、接下來最值得做的 3–5 件、以及最後一段「需要使用者決定」
  的 24 個問題（第 19、20 條已決定），都等使用者看過再動。Audit 本身沒有改遊戲。
- **模擬玩家從 Day 92 存檔往後再跑 10–15 天**（看包廂 I 之後還有沒有它不認得的畫面）：使用者 2026-10-07 17:52 決定先發布、
  不做。目前只驗證到 Day 93–94（`docs/qa/2026-10-07_story_first_seeds.md`）。
- **修 bug 時看到、等使用者決定的事**：`docs/audit/2026-10-06/DECISIONS.md`（料理 prototype 6 條、這一批 3 條、故事與文字 16 條）。
  使用者回答之前，遊戲維持現在的樣子。
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
- rc8.7：新遊戲裡 Lounge、阿拓、鋼琴、予安、二樓來的時間，以及中間等錢的那段感覺對不對（正常玩家模擬：試酒之夜 Day 15–21、
  Lounge 開幕 Day 46–58、鋼琴 Day 69–76、予安 Day 83–88、二樓 Day 67–74；`docs/qa/2026-10-07_story_first_seeds.md`）。
- rc8.8：揭曉後房間裡 Dylan 的名牌、房間分頁的名字（iPhone 寬度、8 個分頁時寫「Jill & Dylan」）。
- rc8.5：營業中切到「休息室」偶爾看到有人；二級休息室和包廂能買；有插圖的故事店會停住；一晚跳出的話少很多、看得懂。

## 下次發布前

照 `docs/RELEASE_CHECKLIST.md`：這一批要求做完、合回 `main` → 完整回歸（在要發布的 commit 上）→ 手冊檢查與 GUIDE 戳記 → 繁體掃描 →
`build_single.py`、`build_artifact.py` → 發布到上面的新網址 → 讀回、`live_check.py` → 報告。一般發布不打 zip。
