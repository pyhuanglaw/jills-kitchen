# 最終回歸的第二個失敗：工作卡在「把菜收回來」那一格寫「Jill 接著做」（2026-10-10）

## 原始案例（保留）

- 測試：`cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back`（`tests/cooking_tests.py`），種子 7140（沒有換）。
- 失敗的版本：8ded2e2，完整回歸 part 1（`regression_8ded2e2_failure.txt`）：`the card says Jill is on her way`。
- 重現：`repro.py`。玩家點爐台把阿德師傅正要去做的炒飯收回來；收回本身是對的（Jill 拿到、沒有重來、師傅放手）。但那一格 Jill 還在主廳
  0 號桌把手上那一步做完（`J.cur` 是那張桌子），卡片照規則寫「第一步：熱區 · Jill 接著做」；下一兩格她出發，卡片就寫「Jill 前往中」。
  卡片的規則（`wfState`／`jillOnIt`，2026-10-09 起）：Jill 正在走去做它才寫「前往中」，地板上還有事要先做就寫「接著做」。

## 為什麼以前會過

- 二分：main（8298e18）、d12a638、c50184d 在這個種子上，點下去那一刻 Jill 剛好已經閒下來（`J.cur` 是空的），卡片當下就寫「前往中」；
  1f7ff75（Jill 走過去摸貓）起，那一刻她還差一格——摸貓在 Jill 閒的時候多抽亂數，整天的時間線差了一點點。
- 20 個種子（7130–7149），三個版本（`frames_*.jsonl`，`sweep2.py`）：
  - 點下去那一刻 Jill 剛好閒著：main 7／20、c50184d 2／20、8ded2e2 2／20。其他時候卡片都先寫「Jill 接著做」。
  - 點下去以後卡片只寫過「Jill 接著做」或「Jill 前往中」，**從來沒有寫回廚師的名字或「等待處理」**；最久 15、14、16 格（約半秒）
    就變成「Jill 前往中」。60 次收回全部正確。
- 所以原本的檢查是靠運氣：它在「點下去那一格」讀卡片，要 Jill 剛好閒著才會過；7140 在舊版本上剛好是少數那幾個種子之一。

## 改了什麼

- 種子不換、其他檢查不動。那一行改成兩個檢查：點下去當下卡片就是 Jill 的（「Jill 接著做」或「Jill 前往中」，不能有廚師的名字）；
  一秒（30 格）內卡片寫「Jill 前往中」。
- 還抓得到（`proof.txt`，做壞的版本由 `mutants_make.py` 從 8ded2e2 的遊戲做出來）：
  - 卡片永遠不寫「前往中」（card_never_on_way）→ 失敗：`the card says Jill is on her way`。
  - 收回以後卡片不寫 Jill（card_no_jill，卡片變成「等待處理」）→ 失敗：`the card is Jill's at once`。
  - 改過的測試在 8ded2e2、main（8298e18）、c50184d 的遊戲上都通過。
