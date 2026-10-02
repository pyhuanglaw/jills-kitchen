# golden_frames 的重錄證明（v2.4 rc7，2026-10-02 15:30）

golden_frames 上一次通過是 rc6 的 1241ee3。之後有一個改動會改變它的畫面：玩家 14:39 要的「每天的帳」，也就是租金、薪水和酒水成本。golden_frames 的兩天是一家 LV1 的小店：沒有員工、沒有 Lounge，所以只有租金在動，每天 $300。

## 方法

1. 用目前的程式跑 `gf_verify.py`，對舊的基準（`tests/golden/frames.json` 和 `tests/golden/screens/`）逐一比對：每一個取樣、每一個欄位、兩天結束時的摘要、每一張畫面。
2. 第 2 天的取樣全部不同，所以用 `dom_dump_day2.py` 在 HEAD（1241ee3，還沒有這次改動）和目前的程式各跑一次。第 2 天開頭的 12 個取樣，傾印取樣時雜湊的那七個元素，再拿兩邊互相比。

## 結果（`report.json`、`dom_diff_day2.json`）

**行為完全相同**：
- 兩天的影格數都相同：7301 和 8028；
- 取樣數也相同：244 和 268；
- 第 1 天每一個取樣的每一個欄位都相同。

第 2 天每一個取樣的 `dom` 都不同。DOM 的差別只有一個：HUD 上的錢從 $1,287 變成 $987，少的正好是第 1 天晚上付的 $300 租金。其他欄位（時間、phase、貓、權重、托盤、畫面像素）都相同。

一天結束時的摘要只有兩個地方不同：錢，以及摘要裡的淨利。差額正是租金：第 1 天 −300，第 2 天累計 −600。`golden_scenario` 的證明也是同一回事（`../golden_scenario_proof.log`）。

### 畫面的差別

| 畫面 | 為什麼不同 | 圖 |
|---|---|---|
| title、prep、service_20s、service_panel、pause、evening | 相同 | — |
| summary | 帳上多了一行「租金」（主廳 $300），淨利和 HUD 上的錢各少 $300，下面的內容往下移了一行 | `cmp_summary.jpg` |
| shop | HUD 和「目前現金」少了 $300 | `cmp_shop.jpg` |
| book_cats、book_mem | HUD 上的錢少了 $300 | `cmp_book_cats.jpg` |

每張比較圖的排法：左邊是舊基準，中間是現在的畫面，右邊紅色是兩者的差別。

## 結論

golden_frames 裡變的只有租金，所以用目前的程式重錄：`python3 tests/run_tests.py --record -k golden_frames`。
