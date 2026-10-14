# v2.6 Release Gate 的證據（2026-10-14）

固定的 commit：先 `80ce485`（手冊稽核、單檔重建後的候選版），完整回歸找到兩個**測試本身**的缺陷，修好後是 `12043ff`（只改測試和證據，
遊戲內容跟 80ce485 一樣：`git diff 80ce485 12043ff -- js css index.html` 是空的）。發布的就是 12043ff。

**四層**：程式寫了／測試確認了／正常遊玩看得到／使用者在 iPhone 上確認了。下面全部是這台機器上的桌面 Chromium（手機尺寸、觸控），**不是實機**。

## 完整回歸（`regression/`）

- `80ce485`：378/380（三份同時跑）。兩個失敗都是測試的缺陷，各自保留原始失敗、說明原因、證明修正後還抓得到原本要防的問題：
  - `v24_rc77_kens_share_of_a_tasting_night`：Python 的 `round()` 對 .5 取偶數，遊戲的 `Math.round` 進位（`ken_round/`）。
  - `qa_the_summary_says_when_the_fridge_was_short`：第二批寫的時候 400 份是最大，第三批加了 550（`summary_fridge/`）。
- `12043ff`：**380/380**。沒有刪測試、沒有跳過、沒有換種子、沒有降低門檻。

## 正常玩家節奏的模擬（`sims/`，12043ff 的遊戲內容，種子 300）

| | 天數 | 頁面錯誤 | 錢 | 評分 | 每晚淨利（最低／平均／最高） |
|---|---|---|---|---|---|
| 全新遊戲 | 1 → 30 | 0 | $2,496 → $25,924 | 3.0 → 3.9 | $496／$4,134／$9,344 |
| 第 61 天存檔 | 62 → 75 | 0 | $163,696 → $314,830 | 4.2 → 4.8 | $32,072／$59,508／$73,241 |
| 第 92 天存檔 | 93 → 102 | 0 | $1,242,530 → $1,597,012 | 4.7 → 4.8 | $60,346／$69,592／$80,923 |

- **故事順序**：全新遊戲裡怡君第 8 天認識、第 14 天搬進來、第 16 天給鑰匙；Madame Lin 第 1 天打招呼；Ken 問酒、Lounge 的念頭都在第 14 天；第 22 天擴建。
  回歸裡的故事順序測試（`v24_day52_save_plays_the_stories_in_order_over_forty_days`、`qa_stories_wait_for_stories_not_for_dates`…）、
  Dylan 揭曉（`dylan_hidden_reveal`、`dylan_reveal_says_it_beside_him`、`qa_after_the_reveal_dylan_is_not_a_stranger`）都通過。
- **故事人物來店**（`*.summary.txt` 的 presence flags：說話的人那時不在店裡座位上）：每一條都是故事的對話畫面（開店前、打烊後的劇情，本來就不需要人坐在店裡）、
  衛生檢查員（他不入座），或客人起身走出去時說的那一句（第 62 天陳伯伯「Jill，謝謝。」、第 65 天 Sophie「嗯。」）。沒有「人不在卻在座位上說話」。
- **第一批的三件事**：三段模擬裡「王家三口」0 次；Dylan 因為賣完生氣離開 0 次、什麼都沒得點而先走 0 次。
- 第 92 天那段的模擬玩家第一個早上就買了冷藏室擴建（一般玩家的買東西規則：錢夠、有用就買）。

## 其他

- 語法檢查 52 個（跟 v2.5.5 一樣）；繁體掃描沒有新的簡體字；單檔版 `jills-kitchen-single-file.html` 跟原始檔一致。
- 手冊：照八項決策看過「一天怎麼玩」「開店前 › 備料」「庫存不夠」「飲料」「員工」「熟客」「擴建」，沒有要改的字（手冊沒有寫到畫面上的位置，
  第三塊砧板寫在工程自己的卡片上、蓋好的那個早上說一次）；稽核戳記改成 v2.6（80ce485）。
- 手機尺寸：回歸裡的 `qa_the_screens_fit_375_390_430`、`qa_the_prep_screens_44_reach_by_real_taps`、`qa_the_staff_x_takes_a_finger`、
  `qa_a_new_game_first_day_by_taps`、`sim_player_plays_three_days_by_taps` 都是用觸控點擊玩的，全部通過。
- 多個工作站同時做、走路：回歸裡 18 個廚房動線／工作站測試，加上第三批的 `kitchen_two_has_a_third_board_at_the_pass`、
  `without_kitchen_two_the_cold_counter_keeps_two`，全部通過。
- 舊存檔：`every_player_save_migrates_plays_a_day_and_keeps_its_story`（使用者每一份存檔都讀進來玩一天）、`old_saves_load`、
  `qa_the_players_checkpoints_resume`（營業中途存的「繼續營業」）全部通過。
