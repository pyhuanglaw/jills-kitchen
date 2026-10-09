# 料理系統合併 main 的驗收紀錄（Release Gate，2026-10-09）

使用者 2026-10-09 的三份文件（原文）：`docs/v24/cooking_final_decisions_2026-10-09.txt`（16 項決策）、
`docs/v24/cooking_merge_authorization_2026-10-09.txt`（自主測試後合併 `main`）、`docs/v24/cooking_release_gate_2026-10-09.txt`
（這份驗收標準，優先適用）。這份紀錄逐條對照 Gate；每一項都寫「用什麼確認的」和證據在哪裡。

## 先講結論

- **合併的遊戲版本＝ commit `8298e18f8f55b0ea2d185f43e6704fdb717864be`**（branch `feature/cooking-gameplay`）。之後的 commit 只有兩個測試
  的修正和文件（`git diff 8298e18 <合併的 commit> -- js css index.html` 是空的）。合併後 `main` ＝【待填】。
- **P0：0 件。**
- **完整回歸**：實際合併的 commit d57bac8 上 **347 項全部通過**（之前在 8298e18 上 345 通過，2 個失敗都是測試的缺陷：改了、證明了）。
- **沒有真實 iPhone**：手機畫面都是桌面 Chromium 開成 iPhone 尺寸（390×844、375×667、430×932、橫向 844×390），不是實機驗收。
- **正式 Artifact 沒有動**（https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA 仍是 rc8.8）。合併 `main` 不等於發布。

## 一、測試環境與證據

- 所有測試對應 commit：最終回歸、長時間模擬、平衡數據都在**固定 commit 的 worktree** 跑（不在開發中的資料夾），避免跑到一半檔案被改。
- 環境：雲端容器（Linux、4 核心），Playwright＋Chromium，`tests/run_tests.py`（`-k` 選測試、`JK_GAME_JS` 換別的 game.js）。
- 證據都在 `docs/evidence/cooking_2026-10-09/`：
  - `regression/`：完整回歸的每一份輸出（中途 ad075ec 的、最後 8298e18 的）。
  - `balance/`：每晚數據（main、c1a12db、89bd685、最終）、Day 30 改善路徑、新遊戲正常玩家。
  - `long_play/`：30 天長時間模擬（每天一行：客人、錢、卡住、兩個 Jill、錯誤、狀態矛盾、途中存檔重開）。
  - `wash2/`：水槽兩個位置的修正（假設實驗、改善路徑、選位置的截圖、測試證明）。
  - `test_proofs/`：每一個改過的測試「為什麼改、改完還抓得到原本的問題」的證明（金樣本、Dylan 種子分布……）。
  - `k13/`、`onfire/`、`onejill/`、`dishes/`：各題自己的證據。
  - 手機畫面：`screens/`（四種尺寸的每一張和總覽）。

## 二、P0（零容忍）逐條

| # | 項目 | 結果 | 怎麼確認的 |
|---|---|---|---|
| 1 | 無法開啟、空白、主要操作失效 | 沒有 | 完整回歸（開店、點餐、做菜、收桌、商店、日誌、存檔）、52 個例行 QA（`qa_`，用真的點畫面）、私人測試版開啟檢查（`tools/qa/cooking_test_check.py`：沒有錯誤、讀 Day 30 存檔、開店）。 |
| 2 | 存檔遺失、損壞、無法載入、舊存檔被覆蓋 | 沒有 | 見「六、存檔」。使用者的每一個存檔都讀得進來、玩一天、故事保留；營業中途存檔再重開 45 次全部接回原本的客人。 |
| 3 | 同時兩個 Jill／跨房間狀態矛盾 | 沒有 | 見「四-B」。長時間模擬每一個畫面都數一次 Jill：0 次出現兩個。 |
| 4 | 員工、Jill、客人永久卡住 | 沒有 | 15 組 × 30 天長時間模擬 0 次卡住（要強制收店的晚上＝0）；`cooking_one_jill_through_whole_evenings_early_middle_late` 每一晚都收得了店。 |
| 5 | 訂單消失、重複出餐、重複收費、金錢異常增加 | 沒有 | 料理流程測試（每道菜剛好走過自己的站、Perfect）、`workflow_every_dish_goes_round_and_none_is_lost_or_made`（每一秒盤子都數得到、不會多也不會少）、長時間模擬每一天「錢的變化＝當天結算的淨利」（每一組、每一天核對，0 天不符；例：Day 92 存檔 30 天 $125 萬 → $363–370 萬）。 |
| 6 | 重要故事因排程永久無法觸發 | 沒有 | 見「五、故事」。這一輪找到並修了一個：試酒那晚的配菜的酒被擠到隔天（台詞「今晚」就錯了）。 |
| 7 | 升級、聘用、解鎖被破壞 | 沒有 | 商店與員工的回歸測試、Day 30 改善路徑（買洗碗機、大髒盤車、請人都有效）、`workflow_the_dishwasher_washes_and_the_big_cart_is_its_own`。 |
| 8 | 手機主要按鈕被擋 | 沒有 | `qa_every_tab_reaches_by_finger`、`cooking_the_pizza_oven_is_clear_of_the_buttons`、`cooking_the_teaching_card_is_quiet`、四種尺寸截圖（見「七」）。 |
| 9 | 新功能破壞舊玩法、無法恢復 | 沒有 | 完整回歸（含故事、貓、熟客、Lounge、二樓）＋長時間模擬。 |

## 三、P1 核心功能

### A. 料理與飲料

| 項目 | 測試 |
|---|---|
| 既有 35 道（33 道＋招牌主菜＋招牌甜點）每一站的流程 | `cooking_every_family_goes_its_own_way`（每道菜剛好走過自己流程的站、照順序、Jill 做是 Perfect）、`cooking_each_dish_with_its_own_beats_starts_raw_and_changes_by_hand`（每道菜生的樣子 → 手做的每一下 → 完成的樣子）、`cooking_plating_happens_where_the_food_is` |
| 招牌主菜、招牌甜點的組合與升級 | `a_second_signature_the_dessert_with_its_own_progression`、`qa_the_signature_editor_shows_the_menus_price`、`v24_the_signature_steppers_stay_on_their_own_line` |
| 生、烹調中、完成、裝盤的樣子 | 同上＋`docs/evidence/cooking_2026-10-09/dishes/`（每道菜的過程圖） |
| 飲料獨立做、獨立完成、獨立送 | `cooking_every_drink_is_its_own_cup`、`qa_a_drink_on_a_ticket_reads_right` |
| 咖啡吧同時 1、2、4 杯 | `cooking_the_bar_holds_one_cup_two_with_the_double_group_head_four_with_kitchen_ii` |
| 同一站多筆訂單、等待、取消、換工作 | `cooking_a_full_place_is_a_quiet_wait`、`cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back`、`cooking_jill_and_the_cooks_hand_work_on`、`cooking_any_dish_answers_the_five_questions` |
| 設備升級前後 | `kitchen_works_walk_in_and_a_second_coffee_machine`、`kitchen_staff_ladder`、Day 30 改善路徑（下面「四」） |

### B. Jill 與員工（任何時刻只有一個 Jill）

| 項目 | 測試 |
|---|---|
| 做菜時被派到外場、收完回廚房、加熱中換房間 | `cooking_one_jill_finishes_her_step_then_goes_and_nothing_of_hers_moves_on_while_she_is_away`（手上那一步做完才走、從廚房的門出去；她不在時鍋裡的照樣煮、交給她的裝盤等她；中途存檔讀回結果一樣；只畫在她所在的房間） |
| 整晚、前中後期 | `cooking_one_jill_through_whole_evenings_early_middle_late`（新遊戲第 1 天、Day 30、Day 92：每一刻每一個房間最多一個 Jill） |
| 員工與 Jill 同時去同一站 | `cooking_jill_and_the_cooks_hand_work_on`、`cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back` |
| 同一張髒桌被重複點 | `workflow_a_table_someone_is_going_to_clear_is_not_given_to_jill_too`（第一次點：說誰正在過去；再點一次：改由 Jill，原本的人放掉這件事） |
| 取消、重新指派、交接 | 同上＋`cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back` |
| 換房間時存讀進度 | `cooking_the_work_survives_a_checkpoint`、`workflow_the_dirty_dishes_survive_a_checkpoint`、`qa_the_players_checkpoints_resume` |
| 長時間 | 長時間模擬每個畫面數 Jill：15 組 × 30 天，0 次兩個 |

### C. 收桌、洗碗、服務流程

| 項目 | 測試 |
|---|---|
| 吃完 → 髒盤 → 收桌 → 送回 → 洗 → 乾淨的回到架上 → 再接客 | `workflow_dirty_dishes_go_back_by_hand_to_the_tub`、`workflow_every_dish_goes_round_and_none_is_lost_or_made` |
| 沒有清潔員／1 位／多位；有沒有洗碗機；車子 10、20 | `workflow_every_dish_goes_round_and_none_is_lost_or_made`（只有 Jill、一位清潔員、兩位清潔員＋洗碗機＋大髒盤車、一位清潔員＋兩位服務生：每一秒數盤子，不多不少、車子不超載）、`workflow_the_dishwasher_washes_and_the_big_cart_is_its_own`、`workflow_a_second_cleaner_washes_beside_the_first` |
| 滿載、多人收桌、送餐順路收盤 | `workflow_a_full_tub_holds_the_table_and_never_the_plating`、`workflow_waiters_keep_serving_and_one_at_most_washes`、`workflow_a_seasoned_waiter_serves_two_tables_in_one_trip` |
| 清潔速度與升級的效果 | Day 30 改善路徑（下面「四」） |

## 四、平衡

**做法**：同一個測試玩家（員工會做的讓員工做、其餘自己點）、同樣的種子，一晚一行（`tools/sims/evening_metrics.py`）：新遊戲第 1–3 天、
使用者的 Day 30／52／92 存檔，各 3 個種子；比較 main（料理系統之前 fc0f5d8）、c1a12db（一個 Jill 之後、第 13 題之前）和最終版本。
另外「改善路徑」（`tools/sims/improvement_path.py`）和新遊戲的正常玩家（`tools/qa/new_game_timeline.py`）。

### 每晚（3 個種子的平均；括號是 main）

| | 客人 | 沒等到就走 | 營業額 | 平均等待（入座到最後一道上桌） | 完成率 |
|---|---|---|---|---|---|
| 新遊戲 第 1 天 | 7.7（16.7） | 1.3（0） | $920（$2,000） | 42 秒（15 秒） | 84%（100%） |
| 新遊戲 第 2 天 | 8.0（17.7） | 2.7（0） | $1,270（$2,770） | 55 秒（15 秒） | 76%（100%） |
| 新遊戲 第 3 天 | 8.7（18.3） | 3.7（0） | $1,313（$3,197） | 52 秒（15 秒） | 70%（100%） |
| Day 30 存檔 | 57.3（84.7） | 34.7（13.7） | $33,697（$50,078） | 33 秒（29 秒） | 62%（86%） |
| Day 52 存檔 | 85.3（92.3） | 40.7（36.7） | $62,070（$70,760） | 39 秒（38 秒） | 68%（72%） |
| Day 92 存檔 | 107.7（120.3） | 24.0（15.7） | $101,788（$118,697） | 32 秒（26 秒） | 82%（89%） |

工作站利用率、Jill 與員工忙碌比例、髒桌／髒盤車／廚房等待造成的損失，每一晚的數字在 `balance/evening_final_8298e18.jsonl`（對照
`evening_main_fc0f5d8.jsonl`）。

### 超過 20% 的變化：原因和改善路徑

1. **新遊戲前三天：客人和營業額大約是 main 的一半。** 原因（都是使用者的決定）：前三天的教學節奏（第 1 天只有炒飯、預計約 10 位客人，
   使用者 2026-10-08 onboarding 規格）、Jill 要真的走到工作站做和裝盤（第 2 題：「前期經營難度提高是可以接受的」，「不縮短所有動作時間」）、
   一個 Jill（第 8 題）、髒盤子要拿回廚房洗（Workflow B）、繞過流理台走（第 13 題，見下面 4）。改善路徑：請人。第 4 天、Bistro 的六張桌子：
   只有 Jill 10 位 → 加一位廚師 11–18 → 再加服務生、清潔員 15–17 位（`balance/improvement_path_ad075ec.txt`）。
2. **Day 30 存檔：客人約少三分之一。** 原因：一位清潔員、沒有洗碗機，洗碗是瓶頸（使用者第 5 題：「第 30 天單一清潔員、沒有洗碗機時，
   一晚約 60 位客人的表現可以接受」「請勿直接提高基本清潔速度」）。現在約 57 位。改善路徑（3 個種子平均，`balance/day30_ways_out_final_8298e18.txt`）：

   | 這樣做 | 客人 | 沒等到就走 | 髒盤車滿、桌子等的桌·秒 |
   |---|---|---|---|
   | 照存檔 | 56.7 | 34.7 | 716 |
   | ＋一位 LV1 清潔員 | 60.7 | 29.0 | 674 |
   | ＋一位 LV3 清潔員 | 62.0 | 27.0 | 645 |
   | ＋商用洗碗機 | 62.0 | 28.3 | 646 |
   | ＋大髒盤車 | 60.3 | 27.0 | 15 |
   | ＋洗碗機＋大髒盤車 | 65.7 | 23.7 | 56 |
   | ＋洗碗機＋大髒盤車＋LV3 清潔員 | 72.0 | 20.7 | 6 |

3. **Day 92 存檔：營業額平均少 14%**（三個種子 −3%、−20%、−18%，其中一個剛好在警戒線上）。原因：髒盤子的流程（Workflow B，main 沒有）、
   一個 Jill、繞過流理台。這一輪修了一個「買什麼、請誰都解不開」的瓶頸（見「水槽兩個位置」）：修之前同一時間只有一個人能洗，Day 92
   的店兩位 LV5 清潔員、洗碗機、大髒盤車都有，還是每晚約 760–960 桌·秒桌子在等髒盤車；修之後約 500–670，客人 102 → 108。
   剩下的改善路徑：髒盤車滿時點它，派 Jill 到第二個位置一起洗（Jill 在 Day 92 大半晚有空）。
4. **第 13 題（繞過流理台）的代價**：出菜等待在前三天多 22–35%（同樣的種子，c1a12db → 最終），Day 30 客人約少一成，Day 52、92 幾乎沒差
   （`k13/`、`balance/evening_c1a12db.jsonl`）。原因是流理台幾乎從牆到牆、廚師站在後面，到後面要從兩端繞；兩端在畫面邊緣，較大的廚房
   （廚房擴建、廚房二期）繞的人會短暫走出 iPhone 的畫面。這是「真的繞過去」的路長；要更短得在流理台中間開一個走道（改廚房的樣子），
   沒有擅自做，列在最後「要使用者決定的事」。
5. **ON FIRE**：前三天比 main 少（一個 Jill 出的菜少）；中後期一晚約四分之三的時間在火上，main 也一樣（`onfire/`）。第 15C 題：沒有改。

### 其他門檻

- 沒有永久瓶頸：前期靠請人、Day 30 靠請人或買設備、Day 92 靠第二位清潔員或點髒盤車派 Jill，都量到改善。
- 沒有無限增加的漏洞：長時間模擬每一天錢的變化都等於當天淨利（逐日核對）；庫存不超過冰箱容量（每天檢查）；盤子守恆（測試每一秒數）。
- 沒有用單一種子下結論：每晚數據 3 個種子、長跑 3 個種子、改善路徑 3 個種子。

### 新遊戲的節奏（正常玩家模擬，要使用者看的地方）

正常玩家（照畫面上看得到的資訊決定、會買菜色、請人、擴建）從第 1 天玩：

- 30 天（89bd685，3 個種子，`balance/new_game_30_days_normal_player_89bd685.json`）：第 30 天時兩個種子還在第 1 級（4 張桌子、1 位員工、
  現金約 $8,000–$10,800），一個種子擴建到 Bistro（第 2 級、6 張桌子、2 位員工、$15,000）。每晚服務約 10–15 位、沒等到就走 15–30 位。
  main 上同樣的玩家：第 12 天擴建 Bistro、第 29 天擴建 Restaurant（`docs/qa/data/2026-10-07_story_first_seed300_decisions.txt`）。
- 100 天（最終版本，2 個種子，`balance/new_game_100_days_normal_player_final.json`；模擬工具遇到不認得的畫面就停，兩組停在第 98、87 天，
  頁面錯誤 0；main 同一個工具停在第 88–94 天）：

  | | 種子 300 | 種子 301 | main（同一個玩家，2026-10-07） |
  |---|---|---|---|
  | 擴建 Bistro | 第 41 天 | 第 24 天 | 第 12 天（種子 300） |
  | 擴建 Restaurant | 第 65 天 | 第 66 天 | 第 29 天（種子 300） |
  | 試酒之夜 | 第 38 天 | 第 10 天 | 第 15–21 天 |
  | 《看看》 | 第 49 天 | 第 22 天 | 第 30–34 天 |
  | 第一次有 $50,000 | 第 60 天 | 第 49 天 | 第 34–37 天 |
  | Lounge I 簽約／開幕 | 第 64／66 天 | 第 53／55 天 | 第 44–56／46–58 天 |
  | 二樓的故事、予安 | 第 98 天還沒開始 | 第 87 天還沒開始 | 第 53–60 天、第 74–81 天 |

  不靠錢的故事照樣來（試酒之夜甚至可能更早）；要錢的晚一些：Lounge 晚約 9–13 天；二樓和予安要先蓋側廳，到模擬結束都還沒存到。

這是第 2 題「前期經營難度提高是可以接受的」的實際樣子。使用者說過不要為了恢復營收縮短動作時間，所以沒有自己調經濟；要不要調（例如
擴建或 Lounge 的價格、第 1 級的員工名額），列在「要使用者決定的事」。

## 五、故事與生活世界

- 回歸裡故事與生活的測試（`v24_`、`v25_`、`rc7`、`rc8`、`story_`、`dylan_`、`lounge_`、`followup_` 開頭的 142 項）在合併的 commit 上全部通過，包括：秀琴阿姨每晚來、聘用與之後的故事（`v24_xiuqin_*`）、怡君《三個選項》《那面牆》、
  Sophie × Mia、Ken 與試酒、Lounge、二樓、員工休息室、相簿與故事照片（`v24_*`、`rc8*`、`story_*`）、
  `v24_day52_save_plays_the_stories_in_order_over_forty_days`（Day 52 存檔往後 40 天，每一段照順序發生）。
- 這一輪找到並修好的排程問題：試酒那晚（第 58 天），配菜的酒被同一晚剛好來的怡君《三個選項》擠到隔天，台詞「今晚」就錯了。改成試酒那晚
  替配菜的酒保留第二個 major 的位置；保留的比剩下的多時，只屬於這一天的那一幕先（PROJECT_MEMORY §2，仍然一天最多 2 個 major）。
- 長時間模擬每天記錄發生了幾段故事：新遊戲 30 天 41–47 段、Day 30 存檔 30 天 70–74 段、Day 92 存檔 30 天 18–23 段，沒有一個種子卡住不動。
- 已知、main 上就有的：少數種子裡揭曉那晚 Jill 說「老公」時離 Dylan 的桌子 67–151 點（不是走到他旁邊說）。

## 六、長期穩定性與存檔

- **長時間模擬**（`tools/sims/long_run.py`，第 3、12、24 天營業到一半存檔 → 關掉頁面 → 重開 → 繼續營業）：
  - 89bd685：新遊戲、Day 30、Day 92 各 3 個種子 × 30 天（`long_play/89bd685/`）：卡住 0、兩個 Jill 0、頁面錯誤 0、狀態矛盾 0；27 次途中
    存檔重開，每次客人組數都一樣接回來。
  - 最終版本 8298e18（水槽兩個位置會影響有清潔員的店，所以 Day 30、Day 92 再跑一次，各 3 個種子 × 30 天，`long_play/8298e18/`）：
    卡住 0、兩個 Jill 0、頁面錯誤 0、狀態矛盾 0；18 次途中存檔重開全部接回；每天錢的變化都等於當天淨利。（其中一組第一次跑時，為了讓
    回歸先跑，我把它暫停了 25 分鐘，恢復後瀏覽器連線已經斷了、第 1 天都還沒開始——是測試環境的問題，不是遊戲；從頭重跑一次，乾淨。）
  - 合計 15 組 × 30 天、45 次營業中途存檔重開。
- **存檔**：`old_saves_load`、`mature_save_loads_into_2_0`、`the_players_saves_load_through_a_real_reload`、
  `every_player_save_migrates_plays_a_day_and_keeps_its_story`（使用者的每一個存檔：讀進來、玩一天、故事保留）、
  `v24_saves_load_and_nothing_fires_on_load`、`unreadable_save_is_kept`、`save_backup_and_restore`、
  `cooking_a_save_past_day_three_before_the_onboarding_change_gets_its_cold_station_on_day_four`、`cooking_the_users_day3_latte_goes_out_by_a_tap`。
  舊存檔有洗碗機的，讀進來送一台大髒盤車（車子照舊 20 個，`cartMig`），只說一次。
- **特殊活動中存檔**：`rc83_a_special_evening_comes_back_with_its_room`（試酒夜、主廚之夜、予安彈琴）、`cooking_a_drink_batch_from_an_older_checkpoint_becomes_its_cups`、
  `workflow_a_second_cleaner_washes_beside_the_first`（兩個人在洗時存檔、讀回，兩個人都接著洗，每個盤子只洗一次）。

## 七、手機畫面

- `tools/qa/gate_screens.py`：390×844（23 張：標題、開店前、第 1 天主廳與廚房的教學卡、Jill 的房間、Day 92 每一個房間、暫停、結算、
  商店每一頁）、375×667、430×932、橫向 844×390（各 5 張）。總覽和幾張重點在 `screens/`（在 89bd685 拍的；水槽兩個位置只多了第二位洗碗的人，
  另外拍在 `wash2/`）。
- 看到的：教學卡沒有蓋住要點的位置（亮起來的爐子在卡片上面）；披薩烤爐不被按鈕擋；Day 92 廚房 7 位廚師、清潔員、服務生同時在，
  沒有重複的人。水槽兩個位置在兩種廚房版面都看得到（`wash2/two_at_the_sink_day92_zoom.png`）。
- 橫向：遊戲的 manifest 是直向（`"orientation": "portrait"`），橫向只是畫面變窄、可以操作，但教學卡和底下的提示會擠在一起。
- 第 13 題：較大的廚房裡，繞過流理台兩端的人會短暫走出 iPhone 的畫面（見「四-4」）。
- 除了截圖，例行 QA 用真的點擊走過開店、營業、收店、商店、存檔、故事面板（`qa_` 52 項）。
- **沒有真實 iPhone。**

## 八、回歸

- 8298e18（遊戲的最終版本）：347 項，**345 通過、2 失敗**（`regression/8298e18_part0..2.txt`）。兩個都是測試本身的缺陷，水槽兩個位置讓
  那一晚的走向變了才露出來：`v24_rc6_story_pages_keep_only_their_own_lines`（拿來演 Sophie 和 Mia 的客人剛好在結帳、兩秒內就走了）、
  `v24_rc6_the_staff_room_plays_a_frame_and_dozes`（撞球那一局開始得晚，打烊結束時測試還在讀店裡的東西）。遊戲做的都對；改了測試，
  在同一個遊戲上重跑通過，故意做壞的版本會失敗（`test_proofs/story_pages.txt`、`staff_room.txt`，ARCHITECTURE「改過的測試」38）。
- 實際合併的 commit d57bac8（遊戲＝ 8298e18，只多這兩個測試的修正和文件）上再跑一次完整回歸：**347 項全部通過**，0 個已知未修
  （`regression/d57bac8_part0..2.txt`，固定在 d57bac8 的 worktree 分三份跑，2026-10-09 05:43–06:31）。
- 中途（ad075ec，345 項）：338 通過，7 個失敗都查清楚——3 個金樣本（重錄，有證明）、4 個在 89bd685 修好（3 個測試假設跟新規則不合、
  1 個遊戲的排程問題）。
- 這一輪改過的測試、原因、證明：`docs/cooking/ARCHITECTURE.md`「改過的測試」第 35、36、37 條；證據 `test_proofs/`、`wash2/test_proofs.txt`。
  每一個都證明了改完還抓得到原本要防的問題（故意做壞的版本會失敗）。沒有刪測試、沒有跳過、沒有為了通過換種子（Dylan 那一個換種子前
  量了 16 個種子在三個版本上的分布）。

## 九、合併

- 合併前：`main` ＝ fc0f5d8b09fc8152991c408a26de96bef49235aa；`feature/cooking-gameplay` ＝【待填】。`main` 是 feature 的祖先，用快轉
  （fast-forward）合併，不強推、不改寫歷史。
- 可以回復的備份：`archive/main-before-cooking-2026-10-09`（＝ fc0f5d8，合併前的 `main`）、`archive/feature-dylan-room`（＝ 09f3312，
  `feature/dylan-room` 獨有的證據檔）。兩條都推到 GitHub、讀回確認過。
- 合併後在 `main` 上：【待填：啟動、讀存檔、核心流程的 smoke test】。

## 十、還沒解決、要使用者決定的事

1. **新遊戲前期的節奏**：正常玩家擴建 Bistro 在第 24–41 天（main 第 12 天）；第 1 級只有 1 個員工名額，要擴建後才能再請人，這是前期慢的
   關鍵。Lounge 晚約 9–13 天開幕；二樓的故事和予安到第 87–98 天都還沒開始（main 約第 55 天、第 75 天）。要不要調經濟（例如第 1 級的
   員工名額、擴建或側廳的價格），還是維持第 2 題。
2. **流理台中間要不要開一個走道**：第 13 題的繞路讓前期出菜等待多 22–35%，較大的廚房裡繞路的人會短暫走出畫面。開走道要改廚房的樣子。
3. **ON FIRE 中後期約四分之三的晚上在火上**（main 就是這樣，第 15C 題照指示沒改）。
4. 揭曉那晚的距離（main 就有）、專職洗碗的人（2026-10-08 的提案，還沒決定）。
5. GitHub branch：這個環境不能刪 branch，可刪清單在 `docs/CURRENT_STATE.md`。
