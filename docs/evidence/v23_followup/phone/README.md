# v2.3 follow-up — phone screenshots on the final code (2026-10-01)

All shots are 390×844, headless Chromium, on f12b94f (the code published as v2.3-rc2). They are T evidence, not O.

The player's Day 52 save is loaded in one of two ways, and each shot below says which:

- **loader**: the test loader. It puts only the save into the browser, so the album's pictures are missing.
- **import**: the game's own 設定 → 讀取存檔, which also brings the album's pictures.

| File | What it shows | Save loaded with |
|---|---|---|
| `r_shop_tabs.png` | The shop after closing (DAY 52), its tabs: 家具與佈置, 店舖工程, 社群與宣傳, 貓咪生活… | loader |
| `r_prep.png` | DAY 53 prep, with the 社群與宣傳 line (「大家在談：南瓜濃湯」 · 今天可以發 3 則) | loader |
| `r_main_dusk.png` | Service at dusk. The room tabs sit under the ticket rail, not over the top row of tables. The story note sits under the tabs: 故事更新 · Dylan 「還在追喔？」 13 / 17 | loader, seed 7, lazy bot |
| `r_journal_social_service.png` | The journal's 社群 page during service (read-only): what people talk about, Jill's three candidates with their pictures, recent posts | import |
| `r_cushion_two.png`, `r_cushion_swap.png` | Two cats side by side on the cushion. Then one leaves and another comes; still side by side, not stacked. Shot after the opening banner and after the album camera's flash | import |
| `campaign_ticket.png` | A cat campaign day: 📱 on a campaign guest's ticket; guests looking for the cats | loader |
| `s_story_0.png` … `s_story_3.png` | The journal's 故事 page, top to bottom: 餐廳故事 (numbered, 更早以前, 「？？？」), then 人物／關係支線 (Ken 1 / 9, Dylan 12 / 17, 王家 1 / 2, 小林 2 / 3, 李先生 1 / 1, …, 「還有 7 段故事還沒開始」) | loader |
| `s_story_detail.png` | One Dylan stage opened to the words said at the time | loader |
| `staff_0.png` … `staff_3.png` | The staff page: work assignment, then the cards with the redrawn portraits | loader |
| `staff_line.png` | A staff line in service with the redrawn portrait (Hugo 「油比較熱。」) | loader |
| `regulars_sophie.png`, `regulars_mia.png` | The journal's 熟客 page with the new Sophie / Mia portraits. Each regular quotes the habit line their tier has unlocked: no 「undefined」. Leo has no quote | import |
| `regcard_sophie.png`, `regcard_mia.png` | Their cards in service (DAY 53) with the new portraits | import |
| `album_new_art.png` | The album with the replaced Story Photos (有你在的晚班, 固定的位置, 一起回家) beside the game's own photos | import |
| `lightbox_*.png` | Each replaced Story Photo full size: 多的, 有你在的晚班, 一起回家, 固定的位置, 還是沒有同意 | import |
| `manual_rooms.png` | The manual: 開店與料理 → 房間 (the tabs under the ticket rail) | loader |
| `manual_story.png`, `manual_social.png` | The manual's 故事 and 社群與宣傳 sections, opened | loader |

In the album shots, the photos were taken with `storyPhoto` on DAY 48–52 so that all five pictures appear. The save
itself has not reached those moments yet.
