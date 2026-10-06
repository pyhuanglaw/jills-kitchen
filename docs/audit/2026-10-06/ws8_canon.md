# PROJECT_MEMORY 等文件的規則來源 — 代理人回報原文（2026-10-06 Audit）

> 這是那一組代理人交回來的原文，沒有改寫。裡面提到的截圖與腳本路徑是當時 session 的暫存資料夾，repo 裡沒有保留；
> 報告引用的截圖已複製到 `img/`（對照見 `README.md`）。文中的「Dylan 決定」「Dylan 會不會注意到」指的是使用者（2026-10-06 起統一寫「使用者」）。

## WS8 canon provenance: summary

This was report-only. I changed nothing under ROOT or in the repo.

**`findings.md` was not written.** The harness refused the file write ("Subagents should return findings as text, not write report files"), so I did not work around it with Bash. The full findings are in the appendix below, in Traditional Chinese, ready to be saved as `ws8_canon/findings.md`.

What I did write in `ws8_canon/`:
- 5 screenshots plus `notes.txt` in `shots/`.
- Search tools `quotes.py`, `fuzzy.py`, `src.sh`, and the quote-search results in `pm_quotes.txt`.

**Statistics.** Main's PROJECT_MEMORY has 130 rule rows:

| Class | Rows | Note |
|---|---|---|
| A | 85 | 17 of them are A†: the player's words exist only in a commit message or report, not in docs/v24 |
| B | 22 | |
| C | 8 | |
| D | 15 | |

So 37 rows (28%) have no player words at all.

**Calibration example (confirmed).** Main's PROJECT_MEMORY still carries both parts, and only the unreleased `feature/dylan-room` (09f3312) corrects them:
- §3 L117 「…不寫他的名字（揭曉前也一樣）」 is B. It comes from commit ec17365 ("no name on him (before the reveal too)").
- §4 L149 「揭曉前他在房間裡穿灰色帽 T、帽子一直戴著」 is C. The player wrote at 07:44 「在房間Dylan就穿帽T一直戴著帽T帽子吧」, with no 揭曉前 and no grey.
- Main's code keeps the hood up after the reveal (`DYLAN_HOME` `hoodUp:true`; screenshot from the Day 89 04:48 save).
- Main's own CURRENT_STATE L48 says 「帽子照玩家 10/3 的話一直戴著」.

### Top findings
- **WS8-01 Medium.** PM §4 L149 narrows the hood rule to 「揭曉前」 and adds 「灰色」. It contradicts CURRENT_STATE L48 and the code.
- **WS8-02 Medium.** PM §3 L117 「不寫他的名字（揭曉前也一樣）」 is an implementation choice still on main. The branch fix also writes a tab rename 「Jill 和 Dylan 的房間」 into canon (C); the player only said 「在房間還是沒寫Dylan」.
- **WS8-03 Medium.** PM §4 L151 「揭曉前…畫面上也不能出現他的頭像」 generalises a complaint that was only about Day 1. It contradicts the game: before the reveal, Dylan the regular has a face in 餐廳日誌 › 熟客 (Day 67 screenshot) and in his lines (game.js L1828).
- **WS8-06 Medium.** PM L11–13, the paragraph on who may edit PM, admits rules the player never approved:
  - 「不看歷史很容易猜錯的、曾經刻意從舊設計改掉的」 need no player approval.
  - Its quoted phrases are not the player's.
  - §11 「看到就不要再改回去」 mixes in implementation fixes and unsourced rows.
- **WS8-10 Medium.** PM L39 and L318 let test-only fixes after the gate rerun only those tests. The player said 「你不可以跳過任何測試」, and testing_strategy §7 ends with 「最終再確認完整 release regression」.
- **WS8-D1 Medium [DOC].** About 20 player quotes behind PM rules live only in commit messages or reports. RELEASE_CHECKLIST §1 requires verbatim filing.
- **Low items:**
  - WS8-04: the 先生 label.
  - WS8-05 [DESIGN]: cooks covering other stations.
  - WS8-07: photos outside a story hold the service.
  - WS8-08: booked-out nights block Lounge stories.
  - WS8-09: Madame Lin day counts and the brass bell.
  - WS8-11: the debugging order is reversed.
  - WS8-12: 只用繁體中文.
  - WS8-13: direction sentences with no source.
  - WS8-14: 予安 three fixed nights.
  - WS8-D2 to D5: stale ARCHITECTURE and LIFE_SYSTEM passages, and report sources missing from the repo.

### The 10 most important B, C and D rules
1. **C**, §4 L149: hood 「揭曉前」 and 「灰色」. The player said 「一直戴著」.
2. **B**, §3 L117: no name in the room, 「揭曉前也一樣」. The player asked for the name on 10-05.
3. **C**, §4 L151: no face or portrait before the reveal, anywhere. The player meant the Day 1 photo only.
4. **B**, §4 L149: 「揭曉前名牌、旁白叫『先生』」 comes from Checkpoint B (4a1a9b2). Main's room shows no name at all.
5. **C**, §3 L108 and §11: cooks cover other stations (`chefCover`). The player said 「有廚師她就不用做」.
6. **D/C**, §0 L11–13: who may write PM.
7. **C**, §0 L39 and §10 L318: the test-only rerun exception.
8. **C**, §9 L279–280: Story Photos outside a story also hold the service, and portrait-only lines are exempt. The player spoke of 劇情 with their pictures.
9. **B**, §2 L85–86: booked-out Lounge nights exclude every Lounge story. This generalises a fix for 予安's trial.
10. **B**, §6: the pacing numbers (一天最多一步、一週以上、12 天、兩天、改裝兩天、5 天) and the brass bell. The player wrote 「一段時間」「幾天後」.

### Checked and fine
These match the player's words:
- the spaces in §5–§8;
- the order and prohibitions of the Madame Lin line;
- the five 晴×阿拓 scenes;
- the three staff lists;
- photos as evidence;
- 「玩家的圖一定停店」;
- saves are never reset;
- Publish ≠ Progress, and no zip;
- the ♥ only for Sophie and Mia;
- the $3,000 loans, repaid automatically above $20,000.

Of the 9 "canon" claims in the V24 reports, 5 are the player's.

### Could not check
These sources are not in the repo:
- the 10-03 message that asked for a project memory;
- the "handover" document;
- the "phase 3 canon" message.

The pre-v2.2 cat traits (sex, 賽跑, 埋伏) have no source in the repo.

### For the whole audit
The brief says "The 74 is before Dylan's reveal". That is wrong:
- every save from day71 on has `stage 3, reveal 69` (day71, 73, 74, 81, 83, 86, 87, 89, 92);
- the saves from before the reveal are day2, day52, day61, day65, day67 and day68.

---

# APPENDIX: full findings (save as `ws8_canon/findings.md`)

# WS8：canon 的來源（2026-10-06，只報告，沒有改任何東西）

ROOT＝`audit_main`（main，0f57a9f，v2.4 rc8.5）。

**玩家的原話**
- `docs/v24/*.txt`、`docs/v23/*.txt`；
- 玩家交來的 brief：`docs/V23_BRIEF.md`、`docs/V23_STORIES_BRIEF.md`。Claude 加的【整合紀錄】不算。

**放在 `docs/v24`、`docs/v23`，但是 Claude 寫的，不算玩家原話**
- `AUDIT_AND_PLAN.md`
- `story_presentation_audit_2026-10-02.md`
- `art_requests_2026-10-03_1539.md`
- `art/tasting_night_pictures_spec_2026-10-04.md`
- `v23/dialogue_audit_2026-10-01.md`
- `v23/story_audit_2026-10-01.md`

歷史只用唯讀的 `git log -S`、`git show`。

**分類**
- **A 玩家明確要求**：
  - **A†**：原話只在 commit 訊息或報告，沒有歸檔到 `docs/v24`。
  - **A（細節 B）**：核心是玩家的，數字或做法是實作補的。
- **B 從實作來的**：commit 或報告這樣做，玩家沒說過。
- **C Claude 推論或延伸**：玩家說的比較窄。
- **D 找不到來源**。

**遊戲畫面只用來觀察。**
- 操作：讀存檔 → 點標題的按鈕 → 點分頁。
- 呼叫遊戲內部只為了讀數值（`S.dylan.stage`、`DYLAN_HOME`），以及把房間的 canvas 原樣存成圖，避開蓋在上面的 COMBO 標記。
- 截圖在 `ws8_canon/shots/`。

## 1. PROJECT_MEMORY.md 逐條（main，130 列）

### 前言與 §0
| # | 規則（§／行；短引） | 類 | 來源 | 備註 |
|---|---|---|---|---|
| P01 | L6「永久 canon 在這份文件…暫時狀態在 CURRENT_STATE」 | B | 9cb384f 的文件分工 | 分工 |
| P02 | L8「原話與本文件衝突時，以『時間較新、玩家明確確認』的那一個為準」 | D | 找不到原話 | 照它，B／C／D 遇到較新的玩家原話應讓位 |
| P03 | L11–13「誰可以改這份文件…值得寫進來的只有三種：不看歷史很容易猜錯的、曾經刻意從舊設計改掉的、玩家有非常明確產品意圖的」 | D | 兩個引號都找不到：「這個是 hard canon，寫進 project memory」「員工變多以後，我就是希望 Jill 明顯多休息」；10/3 要建檔的那則訊息沒歸檔 | 前兩種不需要玩家同意 → WS8-06 |
| P04 | L19–22「來源各代表什麼」 | D | 無 | 流程 |
| P05 | L24–26 canon 衝突就停下來問 | A | `report_is_not_stop_0644`「兩個已確認 canon 直接互相衝突，無法同時成立」；`lounge_origin…1919` §27；`cooks_pacing` #1 | |
| P06 | L28–34 `CONFLICT FOUND` 格式 | B | 9cb384f 自訂 | |
| P07 | L36–38「運算是付費的…Full regression 只留給 release gate」 | A | `testing_strategy_0542`「日常小修改 ≠ 每次 full regression」「正式發布 = full regression required」；10:11「你這樣消耗了很多我的用量」 | |
| P08 | L39「gate 跑完之後，只改測試、不改遊戲檔的修正：重跑那幾個測試即可」 | C | 22:20「你不可以跳過任何測試，你已經做過一次很危險的事了」；`testing_strategy` §7「最終再確認完整 release regression」 | → WS8-10 |
| P09 | L40「長時間模擬要有明確假設」 | D | 無 | |
| P10 | L42–43 REPORT ≠ STOP；只在 canon 衝突、存檔風險、重大決策時停 | A | `report_is_not_stop_0644` §1、§3 | |
| P11 | L45–46 Commit ≠ Push ≠ Publish | A（細節 B） | 10:16「PUBLISH ≠ PROGRESS」、10:34 | 「WIP 隨時 commit/push」是實作 |
| P12 | L48–49 I／T／O；「headless 截圖也只算 T」；「程式存在」≠「玩家感知得到」 | A | `V23_BRIEF.md` §47「Claude/Fable 不得把 headless / simulated touch / seeded test 寫成 O。」；`rc6_final_spec`「存在 ≠ 玩家感知得到。」 | |
| P13 | L51「不要把猜測說成事實」 | A | 21:03「你根本沒查過」；21:05「你應該先查為什麼不一樣」 | |
| P14 | L53「只用繁體中文：遊戲文字、文件、回覆」 | C | 15:08「遊戲內請勿出現簡體中文 一切都是繁體中文 名子可以英文」 | 擴大到文件與回覆，漏了英文名字可以用 → WS8-12 |

### §1 產品核心
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| Q01 | L61–68 表（Restaurant Management＝skeleton…） | D | 找不到 | → WS8-13 |
| Q02 | L70「真正的 fantasy…慢慢生活下去」 | D | 原句找不到 | 方向和 V23 brief 一致 |
| Q03 | L71「…而願意再玩一天？」 | D | 找不到 | |
| Q04 | L73–75「替現在補以前」「我記得這裡以前不是這樣。」 | D | 兩個引號都找不到 | 有引號，卻不是原話 |

### §2 Story scheduler
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| S01 | L81–82「一天一個 major」是舊規則 | A | 15:39「一天可以不只一個劇情不然太慢」；`cooks_pacing` #8 | |
| S02 | L84 2 個 major／2 個 v24／3 個 minor；ambient 不限 | A（細節 B） | `cooks_pacing` #8 | 「ambient 不限」是程式（`LANE_CAP` ambient:99） |
| S03 | L85–86 包場的 Lounge 晚上不跟 Lounge 故事晚上同一晚；順延的包場算今晚 | B | cb3470f，原話只在 commit：「予安彈鋼琴配上大家畫面的時候 遊戲裡居然還沒人 人是後來才陸續進來」「主廚之夜我到結算才知道」 | → WS8-08 |
| S04 | L87–88 LANE_GAP 錯開 | A（細節 B） | #8「同一天兩個故事會用 `LANE_GAP` 錯開」 | 20%／10%／4% 是實作 |
| S05 | L89 同一條故事照順序走 | A | #8 | |
| S06 | L90–91 保留 slot | A（細節 B） | #8「planned visit 之類的重要事件仍有 slot 保護」 | |
| S07 | L92 沒排到不是消失 | A | #8「沒排到不是消失，而是延後排」 | |
| S08 | L94–95「先檢查這條線自己的前置條件…不要先懷疑或改 cap」 | C | #8「不要直接為了縮短晴×阿拓天數硬調她們的 trigger/cooldown。 先確認既有「一天最多 2 個 major beats」的 scheduler 規則是否仍正確存在並運作。」 | 檢查順序相反 → WS8-11 |

### §3 Jill 的工作量與休息
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| J01 | L101–103 產品意圖 | A | `cooks_pacing` #2 | |
| J02 | L106 有廚師就不用 Jill 做，包括第一份 | A | #7「我覺得直接改成不管是不是第一次做那道菜 有廚師她就不用做」 | |
| J03 | L106–107 廚師等級決定難度；招牌菜 LV5 | B | 3b4403f；`chefCan`（game.js L9245） | |
| J04 | L108 `chefCover`：別站的廚師過去接 | C | 同 J02 | → WS8-05 |
| J05 | L109–111 開店與快打烊時在主廳迎客送客 | A†（細節 B） | 25a0710「你就設定jill開店和關店都會在主廳歡迎和送客」 | 10%／88%、「打烊時一定起身」是實作 |
| J06 | L112 休息沒有固定長度 | B | 實作；玩家說的是「持續休息一段合理時間」 | |
| J07 | L113–116 在房間裡自己找事做 | A†（細節 B） | ec17365「Jill有房間後多讓他在房間有事做吧 自動會做的 看閨蜜機電視（可移動的）打手遊 我老婆常常跟網友打pubg 或跟老公聊天 看老公在幹嘛 跟貓咪互動」 | |
| J08 | L117「…不寫他的名字（揭曉前也一樣）」 | B | ec17365 "no name on him (before the reveal too)" | → WS8-02 |
| J09 | L117–118 台詞照 Jill × Dylan 的寫法 | A | `v23/qa4` | |
| J10 | L119–122「長期方向（2026-10-03 玩家）」 | D | 2e8245f 沒有原話 | → WS8-13 |
| J11 | L124–125 不降低 jill_rests 的門檻 | A | `cooks_pacing` #1–2 | |
| J12 | L126「沒有 sous-chef 職位」 | D | 找不到 | |

### §4 世界與角色
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| W01 | L132–133 五隻貓全部活著；禁止 memorial | A | `V23_STORIES_BRIEF` §十「五隻都只是正常活在 Jill’s Kitchen 裡。不要加入死亡、紀念、天使、回憶、過去／現在等設定。」 | 「現實世界的任何死亡資訊絕對不得進入遊戲」找不到原句 |
| W02 | L137–141 五隻貓的 canon | A | V23_STORIES_BRIEF §十；`implementation_pass`（orange longhair、tabby + white 1/3）；22:18–22:54；6ddd455「寶寶眼睛黑眼球旁邊是金黃色」（A†）；22:28「小寶就是寶寶」 | 性別、賽跑、埋伏找不到原話 |
| W03 | L143 貓不是 needs 系統 | A | 18:53「不要 pet needs。」 | |
| W04 | L144 偷食物：不是每次，永遠偷不成功 | A | 22:26「…但不是每次 然後不要讓他偷成功」；22:27「…也不要讓他偷成功」 | 包包只有「包包會偷雞腿類的 但比較常一直在底下看」，對包包是小延伸 |
| W05 | L146「Jill：自主的人，不是完全由玩家操控的 avatar」 | D | 找不到 | |
| W06 | L146 Jill 對 Dylan 的私事很低調 | A | `qing_tuo` brief §三「Jill 注重隱私。她不會主動跟員工介紹…」 | |
| W07 | L148 Dylan 從 Day 1 就是丈夫；揭曉仍然存在 | A | 18:53 §八「這點是 hard canon。」；`lounge_origin` §14；252ff1c | |
| W08 | L149「揭曉前名牌、旁白叫『先生』」 | B | 4a1a9b2；Checkpoint C 報告 L25 | → WS8-04 |
| W09 | L149「對話照常是夫妻，不要神秘兮兮」 | D | 找不到 | |
| W10 | L149「揭曉前…穿灰色帽 T、帽子一直戴著」 | C | 07:44「在房間Dylan就穿帽T一直戴著帽T帽子吧」；07:13「…不然揭曉前就知道了」 | → WS8-01 |
| W11 | L150 讀書；很少喝酒；不要太早說出司法官 | A | 18:54 §六；19:19 §18 | |
| W12 | L151 揭曉前不露臉、不出現頭像 | C | acd1d28「我發現dylan第一天就露臉了」「第一天就寫jill先生但不露臉」 | → WS8-03 |
| W13 | L151–152 Day 1 的照片：「Jill 先生」、不放頭像 | A† | acd1d28 | |
| W14 | L153–154 Madame Lin 時代不去隔壁；《簽約》才認識 Evan | A（細節 B） | `lounge_origin` §11C、§18 | |
| W15 | L156–158 Knowledge is local | A | `lounge_origin` §2、§14 | |

### §5 空間
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| R01 | L164–167 私人房間從 Day 1 就在；沙發在房間 | A（細節 B） | 18:53；18:54；19:23；22:32 | 「廚房後面」「queen bed」是用語 |
| R02 | L169–171 Lounge 是隔壁的獨立店面 | A（細節 B） | `lounge_origin` §0【HARD CANON】 | |
| R03 | L173–174 二樓：整層一次租；在 Lounge 之後；不依賴《那面牆》；找到貓不等於解鎖 | A | `second_floor_and_long_arcs` §2；`implementation_pass` I1；`second_floor_prerequisite_1025` | |
| R04 | L175–177 租下二樓時休息室已經在 | A† | b196ee3 的 hard canon 原話 | |
| R05 | L178–182 $510,000、包廂 12 天、`srLeaseMig` | B | b196ee3 | |
| R06 | L184–185 寶寶最先上樓，柔柔觸發劇情 | A† | 6ddd455；22:14；22:44 | |
| R07 | L187–188 休息室是真正的房間；禁止疲勞條等等 | A | `rc6_final_spec`；`rc6_spec_spaces`；10-04「有牆、有門的獨立房間」 | |
| R08 | L190–191 包廂：禁止 VIP meter、訂金、no-show、門的小遊戲 | A | `private_dining_room_brief`；`rc6_final_spec` | |

### §6 Madame Lin 與 Ken 的三張圖
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| L01 | L197–198 Madame Lin 的身分 | A | `lounge_origin` §1、§2、§17 | |
| L02 | L200「一天最多推進一步」 | B | 4a1a9b2、a95fcd2 | → WS8-09 |
| L03 | L201 《隔壁》的台詞 | A | §3 | |
| L04 | L202 黃銅小門鈴之後每天會響 | B | 4a1a9b2；玩家只說「禮物可以是：小植物、小型實用物、簡單開店禮」 | |
| L05 | L203–204 為什麼不賣酒；Ken 不是 quest giver | A | §4–§8 | 玩家寫「你真的不賣酒？」，這裡寫成「妳」 |
| L06 | L205 一週以上；「月底」＝12 天 | B | 4a1a9b2；玩家：「這個生活模式必須先存在一段時間」 | → WS8-09 |
| L07 | L205–206 只是想退休 | A | §7【HARD CANON】 | |
| L08 | L207–208 Jill 先說，書在後；Dylan 不替她決定 | A | §9、§10、§28 | |
| L09 | L207「至少隔兩天」 | B | 玩家：「Dylan 幾天後默默看 bar design book」 | → WS8-09 |
| L10 | L209 《看看》是同一幕；Evan 原本就在 | A | §11、§11C | |
| L11 | L210「4B 台詞：『Ken 在妳那邊吃完飯，就過來這裡坐。』」 | B | 遊戲裡的 `evan_origin`；玩家檔案裡沒有；「4B」查不到出處 | |
| L12 | L211「再想想」不會消失 | B | 4a1a9b2 | |
| L13 | L212–213 《簽約》；揭曉後的介紹 | A | §13、§13A | |
| L14 | L213 揭曉前「Evan，這 Jill 老公。」；「說一個字」 | B | Checkpoint C 報告 L25 | |
| L15 | L214 改裝兩天 | B | a95fcd2 | |
| L16 | L214 Evan 從不招募 | A | 10:32「…Evan 一開始就要在酒吧裡…原本就在的員工」 | |
| L17 | L215–216 Madame Lin 當客人：「坐哪？」 | A | §17 | |
| L18 | L215 開幕 5 天以上 | B | 玩家：「The Lounge 開幕一段時間後」 | → WS8-09 |
| K01 | L220–227 名稱「品酒之夜」；前三次各一張圖 | A | `ken_tasting_pictures_2026-10-04.txt`；改名的原話只在 25d53f8 | |
| K02 | L229 第一張用現有的圖；不生假圖 | A† | rc8.4 報告「不要生假圖」「不要拿同一張冒充三張」；15879e0 | 歸檔的檔案寫的是「我之後再給你三張圖」 |
| K03 | L230–232 rc8.4 的做法；「就用這張。」 | A†（細節 B） | 922223b；rc8.4 報告 | |

### §7 晴 × 阿拓
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| T01 | L238 held；沒有第六幕 | A | brief：「不要為了湊數拆成六幕。」 | |
| T02 | L238–239 揭曉後才開始；告白要有圖 | A† | 252ff1c「DYLAN揭曉才進那個劇情阿 我遊戲是邊玩邊修改 玩到很後面才追加的劇情 之後的玩家從第一天開始玩 不會到這麼後面才揭曉 而且有告白劇情一定要有圖」 | PM 用「……」略掉了中間的理由 |
| T03 | L240–249 五幕的內容 | A | brief（含修訂版第五幕）；19:19；19:42 | |
| T04 | L251 誰什麼時候知道 | A | brief #10、#13、#27 | |
| T05 | L252 包場夜打烊後可以 | A† | QING_TUO 報告 L51「包場夜打烊後店員還是可以留下的吧 只要看你需要的店員那天有沒有上班」 | |
| T06 | L253「從工作開始」不拍照 | A† | cb3470f「多的不用圖」 | |

### §8 員工
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| E01 | L259 三種職種各自的名額 | A | §21 | |
| E02 | L260–261 舊員工全部留下；請了就沒有解雇 | A（細節 B） | 22:39「員工如果請了就不要再有解雇的選項了」；§23 | |
| E03 | L262 Lounge 名單分開 | A | §22；`staff_pools_1907` | |

### §9 故事與寫作
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| N01 | L268–269 不是 quest list；暫停與恢復 | A | `story_presentation_1032`；qing_tuo #33 | |
| N02 | L270 三層 | A | `implementation_pass` D | |
| N03 | L271–274 不說破情緒；不要全知心理師 | A | 「Do not make every NPC an emotionally omniscient therapist.」 | 「原來幸福就是這麼簡單。」「一路走來真的不容易。」是加的例子 |
| N04 | L275 台詞守則 | A | `v23/qa4` | |
| N05 | L277–279 玩家的圖一定停店 | A | 「有跳出我生成圖片的畫面的劇情 都是要 停止餐廳營業 玩家手動按才繼續 避免玩家沒注意到」 | |
| N06 | L279–280 故事以外拍到的 Story Photo 也停；只有頭像的台詞不算 | C | 同 N05；「聯名酒沒有跳照片」 | → WS8-07 |
| N07 | L282–284 照片是發生過的證據 | A | `implementation_pass` P | |
| N08 | L285–286 Day 1 的照片 | A | `life_album_first_photo` | |
| N09 | L288–289 圖片清單；遊戲裡留位置 | A（細節 B） | 22:01；22:13；19:20 | 4:3 ≥1440×1080 是實作；清單本身寫 1448×1086 |

### §10 測試、存檔、發布
| # | 規則 | 類 | 來源 | 備註 |
|---|---|---|---|---|
| X01 | L295–296 不為了讓測試變綠而改 gameplay | A（細節 B） | #1「目標不是把測試硬弄綠」 | |
| X02 | L297 bot 不是真人 | B | 經驗 | |
| X03 | L298–299 不要 seed-hunt | B | 經驗 | |
| X04 | L300 normal play 是最後的判斷 | A | `rc6_final_spec` | |
| X05 | L302–305 存檔；不要用文字框複製 | A | `testing_strategy`；§23；21:20、21:21 | |
| X06 | L307–313 店主手冊 | A†（細節 B） | acd1d28；d1dbbda；abc9d38 | |
| X07 | L316–317 Publish ≠ Progress | A | 10:16、10:34 | |
| X08 | L318 永遠不跳過測試 | A | 22:20；22:22「這個不能跳過任何測試的規定應該要永久記憶。」 | 後半句見 P08 |
| X09 | L319 讀回、live_check | B | 流程 | |
| X10 | L320 不打 zip | A† | 139bc68 | |
| X11 | L322–325 Git branch（兩個引號） | D | 哪裡都找不到 | |

### §11 已改掉的舊規則
| # | 舊 → 新 | 類 | 來源 |
|---|---|---|---|
| O01 | 1 個 major → 2／2／3 | A | 同 S01 |
| O02 | 第一份一定 Jill 做 → 有廚師就不用 | A | 同 J02 |
| O03 | 沒有廚師的站全部 Jill 做 → 別站廚師幫忙 | C | 同 J04 |
| O04 | 打烊在沙發 → 在主廳 | A† | 同 J05 |
| O05 | 共用名額 → 三種，Lounge 另一份 | A | §21–22 |
| O06 | Lounge 是一個房間 → 隔壁的店 | A | §0 |
| O07 | Evan 招募 → 從不招募 | A | 10:32 |
| O08 | 《今天喝？》舊台詞 | A | §18；18:53 §九 |
| O09 | 《講完》舊稿 | A | 修訂版第五幕 |
| O10 | 贊助 $20,000 → 借 $3,000 | A | 21:57「只要你的錢超過20,000結算的時候就自動還錢」；21:58「首日贊助不用」 |
| O11 | 新網址 | D | ec985d1 沒有引玩家的話 |
| O12 | 不打 zip | A† | 139bc68 |
| O13 | `wip/lin` → `main` | D | 同 X11 |
| O14 | 候位改到店門口 | A†（細節 B） | 「排隊的人可不可以改到店門口啊 在主廳好礙事」；「主廳長椅給貓」是實作 |
| O15 | PERFECT 橫幅 | A†（細節 B） | 「可以不要一直跳出perfect擋住選區嗎」 |
| O16 | 秀琴的閒聊 6 次 → 每人 3 次 | B | b443ab5（修 bug）→ WS8-06 |
| O17 | ♥ 只給 Sophie 和 Mia | A | 「B. 愛心只給 Sophie 和 Mia；熟客不再有任何記號。」 |

### §12
| # | 規則 | 類 | 來源 |
|---|---|---|---|
| Z01 | L355 予安「固定一週三晚」 | B | QING_TUO 報告 "not asked for in a brief" → WS8-14 |
| Z02 | L355–356 開店前不能選 | A† | 6ddd455「予安班表不能選好了」 |

## 1b. 其他文件

**CLAUDE.md**
| 列 | 規則 | 類 | 來源／備註 |
|---|---|---|---|
| CL01 | L6 先想是不是 regression | D | |
| CL02 | L13 只用繁體中文 | C | → WS8-12 |
| CL03 | L14–18 回報用白話繁中（引號） | D | 引號只在 CLAUDE.md 自己裡面 |
| CL04 | L19–20 發布節奏 | A＋D | 批次發布是 10:16／10:34；其他找不到 |
| CL05 | L21 | A | |
| CL06 | L22 | A | |
| CL07 | L23–24 branch | D | |
| CL08 | L25 | A | |
| CL09 | L26 | A† | |
| CL10 | L27 | A | |
| CL11 | L28 hard canon | D | |
| CL12 | L30 | D | |

**CURRENT_STATE.md**
| 列 | 規則 | 類 | 來源／備註 |
|---|---|---|---|
| CS01 | L3 | B | |
| CS02 | L11–12「發布的 commit 一定在 main 上」 | D | |
| CS03 | L38–39 新網址 | D | |
| CS04 | L48「帽子照玩家 10/3 的話一直戴著」 | A | 跟 PM L149 矛盾 |
| CS05 | L68–69 「♥ 陳伯伯」 | A | |
| CS06 | L70 不要用文字框複製 | A | |

**ARCHITECTURE.md**
| 列 | 規則 | 類 | 來源／備註 |
|---|---|---|---|
| AR01 | L60 工程守則 | B | |
| AR02 | L72 工程守則 | B | |
| AR03 | L75「廚師只做 Jill 已經做過至少一次的菜（`S.xp[d]>0`）…（招牌菜永遠除外）」 | B | 過時 → WS8-D2 |
| AR04 | L78 | B | |
| AR05 | L80–85 門口長椅等位 | B | 過時 → WS8-D3 |
| AR06 | L89–91 | B | |
| AR07 | L98 貓咪世界規則 | A | |
| AR08 | L102 不加數值 | A | |
| AR09 | L103 Dylan 的階段不在 UI 顯示 | D | |
| AR10 | L114–126 兩個名單 | A | |

**LIFE_SYSTEM.md**
| 列 | 規則 | 類 | 來源／備註 |
|---|---|---|---|
| LS01 | L9 | B | |
| LS02 | L11「營業中玩家永遠優先…營業中 Jill 完全由原本的服務邏輯控制」 | B | 過時 |
| LS03 | L12 不新增數值 | A | |
| LS04 | L35 85% 沙發 | B | 過時 |
| LS05 | L95–98 Dylan 是從外面來的熟客 | B | 前提過時 |
| LS06 | L100 長椅 | B | 過時 |
| LS07 | L101 不是員工 | B | |
| LS08 | L109 長椅與貓 | B | 過時 |

**V24 報告裡的 canon 說法**
| 列 | 說法 | 類 | 來源／備註 |
|---|---|---|---|
| RP01 | RC4 L15 秀琴 canon change | A | |
| RP02 | RC4 L24「canon from the code」 | B | 沒有進 PM |
| RP03 | RC5 L93／L196 參考圖裡的貓不是 canon | A | 「The supplied image is a CONCEPT reference, not permission to alter cat identities.」 |
| RP04 | RC7_3 L60 | A | |
| RP05 | RC7_5 L50「Jill has several cameras」 | A | 「她本來就有多台拍立得」 |
| RP06 | QING_TUO L4「the handover」「phase 3 canon」 | D | |
| RP07 | QING_TUO L11–16 | A | |
| RP08 | RC8_2 L15「不寫他的名字」 | B | |
| RP09 | Checkpoint C L25「先生」 | B | |

## 2. 需要 Dylan 決定

### WS8-01 [CANON] Medium PROJECT_MEMORY 把「帽子一直戴著」縮成「揭曉前」，還加了「灰色」；main 上兩份文件互相矛盾
- 在哪裡：
  - PM §4 L149；
  - CURRENT_STATE L48；
  - Jill 的房間（Day 89 04:48 存檔，已揭曉，390 寬）。
- 怎麼重現（玩家動作）：
  1. 讀存檔，標題按「繼續營業 · 18:59」。
  2. 點分頁「Jill 的房間」，看書桌前的 Dylan。
  3. 對照 PM L149 與 CURRENT_STATE L48。
- 看到什麼／應該是什麼：
  - PM：「揭曉前他在房間裡穿灰色帽 T、帽子一直戴著，讓玩家看不出是他。」
  - 玩家 07:44：「在房間Dylan就穿帽T一直戴著帽T帽子吧」。
  - 玩家 07:13：「Dylan在書房的時候有辦法讓玩家看不出來他是Dylan嗎？就比較宅的樣子頭像一樣穿搭不同？不然揭曉前就知道了」。這說明了用意，但 07:44 的指示是「一直」。
  - 程式：4112608；`DYLAN_HOME`（game.js L8835）`hoodUp:true`，揭曉前後一樣。截圖裡揭曉後帽子戴著。
  - CURRENT_STATE L48：「帽子照玩家 10/3 的話一直戴著」。
  - 「灰色」來自實作的顏色，以及 Claude 寫的圖片清單「灰色連帽衫、耳機」。
- 證據：
  - `shots/r04_room_1.png`、`r04_canvas_1.png`、`r05_desk_crop.png`；
  - `S.dylan.stage`＝3（觀察）；
  - `git log -S'灰色帽'` → 9cb384f；
  - 09f3312（feature/dylan-room）改成「揭曉前、揭曉後都一樣」，還沒合回 main。
- 確定程度：已用 UI 重現。
- Dylan 玩幾分鐘內會不會注意到：不會。但照 PM 做事的 agent 會在揭曉後把帽子拿掉。
- 備註：
  - 玩家的存檔在 Day 69 揭曉，所以 07:44 時玩家玩的是揭曉後的遊戲。
  - 需要 Dylan 決定：揭曉後帽子要不要戴？顏色算不算 canon？
  - 較窄的寫法：「在房間裡穿帽 T、帽子一直戴著（07:44）」。

### WS8-02 [CANON] Medium 「房間裡不寫他的名字（揭曉前也一樣）」是實作的選擇，main 還留著
- 在哪裡：PM §3 L117；rc8.2 報告 L15；Jill 的房間。
- 怎麼重現（玩家動作）：同 WS8-01，看他頭上有沒有名字。
- 看到什麼／應該是什麼：
  - 出處是 ec17365 的 commit 訊息 "no name on him (before the reveal too)"。
  - 玩家那次的原話裡沒有講名字。
  - 玩家 2026-10-05（只在 feature/dylan-room）：「Dylan已經揭露但在房間還是沒寫Dylan」。
  - main 的遊戲：揭曉後他頭上沒有名字，分頁寫「Jill 的房間」。這是已知的待辦，這裡只報文件的部分。
- 證據：
  - `shots/r05_desk_crop.png`；
  - `git log -S'揭曉前也一樣'` → ec17365；
  - 09f3312 自己寫 "the implementation's choice, not the player's"。
- 確定程度：已用 UI 重現。
- Dylan 玩幾分鐘內會不會注意到：會（已經回報過）。
- 備註：
  - branch 的修正同時把分頁「Jill 和 Dylan 的房間」寫進 PM，這是 C。
  - 玩家 18:53 說過：「名稱可以依現有 UI 命名方式微調，但玩家理解上就是 Jill 與 Dylan 的私人房間」。
  - 需要 Dylan 決定：合回 main 時，這兩句要不要算 canon。

### WS8-03 [CANON] Medium 「揭曉前…畫面上也不能出現他的頭像」比玩家說的寬，跟現有設計衝突
- 在哪裡：PM §4 L151；餐廳日誌 › 熟客（Day 67 存檔，揭曉前，stage 2）。
- 怎麼重現（玩家動作）：標題 → 「餐廳日誌」→「熟客」→ 找到 Dylan。
- 看到什麼／應該是什麼：
  - PM：「揭曉前，畫到 Dylan 的圖不能露臉（背影或不露臉）；畫面上也不能出現他的頭像。」
  - 玩家只講過 Day 1：「我發現dylan第一天就露臉了」「第一天就寫jill先生但不露臉」（acd1d28）。
  - 「背影」的要求來自 Claude 寫的圖片清單。
  - 遊戲從 V16 起，揭曉前他就是有頭像的熟客：熟客頁是「Dylan · Jill 的老客人」，營業中他說話也帶頭像（game.js L1828）。
  - 照字面做，會把熟客 Dylan 的頭像拿掉。
- 證據：`shots/j02_regulars_dylan_day67_before_reveal.png`。
- 確定程度：已用 UI 確認。
- Dylan 玩幾分鐘內會不會注意到：不會。
- 備註：
  - 較窄的寫法：「以『先生』身分出現的他（房間、Day 1 照片、插圖）不露臉；熟客 Dylan 照舊」。
  - 需要 Dylan 決定。

### WS8-04 [CANON] Low 「揭曉前名牌、旁白叫『先生』」是 Checkpoint B 的實作
- 在哪裡：PM §4 L149。
- 看到什麼：
  - 出處是 4a1a9b2 "Before Dylan's reveal the panel calls him 「先生」" 與 Checkpoint C 報告 L25。
  - 玩家只為 Day 1 說過「第一天就寫jill先生」。
  - main 的房間沒有任何名牌；`dyHomeTag` 只在 branch 上。
- 備註：需要 Dylan 決定稱呼。

### WS8-05 [CANON][DESIGN] — 「別站的廚師過去接」
- 在哪裡：PM §3 L108；§11；`chefCover`（game.js L5101）。
- 看到什麼：
  - 玩家：#4「第一次做的菜是她要做 其他時候廚師都可以自己接手」；#7「…有廚師她就不用做」。
  - 跨站支援是延伸。較窄的讀法：那一站有廚師，Jill 就不用做。
  - CURRENT_STATE L85 已經把「會不會讓雇人變得不重要」列為要玩家玩過才知道的事。
- 備註：需要 Dylan 決定。

### WS8-06 [CANON] Medium PM 的「誰可以改」讓實作決定進入 canon；§11 混了實作修正
- 在哪裡：PM L11–13；PM §11；CLAUDE.md L28。
- 看到什麼：
  - 「不看歷史很容易猜錯的、曾經刻意從舊設計改掉的」不需要玩家同意。
  - L11 的兩個引號找不到出處。
  - 同一段要求「附上日期和原話」，但 B＋D 有 37 列沒有原話。
  - 「看到就不要再改回去」的表裡有 B（秀琴 3+3）、C（廚師跨站支援）、D（網址、branch）。
  - 玩家 10-06：「不要因為你覺得某個做法比較好，就直接把它變成 PROJECT_MEMORY 的規則。」
- 備註：需要 Dylan 決定：PM 是否只收你的決定，實作另外標明。

### WS8-07 [CANON] Low 圖片停店延伸到故事以外的 Story Photo
- 在哪裡：PM §9 L279–280；9b0b5f6。
- 看到什麼：
  - 玩家說的是「有跳出我生成圖片的畫面的劇情」。
  - 「故事以外拍到也停店」「只有頭像的台詞不算」是加的。
  - 可能跟同一晚的「聯名酒沒有跳照片」有關。
- 備註：需要 Dylan 決定。

### WS8-08 [CANON] Low 包場夜不排 Lounge 故事：從一次推廣成全部
- 在哪裡：PM §2 L85–86；對照 §7 L252。
- 看到什麼：
  - 修法原本只針對予安試彈（cb3470f）。
  - §7 有玩家允許打烊後的幾幕在包場夜發生。
- 備註：需要 Dylan 決定範圍。

### WS8-09 [CANON] Low Madame Lin 線的天數與門鈴寫成 canon
- 在哪裡：PM §6 L200、202、205、207、214、215。
- 看到什麼：
  - 「一天一步」「一週以上」「12 天」「兩天」「改裝兩天」「5 天以上」「門鈴」都是實作。
  - 玩家說的是「一段時間」「幾天後」「開幕一段時間後」「小植物、小型實用物、簡單開店禮」。
- 備註：需要 Dylan 決定：這些是 canon，還是可以調。

### WS8-10 [CANON] Medium 「只改測試的修正，重跑那幾項即可」是玩家沒給的例外
- 在哪裡：PM L39、L318。
- 看到什麼：
  - 玩家 22:20、22:22 說不能跳過任何測試。
  - `testing_strategy` §7 寫「最終再確認完整 release regression」。
  - rc8 用過這個例外（8f7d6b2 "tests only; the game is 252ff1c's"）。
- 備註：需要 Dylan 決定。

### WS8-11 [CANON] Low 檢查劇情節奏的順序被倒過來
- 在哪裡：PM §2 L94–95。
- 看到什麼：玩家 #8 要先確認 scheduler，而且不要硬調 trigger/cooldown；PM 從那一次的結果歸納出相反的順序。
- 備註：需要 Dylan 決定。

### WS8-12 [CANON] Low 「只用繁體中文」擴大了範圍
- 在哪裡：PM L53；CLAUDE.md L13。
- 看到什麼：
  - 玩家 15:08：「遊戲內請勿出現簡體中文 一切都是繁體中文 名子可以英文」。
  - CLAUDE.md 引的 10-03 原話是「以繁體中文為主」，而且沒歸檔。
  - 報告和 commit 實際上多半是英文。
- 備註：需要 Dylan 決定。

### WS8-13 [CANON] Low 找不到來源的方向句
- 在哪裡：
  - §1 L61–75；
  - §3 L119–122、L126；
  - §4 L146 的「不是 avatar」；
  - §4 L149 的「不要神秘兮兮」。
- 看到什麼：這些句子都標成玩家的方向，但找不到原話；也沒有發現跟玩家原話衝突。
- 備註：需要 Dylan 確認。

### WS8-14 [CANON] Low 予安「固定一週三晚」
- 在哪裡：PM §12 L355。
- 看到什麼：玩家只說「予安班表不能選好了」。「三晚」是 rc8 的實作。
- 備註：需要 Dylan 決定。

## 3. [DOC]

### WS8-D1 [DOC] Medium 玩家原話只在 commit 或報告裡
- 在哪裡：`docs/RELEASE_CHECKLIST.md` §1 要求逐字歸檔到 `docs/vNN/`。
- 看到什麼：
  - 17 列 A† 的原話只在這些地方：25a0710、ec17365、6ddd455、acd1d28、d1dbbda、abc9d38、b196ee3、252ff1c、cb3470f、b6be7c2、25d53f8、139bc68，以及 rc8.3、rc8.4、QING_TUO 報告。
  - b6be7c2 的原話：「第81天Dylan情人節去酒吧欸 他第一次去酒吧的故事都還沒開始前他不能去酒吧」。
  - CLAUDE.md L14–15 與 PM L322 的引號哪裡都找不到。

### WS8-D2 [DOC] Low ARCHITECTURE L75 的廚師規則過時
- 看到什麼：`chefCan` 不再看 `S.xp`，招牌菜要 LV5。

### WS8-D3 [DOC] Low 等位長椅的說明過時
- 在哪裡：ARCHITECTURE L80–85；LIFE_SYSTEM L100、L109。
- 看到什麼：rc8.3 起客人在店門口外面等（`pickSpot` 用 `QOUT`，game.js L765）。

### WS8-D4 [DOC] Low LIFE_SYSTEM 過時
- 在哪裡：LIFE_SYSTEM L11、L95–98；ARCHITECTURE L17。
- 看到什麼：
  - L11 的絕對句已過時。
  - L95–98 的前提是 Dylan 從外面來。玩家 18:53：「不要再把 Dylan 預設成：「從外面來餐廳的人。」」。
  - 開頭的警告只點名沙發；ARCHITECTURE L17 還把 Dylan 的規則指到這份文件。

### WS8-D5 [DOC] Low 報告引用了 repo 裡沒有的來源
- 看到什麼：QING_TUO 報告的「handover」「phase 3 canon」，以及 PM 的「4B」，在 repo 裡都找不到。

## 4. 統計

PM 共 130 列：

| 類 | 列數 | 說明 |
|---|---|---|
| A | 85 | 68 列原話已歸檔，17 列 A†；其中 16 列是 A（細節 B） |
| B | 22 | |
| C | 8 | P08、P14、S08、J04、W10、W12、N06、O03 |
| D | 15 | |

依節：

| 節 | A | B | C | D |
|---|---|---|---|---|
| §0 | 6 | 2 | 2 | 4 |
| §1 | 0 | 0 | 0 | 4 |
| §2 | 6 | 1 | 1 | 0 |
| §3 | 6 | 3 | 1 | 2 |
| §4 | 10 | 1 | 2 | 2 |
| §5 | 7 | 1 | 0 | 0 |
| §6 加 Ken | 12 | 9 | 0 | 0 |
| §7 | 6 | 0 | 0 | 0 |
| §8 | 3 | 0 | 0 | 0 |
| §9 | 8 | 0 | 1 | 0 |
| §10 | 7 | 3 | 0 | 1 |
| §11 | 13 | 1 | 1 | 2 |
| §12 | 1 | 1 | 0 | 0 |

其他文件：

| 文件 | A | B | C | D |
|---|---|---|---|---|
| CLAUDE.md | 6 | 0 | 1 | 6 |
| CURRENT_STATE | 3 | 1 | 0 | 2 |
| ARCHITECTURE | 3 | 6 | 0 | 1 |
| LIFE_SYSTEM | 1 | 7 | 0 | 0 |
| 報告 | 5 | 3 | 0 | 1 |

**絕對字眼**
- 玩家自己說的：
  - 「一定暫停營業」
  - 「從不招募」
  - 「不可以跳過任何測試」
  - 「每張只在對應場次首次出現」
  - 「Staff Room 就必須已經存在」
  - 「只有 Sophie 和 Mia」
  - 「T 不能寫成 O」
- 加上去的：
  - 「揭曉前」（W08、W10、W12、L14）
  - 「揭曉前也一樣」（J08）
  - 對包包的「永遠偷不成功」
  - 「一天最多推進一步」
  - 「固定一週三晚」
  - 「只用繁體中文…文件、回覆」
  - 「打烊時一定起身」
  - 「只有頭像的台詞不算」
  - 「值得寫進來的只有三種」
  - 「發布的 commit 一定在 main 上」
- 已過時的：
  - LIFE_SYSTEM「營業中玩家永遠優先」
  - ARCHITECTURE「招牌菜永遠除外」

## 5. 沒問題的、沒能查的
- 沒問題：
  - §5–§8；
  - Madame Lin 線的順序；
  - 晴×阿拓；
  - 員工名單；
  - 照片是證據；
  - 圖片停店；
  - 存檔不重置；
  - 發布規則；
  - zip；
  - ♥；
  - 借錢。
- AUDIT_AND_PLAN 的「canon from the code」沒有進 PM。
- 沒能查：
  - 10-03 要求建立 project memory 的那則訊息；
  - handover；
  - phase 3 canon；
  - v2.2 以前的貓咪設定。
- 給整個稽核：Dylan 在 Day 69 揭曉。day71 以後的存檔都已經揭曉；揭曉前的存檔是 day2、day52、day61、day65、day67、day68。