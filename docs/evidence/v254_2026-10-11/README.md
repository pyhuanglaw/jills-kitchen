# v2.5.4 證據（2026-10-11）

使用者 2026-10-11 的三項決策（原文：`docs/v24/three_decisions_2026-10-11.txt`）。

- `restock/`：決策一（一鍵補貨先退下架庫存、照原進貨價退）。`mutants_make.py` 做出 10 個故意做壞的版本，`mutants.txt` 是三個測試
  （`stock_one_tap_restock_sends_back_the_dishes_off_the_menu_first`、`stock_returns_never_pay_back_more_than_was_paid`、
  `stock_one_tap_restock_leaves_no_dish_of_tonight_empty`）對它們的結果。第一次跑時 `refund_rounds_up`（退款無條件進位）沒有被抓到：
  測試裡「兩種價錢混在一起」的那一步剛好平均是整數（91＋130＋130＝351，三份平均 117），進位跟捨去一樣。把那一步改成一份活動價、
  一份原價（平均 110.5）以後重跑，它就失敗了（結果在 `story_visit/mutants.txt` 最後一段）。
- `story_visit/`：決策二（故事安排來的那一次不會等到生氣離開）。10 個故意做壞的版本，測試
  `story_a_beats_visitor_is_not_sent_away_by_the_ordinary_wait` 全部抓到。
