# v2.3 late game (rc3) — phone screenshots (2026-10-01)

Headless Chromium. The live side-room shots are on the release code (10456ea); the kitchen and street shots on f6f856d;
the placed window shots and the shop shots on b11c328 — the two later commits (the compact COMBO pill, the window's pull)
show on none of those. The player's Day 52 save 
(`tests/saves/player_day52.json`) loaded with the test loader, 390×844 unless the file name says otherwise. They are
**T** evidence (the code does this on a phone-sized screen), not **O** (nobody has seen it on the player's iPhone yet).

"Placed" means the script put cats on the window places to show each step; "live" means a lazy evening ran and the
cats went wherever they chose.

| File | What it shows | How |
|---|---|---|
| `side_booths_0.png` | The side room in service as the save has it: the back row four-top booths, six two-tops in front | live, seed 9102, 150 s |
| `side_booths_1.png` | After 側廳卡座 「中間那排」: two rows of booths, the front row still two-tops | live, 150 s |
| `side_live_60s.png`, `side_live_150s.png`, `side_live_240s.png` | 側廳卡座 both rows and the whole window line, one evening at 60 / 150 / 240 s: at 60 s 小齁 sits on the low step; at 150 s 寶寶 is in the tunnel (not on the window) and the side room is full; at 240 s 寶寶 is in the hammock — under the 故事更新 note (小林 「你哪次不是這個？」 3 / 3), which sits under the room tabs over the window's middle. In play the note hides after 7 s; the test bot runs the evening faster than the note's timer, so it stays on these shots. The compact COMBO pill sits right of the window seat | live |
| `booth_card.png` | 家具與佈置: 側廳的桌子 (its text now points to 側廳卡座), then 側廳卡座 ●○○ with 「換中間那排 $18,000」 | shop after closing |
| `booth_reveal.png` | The reveal: 完工 · 側廳卡座：中間那排 · Jill「三個人來，也有地方坐了。」 · 現在可以：側廳中間那排：三張四人卡座 · 去看看 / 繼續買東西 (shot mid fade-in) | shop |
| `booth_peek.png` | 去看看: the side room with the middle row changed, the banner under the tabs | shop → peek |
| `side_window_t1_390x844.png` … `side_window_t5_390x844.png` | The window at each step, cats placed on the places that step adds (at most three on the window plus the 窗邊貓架, none overlapping): 1 窗邊貓架 · 2 軟墊窗台 · 3 多層窗邊步道 · 4 窗邊吊床 · 5 多貓觀景平台 | placed, service |
| `side_window_t1_375x667.png` … `t5` | The same on an iPhone SE-sized screen: every cat clear of the room tabs and the 庫存 / 今日任務 chips | placed |
| `win_card_t1.png`, `win_card_t5.png` | 貓咪生活 → 側廳的大窗: at step 1 (用過的 …, next step and price) and at step 5 (all five pips, 整面窗都是牠們的了。) | shop |
| `win_reveal_t2.png`, `win_reveal_t5.png` | The reveals for 軟墊窗台 and 多貓觀景平台 (shot mid fade-in) | shop |
| `shop_kitchen_works_390.png`, `shop_kitchen_works_done_390.png` | The kitchen tab's 後場工程, before and after buying 走入式冷藏庫 and 廚房二期 | shop |
| `reveal_walkin_390.png`, `reveal_kitchen2_390.png` | Their reveals | shop |
| `kitchen_k2_390.png` | The next evening's kitchen: the walk-in door bottom left (庫存 311/400), two coffee machines top right, the COMBO pill compact | live |
| `front_house.png`, `front_walkers.png` | The street: the dog's house by the door; five walkers with five kinds of dog | live / placed walkers |
| `house_*_lie/sit/drink.png`, `house_sheet.png` | Each of the five dogs at the house: lying, sitting up, drinking | placed pose |

Not hidden: the clock in the top bar reads 17:00 in the live side-room shots although they are 60–240 s into the
evening — the test bot advances the game without redrawing the top bar's clock; the canvas is current.
