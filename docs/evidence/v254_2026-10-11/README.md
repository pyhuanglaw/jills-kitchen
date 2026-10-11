# v2.5.4 證據（2026-10-11）

使用者 2026-10-11 的三項決策（原文：`docs/v24/three_decisions_2026-10-11.txt`）。

- `restock/`：決策一（一鍵補貨先退下架庫存、照原進貨價退）。`mutants_make.py` 做出 10 個故意做壞的版本，`mutants.txt` 是三個測試
  （`stock_one_tap_restock_sends_back_the_dishes_off_the_menu_first`、`stock_returns_never_pay_back_more_than_was_paid`、
  `stock_one_tap_restock_leaves_no_dish_of_tonight_empty`）對它們的結果。第一次跑時 `refund_rounds_up`（退款無條件進位）沒有被抓到：
  測試裡「兩種價錢混在一起」的那一步剛好平均是整數（91＋130＋130＝351，三份平均 117），進位跟捨去一樣。把那一步改成一份活動價、
  一份原價（平均 110.5）以後重跑，它就失敗了（結果在 `story_visit/mutants.txt` 最後一段）。
- `story_visit/`：決策二（故事安排來的那一次不會等到生氣離開）。10 個故意做壞的版本，測試
  `story_a_beats_visitor_is_not_sent_away_by_the_ordinary_wait` 全部抓到。
- `names/`：決策三（同一晚一般客人不重名）。7 個故意做壞的版本，測試 `guests_one_evening_does_not_repeat_a_name` 全部抓到。
  `no_fresh_name`（等於拿掉這次的修改）那一段就是改之前的樣子：使用者第 92 天存檔的一晚（75 組客人，其中 65 組是沒有自己名字的
  一般客人），有 16 個名字出現不只一次。v2.5.3 原本的遊戲直接跑這個測試會在開頭就停（測試要讀新加的備援名單），所以用這個版本代表。
  第一次寫好時測試就抓到一個沒想到的情況：「美食家」這一類自己的名字只有 Chloe、Emma 兩個，後期一晚的美食家多，連 8 個備援名字都
  用完，又開始重複 —— 所以改成大人可以借用上班族那一批沒用過的名字（`no_borrowing` 就是沒有這一步的版本）。
- `golden/`：金樣本 `golden_scenario` 重錄。三天裡只有「評論」的雜湊變了（`scenario_before.json` 是重錄前）；評論的差別只有名字，
  星數、內容、標籤都一樣（`reviews_diff.txt`，第 3 天的雜湊變是因為評論清單會累積前兩天的）。拿掉決策三的版本跟舊金樣本完全一樣——
  原因是決策三換掉了同一晚重複的名字，錢、客人數都沒變。重錄後還抓得到改動（`after_record.txt`）：名字回到 v2.5.3、v2.5.3 本身、
  每道菜成本 +$1——都失敗。
