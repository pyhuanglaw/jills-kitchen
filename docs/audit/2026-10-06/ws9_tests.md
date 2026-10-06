# 回歸測試的盲點 — 代理人回報原文（2026-10-06 Audit）

> 這是那一組代理人交回來的原文，沒有改寫。裡面提到的截圖與腳本路徑是當時 session 的暫存資料夾，repo 裡沒有保留；
> 報告引用的截圖已複製到 `img/`（對照見 `README.md`）。文中的「Dylan 決定」「Dylan 會不會注意到」指的是使用者（2026-10-06 起統一寫「使用者」）。

## WS9 (regression suite): summary

**Where the findings are.** I could not write `findings.md`: the tool refused with "Subagents should return findings as text, not write report files". The full findings follow this summary, in the brief's format and in Traditional Chinese, ready to save as `/tmp/claude-0/-home-user/64ee893e-2a9e-517e-af2d-4f2493c4fa84/scratchpad/audit/ws9_tests/findings.md`.
- **Per-test appendix (247 rows):** `…/ws9_tests/work/notes.tsv`. Columns are name, primary method, secondary method, and what the test would catch (in Chinese). File and line for each test are in `work/tests.json`.
- **Evidence:** `…/ws9_tests/probe/` and `probe/resume/`. The scripts are in `…/ws9_tests/work/`.
- **What I changed:** nothing in ROOT, and I did not run the suite.

### Top findings
- **WS9-01 [BUG] High.** If the app is reloaded while a held story panel is open, the scene is marked as done and never plays again. Its story page keeps only the lines already shown.
  - Reproduced by taps on the Day 61 save: 晴 × 阿拓 《炸雞好了沒？》 at 18:48, one tap, background, reload, then 「繼續營業 · 18:48」.
  - After that there is no panel, and the story page has 2 lines; the control run has 5.
  - Internals were used only to make the scene due and to fast-forward the early service. The background was simulated with a visibilitychange event.
- **WS9-02 [TEST] High.** The harness sets `window.__noScenes=true`.
  - Only 17 of 247 tests turn story panels on, plus 1 that only turns on the hold. No multi-day test and no golden runs with panels.
  - With panels off the game still marks a picture as seen. So `v24_yijun_comes_to_eat…`'s check 「the player's picture was shown with it」 passes while nothing is on screen.
- **WS9-03 [TEST] High.** The game has 114 doAct button actions:
  - 57 are clicked for real somewhere; 1 only by a JavaScript click.
  - 23 only by a synthetic button, including 一鍵補到建議量 and most shop purchases.
  - 33 are never touched, including buyPD, buyUp, buyLounge and illus.
  - The rc6 check `includes('buyPD:1')` (5bb4806) accepted the broken button output as correct.
  - Private Dining I works today by a real tap (I checked), but no test guards it.
- **WS9-04 [TEST] High.** 22 of the 29 player saves hold a mid-service checkpoint, yet `load_save` and the all-saves test always tap 「不繼續，從開店前重來」.
  - Only the Day 87 save is ever resumed.
  - Two test descriptions promise restore checks the tests never make.
  - Nothing guards the hand-kept `G_STATES` list, which caused the rc8.3 bug.
  - I tapped 繼續營業 on 13 checkpoint saves: 8 resume fully. The other 5, all rc5–rc6 saves, fall back by design with an on-screen message; the console reason is "room changed".
- **WS9-05 [TEST] Medium.** The goldens were re-recorded in every release from rc6 to rc8.5 except rc7.6 and rc8.4 (20 commits between 10/01 and 10/04).
  - rc8.5 re-recorded all three (Day 1 went from 16 to 18 guests) without the earlier proof that turning the change off makes the old golden pass.
  - They only cover a new game's Days 1–3, with panels off.
- **WS9-06 [TEST] Medium.** Several tests check probabilistic behaviour on one seed; 4 tests had their seed changed 8 times in all.
  - jill_rests 7→16: the evidence is honest (15/20 vs 16/20 seeds), but the test fails on about 1 in 4 random-stream changes and invites picking a passing seed.
  - The forty-days test's own comment says 「every target on four of seven」.
- **WS9-07 [TEST] Medium.** The test environment differs from your phone in ways that each match a bug you found:
  - Chromium only (rc7.1 iPhone freeze).
  - No finger tap on the game canvas, ever (rc7.2 tap on a line).
  - Width 375 in 4 tests, 430 in 1.
  - Frozen time (rc7.2 log ×).
  - Fonts blocked (the signature stepper jump).
- **WS9-08 [TEST] Medium.** No test plays a whole day by taps, and 119 tests stock the fridge without the button. The rc8.1 tutorial-tip bug slipped through because 「the tutorial bot does it in seconds」.
- **WS9-09 [TEST] Low.** 4 checks always pass (plus 2 half-vacuous ones), 2 lines are dead `if False` code, and 3 test descriptions claim more than they check.
- **WS9-10 [DOC] Low.** The saves README says one test loads every save; four do, and one of them plays a day per save (155 s). Seven saves are missing from its table. The release checklist's "every fixture" conflicts with your 05:42 strategy (需要 Dylan 決定).
- **WS9-11 [TEST] Low.** 7 tests check the code's text (`String(fn).includes(...)`) rather than behaviour.
- **WS9-12 [DESIGN] —** How many held panels or pop-ups in an evening is "too many"? A pacing E2E test needs this number before it can fail.

### Method breakdown
| Method | Primary | Primary or secondary |
|---|---|---|
| INT (internal calls) | 121 | 193 |
| BOT (bot plays the service) | 61 | 106 |
| UI (real taps on screen) | 39 | 69 |
| INV (invariants) | 15 | 32 |
| STAT (static text/code) | 8 | 17 |
| GOLD (golden snapshot) | 3 | 4 |
| Total | 247 | |

- **By file (primary):**

| File | INT | BOT | UI | INV | STAT | GOLD |
|---|---|---|---|---|---|---|
| run_tests | 44 | 16 | 21 | 8 | 3 | 3 |
| v23_tests | 18 | 5 | 3 | 2 | 2 | 0 |
| v24_tests | 59 | 40 | 15 | 5 | 3 | 0 |

- 158 tests click at least one real button, mostly to move between screens.

### Past bugs
- Twelve of the rc6–rc8.5 bugs you reported are in the past-bugs table (the 13th row, the hearts, was a design question). None was a logic error, and the suite caught none of them.
- The release gates do catch logic bugs, for example b443ab5, 57e6f80, 96ad643 and e797665.

### Proposed E2E tests (7)
1. A new game, Days 1–3, played by finger.
2. The Day 92 evening by taps, panels on, every room tab.
3. Every shop button tapped once (3 saves, 4 widths).
4. Special evenings with reload, including a held panel, plus a static `G_STATES` check.
5. 繼續營業 on representative saves.
6. 14 days with panels on at your pace, at release only.
7. Widths 375/390/430, touch, real fonts.

### Low-value, redundant and flaky tests
- 5 single-seed tests.
- 4 all-saves loops that could be merged into one.
- The always-true lines and the 7 code-text checks.
- Deleting any test: 需要 Dylan 決定.

### Checked and fine
- `G_STATES` is complete today.
- The Staff Room II and Private Dining I buttons work by real tap.
- The rc8.5 stray-attribute sweep is a good guard.
- 13 checkpoint resumes showed no page errors.
- `autoStock()` buys exactly what 一鍵補到建議量 buys.
- Save migration coverage is strong.
- The jill_rests re-seed evidence is honest.

### Could not check
- A real iPhone or WebKit (only Chromium is installed here).
- Real fonts, and touch hold or swipe.
- The full 247-test run; I used the rc8.5 logs instead.
- How often Safari drops the tab (how often WS9-01 happens).
- Picture stories that use `scene()` on reload.
- The thresholds in WS9-12.

---

# 以下是 findings.md 的完整內容（可直接存成 …/ws9_tests/findings.md）

# WS9：回歸測試（247 個）的 Audit

- **對象：** `tests/run_tests.py`（95）、`tests/v23_tests.py`（30）、`tests/v24_tests.py`（122），main @ 0f57a9f（v2.4 rc8.5）。
- **我做了什麼：**
  - 沒有改任何檔案，也沒有跑整套測試。
  - 用了 rc8.5 自己的回歸紀錄（`docs/evidence/v24_rc8_5/regression/`）和唯讀的 git log／git show。
  - 用 audit_lib 做了探針（390 寬、觸控、故事面板開著）。
- **內部函式：** 只用來「觀察」或「更快到達某個狀態」，用到的地方都有寫明。
- **工作檔：** `work/`。分類表 `work/notes.tsv`（附錄 A），按鈕覆蓋 `work/acts_final.json`（附錄 B），探針腳本也在這裡。
- **證據：** `probe/`、`probe/resume/`。

## 先講結論

- **這套測試很會抓規則和邏輯：** 經濟、故事條件、存檔搬家、員工名單、預約規則都測得到。
  - rc7.2–rc8.5 的關卡真的抓到過邏輯 bug。
  - b443ab5：秀琴的閒聊上限讓《那面牆》永遠開始不了。這是四十天、多種子的模擬抓到的。
  - 57e6f80：客滿時，故事在等的熟客在門口被擋掉。
  - 96ad643：Ken 品酒夜的場景被打烊訊息蓋掉。
  - e797665：員工從 Lounge 的街門進出。
- **它幾乎看不到「玩家看到什麼、點什麼」：**
  - 故事面板預設關著。
  - 很多購買是直接呼叫函式。
  - 幾乎都是 390 寬、用滑鼠、時間凍結、只有 Chromium、字型被擋。
  - 玩家的中途存檔都選「從開店前重來」。
- **結果：** rc6–rc8.5 你玩出來的 bug 幾乎都落在這一塊：死按鈕、面板、繼續營業、手指點不到、提示蓋住畫面。
- **新的遊戲 bug：** 這次順著測試缺口找到一個，見 WS9-01。

## 方法統計

方法的代號：

- **UI：** 真的點／觸控畫面上的元素，而且點的結果就是被檢查的東西。
- **INT：** 呼叫內部函式，或直接改狀態。
- **BOT：** 用測試機器人跑營業。
- **GOLD：** 固定種子的標準答案。
- **INV：** 不變量。
- **STAT：** 靜態檢查文字、程式碼或文件。

| 主要方法 | run_tests | v23_tests | v24_tests | 合計 | 當主要或次要 |
|---|---|---|---|---|---|
| INT | 44 | 18 | 59 | **121** | 193 |
| BOT | 16 | 5 | 40 | **61** | 106 |
| UI | 21 | 3 | 15 | **39** | 69 |
| INV | 8 | 2 | 5 | **15** | 32 |
| STAT | 3 | 2 | 3 | **8** | 17 |
| GOLD | 3 | 0 | 0 | **3** | 4 |
| 合計 | 95 | 30 | 122 | **247** | |

其他數字：

- 至少真的點一顆按鈕：158 個，多半是為了換畫面。
- 打開故事面板：17 個（另 1 個只開「停住」）。
- 觸控：8 個開觸控，其中 6 個真的用手指點，全部點在 HTML 元素上，沒有一個點在餐廳畫布上。
- 寬度：375 有 4 個，430 有 1 個，電腦寬 1 個，其他都是 390。
- 時間：只有 1 個測試時間在走。
- 補貨：119 個不用按鈕補貨。
- 重新載入：37 個。
- 用玩家自己的 checkpoint 按「繼續營業」：只有 1 個。

---

## Findings

### WS9-01 [BUG] High 故事面板停住店的時候 App 被關掉或重新載入，那一段故事永遠只剩前幾句，不會再演
- **在哪裡：**
  - 營業中、任何作者寫的「店裡暫停中」故事面板。
  - 重現用 `player_day61_0933.json` → 準備 DAY 62，390×844 觸控，面板開著。
- **怎麼重現（玩家動作）：**
  1. 開檔 → OPEN FOR DINNER →「準備 DAY 62」→「一鍵補到建議量」→ 開店。
  2. 18:48 左右，晴 × 阿拓《炸雞好了沒？》跳出來，店停住（「店裡暫停中 · 晴 & 阿拓」）。
  3. 點一下，看到「沒有。」。
  4. 切到別的 App。遊戲會寫 checkpoint；接著 Safari 丟掉分頁，或你自己重新整理。
  5. 再打開，點「繼續營業 · 18:48」。
- **看到什麼：**
  - 店接回來了（「從 18:48 繼續今天的營業」），但面板沒有回來。
  - 那一段已經記成發生過（`evState('qt_1').n`=1），不會再演。
  - 日誌 → 故事 → 晴 & 阿拓 第 1 段只剩兩句：沈晴「炸雞好了沒？」、阿拓「沒有。」。
  - 摘要卻寫「晴問炸雞好了沒；阿拓說沒有；晴說看起來好了。」
- **應該是什麼：**
  - 對照組是同一存檔、同一時間點、不重新載入，五句都在：「炸雞好了沒？」「沒有。」「看起來好了。」「妳跟 Hugo 講一樣的話。」「那代表我們兩個都正常。」
  - 接回來時，那一段應該從頭（或從斷掉的那句）再演，至少故事頁要留下完整台詞。
- **證據：**
  - 截圖：
    - `probe/10_held_beat.png`
    - `probe/11_title_after_reload.png`
    - `probe/12_after_resume.png`
    - `probe/13_story_page_reload.png`（兩句）和 `probe/13_story_page_control.png`（五句）
  - 紀錄：`probe/probe_hold_reload_log.txt`、`probe/probe_hold_reload2_log.txt`。
  - 腳本：`work/probe_hold_reload.py`、`work/probe_hold_reload2.py`。
- **原因（程式）：**
  - 作者寫的故事一跳出來就記成發生過。
  - 台詞是一句一句出現時才寫進故事頁（`shRec`），而且「the first time is the one kept」（game.js:1859）。
  - 切到背景或關頁會寫 checkpoint（game.js:9682–9683），但 `snapshotService` 不存開著的面板。
- **確定程度：** 已用 UI 重現。
  - 為了快一點到那個時間點，有兩處用了內部手段：營業前段用測試機器人代打；用內部函式讓 `qt_1` 現在就該發生（跟套件的 `v24_rc6_an_authored_beat_holds_the_service_until_it_is_read` 一樣做法）。
  - 「切到背景」是送 `visibilitychange` 事件，模擬手機的行為。
  - 其他步驟都是真的點：重新載入、點「繼續營業」、點面板、開日誌。
  - 有插圖、作者寫的故事（例如 Ken 和杜的照片那兩段）很可能一樣會斷。照片本身在跳出來時就進相簿並存檔了（`storyPhoto`），不會丟。
- **Dylan 玩幾分鐘內會不會注意到：** 不太會。面板只是沒回來，看起來像那段結束了，要去故事頁才看得出只剩兩句。
  - 但碰到的機會不小：你的 29 份存檔裡有 22 份帶著營業中的 checkpoint。
  - rc8.5 起，有你插圖的故事都會停住店等你點。
- **備註：** 找不到文件說這是刻意的。沒有任何測試在面板開著時重新載入。

### WS9-02 [TEST] High 測試預設把故事面板關掉，247 個裡只有 17 個打開，玩家實際看到的節奏幾乎沒有被測
- **在哪裡：** `tests/run_tests.py:67`：`window.__noScenes=true;   // v2.2: portrait scenes (a full-screen tap-to-continue panel) stay off unless a test turns them on`
- **怎麼重現：** 讀那一行；在測試檔裡找 `__noScenes=false`、`__holds=true`。
- **看到什麼：**
  - 17 個打開面板（另 1 個只開停住）。多半是直接呼叫 `scene()` 或 `run()` 看一個面板，用 `dlgNext()` 函式翻頁，不是點。
  - 所有多天測試都是面板關著跑：Day 52 四十天、新遊戲十四天、每份存檔玩一天、十天穩定性。三個 golden 也是。
  - 面板關著時故事不會停住店，所以一晚的時間軸、客人耐心、被打斷幾次，都跟你玩的不一樣。
  - 面板關著時遊戲照樣把插圖記成看過：game.js:9740 的 `illusSeen` 在 `__noScenes` 判斷之前。所以 `v24_yijun_comes_to_eat_and_her_mother_walks_over` 的「the player's picture was shown with it」在畫面上什麼都沒出現時也會過。
- **應該是什麼：** 要有幾個面板開著、一路用點的讀完的整晚或多天測試（E2E-2、E2E-6）。
- **證據：**
  - rc8.5 報告：「不在清單裡的故事跳出插圖時（怡君第一次來、Lounge 第一晚），店照常跑。」那段的測試一直通過。
  - rc7.2：「秀琴阿姨出場要暫停遊戲吧 有劇情的」。
  - WS9-01。
- **確定程度：** 已從測試程式碼確認。
- **Dylan 玩幾分鐘內會不會注意到：** 不會注意到測試本身，但會碰到漏網的節奏問題（rc7.2、rc8.5 都是你先發現的）。
- **備註：** 面板關著讓長測試跑得快，這個選擇合理。問題是沒有另一層把面板打開來測。

### WS9-03 [TEST] High 114 個按鈕動作裡，只有 57 個有測試真的按過畫面上的那顆按鈕
- **在哪裡：** game.js 的 `doAct0`（114 個 case）對照三個測試檔；清單在附錄 B。
- **怎麼重現：** 對每個 `data-act`，找有沒有測試對畫面上那顆做 Playwright click 或 tap。
- **看到什麼：**
  - 真的點過：57 個。
  - 只用 JavaScript `.click()`：1 個（`cnPlan`）。
  - 只用「臨時做一顆假按鈕再 click」或直接 `doAct`：23 個。包括：
    - 每天最常按的「一鍵補到建議量」（`restock`）。
    - 家具、工程、設備的購買：`buyDecor` `buyEq` `buyExt` `buyWin` `buyOps` `buySeason` `buyLgFurn` `buyFrontTable` `buySideTable`。
    - `expand`、`crewUp`、`hireLounge`、`rd`／`rdSpecial`／`labTry`、`wineDev`／`wineT`／`wineCourse`、`contractSign`、`album`、`revealClose`。
  - 沒有任何測試碰過：33 個。包括：
    - 包廂「動工」`buyPD`、租二樓 `buyUp`、蓋 Lounge `buyLounge`。測試都直接呼叫 `buyUp()`、`buyLounge()`。
    - 看插圖 `illus`、宣傳 `campaign`、價格 `price`、速度 `speed`、`music`／`sfx`／`theme`。
    - 設定裡的「複製備份文字」「貼上備份文字恢復」。
    - 開店前「退掉不在菜單上的庫存」（`discardAsk`／`discardAll`）。
  - **rc6 的 bug 是怎麼被鎖住的：**
    - `v24_rc6_private_dining_story_needs_two_tables_and_a_lived_in_staff_room` 用自己的假格式化函式檢查 `secUpRooms(1e9,(c,a,k,l)=>a+':'+k).includes('buyPD:1')`（5bb4806，10/02）。
    - 真的按鈕當時寫出的就是那個光禿禿的「1」，所以這個檢查把 bug 當成正確答案。
    - rc8.5（922595f）改成 `includes('buyPD:data-k="1"')`，檢查的仍是程式傳的字串，不是畫面。
  - **rc8.5 的保險沒涵蓋包廂：**
    - `rc85_the_rooms_upstairs_are_bought_by_their_buttons` 掃過 Day 92 每個商店分頁的怪屬性，也真的按了休息室 II。
    - 但 Day 92 存檔還沒有包廂（要先有《關上門以後》），所以 `buyPD` 從沒被掃到、也沒被按過。
- **我檢查的：**
  - Day 92 存檔，用內部函式讓包廂出現（只為了到達狀態），再真的點「私人包廂 I 動工 $240,000」。
  - 錢 1,179,146 → 939,146，隔天完工，沒有錯誤（`probe/02_pdr_offered.png`、`probe/03_after_pdr_tap.png`、`probe/04_day93_prep.png`）。
  - 今天它是好的，只是沒人守著。
- **確定程度：** 覆蓋數字從程式碼和 git 確認；包廂按鈕已用 UI 驗證。
- **Dylan 玩幾分鐘內會不會注意到：** 會。就是你 10/04 說的「無法升級到二級休息室 訂購70000按不下去」。
- **備註：** 建議 E2E-3。

### WS9-04 [TEST] High「繼續營業」幾乎沒有測：玩家的 22 份中途存檔，測試都選「不繼續，從開店前重來」
- **在哪裡：** `tests/v24_tests.py:10` 的 `load_save()`，和 `every_player_save_migrates_plays_a_day_and_keeps_its_story`：只要有 `openFresh` 就按它。
- **怎麼重現：** 讀這兩段；看 `tests/saves/*.json` 的 `checkpoint`。
- **看到什麼：**
  - 29 份玩家存檔有 22 份帶營業中 checkpoint。
  - 用玩家 checkpoint 按「繼續營業」的只有 `rc83_a_special_evening_comes_back_with_its_room`（Day 87）。它是 rc8.3「Day 87：營業中存檔「繼續營業」變空店（29 組→0）」之後才加的。
  - `service_checkpoint_resumes_the_day` 和 `a4b_a_mid_service_checkpoint_is_consistent_and_the_day_finishes_after_it` 用的是測試自己做的 checkpoint，在普通的一天。
  - 兩個測試的說明寫了要檢查，實際沒有：
    - `the_lounge_is_the_same_restaurant_one_guest_one_visit_one_tab` 寫「and a mid-day checkpoint restores the Lounge seats with their guests.」，但算出 `cpd` 就沒再用。
    - `v24_the_night_cut_short_is_not_counted_and_comes_again` 寫「and a checkpoint reload in the evening plays it as if nothing happened.」，但整個測試沒有重新載入。
  - 沒有測試在面板開著時重新載入（WS9-01）。
  - `G_STATES`（game.js:8444）是手寫清單，rc8.3 就是少了 `piano`／`toHost`／`host`。
    - 今天是完整的：`waitSofa`、`sitDown` 等是 Dylan 的狀態，不是客人的。
    - 但以後漏加，沒有測試會叫。
- **我真的點了 13 份帶 checkpoint 的存檔：**
  - 完整接回：Day 2、30、46、81、83、86、89（21:43）、89（18:59）。
  - 退回：Day 65、67、71、73、74，都是 10/02 用 rc5–rc6 存的。畫面上是「今天的店內狀況無法完整還原，從 17:07 重新開店（今天的營收與客人數都保留，店裡的客人會重新入座）」，console 的原因是 `room changed`。
  - 這是設計好的退路，不算 bug，但沒有測試記下哪份該接回、哪份該退回。
  - 順帶看到（Low）：Day 74 在 21:48 退回後，一接回就跳出停住店的故事。面板底下時鐘顯示「17:00」，同時跳「RUSH HOUR 晚餐尖峰時段開始！」和「21:30 打烊，不再接新客人」（`probe/resume/resume_day74.png`）。只有舊版本存檔會遇到。
- **證據：** `probe/resume/resume_log.txt`、`probe/resume/resume_why_log.txt`；腳本 `work/probe_resume_eras.py`、`work/probe_resume_why.py`。
- **確定程度：** 接回結果已用 UI 確認；測試覆蓋從程式碼確認。
- **Dylan 玩幾分鐘內會不會注意到：** 會，rc8.3 就是你發現的。
- **備註：** 建議 E2E-4、E2E-5，再加一個靜態檢查：每個指派給客人群組的 `state` 都在 `G_STATES` 裡。

### WS9-05 [TEST] Medium 三個 golden 幾乎每一版都重錄，而且只看新遊戲前三天、面板關著
- **在哪裡：** `tests/golden/`（`golden_scenario`、`golden_frames`、`cat_personality_fingerprint`）。
- **怎麼重現：** `git log --format='%h %ad %s' --date=short -- tests/golden`。
- **看到什麼：**
  - 09/26 起有 37 個 commit 改過，10/01–10/04 就有 20 個（`frames.json` 18 個）。
  - rc6 到 rc8.5 之間，只有 rc7.6、rc8.4 沒重錄。
  - rc8.5（ae64e56）三個一起重錄，Day 1 客人 16→18 組。
    - commit 寫「all from the random stream the small-talk budget moved, none a behaviour broken」，證據是貓的狀態比例和 Jill 摸貓。
    - 沒有以前那種「把改動關掉，舊答案照樣通過」的證明。以前的例子：66eb6cf「checked by putting those back, which passes the old baseline」、4a1a9b2「the old baselines pass untouched」、e5c6936「with the named change reverted, the old golden matched exactly」。
- **判斷：**
  - golden 是「變了沒」的警報，不是「對不對」。亂數一動就整片重錄，那一版等於沒人守。
  - 它抓過真的東西：e5c6936「Found by the golden screens: the journal's 社群 page ... was there from day 1」。
  - 所以值得留，但重錄應附證明。
- **確定程度：** 已從 git 確認。
- **Dylan 玩幾分鐘內會不會注意到：** 不會。
- **備註：** 要不要把「重錄附證明」寫成規則：需要 Dylan 決定。

### WS9-06 [TEST] Medium 一個種子檢查機率性的事，亂數一動就換種子，等於挑會過的種子
- **在哪裡：** 下面四個測試，種子共換過 8 次。
- **怎麼重現：** 讀測試註解；`git log -S` 找種子的改動。
- **看到什麼：**
  - `jill_rests_when_staff_cover_the_floor`：
    - 種子 7→16（rc8.5）。檢查「一個人顧店的一天至少摸一次經過的貓」。
    - 證據：`jill_pats_*.txt`，rc8.4 的 20 個種子裡 15 天有摸，rc8.5 是 16 天。
  - `v24_day52_save_plays_the_stories_in_order_over_forty_days`：
    - 種子基數 7000→7400（3836908）→7600（22d92e0）→7000（b443ab5）。
    - 註解：「every target on four of seven (rc8.1 four). 7000 meets every target on rc8.1 and on the release.」
  - `lounge_i_content_bar_food_in_the_kitchen_wine_at_dinner_the_cast_by_name`：51→52→51→53。
  - `v24_rc6_new_things_are_talked_about`：改成三個晚上。這是對的方向。
  - 也只用一個種子量一晚的：`rc85_the_crew_go_up_to_the_staff_room_in_a_busy_evening`、`rc85_small_talk_is_rare_and_makes_sense`。
  - 每次發布都在付這個成本：
    - rc8.5 第一次 gate 242 過、5 失敗，報告說「都是『誰在什麼時候說話』改了以後亂數順序跟著動，沒有行為壞掉」。
    - rc8.3 gate 是 237 過、5 失敗。
    - rc8 gate「two tests that leaned on one seed's day」（8f7d6b2）。
- **判斷：**
  - jill_rests 7→16 的證據是誠實的，我同意行為沒變。
  - 但這個測試每次亂數一動就有大約四分之一機會失敗，然後再換種子。
  - 比較好的做法：多種子門檻（例如 20 個種子 ≥12 天），或直接測機制（她閒著、貓在身邊 → 摸）。
  - 四十天那個：真正的證據是多種子模擬（`docs/evidence/.../day52_seeds.txt`），它抓過 b443ab5。該被當成測試的是分佈，不是一個種子。
- **確定程度：** 已確認。
- **Dylan 玩幾分鐘內會不會注意到：** 不會。

### WS9-07 [TEST] Medium 測試環境跟你的 iPhone 不一樣：只有 Chromium、幾乎都用滑鼠、幾乎都 390 寬、時間凍結、字型被擋
- **在哪裡：** `run_tests.py` 的 `Game`。
- **怎麼重現：** 統計 `touch=True`、`viewport`、`manual=`、`page.route`。
- **看到什麼：**
  - **只有 Chromium：** rc7.1「文字框備份讓 iPhone 當機」這種事抓不到。報告自己寫「A Chromium touch test is not an iPhone.」
  - **觸控：** 8 個開觸控，其中 6 個真的用手指點，都點在 HTML 元素上。
    - 餐廳畫面（桌子、出菜口、貓）只用滑鼠點，或直接呼叫處理函式，例如 `v24_rc7_2_a_tap_on_the_pass_sends_the_plates`。
    - rc7.2（e4e2b07）：「A line with a face (22:07) answers the touch itself (pointerdown) ... on the phone the tap went nowhere」。當時 `v24_rc6_a_name_finds_its_person_and_a_person_its_name` 用滑鼠點，通過。
  - **寬度：** 375 只有 4 個，430 只有 1 個，電腦寬 1 個。
  - **時間：** 只有 1 個測試時間在走。
    - rc7.2「這個對話框的叉叉按不了很久了」：「the button under the finger was replaced between the touch and the click」（5e25fa1）。
    - `followup_a_busy_service_keeps_every_line_and_the_journal_is_reachable` 點 × 一直成功，因為按下和放開之間不會多一句。
  - **字型：** 全部擋掉 Google Fonts（run_tests.py:93–94）。`v24_the_signature_steppers_stay_on_their_own_line` 註解：「the player's phone font is narrower than this browser's, so the jump showed there and not here」。
- **確定程度：** 已確認。
- **Dylan 玩幾分鐘內會不會注意到：** 會，上面的例子都是你先發現的。
- **備註：**
  - 觸控、寬度、時間在走時點、真字型，這幾項都便宜（E2E-1、E2E-7）。
  - WebKit 這台機器沒裝；要不要花這個成本，需要 Dylan 決定。

### WS9-08 [TEST] Medium 沒有任何測試用點的玩完一整天；營業都是測試機器人用內部函式打的
- **在哪裡：** `play_day`、`__bot`、`__actLazy`、`to_service`、`_lazy_days`。
- **怎麼重現：** 讀這幾個函式。
- **看到什麼：**
  - 帶位、點餐、做菜、上菜、結帳全靠機器人。`touch_controls` 用滑鼠測過單一的點擊判定，但沒有串成一晚。
  - 119 個測試直接用 `autoStock()` 或假按鈕補貨；真的按補貨按鈕的 4 個都不是「一鍵補到建議量」。
    - `autoStock()` 補的量跟那顆按鈕一樣（對過程式碼），缺的是按鈕本身：在哪、能不能按、有沒有被蓋住。
  - rc8.1「這一段開店很久都不消失！緊急處理發佈更新」：db8dd56 說「the tutorial bot does it in seconds, a player who has not tapped the table yet kept the tip over the room」。
- **確定程度：** 已確認。
- **Dylan 玩幾分鐘內會不會注意到：** 會（rc8.1）。
- **備註：** E2E-1、E2E-2。

### WS9-09 [TEST] Low 永遠成立的檢查，和說明寫得比實際多的測試
- **在哪裡、看到什麼：**
  - 永遠不會失敗：
    - run_tests.py:1722：`check(met or True, 'a meeting is a 70% roll; when it happens both journals remember it')`
    - run_tests.py:1781：`check(g.ev("$('#screen').innerText.includes('？？？')") is not None, 'hidden achievements are veiled')`
    - v23_tests.py:1200：`check(g.ev("!S.achievements||!S.achievements.allprojects||true"), 'the five-project achievement is untouched')`
    - v23_tests.py:1306：`check(g.ev("goalLadder().every(x=>!/側廳卡座/.test(x.n))") or True, 'the goal ladder only offers it when it can be bought')`
  - 一半永遠成立：v23_tests.py:264（`R.sched.length >= 0`）、run_tests.py:3164（`(R.log||[]).length >= 0`）。
  - 被關掉的程式：run_tests.py:695 `g.ev("__bot(40000,1/30)") if False else None`；:2339 `g.tap('#scene') if False else None`。
  - 說明寫得比做的多：
    - `jill_rests_when_staff_cover_the_floor` 說「gets up the moment a table is tapped. Tapping sleeping 包包 gives visible feedback」，實際是 `R.jill.q.push(t.i);endRest()` 和 `tapCat(...)`。
    - WS9-04 的兩個。
    - `album_notes_and_journal` 還寫「caps ordinary photos at 30」，但 rc7.5 起上限是 240。它比對的是 `albumCap()`，所以照樣會過。
- **怎麼重現：** 打開上面的行號。
- **確定程度：** 已確認。
- **Dylan 玩幾分鐘內會不會注意到：** 不會。
- **備註：** 改或刪的是那幾行，不是測試。

### WS9-10 [DOC] Low tests/saves/README.md 說只有一個測試載入全部存檔，其實有四個；7 份存檔不在表裡
- **在哪裡：** `tests/saves/README.md`、`docs/RELEASE_CHECKLIST.md:124`。
- **看到什麼：**
  - README 寫「the one test that loads them all (`v24_rc6_the_floor_and_its_rooms_are_tabs`) only checks that each loads clean」。
  - 實際會自動納入每份新存檔的有四個：
    - `v24_saves_load_and_nothing_fires_on_load`
    - `v24_rc6_the_floor_and_its_rooms_are_tabs`
    - `v24_rc8_the_restaurants_three_lists_and_the_lounges_one`
    - `every_player_save_migrates_plays_a_day_and_keeps_its_story`：每份玩一整天，155.5 秒，全套第三慢。
  - 表裡缺：`player_day2_2155`、`day81_2206`、`day83_2218`、`day86_2229`、`day87_2257`、`day89_0448`、`day89_2320`。
  - checklist「Mature saves migrate: every fixture in `tests/saves/`」，跟你 05:42 的話方向不同：「不要讓 regression time 隨存檔數量線性膨脹。」「請選少量「代表性存檔」做 compatibility / migration coverage。」
- **判斷：**
  - 每份「讀得進來」很便宜，值得留。
  - 會一直變長的是「每份玩一整天」。
  - 四個測試可以合成「每份只開一次，做所有檢查」。
- **確定程度：** 已確認。
- **Dylan 玩幾分鐘內會不會注意到：** 不會。
- **備註：** 要不要縮成代表性存檔，需要 Dylan 決定。你也說過「不要刪除既有重要 regression coverage」。

### WS9-11 [TEST] Low 7 個測試檢查的是程式碼長什麼樣子，不是遊戲做了什麼
- **看到什麼：**
  - `v24_back_of_house_is_a_work_area_and_keeps_its_two`：`"opsLv('room')" in String(drawKitchenRoom)`、`String(drawBackRack).includes('seat')`
  - `v24_the_wall_is_written_to_the_rules`：`when.toString().includes("'wall_settle'")`
  - `rc83_small_things_from_the_players_evenings`：`"banner('✨ PERFECT! ✨'" not in src`、`homeItems.toString().includes(...)`
  - `v24_rc6_the_staff_room_comes_from_a_need_and_grows_in_place`：`String(drawSrKitchenette).includes("srTrace('cup')")`
  - `v24_rc6_private_dining_reservations_follow_the_rules`：`String(orderItems).includes('pdRes')`
  - `v24_rc73_jills_room_is_there_from_day_one`：`'drawSofaGroup' not in String(drawScene)`
  - `v24_rc74_favourites_learned_in_play_and_marked_on_the_menu`：`'sat+=6' in String(collect)`
- **判斷：**
  - 改名或重構時會假警報；換個寫法畫錯東西又照樣過。
  - 另一種文字檢查（台詞、禁用詞、數 `portraitData(`）是刻意的絆線，有用，不在這 7 個裡。
- **確定程度：** 已確認。
- **Dylan 玩幾分鐘內會不會注意到：** 不會。

### WS9-12 [DESIGN] — 面板開著時，一晚被停住幾次、跳出幾則訊息，算太多？
- **現況：** 現在寫下來的只有三個數字。
  - 一天最多兩個主要故事（rc7）。
  - 路人閒聊一晚最多 10 句（rc8.5）。
  - `rc85_small_talk_is_rare_and_makes_sense` 的「跳出 ≤45 則」（之前約 93 則）。我不確定 45 是不是你定的。
- **需要 Dylan 決定：** 普通一晚最多被停住幾次、最多跳出幾則。沒有這個數字，E2E-6 只能記錄、不能判失敗。

---

## 盲點逐項

| 盲點 | 現況 | 過去的例子 |
|---|---|---|
| 面板預設關 | 17/247 打開；多天測試和 golden 全關 | rc7.2 秀琴不停店、rc8.5 插圖不停店、WS9-01 |
| 390 以外的寬度 | 375：4 個；430：1 個；電腦寬：1 個 | 375×553 時「繼續營業」在畫面外 |
| 觸控 vs 滑鼠 | 手指點 6 個，全在 HTML 元素上；畫布 0 個 | rc7.2 有頭像的台詞 |
| 重新載入／繼續營業 | 會重新載入 37 個；玩家 checkpoint 接回 1 個；面板開著時重新載入 0 個 | rc8.3、WS9-01 |
| 一整天用 UI | 0 個 | rc8.1 提示 |
| 按鈕 vs 函式 | 真的點 57、只用 JS click 1、只用假按鈕 23、沒碰過 33 | rc6–rc8.5 二樓房間 |
| 各時代存檔搬家 | 強：4 個測試讀每份存檔 | 都跳過 checkpoint；rc5–rc6 的 checkpoint 會退回，沒人記下來 |
| 手冊 vs 遊戲 | 只比對字串；戳記 `'— last: v2.4 rc8'` 對任何 rc8.x 都會過 | rc7.5 手冊寫相簿上限 30（實際 240），沒有測試會抓到 |
| 長時間多天 | 四十天（一個種子、面板關、`autoStock`）、十四天、十天 | 分佈靠手動多種子模擬（抓過 b443ab5） |
| 面板開著的節奏 | 沒人量 | rc8.5「跳出的對話有些太重複沒有意義 又太頻繁」 |
| golden 重錄頻率 | 10/01–10/04 共 20 次 | WS9-05 |
| 換種子 | 4 個測試換了 8 次 | WS9-06 |
| 字型 | 全擋 | 招牌菜 −／＋ 跳動 |
| 時間凍結 | 只有 1 個測試時間在走 | rc7.2 對話紀錄 × |
| 瀏覽器 | 只有 Chromium | rc7.1 iPhone 當機 |

## 過去的 bug：當時有沒有測試抓得到？

| 版本 | 你說的或 bug | 有測試會抓嗎 | 為什麼沒抓 | 現在守著的 | 哪個 E2E 會抓 |
|---|---|---|---|---|---|
| rc6 09:55 | 菜單滿了，酒吧小點加不上去 | 沒有 | 菜單滿的測試都在新遊戲 | `v24_rc6_bar_bites_take_no_menu_slot` | E2E-2 |
| rc6–rc8.5 | 「無法升級到二級休息室 訂購70000按不下去」 | 錯的測試 | 呼叫函式；`includes('buyPD:1')` 把錯的當答案 | `rc85_the_rooms_upstairs_are_bought_by_their_buttons`（沒涵蓋包廂） | E2E-3 |
| rc7.1 | 文字框備份讓 iPhone 當機 | 不可能 | 只有 Chromium | 沒有 | 只有 WebKit 或真機 |
| rc7.2 22:07 | 有頭像的台詞手指點沒反應 | 有測試但用滑鼠，過了 | 滑鼠不是觸控 | `v24_rc7_2_a_named_guests_line_answers_a_touch` | E2E-1、E2E-7 |
| rc7.2 22:28 | 「這個對話框的叉叉按不了很久了」 | 有測試點 ×，過了 | 時間凍結 | `v24_rc7_2_a_regulars_head_at_a_busy_table_and_the_log_closes` | E2E-1、E2E-2 |
| rc7.2 22:29 | 「點桌子的時候不小心點到常客的頭就會跳他的說明整個擋住你的操作」 | 沒有 | 只在桌子沒事時點 | 同上 | E2E-1、E2E-2 |
| rc7.2 21:49 | 「秀琴阿姨出場要暫停遊戲吧 有劇情的」 | 沒有 | 面板關；新需求 | `v24_rc7_2_xiuqin_first_evening_holds_the_service` | E2E-6 |
| rc8.1 | 「這一段開店很久都不消失！緊急處理發佈更新」 | 沒有 | 機器人幾秒做完 | 只有 `golden_frames` 間接守 | E2E-1 |
| rc8.3 | 「Day 87：營業中存檔「繼續營業」變空店（29 組→0）」 | 沒有 | 沒有特別晚上的接回測試；`G_STATES` 漏了 | `rc83_a_special_evening_comes_back_with_its_room` | E2E-4、E2E-5 |
| rc8.5 | 「員工休息室我正常遊玩時完全看不到」 | 沒有 | rc6 測試只看打烊後、安靜的一天 | `rc85_the_crew_go_up_…`（看內部狀態、一個種子） | E2E-2 |
| rc8.5 | 「有跳出我生成圖片的畫面的劇情 都是要 停止餐廳營業 玩家手動按才繼續」 | 沒有；而且說「shown」 | 面板關；比較像補需求 | `rc85_a_picture_always_holds_the_service` | E2E-2、E2E-6 |
| rc8.5 | 「跳出的對話有些太重複沒有意義 又太頻繁」 | 沒有 | 沒人量（約 93 則） | `rc85_small_talk_is_rare_and_makes_sense` | E2E-6 |
| 已知，分支已修 | 「Dylan已經揭露但在房間還是沒寫Dylan」 | 不可能 | PROJECT_MEMORY:117「不寫他的名字（揭曉前也一樣）」；測試只守寫下來的規則 | 沒有 | 規則確定後用 E2E-2 |

**小結：** 這十幾個你玩出來的 bug，沒有一個是邏輯算錯，全部是「看得到、點得到、接得回來」那一層。

## 建議的 E2E 玩家路徑測試（7 個）

共同做法：

- 觸控，面板開著。
- 時間在走的時候點。
- 可以讀狀態決定點哪裡，但動作只能是點畫面。
- 每個都附截圖。

### E2E-1 新遊戲前三天，全用手指
- **步驟：**
  1. OPEN FOR DINNER →「一鍵補到建議量」→ 開店。
  2. 整晚用點的：帶位、點餐、爐台與托盤、出菜口、結帳收桌。
  3. 面板出現就一句句點。
  4. 結算 → 用按鈕買一樣東西 → 準備 DAY 2。
  5. 重複到 Day 3。
  - 點的節奏像人：每 0.5–1 秒一下。
- **檢查：**
  - 沒有錯誤。
  - 每次點擊都有可見反應（「死點擊」就失敗）。
  - 沒有東西蓋住餐廳超過 15 秒。
  - 錢對得上結算。
- **會抓：** rc8.1、rc7.2 那三個、任何按不下去的按鈕。
- **成本：** 寫一次用點的機器人（audit_lib 的 `tap_scene` 已有一半），每次約 6–8 分鐘。

### E2E-2 Day 92 的一晚：用點的、面板開著、每個房間都看
- **步驟：**
  1. 準備 DAY 93 → 補貨 → 開店，員工做事。
  2. 定時點每個房間分頁並截圖。
  3. 開菜單頁開關一道菜。
  4. 面板出現就點完 → 結算。
- **檢查：**
  - 營業中休息室畫面上看得到員工。
  - 插圖面板出現時時鐘停住。
  - 故事頁句數等於面板出現過的句數。
  - 跳出數量記下來。
  - 錢對得上。
- **會抓：** rc8.5 休息室、插圖不停、rc6 菜單上限。
- **成本：** 約 2–4 分鐘。

### E2E-3 店裡每顆按鈕都真的按一次
- **步驟：**
  - 存檔：新遊戲 Day 6 以後、Day 61、Day 92。
  - 用內部函式補錢、讓包廂出現，只為了到達狀態。
  - 每個沒 disabled 的 `[data-act]`，各在一份新副本裡真的點一下。
  - 375／390／430／電腦寬各跑一次。
- **檢查：**
  - 點了有東西變，或畫面說明為什麼不行。
  - 沒有錯誤。
  - 按鈕中心點是它自己，沒被蓋住。
- **會抓：** 二樓房間按鈕；「電腦版升級餐廳點不到右邊的項目」；附錄 B 裡的商店動作。
- **成本：** 每份存檔 1–2 分鐘。

### E2E-4 特別的晚上：中途離開再回來
- **步驟：**
  - 從 Day 87、89、92 用內部函式設成特別的晚上（品酒夜、主廚之夜、予安、Madame Lin、包廂、貓不見）。
  - 在三個時間點各做一次：切背景 → 重新載入 → 點「繼續營業」。三個時間點是故事前、面板開著（第二句）、故事後。
- **檢查：**
  - 完整接回，沒有「無法完整還原」。
  - 面板那次：那一段重新出現，故事頁台詞完整。
  - 加一個靜態檢查：所有指派給客人群組的 `state` 都在 `G_STATES`。
- **會抓：** rc8.3、WS9-01。
- **成本：** 3–5 分鐘。

### E2E-5 你自己的「繼續營業」，幾份代表性存檔
- **步驟：**
  1. 存檔：Day 2、30、74、89、最新一份。
  2. 點「繼續營業」→ 玩 2 分鐘。
  3. 切背景 → 重新載入 → 再點「繼續營業」。
  4. 玩完這一天。
- **檢查：**
  - 每份的預期結果（接回或有訊息的退回）寫在表裡。
  - 兩次接回之間，錢、客人數、故事計數不變。
  - 這一天結束得了。
- **會抓：** rc8.3；以後讓目前存檔也退回的改動。
- **成本：** 每份約 1 分鐘。可以併進 `every_player_save_migrates…`。

### E2E-6 兩週、面板開著、照你的節奏（只在發布前跑）
- **步驟：** Day 61 連續 14 天。每天按「一鍵補到建議量」→ 開店 → 員工做事 → 面板點完 → 結算。
- **檢查：**
  - 沒有錯誤、故事順序對、主要故事每天 ≤2。
  - 每晚記錄停住幾次、停多久、跳出幾則、閒聊幾句；門檻等 WS9-12。
- **會抓：** rc8.5 閒聊；rc7.2 秀琴；rc6「阿拓跟晴毫無進展」那種卡住。
- **成本：** 約 25–30 分鐘。

### E2E-7 三種寬度、真觸控、真字型
- **步驟：**
  - 寬度 375×667、390×844、430×932。
  - 路徑：標題 → 開店前 → 營業 → 暫停選單 → 日誌（故事頁；相簿點開照片、左右滑）→ 升級餐廳（橫向捲動分頁列）→ 每個分頁。
  - 讓字型真的載入。
- **檢查：**
  - `overflow()` 沒有被切掉的東西。
  - 按鈕中心點是它自己。
  - 相簿能左右滑。
  - 用 CDP 試長按。
- **會抓：** 招牌菜 −／＋ 跳動；375×553 的「繼續營業」；rc7.2 的觸控；新聞在 390 被切。
- **成本：** 每個寬度 2–3 分鐘。

### 時間怎麼排
- 每次完整回歸都跑：E2E-3、4、5，約多 10 分鐘。
- 1、2、7：約多 15–20 分鐘。
- 6：只在發布前跑，約 30 分鐘。
- 對照：rc8.5 完整回歸是 3,077 秒測試時間，分三份同時跑，每份約 17 分鐘。

## 低價值、重複、不穩定的測試

你說「不要為了讓 247 變 300 而增加低價值測試。」所以我只建議多 7 個 E2E，下面的清理不增加測試數。刪不刪測試，需要 Dylan 決定。

- **不穩定（一個種子）：**
  - `jill_rests_when_staff_cover_the_floor`
  - `v24_day52_save_plays_the_stories_in_order_over_forty_days`
  - `lounge_i_content_bar_food_in_the_kitchen_wine_at_dinner_the_cast_by_name`
  - `rc85_the_crew_go_up_to_the_staff_room_in_a_busy_evening`
  - `rc85_small_talk_is_rare_and_makes_sense`
  - 建議改成多種子門檻或測機制。
- **重複：**
  - 四個「每份存檔都開一次」的測試，合成一次載入多項檢查。
  - 兩個 golden 每次一起重錄：留著，但附證明。
- **低價值的行：** 4 個永遠成立 + 2 個一半成立、2 行 `if False`、7 個程式碼長相檢查。
- **宣稱多於實際：**
  - `v24_yijun_comes_to_eat_and_her_mother_walks_over`（「shown」只看紀錄）
  - `v24_rc7_2_a_tap_on_the_pass_sends_the_plates`（呼叫函式）
  - `rc85_the_crew_go_up_…`（看內部狀態）
  - `jill_rests_…`（說點，但沒點）

## 檢查過、沒有問題的
- `G_STATES` 今天完整。
- 包廂 I「動工」、休息室 II「訂購」用真的點都買得到。
- rc8.5 的怪屬性掃描是好保險。
- 13 份 checkpoint 接回都沒有頁面錯誤：8 份完整，5 份照設計退回、有訊息。
- `autoStock()` 和「一鍵補到建議量」補的量一樣。
- 存檔搬家覆蓋強：每份玩家存檔至少被 4 個測試讀進來。
- 關卡確實會抓邏輯 bug。
- jill_rests 換種子的證據是誠實的；我不同意的是設計，不是那次的判斷。

## 沒辦法檢查的
- 真的 iPhone、Safari、WebKit（只有 Chromium）。
- 真字型。
- 觸控的長按和滑動。
- 整套 247 個測試（沒跑，用 rc8.5 的紀錄）。
- Safari 多常丟掉分頁，也就是 WS9-01 的頻率。
- 走 `scene()` 的插圖故事在重新載入時會怎樣。
- E2E-6 的門檻（WS9-12）。

## 附錄 A：247 個測試逐一分類
- 檔案：`…/ws9_tests/work/notes.tsv`（tab 分隔，247 列，已驗證沒有缺漏或重複）。
- 欄位：
  - `name`：測試名稱。
  - `primary`、`secondary`：方法，代號見上面「方法統計」。
  - `catches`：這個測試失敗時，玩家會看到什麼問題（中文）。
- 檔案與行號：`work/tests.json`。
- 「假按鈕」＝測試自己做一顆按鈕、塞 `data-act` 再 click，不是畫面上那顆。

## 附錄 B：114 個按鈕動作的覆蓋（`work/acts_final.json`）
- **真的點過（57）：** bdAdd bdAddD bdOpen bdRm bdRmD book bookSocial btab buyGear buyProject buySR buySideBooth buyTable closeEarly closeNow closeSub export guide hire import importYes ktCancel ktHold linSign load menuAdd menuRandom menuSwapDo menuSwapNo nextDay open openFresh peek photo postsAll reset1 reset2 resume revealPeek revealPrep save settings sigMake sigPick sigdOpen staffTab start stock stockTo story tab toPrep toShop toggle upGo upLook upPlanBig
- **只用 JavaScript click（1）：** cnPlan
- **只用假按鈕或直接 doAct（23）：** album buyDecor buyEq buyExt buyFrontTable buyLgFurn buyOps buySeason buySideTable buyWin contractSign crewUp expand hireLounge labTry rd rdSpecial restock revealClose seasonUse wineCourse wineDev wineT
- **沒有任何測試碰過（33）：** backShop bookStory buyLounge buyPD buyUp campaign cnCancel contractEnd copyBackup discardAll discardAsk extStyle illus importNo jillPost labPick linTake loungeGo music pasteBackup pasteCancel pasteGo price reco resetNo roomGo setT sfx sigOpen speed starUp tastingDir theme

## 附錄 C：探針
- **按鈕：** `work/probe_rooms.py`，紀錄 `probe/probe_rooms_log.txt`，截圖 `probe/00–04`。
- **面板開著時重新載入：** `work/probe_hold_reload.py`、`work/probe_hold_reload2.py`，紀錄 `probe/probe_hold_reload*_log.txt`，截圖 `probe/10–13`。
- **13 份存檔的「繼續營業」：** `work/probe_resume_eras.py`、`work/probe_resume_why.py`，紀錄 `probe/resume/resume_log.txt`、`probe/resume/resume_why_log.txt`，截圖 `probe/resume/`。