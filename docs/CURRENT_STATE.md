# Jill's Kitchen — 目前狀態（暫時的，會一直更新）

這份只放「現在」的狀態：branch、版本、待辦、待確認。永久的設計規則在 `docs/PROJECT_MEMORY.md`，不要寫到這裡；這裡的內容過時了就
直接改掉或刪掉。最後更新：2026-10-04，branch 整理之後（v2.4 rc8.3 已發布）。

## Repo 與 branch

- GitHub：`pyhuanglaw/jills-kitchen`，預設 branch 是 `main`。
- **`main` ＝ Jill's Kitchen 的正式主線**：目前的、穩定的、發布出去的版本都在這裡。最新正式版是 e797665（v2.4 rc8.3），之後
  `main` 上只有文件與紀錄。從 v2.2.1 起的完整開發歷史都在 `main` 上。
- 還沒做完的遊戲功能，另外開短期的 `feature/…` 或 `wip/…` branch；做完、測試通過才回到 `main`，發布的 commit 一定在 `main` 上。
  文件與紀錄可以直接在 `main`。不要讓工作 branch 跟 `main` 長期並行。
- 目前的工作 branch：`feature/ken-tasting-pictures`——品酒之夜的圖片與改名，進行中，見下面「進行中／等待玩家素材」。
- `wip/lin`：舊的開發 branch 名稱（Madame Lin 是遊戲裡的一條故事線，不是這個專案的主線）。2026-10-04 起不再使用；它指向的 b87b77b
  就是 `feature/ken-tasting-pictures`，沒有別的內容。玩家已同意刪除；這個工作環境不能刪 GitHub 上的 branch，要在 GitHub 網頁刪。
- `archive/rc7.6-import-main`（d0947ea）：2026-10-03 把 rc7.6 的 12 個 zip 匯入 GitHub 時建的那一個 commit，原本的 `main`。跟現在的
  `main` 沒有共同祖先，只是保存，不合併。
- `claude/jills-kitchen-github-setup-4x7483`（8ca784b）：接在那個匯入 commit 後面，把網址改到新的 artifact；同樣的改動已在主線上
  （ec985d1）。玩家已同意刪除，同樣要在 GitHub 網頁刪。
- 2026-10-04 的整理：`main` 從 d0947ea 強制改指到 b865d3c（舊的保存在 `archive/rc7.6-import-main`）。要復原：
  `git push --force-with-lease=refs/heads/main:<目前的 main> origin d0947ead2c18167ab3955fef51478a9168f5b8fd:refs/heads/main`。
- 本機的 `bundle` remote 是原開發 session 的備份 bundle，只是還原來源，不推送。
- 版本 tag（`v2.4-rc8` 到 `v2.4-rc8.3` 等）只在本機：推 tag 到 GitHub 時連線會被中斷。各版的 commit 寫在它的發布報告裡。
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

## 尚未發布的工作

### 已完成、尚未發布

- 沒有。`main` 上沒有未發布的遊戲程式。

### 進行中／等待玩家素材

- **品酒之夜（Ken 前三次）的圖片**（branch `feature/ken-tasting-pictures`：b87b77b 圖片、25d53f8 改名；**沒發布、沒跑完整回歸，
  還不能合回 `main`**）
  - 改名已做（25d53f8，玩家 2026-10-04「ken品酒夜 請改成品酒之夜」）：遊戲裡的「Ken 的品酒夜」「品酒夜」都改成「品酒之夜」，相關測試
    跟著改，相關的 11 個測試通過。跟圖片一起發布。
  - 規則（玩家 2026-10-04 決定，不要再問 A／B／C）：Ken 前三次自己安排的品酒夜，各自一張專屬 Story Photo，每張只在那一晚第一次
    出現，也放進相簿連著看；第三次之後的品酒夜不再出現圖。詳細在 `docs/PROJECT_MEMORY.md` §6，原文
    `docs/v24/ken_tasting_pictures_2026-10-04.txt`。
  - 第一張：沿用現有的那張（`ken_t1`）。
  - **缺第二、第三張：等玩家提供。** 規格與內容要求：`docs/v24/art/tasting_night_pictures_spec_2026-10-04.md`（已給玩家）。圖來之前
    不要自己生假圖，也不要拿同一張圖冒充三張。
  - 收到圖之後依序要做：
    1. 修正 b87b77b 的代用圖行為：現在第二、三次開場會顯示程式畫的「插圖待補」代用圖，改成沒有真的圖就不顯示。
    2. 修正 b87b77b 的第一張：它假設三張都是新圖、第一張會被換掉；改成第一張保留現有的 `ken_t1`，第一次品酒夜的相簿照片也用
       這張，只有第二、三張是新圖。
    3. 把第二、三張放進遊戲。
    4. 完整回歸（全部測試）通過。
    5. 合回 `main`，再照 `docs/RELEASE_CHECKLIST.md` 發布。

## 測試

- 242 個測試（`tests/run_tests.py` 95、`tests/v23_tests.py` 30、`tests/v24_tests.py` 117；`python3 tests/run_tests.py` 全跑，`-k a,b,c`
  跑指定的）。最近一次完整回歸：rc8.3 的 e797665 上 242/242（`docs/evidence/v24_rc8_3/regression/`）。
- 已知會在單一 seed 上偶爾落差的機率性測試，都在測試註解裡寫了量過的分布（例：`lounge_i_content_bar_food…`、
  `v24_rc6_new_things_are_talked_about`）。

## 待辦／待確認

- ~~營業中存檔、「繼續營業」在特別的晚上會變成空店~~：rc8.3 已修（`rc83_a_special_evening_comes_back_with_its_room`）。原本的說明：存檔時有人在
  `piano`（予安彈琴）、`toHost`／`host`（Ken 主持品酒夜）這些狀態，`restoreService` 的 `G_STATES` 不認得，整個還原失敗，
  退回「同一時間、店是空的」；主廚之夜的 `R.cn`、品酒夜的 `R.kt`、予安的 `R.ya` 也不會還原。存檔本身沒有壞，只是那一晚
  的客人不見。修法：還原時接受這些狀態，並重建 `R.ya`／`R.kt`／`R.cn`（玩家 Day 87 存檔可以重現：19:19 的 29 組客人變 0）。
- **太太的手機不用登入就能匯出／備份存檔**：還沒解決，需要玩家用手機實測。不要用「文字框複製」的方式（會讓 iPhone 當機）。
- `docs/evidence/v24_rc8/release/qing_tuo/` 的重拍截圖缺《講完》那一組（截圖腳本逾時）；原本的 q5 在 `docs/evidence/v24_rc8/qing_tuo/`。

## 玩家回報、下一批

- 玩家 2026-10-03 晚上 Day 83–89 的回報都在 rc8.3 做完了（`docs/V24_RC8_3_REPORT.md`）。
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

## 下次發布前

照 `docs/RELEASE_CHECKLIST.md`：這一批要求做完、合回 `main` → 完整回歸（在要發布的 commit 上）→ 手冊檢查與 GUIDE 戳記 → 繁體掃描 →
`build_single.py`、`build_artifact.py` → 發布到上面的新網址 → 讀回、`live_check.py` → 報告。一般發布不打 zip。
