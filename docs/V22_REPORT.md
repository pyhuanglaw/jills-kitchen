# Jill's Kitchen 2.2 — UX, presence and faces: release report (2026-09-30)

## 1. Versions
- Artifact https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps — **Version 32**, label "2.2" (Version 31 = "2.2 UX
  checkpoint" = `511f237`; Version 30 = 2.1). Single file `jills-kitchen-single-file.html` (1,587 KB — the portraits
  are inlined as WebP data URIs, 802 KB).
- Repo: `v2.1` / `stable-v2.1` = `da79864` (preserved). `v2.2-ux-stable` = `511f237` (A–E + O, the checkpoint gate).
  **`v2.2` (annotated tag) = `962b494`**, the QA commit: goldens, docs, single file — the code published as Version 32.
  Commits after the checkpoint, in order: F+G `9fec026`, Dylan presence + H `c5dcb11`, I/K/T + fridge invariant
  `78b6195`, J `4498e37`, L/M/N `53f3e1c`, I+ art direction `75aeb75`, Dylan audit evidence `566c2a1`, P `ffc8591`,
  Q portraits `e17b79a`, Q+ sprites `c43ed2a`, R storefront `2fbf683`, U+V+W+X `f0aca88`, V++ two Wangs `87a1a15`,
  Q++ Jill/Dylan as character translations `de74ba6`, QA `962b494`. A docs-only commit after the tag pins these
  numbers (no code change; the published page and the single file are `962b494`).
- The reconciliation checklist is `docs/V22_QUEUE.md` (every item of the brief and of every later message with
  DONE / PARTIAL / DEFERRED / BLOCKED / NOT STARTED). This report copies its conclusions; the queue file is the source.

## 2. What the player sees
- **Stability (A1–A5)**: the restock suggestion holds still for the day and a failed purchase changes nothing and says
  why; the game never buys stock for the player and money never goes negative (a payroll shortfall is recorded in
  `wageOwed`, nothing else); the pause menu and every sheet fit a short phone (scroll instead of loss); the album opens
  without a render storm and progress survives a kill (checkpoint on `visibilitychange`/`pagehide`); money is one number
  on every screen (the side hall and the summary included).
- **Management**: staff grouped by job; restock +1 / 建議 / 補滿 within the fridge and the money; service speed
  0.75/1/1.5/2× coherent (hand timing capped at 1.5× real time on Jill's own tray); the rating card in a hierarchy with
  the records as chips; the scroll position kept on local edits; set-menu sales on the summary and the 餐廳 tab; the
  weather recommendation's one-tap 加入今日菜單 when a slot is free (a full menu is told, nothing removed silently).
- **Shop**: 家具與佈置 / 店舖工程 / 貓咪生活 (+ the existing kitchen / menu / staff / signature tabs); the cats' things in
  tiers (基本 / 舒適 / 豪華); the three dreams (glass front $100k, wooden ceiling and fans $180k, the catwalk $300k) with
  their own horizons and effects in the room.
- **Dining room**: quiet luxury — oatmeal booths on walnut with one brass line, a greige rug, charcoal-and-oatmeal tier-2
  chairs, muted clay pots; art under the sign, plants and lamps inside the phone's view; the old kitchen strip reduced to
  the bus tub, the bell and the stock board under the heat-lamp rail. Cats on the catwalk and at the grass pot.
- **Jill and Dylan in the world (Q+/Q++)**: a character translation of the portraits into the game's cute language —
  masses that survive at phone scale. Jill is the owner who cooks and serves, not staff: her own cream linen shirt with
  the sleeves rolled to the elbow, khaki trousers, a natural-linen half apron with the cat patch, the long dark ponytail
  over her shoulder, the straight fringe, earrings, a bright face — the light warm figure in a room of darker clothes;
  no uniform white, no bib, no black trousers, no toque, no name label anywhere. Dylan: a thick tousled crop (a style
  that is his alone), strong brows, a long dark-navy cardigan over a white tee, a watch, a cat mug when he sits; his
  floor name shows only for a moment after a tap or a line. Guests and crew never get her tail, his crop, a white top,
  a white tee under a cardigan, her shirt or her trousers. Verified in the Day 30 room with 13 parties and staff on the
  floor and at the pass beside four chefs (`docs/evidence/v22_art/sprites_q2_*.png`). 王先生 (glasses, brown jacket
  over light blue) and 王太太 (brown bob, pink cardigan) are two people at one table.
- **Storefront**: warm plaster and stone with a brass line, the dining room visible through the windows (a cat on the sill
  inside), stone flags that hold puddles in the rain, light on the pavement at dusk; the glass front is one wide window.
- **Faces**: the supplied portraits appear at the morning remark, the expansion, the construction card, the quiet
  reveal, every Jill/Dylan exchange during service (a card with both faces, the speaker lit), every regular's line (their
  own face, the person they answer beside them), and in the 熟客 page; six staff faces by role and hiring order; a
  fallback to the plain presentation when assets are absent.
- **Dylan**: he is around most days (schedule .6/.55/.85/.97), comes back later in the same day when the room was full
  (up to four tries, no queue jumping, and a look in from the door once he is someone you know), orders his usual and
  Jill sometimes already knows it, says one line per visit whether or not she is idle (a word when she is busy), the
  regulars notice him now and then; the clues accumulate in kinds (usual, look, noticed, knows, tidy, pet, pause);
  Stage 2 eligibility and the reveal are untouched; his floor name shows only for a moment after a tap or a line.
- **Reviews and lines**: a review names a cat only when that table met one, doing what it was actually doing; every
  dialogue pool cycles (a 48-line session ring + 60 lines in the save) and reviews are checked against the book.
- **Hospitality**: Jill's Card (every fifth visit a dessert on the house), the player's 招待 chip on a ticket (two a
  day), the anniversary treat.
- **World memory**: days later, a regular brings up the side room that opened, the record rainy day, the record day, the
  first special, a project, the expansion, the reveal — once, at most one a day, read from days the save already keeps.
- **Album**: the 相簿 reads forward as the restaurant's story — weeks, what happened that week, that week's photos, and
  today at the end (還在繼續); the lightbox walks the same order.
- **Desktop**: a window ≥ 900 px is not a 540 px column: the column is as wide as the room at that height (no dark
  bands), sheets stay a readable 720 px, the mouse cursor says what can be tapped, Space/Escape/Enter work, a resize
  mid-service re-lays everything out; below 900 px the phone layout is untouched.
- **Cooking**: the 2.1 choreography (vessel moves, colander, toss, rest-and-slice, sauce at the pass) merged onto the
  v2.2 hand timing.

## 3. Save compatibility
- The player's Day 30 save is the mature regression fixture only (nothing is keyed to it); it loads, plays two full days
  at normal speed on a touch phone viewport (smoke below), checkpoints and resumes mid-service (`a4b_`), and every save
  test passes (v1.6 / v1.7 / v1.8 / pre-2.0 Day-25 fixtures).
- New optional fields: `said`, `worldMem`, `worldMemDay`, `grewDay`, `firstSpecial` (2.1), `setHist`, `lastSummary.setSales`,
  `wageOwed`, `today.sugKey/sug`, `dylan.orders/doorDays/noticedDay`, `gear`/`gearUse` tiers, `newRooms.glass/ceiling/catwalk`,
  `wangMig`, `regulars.wangwife`, `regMem.wangwife`, `catFam.wangwife`. All filled by `fillDefaults` or on first use.
- One migration runs once: `legacyWang` — the old couple record `wang` becomes 王先生 (`wang`) and 王太太 (`wangwife`);
  she inherits the shared history (she was there for every counted visit), the solo-visit facts stay with the right
  person, `wangMig=1` stops it from running again (`mature_save_loads_into_2_0` asserts the record count grows by one
  and the two counts match; `wangs_are_…` asserts the split).
- Photos live in IndexedDB as before; a JSON fixture without the photo store shows empty frames (a fixture limit, noted
  on the album checkpoint).

## 4. Testing
- Lint: `npm run lint` — 0 errors.
- Full suite `python3 tests/run_tests.py` (index.html): **79 passed, 0 failed** on the final build (`docs/evidence/v22_suite_final.log`; 66 at the checkpoint gate, 13 v2.2 tests added after it).
- New v2.2 tests (in the suite): a1–a5 (+a4b), b, c, d, e, o, f, g, `dylan_is_a_presence_not_a_story_trigger`,
  h_i_k_t, j, l_m_n, q, q_plus, u_v, w, x, `wangs_are_two_people_who_usually_come_together`,
  `z_regression_rooms_kitchen_construction_and_staff_assignment`.
- Required regression coverage (24 items): restock suggestion stability ✔ · atomic restock ✔ · no auto-buy ✔ · money
  never negative ✔ · service → menu on a short phone ✔ · journal → album ✔ · money display across screens ✔ · staff
  grouping ✔ · speed coherence ✔ · rating card ✔ · scroll preservation ✔ · checkpoint round trip ✔ · Day 30 migration ✔
  (loads, plays, checkpoint; the final smoke) · weather reco add ✔ (N) · staff assignment ✔ (z) · set sales ✔ (M) ·
  review duplicate suppression ✔ (G) · cat-context review ✔ (F) · room navigation ✔ (z) · kitchen service ✔ (z, plus the
  2.0 kitchen tests) · mobile touch ✔ (touch contexts; `touch_controls`) · desktop resize ✔ (X) · album persistence ✔ ·
  construction ownership ✔ (z).
- Goldens: `golden_scenario`, `golden_frames`, `cat_personality_fingerprint` re-recorded once, after the RNG
  invariants were checked again on the final build (`docs/evidence/v22_rng_invariants.md`, last section) — the random
  sequence moved with every feature that draws from it (reviews, Dylan's schedule, the grass pot, treats, the two Wangs),
  the goldens are digests of a seeded Day 1, so they had to move; the invariants behind them did not.
- Normal-speed smoke on the Day 30 save (`smoke22.py`, real time, touch phone 390×664, two days, speeds cycled
  0.75/1/1.5/2×, the pause menu opened on screen, restock with the shortcuts): **no errors, no off-screen modal, money
  checks 1480 / mismatches 0, wageOwed 0**; $70,588 → $137,304 → $202,841 (day 1: 87 guests, 5 lost, rev $51,440, net
  $52,606, rating 4.83→4.76; day 2: 99 guests, 2 lost, rev $55,800, net $65,537, rating 4.76→4.78). Sold out by closing
  on day 2: 巴斯克乳酪蛋糕, 拿鐵咖啡, 提拉米蘇, 松露燉飯, 檸檬氣泡水, 海鮮義大利麵 — see §7.
- Dylan presence audit (`dylan22.py`, 12 lazy days from the Day 30 save): before — scheduled 8/12, entered 6/12, spoke
  3/12; after — scheduled 12/12, entered 12/12, spoke 12/12, paid visits 12; stage unchanged (`docs/evidence/
  v22_dylan_audit_*.log`).

## 5. Performance
`docs/evidence/v22_perf.md`: headless Chromium (software rasterization), the Day 30 save 200 s into service. Phone
390×800: v2.1 21.9 ms/frame (18 groups) vs v2.2 19.7 (11 groups) — unchanged within noise; drawing dominates.
Desktop 1440×900: v2.1 30.2 ms at 540×851 (the old column) vs v2.2 38.2 ms at 1121×849 — 2.1× the pixels for 1.26× the
time. The backing store is now capped at ≈ 1600 px wide so a 2× display never draws the room at 2242 px. No real device
was measured.

## 6. I / T / O per section (Implemented / Tested / Observed on a checkpoint screenshot)
| Section | I | T | O |
|---|---|---|---|
| A1–A5 stability | ✔ | a1–a5, a4b | smoke (HUD money, pause menu, summary) |
| B–E, O management | ✔ | b, c, d, e, o | checkpoint screenshots (gate) |
| F cat-grounded reviews / G no repeats | ✔ | f, g | review text in the book on the Day 30 save |
| V+ Dylan presence (3 knobs) | ✔ | dylan_is_a_presence…, dylan_stays…, dylan_hidden_reveal | audit logs; cards during service |
| H shop taxonomy / I decoration / K strip / T dreams | ✔ | h_i_k_t | shop tabs, room before/after, ceiling + catwalk |
| I+ quiet luxury | ✔ | (visual) | `docs/evidence/v22_art/dining_before_after_*.png` |
| J cat tiers + grass | ✔ | j | grass pot, catwalk perches at phone scale |
| L/M/N hospitality, set sales, weather add | ✔ | l_m_n | 招待 chip, Jill's Card row in the book |
| P cooking choreography | ✔ | cooking tests | kitchen view |
| Q portraits / Q+ Q++ sprites | ✔ | q, q_plus | scenes, cards; the Day 30 room at phone scale before/after (`sprites_q2_room_before_after.png`), beside the cleaner and the chefs |
| R storefront | ✔ | (street test) | `storefront_before/after.png` |
| S UI hierarchy | ✔ | (visual) | PERFECT banner |
| U world memory / V faces | ✔ | u_v | `regulars_faces_and_book.png` |
| V++ two Wangs | ✔ | wangs_are… | `wangs_two_people.png` |
| W album | ✔ | w | `album_living_history.png` |
| X desktop | ✔ | x_a_desktop… | `desktop_before_after_1440.png` |
| Y Day 30 | ✔ | smoke, a4b, save tests | smoke log |
| Z regression list | ✔ | z_regression… (+ the rest of the suite) | — |

## 7. Balance observations — measured, not changed (Z)
Nothing in the economy, prices, demand, patience, rating weights or difficulty was rebalanced. What the measurements
say, for a design decision:
- A mature day earns ~$52–66k net on ~$51–57k revenue with ~87–100 guests; two days took the Day 30 save from $70,588 to
  $202,841 (gate smoke: $207,375). At that rate the $100k/$180k/$300k dreams are 2 / 3–4 / 5–6 days away.
- The fridge (180, +80 with the cooler) is below a mature day's demand (~250 items): six dishes sell out by closing even
  after 補到建議 + 補滿, and "sold out" is structural, not a restock mistake. From Day 3 a sold-out dish is simply not
  offered (A2), so the cost is lost orders, not angry tables.
- Payroll: wages are paid from the day's cash; a shortfall is recorded (`wageOwed`) and nothing else happens — the
  design question (debt? morale?) is open and was deliberately left open.
- Days 1–2 keep the tutorial's automatic provisioning (the only auto-buy left, by design).
- Rating on the Day 30 save moves 4.76–4.85 day to day with 2–5 lost guests; the 40-review window makes one busy day
  visible.
- Dylan: Stage 2 becomes eligible at the next service on the Day 30 save (10 visits / stage 1); the reveal remains gated
  by the evening scenario (`dylan_hidden_reveal`: 6/6 seeds within 14 evenings, evenings 1–11).

## 8. Deferred / partial / blocked
- DEFERRED: a permanent name label for Jill or Dylan (by instruction: the silhouette is the label; Dylan's shows for a
  moment on a tap or a line; the kitchen view's 'Jill' tag was removed).
- DEFERRED: achievement days in the album's story (a migrated save dates them the day they were granted — the Day 30
  save has 聘請第一位員工 = DAY 27); the story uses only days written when the thing happened.
- PARTIAL: the seat-moment lines of the Wangs' shared moments (anniversary, flowers, share) are spoken by the lead
  (王先生) unless a line names her; every line has a single speaker, never "the couple".
- PARTIAL: the tickets' small face for a couple's table is the two sprites side by side (not the supplied portraits — the
  strip is 13 px tall).
- Not built (never in the brief): Steamworks, a runtime LLM, cats outside, chores/meters, dating progression, debt.

## 9. Portraits — the assets report
- Paths: `assets/portraits/src/` (the three supplied sheets, untouched), `assets/portraits/<id>.png` (full-res crops,
  alpha kept), `assets/portraits/web/<id>.webp` (display, ≤ 640 px tall), `js/portraits.js` (generated, 802 KB), cut by
  `tools/portraits.py` (crops chosen by eye; the figures' interiors made opaque where the sheet's cut-out left holes;
  feathered only where a crop runs through the drawing; nothing redrawn, stretched or recoloured).
- Shown: morning remark (prep), expansion scene, construction card, the quiet reveal, Jill ↔ Dylan exchanges during
  service (card), every regular's line (card), the 熟客 page rows, the tap card on a seated regular. Not shown: toasts
  for stock/money, PERFECT/COMBO, duty lines, generic guests, tickets.
- Viewports tested: 390×800 / 390×664 / 375×553 (phone), 1440×900 / 1280×800 / 1000×700 (desktop, container queries
  at ≥ 720 px); the face is always above the text box and inside the viewport (`q_` test).
- Fallback: without `window.PORTRAIT_DATA` every card and scene keeps the plain presentation — no placeholder.
- Transparency: preserved (alpha from the sheets; interiors solid).
- Staff mapping (by role and hiring order, never by appearance): 阿德師傅 → staff_1, Marco → staff_2, 小林師傅 → staff_3,
  小茉 → staff_4, Kai → staff_5, 秀琴阿姨 → staff_6; every other staff name keeps the plain presentation.
- Regulars: chen, mia, xiaolin → 小林 (`koba`), leo, sophie, mr_wang → 王先生 (`wang`), mrs_wang → 王太太 (`wangwife`).
  **Open question for the author**: the 13-sheet's third figure (mapped to 小林 by the given order) reads as a young
  woman and the fifth (Sophie) as a man in a suit; if the given order was meant differently, swapping two entries in
  `CROPS`/`PORTRAITS` is a one-line change — nothing was inferred from appearance.
- Jill's world sprite and Dylan's were redesigned twice: Q+ (the portrait's clothes, literally — which read as staff
  at phone scale) and Q++ (the character translation above, per the acceptance feedback); the Wangs' sprites to theirs (V++).

## 10. Not verified on a real device
Nothing in this session ran on a phone or a desktop browser with a GPU: the frame costs above are headless software
numbers; touch was simulated (Playwright touch contexts); the portrait cards' legibility at 2× on an iPhone, the desktop
layout on a real 27-inch window, the service worker / cache behaviour of the new single file, and the sound are all
still to be checked by hand. Suggested first playtest: the Day 30 save on a phone for two evenings (watch a couple's
card, the album story, a Dylan card), then a desktop window resized mid-service.
