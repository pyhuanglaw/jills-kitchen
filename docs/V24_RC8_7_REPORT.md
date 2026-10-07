# JILL'S KITCHEN v2.4 rc8.7 — 發布報告（2026-10-07）

rc8.7 建立在 rc8.6（Version 8）之上，內容是使用者 2026-10-07 定下的「故事優先」架構（branch `feature/lounge-decided`）。使用者
2026-10-07 17:52：「handler 補好並確認能跨過 Day 93 後，就直接做發布前完整回歸；沒發現新的 release blocker 就合併 main 並發布。」
當天定規則的原話都收在 `docs/v24/story_first_canon_2026-10-07.txt`。

**怎麼報告**（`docs/RELEASE_CHECKLIST.md` §3）：分四層——程式寫了／測試確認了／正常遊玩看得到／使用者在 iPhone 上確認了。這份
報告裡沒有任何一項是使用者在 iPhone 上確認過的。

- Branch `main`，tag `v2.4-rc8.7` ＝ commit `24ecf98`（`feature/lounge-decided` 快轉合回 `main`）。
- 發布到正式網址：https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA ——**Version 9（version id `1791399641-9e7c`）**。

## 1. 這一批有什麼（玩家打開遊戲會看到的）

總原則（使用者 2026-10-07，永久）：**故事的門，用故事的鑰匙開；空間與豪華升級的門，用錢開。**

| 你會看到的 | 原因與改法 | 來源 |
|---|---|---|
| 《看看》那天 Jill 就決定接下隔壁。同一天「升級餐廳 › 店舖工程」就有 Lounge I「簽約・開工 $50,000」，錢不夠時卡片只寫「還差 $X」。不用升到 Fine Dining，不看評分，也不用等 Madame Lin 的最後一晚 | 舊規則是 Fine Dining＋$120,000，還要等她最後一晚（rc8.5） | 使用者 10/6、10/7 |
| Ken 的試酒之夜只看 Ken 自己的故事：配菜的酒兩次、聊過 Lounge 的想法兩次、他實際來過 4 次以上。日誌「晚餐之後」那一章也不再藏到 Fine Dining | 舊規則偷偷要 Fine Dining（`S.level>=4`） | 使用者 10/7 |
| Lounge II $80,000、Lounge III $150,000，都沒有等級條件 | 舊規則：II 要 Fine Dining＋$160,000，III 要 JILL＋$220,000 | 使用者 10/7（版本 A） |
| 阿拓在 Lounge I 的名單上，是 Bar Food 料理員，在廚房做事。晴 × 阿拓的故事不用再等 Lounge II；Lounge II 起多安安、許葳 | 舊規則：阿拓要等 Lounge II | 使用者 10/7 |
| 鋼琴在「店舖工程 › Lounge」那一段：$100,000，Lounge 開了就能買，沒有「遠程」標籤。予安的故事只等鋼琴 | 舊規則：$240,000，要 JILL 和 Lounge II，放在「夢想工程」 | 使用者 10/7 |
| 二樓的故事（《大家待的地方》、打電話給房東）不用等 JILL，也不用先存到 $120,000。二樓卡片寫「開工 $160,000」，下面另寫「租金 +$4,000／日，從開工那天起在結算裡扣」。員工休息室第一階段跟著開工就有 | 舊規則：整層 $510,000 | 使用者 10/7 |
| 店主手冊「Lounge 的人」照新名單寫。安安、許葳要等 Lounge II 蓋好才會出現在手冊裡 | 名單改了 | 使用者 10/7 |

員工休息室 II（$70,000）、III（$90,000）和私人包廂都沒有改。

**不在遊戲畫面裡、但在這一批的工具**（QA 用，不在發布的頁面裡）：

- 模擬玩家（`tools/qa/sim_player.py`）現在認得空間完工的展示畫面。它會等動畫播完，或像玩家一樣點一下跳過；看到完工卡片就選「回到開店準備」，再照常開店。
- 用存檔驗證過：Day 93 包廂 I 完工的那天整天自動走完，Day 94 也照常。測試 `sim_player_waits_out_a_space_shown_on_its_first_day` 也涵蓋這一段。
- 另外加了 `tools/qa/story_waits.py` 和模擬時間線的 `--probe`，用來把「故事等多久、錢等多久、玩家自己等多久」拆開。

**沒有在這一版的**

| 項目 | 狀態 | 為什麼 |
|---|---|---|
| `feature/dylan-room`（Dylan 在房間的名字） | 還沒合回 | 照使用者的指示這一輪不動 |
| `proto/cooking-flow`（料理流程試玩） | 停止 | 使用者 10/7：不合併、不發布 |
| 模擬玩家從 Day 92 存檔往後再跑 10–15 天 | 沒有跑 | 使用者 17:52：「不要再跑 seed、不要再做額外研究」，直接進發布 |
| 開店前的客人預估（WS2-09） | 沒有改 | 會動到每天的備料和花費（經濟） |
| `docs/audit/2026-10-06/DECISIONS.md` 的 28 條 | 等使用者決定 | 創作與設計的問題 |

## 2. 店主手冊（MANUAL AUDIT）

檢查了全部 12 張卡：一天怎麼玩、營業中、開店前、打烊以後、熟客、Lounge：留下來的地方、二樓、Jill 的房間、五隻店貓、日誌與故事、
社群與宣傳、存檔與備份。

- **改了**：「Lounge：留下來的地方 › Lounge 的人」改成「Evan 在 Lounge 蓋好那天就在吧台，沈晴、阿拓可以聘。Lounge II 起多安安、許葳。」
  這一句的出現條件（`GUIDE_WHEN`）也一起改，安安、許葳要等 Lounge II 蓋好才出現。合併時只改了句子、漏改條件，發布前核對手冊時
  發現（測試 `rc8_the_manual_shows_a_space_once_the_shop_has_it` 也會擋），a0ee007 修好。
- **確認不用改**：沒有任何一句寫 Lounge、試酒之夜、鋼琴、予安或二樓要什麼等級、評分或 Fine Dining。
  - 「擴建」那一條寫的是餐廳自己的擴建（Bistro → JILL 各要評分），跟這一批無關。
  - 「主廚之夜」仍然是 Lounge II＋招牌菜，遊戲沒改。
  - 「租金」那一條（新的空間各有自己的一份，結算一項一項列）涵蓋二樓的 $4,000／日；二樓卡片上也直接寫。
  - Lounge I 要什麼、鋼琴多少錢，商店卡片上就寫了。照 rc8.6 手冊的原則，畫面看得到的不重複寫。
- 戳記：`last: v2.4 rc8.7, 2026-10-07`。手冊的測試（`followup_the_manual_describes_the_current_game`、
  `v24_manual_tutorial_and_news_cover_the_new_content`、`rc8_the_manual_shows_a_space_once_the_shop_has_it`、
  `qa_the_stock_rule_is_said_the_way_it_works`）都過。

## 3. 文字

繁體掃描（`tools/hans_scan.py js/game.js index.html` 和這一版的新文件）：遊戲裡只有預期的合法字形（干貝、沉、宿舍），跟 rc8.6 一樣。新文件（這份報告、CURRENT_STATE、QA 文件、使用者原話）掃到的，只有這一行列出的那幾個字。

## 4. 測試與存檔

- **完整回歸**：在 **`24ecf98`（就是發布的這個 commit）上跑，305 個全部通過**；0 個失敗，0 個已知未修。
  - 其中 50 個是例行 QA，5 個是模擬玩家自己的測試。
  - 從固定在這個 commit 的獨立 worktree 分三份同時跑：102＋102＋101，共 38 分鐘。
  - 紀錄：`docs/evidence/v24_rc8_7/regression/full_regression_24ecf98_shard*.log`。
- **這一批中途的紀錄**（不算 release gate）：
  - 合併 commit `c614255` 的完整回歸開跑後我把它停掉了。發布前核對手冊時發現，合併漏改了一句話的出現條件，
    `rc8_the_manual_shows_a_space_once_the_shop_has_it` 一定會失敗。`a0ee007` 修好。
  - `a0ee007` 先跑合併影響到的 96 個測試：94 過、2 失敗，兩個都是測試還照舊規則寫：
    - Lounge I 的測試還在讀手冊裡已經拿掉的「怎麼來的」；
    - 章節的測試拿「晚餐之後要等 level 4」當例子，但使用者 10/7 拿掉了這個條件。
  - `24ecf98` 改了這兩個測試，遊戲沒改，兩個都過。紀錄：`targeted_a0ee007_shard*.log`。
- **發布前確認**：
  - `main` 是快轉合回（3182df6 → 24ecf98）。衝突是先在 `feature/lounge-decided` 上把 `main` 合進來解掉的（`c614255`），
    `main` 本身沒有被改寫。
  - 發布的頁面裡沒有 `prototype/`（料理試玩沒有合併）。
  - `single_file_in_sync` 通過：在發布的 commit 上重建單檔版，跟 commit 裡的一個字不差。
  - Tag `v2.4-rc8.7` 只在本機：推到 GitHub 時連線一樣被中斷。
- **發布後檢查**（`tools/sims/live_check.py`，紀錄在 `docs/evidence/v24_rc8_7/live/`）：
  - 從 tag 建的頁面（6,853,412 bytes）一個字不差地在線上頁面裡（6,853,964 bytes），主機只加了 552 bytes 的外框。
  - 用玩家 Day 92 存檔（打烊後存的）走完一輪：升級餐廳 → Day 93 開店前 → 玩完 Day 93（主廳、側廳、門口、Lounge、廚房、
    Jill 的房間）→ 結算 → 員工頁 → Day 94 開店前 → 重新整理後標題還是 DAY 94。
  - 頁面錯誤 0。
- **存檔相容**：舊存檔讀檔的測試都過：
  - `every_player_save_migrates_plays_a_day_and_keeps_its_story`、`the_players_saves_load_through_a_real_reload`、
    `mature_save_loads_into_2_0`。
  - Lounge I 的六種舊存檔都能簽約，付過 $120,000 的不會再收一次：「再想想」、沒回答的卡片、《看看》到那晚之間、
    已經接了、還在等她最後一晚、已經付了 $120,000。
  - `tests/saves/` 的玩家存檔沒有改。
- **截圖**（390×844，`docs/evidence/v24_rc8_7/screens/`）：
  - `01_lounge1_after_the_viewing_390.png`：玩家的 Day 52 存檔走到《看看》，當天晚上的「店舖工程 › Lounge」顯示
    「簽約・開工 $50,000」，卡片寫沈晴、阿拓可以請。
  - `02_piano_in_the_lounge_section_390.png`：玩家的 Day 81 存檔（Lounge III），把鋼琴拿掉、看還沒買的樣子：鋼琴在
    Lounge 那一段，「開工 $100,000」，沒有「遠程」。
  - `03_the_floor_160000_and_rent_390.png`：玩家的 Day 81 存檔，打過電話給房東之後：「開工 $160,000」，下面寫
    「租金 +$4,000／日」。

## 5. 四層

- **程式寫了**：上面全部。
- **測試／模擬確認了**：上面全部，每一條都有測試（例：`v24_story_first_the_doors_of_the_stories_open_with_story_keys`、
  `v24_the_tasting_night_comes_from_kens_story_alone`、`v24_lounge_one_after_the_viewing_and_50000_no_wait_for_her_last_night`、
  `v24_rc6_the_staff_room_comes_from_a_need_and_grows_in_place`）。手機 390×844 的截圖在 `docs/evidence/v24_rc8_7/screens/`。
- **正常遊玩看得到**：
  - 新開的遊戲才會走到這些改變。正常玩家模擬（seed 300／301／302）的日子：
    - 試酒之夜 Day 15–21；《看看》 Day 30–34。
    - Lounge 開幕 Day 46–58，阿拓同一天進來；Lounge II Day 56–60；Lounge III Day 63–68。
    - 鋼琴 Day 69–76；予安加入 Day 83–88。
    - 二樓的故事 Day 53–60 開始；打給房東 Day 66–73；二樓＋休息室 Day 67–74。
    - 來源：`docs/qa/2026-10-07_story_first_seeds.md`。
  - 你的 Day 92 存檔：已經是 JILL，Lounge III、鋼琴、二樓（Day 85 租下）都有了，所以讀進來幾乎看不到差別，只有手冊
    「Lounge 的人」那一句改了。
- **使用者在 iPhone 上確認**：還沒有。
