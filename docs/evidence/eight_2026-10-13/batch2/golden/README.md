# 金樣本 `golden_frames` 重錄（第二批，2026-10-13）

照以前的規矩（`docs/evidence/` 裡 v2.5 兩次重錄的做法）：先證明差異只來自這次改動，再重錄，再證明重錄後它還抓得到改動。

1. **重錄前**（第二批的程式，`tests/golden` 還是 1c2db6e 的）：`golden_frames` 只報一個差異——
   `prep: pixels differ in box (16, 283, 374, 741)`。兩天逐格的抽樣、每天結束的摘要（金錢、客人、評分……）、其他 9 張畫面
   （標題、營業中 20 秒、廚房卡片、暫停、傍晚、結算、商店、日誌的貓和回憶）都和 1c2db6e 一樣。
   - `prep_old.png`（1c2db6e）／`prep_new.png`（這一批）／`prep_diff.png`（差異）：第 1 天開店前，天氣卡下面多了「備料」卡片
     （冰箱 0/40 份、照建議量還要補 15 份 $525、一鍵補到建議量 $525），下面的「今日任務」「今日推薦」等往下移；原本在最底下的冰箱條和按鈕
     在這張截圖的範圍外。這正是決策四要的改變。
2. **重錄**：`python3 tests/run_tests.py -k golden_frames --record`。`git status` 只有 `tests/golden/screens/prep.png` 改變；
   `tests/golden/frames.json` 和其他 9 張圖逐位元組沒變。
3. **重錄後的證明**（`proof.txt`）：同一個 build 跑 `golden_frames` 通過；把補貨卡片裡那行字往下挪 1 px 的版本、把結算頁帳目往下挪 1 px 的版本
   （`../mutants_make.py` 的 `golden_card_1px`、`golden_summary_1px`）都失敗——它還看得到開店前畫面和其他畫面的改變。
