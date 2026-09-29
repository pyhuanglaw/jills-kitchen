# v2.2 performance — before / after (headless Chromium, software rasterization)

Method: `scratchpad/perf22.py` — the player's Day 30 save, a full fridge, the perfect bot, 6000 frames (≈ 200 s of
game time) into the service so the room is busy, then 3 × 300 frames timed from Python (manual RAF: one `__tick` =
one full frame, sim + draw; the RPC overhead is identical for both builds; the minimum of three runs). `draw_only`
re-draws the scene without advancing the simulation. The baseline is the v2.1 single file (`git show
v2.1:jills-kitchen-single-file.html`), the candidate the v2.2 single file. Headless Chromium rasterizes the canvas in
software, so the absolute numbers are far above what a phone or desktop GPU produces — only the ratio matters, and
nothing here was run on a real device.

| viewport | build | canvas (px) | groups in the room | ms / frame | ms / draw only | JS heap |
|---|---|---|---|---|---|---|
| phone 390×800 | v2.1 | 390×751 | 18 | 21.9 | 21.4 | 26 MB |
| phone 390×800 | v2.2 | 390×751 | 11 | 19.7 | 20.2 | 30 MB |
| desktop 1440×900 | v2.1 (540 px column) | 540×851 | 16 | 30.2 | 30.9 | 22 MB |
| desktop 1440×900 | v2.2 (X: the column is the room) | 1121×849 | 8 | 38.2 | 43.1 | 15 MB |

Reading: on the phone the frame cost is unchanged within noise (the group counts differ because the day's schedule
differs — Dylan's presence, the two Wangs). Drawing dominates; the simulation is a small fraction. On the desktop the
v2.2 canvas has 2.1× the pixels of the old column and costs 1.26× per frame — the draw cost grows sub-linearly with the
area. To keep a 2× display from drawing the room at 2242 px wide, `layoutAll` caps the backing store at ≈ 1600 px
(`DPR = min(2, devicePixelRatio, 1600 / width)`); phones keep their 2×.

The 802 KB of portrait data (`js/portraits.js`, WebP data URIs) is decoded lazily by the browser when a card first
shows a face; it is not in the frame loop. Single file: 1,587 KB (v2.1: 699 KB).
