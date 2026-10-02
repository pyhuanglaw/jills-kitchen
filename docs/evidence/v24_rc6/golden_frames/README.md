# golden_frames 的重錄證明（v2.4 rc6，2026-10-02 12:15）

golden_frames 上一次通過是在 bd3c4ec（05:07）。之後有這些改動會改變它的畫面：客人的穿搭（07:05、08:12，以及今天的「客人不穿白色上衣」）、誰在哪裡（07:09）、日誌的關閉按鈕（09:51）、客人台詞（09:39）。

## 方法

把目前的 `js/game.js` 複製到 HEAD 的乾淨 worktree，只把會改變亂數的兩組台詞改動放回舊版（`../golden_scenario_proof_revert.py`）：
- 客人台詞，09:39；
- 新東西被談論的座位台詞池。

然後用 `gf_verify.py` 跟舊的基準（`tests/golden/frames.json` 和 `tests/golden/screens/`）比對：每一個取樣、每一個欄位、兩天結束時的摘要、每一張畫面都比。

## 結果（`proof_report.json`）

**行為完全相同**，兩天都是：
- 影格數相同：7301／8028；
- 取樣數相同：244／268；
- 每一個取樣的這些欄位都相同：時間 `t`、`phase`、貓的狀態 `cats`、權重 `weights`、托盤 `tray`；
- 一天結束時的摘要也相同：錢、營業額、客人數、評價、熟客、庫存、貓、相簿。

只有畫面像素 `scene` 和 DOM `dom` 不同。
- 第 1 天：161／145 個取樣不同；
- 第 2 天：184／166 個取樣不同。

### DOM 的差別（`dom_dump.py`）

在 bd3c4ec 和證明用的程式各跑一次，傾印取樣時雜湊的那七個元素，圖片的 data URL 先換成同一個字。

結果唯一的差別：客人說話的 toast 多了 class `who`。這是 07:09「點一句話找到說話的人」。其餘差別都是圖片本身：票上客人的頭像，衣服換了。

### 畫面的差別

| 畫面 | 為什麼不同 | 圖 |
|---|---|---|
| title、prep、evening、summary、shop | 相同 | — |
| service_20s、service_panel | 兩位客人的衣服：花呢外套；淺藍襯衫，不再是白色 | `cmp_service_20s.jpg`、`zoom_guests_day1.jpg` |
| pause | 票上客人頭像的肩膀（衣服） | `cmp_pause.jpg` |
| book_cats | 日誌是高的那一種：標題固定在上面，最下面有「關閉日誌」（09:51） | `cmp_book_cats.jpg` |
| book_mem | 同上；「被拍了」那張照片裡客人的衣服 | `cmp_book_mem.jpg` |

圖的排法是：左邊舊基準，中間現在的畫面，右邊紅色是差別。

## 結論

golden_frames 裡變的只有：
- 客人的穿搭；
- 說話的 toast 可以點（`who`）；
- 日誌的版面；
- 台詞（另外由 golden_scenario 的證明涵蓋）。

所以用目前的程式重錄：`python3 tests/run_tests.py --record -k golden_frames`。
