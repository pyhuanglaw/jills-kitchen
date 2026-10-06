# 以後怎麼測（QA）

三層，便宜到貴。目標不是少測，是**測試會累積**：能自動驗的問題，被發現一次就變成測試，下次不用再花 AI 重新玩一次才發現。

| 層 | 什麼時候 | 跑什麼 | 多久 |
|---|---|---|---|
| 1. 例行 QA | 每次改完遊戲 | `python3 tests/run_tests.py --qa`，加上這次改動相關的測試 `-k 名稱` | 約 10–15 分鐘 |
| 2. 發布前完整回歸 | 使用者說「發布」 | `python3 tests/run_tests.py`（全部，含例行 QA），照 `docs/RELEASE_CHECKLIST.md` | 約 50 分鐘（分三份同時跑約 17 分鐘） |
| 3. 全面 Audit | 隔一段時間、大改版之後、或使用者要 | `docs/audit/PLAYBOOK.md`（多組代理人實際玩、讀、挑） | 幾個小時 |

## 1. 例行 QA 會自動檢查什麼

全部用 `tests/player.py` 操作：真的點在畫面上的位置（手機觸控，電腦版用滑鼠）、故事面板開著、一句句點完。按鈕被蓋住、
跑出畫面、滑鼠捲不到，就算「點不到」。測試在 `tests/qa_tests.py`，名字都是 `qa_` 開頭。

**一直要對的（壞了就失敗）**
- 一整天用點的走得完：新遊戲 Day 1（教學、開幕的故事會停住店）；後期 Day 92 → 準備 DAY 93 → 一鍵補到建議量 → 開店 → 整晚 →
  結算 → 升級餐廳 → 準備 DAY 94。看得到的字裡沒有 `undefined`、`NaN`。
- 商店每個分頁的每顆按鈕（新遊戲第 7 天的小店、Day 92 的後期），用手指按一次，都要有反應（錢、存檔、畫面、提示或卡片會變）。
  二樓房間的按鈕死了幾個月就是因為沒有這個。開店前畫面（菜單、冰箱、售價、補貨）的每顆按鈕也一樣。
- 包廂「動工」用點的買得到。
- 使用者自己的營業中存檔（Day 2、30、46、81、83、89 兩份）按「繼續營業」，店裡的客人照原樣回來，還能繼續玩。
- 375／390／430 三種寬度：標題、開店前、營業中、商店每個分頁、日誌每個分頁、設定，沒有東西跑出畫面、沒有字被切掉。
- 商店和日誌的每個分頁，三種寬度都用手指滑得到、點得開。
- 故事等的是前面的故事和條件，不是日期（使用者 2026-10-06：「你不要固定某個故事是某一天」）。新加的故事如果寫了「第幾天以後」，
  這個測試會失敗，要先看過再決定。

**已知未修（`tests/qa_known_open.json`）**：Audit 找到、還沒修的問題，每一條都已經有測試在等。失敗時顯示 `OPEN`，不算整套失敗；
**修好的那一天它會顯示 `FIXED` 並讓整套失敗**，提醒把那一條從清單拿掉——從那以後它就是那個修正的回歸測試，同樣的問題不會再回來。
只有「問題本身那一條檢查」失敗才算 `OPEN`；測試連那個情況都沒準備到（`setup_check`，例如存檔裡找不到那顆按鈕）或測試自己
壞掉，一律是 `FAIL`——不然壞掉的測試會一直假裝成「還沒修」。
目前的清單：

| 測試 | 問題 |
|---|---|
| `qa_a_held_story_survives_leaving_the_app` | 故事停住店時離開 App，回來那段只剩看過的幾句 |
| `qa_leaving_while_closing_after_a_resume_keeps_the_day` | 繼續營業後在收店時離開，那一天不見 |
| `qa_a_checkpoint_survives_a_new_table_count` | 改過桌數以後，舊的營業中存檔接回變空店 |
| `qa_every_tab_reaches_by_mouse_in_a_small_window` | 電腦版小視窗，滑鼠到不了「員工」「招牌菜」 |
| `qa_the_selected_tab_is_on_screen` | 商店選中的分頁在畫面外 |
| `qa_the_pause_button_works_outside_the_service` | 開店前、商店的「II」按不到 |
| `qa_a_drink_on_a_ticket_reads_right` | 點單上點酒跳「undefined都在忙！」 |
| `qa_waiting_staff_do_not_stand_on_one_spot` | 閒著的員工疊在同一點 |
| `qa_the_inspection_money_is_in_the_summary` | 衛生檢查的錢不在結算 |
| `qa_table_hearts_only_for_sophie_and_mia` | 桌上的愛心還給所有回頭客 |
| `qa_the_album_counts_all_five_cats` | 相簿寫「1 隻貓都在」 |
| `qa_photos_of_jills_room_are_taken_in_her_room` | Jill 房間的照片拍成主廳 |
| `qa_a_favourite_is_missed_only_when_it_is_off_the_menu` | 熟客說「今天沒有」其實有 |
| `qa_a_new_game_gets_no_old_version_notes` | 新遊戲看到舊存檔的版本公告 |
| `qa_every_level_named_in_the_text_exists` | 「擴建到 Jill's Kitchen」沒有這一級 |
| `qa_restock_says_why_it_cannot` | 「補滿」塞滿冰箱後，「一鍵補到建議量」按了沒反應也不說為什麼 |
| `qa_a_review_talks_about_the_food_not_the_glass` | 評論把配餐的酒當成菜寫（「氣泡酒的火候剛剛好」） |

**修 bug 的規矩**：修正時附上能防止它再發生的測試。如果它已經在已知未修清單裡，修好、讓測試通過、把那一條拿掉；
如果是新發現的、能自動驗的問題，先寫測試（會失敗），再修。

## 2. 例行 QA 不會（也不該）自動判斷的

這些每次都要人或 AI 看，不要為了自動化寫沒有意義的檢查：
- 台詞像不像人講的、會不會太多太重複（`tools/qa/evening_census.py` 只負責數）。
- 故事好不好、每一幕有沒有起承轉合、前後矛盾。
- 後期會不會無聊、錢有沒有意義。
- 功能雖然存在，正常玩家感不感受得到（`tools/qa/life_visibility.py` 只負責量「在哪裡、多常」）。
- 店主手冊像不像寫給玩家看的。
- 真的 iPhone（字型、Safari、記憶體）：測試只有 Chromium，`T` 不等於 `O`。

## 3. 給下一個 session

- 改完遊戲：先跑 `--qa`，再跑這次改動相關的測試；回報時照 CLAUDE.md 分清楚「程式寫了／測試確認了／正常遊玩看得到／使用者 iPhone 確認了」。
- **不要重做已經自動化的探索**：按鈕有沒有反應、畫面寬度、繼續營業、一整天走不走得完——`--qa` 已經在看；已知未修的問題不要當新發現。
- 全面 Audit 照 `docs/audit/PLAYBOOK.md`；上一次的結果在 `docs/audit/2026-10-06/`。
- 測試的自動玩家 `__bot` 會跳過收店那段，收店時才發生的事要用 `Player.play_evening()` 看（見 PLAYBOOK「工具」）。
