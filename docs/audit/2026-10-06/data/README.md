# 這次 Audit 的資料表

- `tests_by_method.tsv`：247 個測試，每一個用什麼方法（UI 真的點／INT 呼叫內部／BOT 機器人／GOLD／INV 不變量／STAT 靜態）、壞掉時玩家會看到什麼（WS9）。
- `buttons_pressed.tsv`：中期與後期存檔裡每一顆實按過的按鈕和結果，880 列（WS2）。以後的按鈕實按測試是 `tests/qa_tests.py` 的 `qa_every_button_*`。
- `manual_entries.tsv`：店主手冊每一項的分類（WS5）。
- `story_gates.md`：故事是照條件接下去，還是綁天數（主 session 讀程式）。
- `new_game_timeline_*.txt`：新遊戲從第一天開始，每一天發生的故事（`tools/qa/new_game_timeline.py`）。一個種子是一種可能的玩法，不是標準答案。
