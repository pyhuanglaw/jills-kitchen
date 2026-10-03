# JILL'S KITCHEN v2.3 — Release Candidate Report (2026-09-30)

Legend — **I** implemented (code in repo), **T** tested (automated test / seeded simulation), **O** observed (screenshot inspected by me in headless Chromium at 390×844). Nothing here was observed on a phone.

Rollback points untouched: `v2.2.1` = 7dbcaff (artifact Version 33), `v2.2`, `v2.2-ux-stable`, `v2.1`. v2.3 checkpoints: Phase 0 → `docs/V23_AUDIT.md`; Phase 1–2, 3, 4, 5 (see `git log`), Phase 6 `ada6446`, Phase 7–9 `7ba4145`, Phase 10 (this commit, tag `v2.3-rc1`).

## 1. What was implemented (I)
- Story/relationship foundation: `S.story` (facts, per-pair relationship facts, event state, Story Photos, named-guest history, trace); `storyTick()` at nine boundaries only (daystart / seat / order / collect / lounge / leave / evening / close / dayend / cat), never per frame.
- Lounge origin (Ken → wine question → pairing talk / 杜's argument → the idea returning → one tasting night with one player choice → Jill's after-close realisation → project revealed, can be deferred, never lost).
- Lounge I / II / III (structure, seats, wine, Bar Food through the Main Kitchen, Lounge staff in the existing 工作分配, optional Bar 小廚 at III), dark visual direction per your correction.
- Staff growth: coarse station/wine familiarity, tenure (legacy crew marked 從 v2.3 起算), veterans answer newcomers.
- 74 story events (12 major / 39 minor / 23 ambient) covering every arc in §3; 11 Story Photo slots (§7).
- Reviews 2.0, Social page, 5 campaigns (§8). Named guests are persons (with company too, one visit a day), have a card, a usual table, facts.

## 2. Architecture actually used (I)
One save object, no second simulation. Facts are idempotent by key and dated (`factSet` / `relSet` with per-day option); familiarity is *computed* from pair facts (`famOf`, 0–3), never stored or shown. Events are data (`STORY_EV`: lane, class, `at`, `when`, `w`, `cd`, `once`, `floor`, `present[]` fallbacks, `run`). Lane caps major 1 / minor 2 per day; misses raise weight; Class A with enough misses goes first. Presentation fallbacks per event; character-required beats simply wait. Romance exists only through `romanticEligible()` on the two whitelisted pairs and needs qualitative facts (choseNear, madeSpace, sharedFood, waitedFor). Nothing in the schedule or social layer consumes the day's random stream (hash-based coins), so v2.2 goldens stay valid except one legitimate re-record (§10).

## 3. Story arcs implemented (I / T)
| Arc | Beats | Test/sim |
|---|---|---|
| Sophie × 寶寶 | 4 beats + glance, permanent pad, Story Photo | T (test + sim: completes ~day 93 on the Day 46 save) |
| Sophie × Mia | A recognition → B shared evening → C seat chosen near (other seats free) → D bag off the held stool (3 presentations) → E shared plate → F waiting (only if Mia is really on the way) → G leaving together (album 《今天一起走》) → H arriving together (Jill 「今天一起？」, Story Photo) → afterwards sits near / arrives together sometimes | T (phase7 test; 60-day sim reached H on day 100) |
| Ken × Monsieur 杜 | usual stools, Evan 「還沒看到」, arguments, ordering together, 晴 「你今天不等杜先生？」, absence noticed both ways, waiting for each other, Evan's second coaster, REQUIRED friendship photo 《還是沒有同意》, later 《固定的位置》, Evan 「聽說這裡是你害的」 | T (photo on day 65–73 in sims; `romanticEligible` false with fam 3) |
| 晴 × 阿拓 | fryer friction → synchrony (6 shared shifts) → 「多的」 after close → repeats → photo 《多的》 → absence beat when he is gone (fired = inactive, no deadlock) → 《有你在的晚班》 | T |
| 老饕 | 「靠這一道走天下？」 (only with one Signature), Sophie's line, 「兩道走天下」 when he eats the dessert (works on old saves that already have it) | T |
| Madame Lin | sees only what changed since her last look (9 things), 「還沒換啊」, plant gift after 3 changes (permanent prop, main-hall corner) | T |
| 周董 | fixed 「隨便」 order after 3 visits, usual table, side hall when taken, sold-out dessert 「那明天再來」 (comes back), stays when 包包 sleeps beside him, staff know what 隨便 means | T |
| Critic / Inspector | return line 「今天還戴帽子？」; inspector off duty after ≥2 real inspections, then rare regular | T |
| 王家 | solo-visit tease, 王太太 × Dylan pre/post reveal, anniversary photo slot | T |
| Mia / 小林 / Leo / Dylan / cats | 「以前還沒有側廳」 only if her first counted visit predates it; 小林's drink before he asks + 「今天不要那個」; Leo's five cats only when five are visible; Dylan 「她們是不是——」 and 「以前我也——」; Valentine's each year different; regulars who know a cat by name, 陳伯伯 × 樾樾, Momo × 柔柔 | T |
| Staff | new hire asks / veteran answers, 「第二層左邊」 in a rush, staff-meal dessert-box joke + two boxes later (once per restaurant), ensemble photo slot | T |
| Milestone | 《好像真的開起來了》 at the first books line crossed after v2.3 began, with Dylan / longest-tenured / alone | T |

## 4. Lounge I / II / III behaviour (I / T / O)
I: 6 stools + 3 tables, 3 wines; II: 8 stools, +table, sofa, 5 wines, 2nd bartender; III: quiet corner (bottom-left), wine wall. Waiting → stool (60%) → dining when a table frees (tab settled, same group); dinner → Lounge afterwards by type; Lounge-direct guests look in the Lounge before the full dining room turns them away. Eat timers ×2.4, patience drain ×.5. Bartender takes orders/tabs at tables when no Lounge server has that duty and always carries the glasses. O: `docs/evidence/v23/lounge1_*`, `lounge2_*`, `lounge3_*`, `p7_bag_on_stool.png`.

## 5. Staff integration (I / T)
Bartender role (`lbar`), Lounge 外場 duty on the board, 安安 (waiter from II), 阿拓 (chef from II, quicker on bar food), Evan/沈晴 portraits from the approved sheets. Familiarity per area per worked day; wine glasses counted; tenure by days worked. Fired staff: their events are ineligible, nothing waits (test asserts).

## 6. Relationship behaviour (T, sims)
60-day sim from the Day 46 save (Lounge III, seed 5): Sophie|Mia copresent 25 → all eight phases; Ken|杜 copresent 46, sharedTable 16, argued 11, waitedFor 16, leftTogether 30; 晴|阿拓 shift 60, gesture 7. Major beats per day: 53 days with 0, 7 with 1. Romance flag true only for Sophie × Mia.

## 7. Story Photos and missing art (I / T / O)
Unlocked from the approved sheets (`tools/story_art.py` → `js/story_art.js`, in the single file): `sophie_mia_arrive` 《今天一起來》, `sophie_mia_leave` 《一起回家》, `ken_du` 《還是沒有同意》, `ken_du_seat` 《固定的位置》, `qing_tuo` 《多的》, `qing_tuo_late` 《有你在的晚班》. Staged (drawn from real sprites): `sophie_mei`, `opened_up`. **Missing final art (slot + unlock path exist; the milestone is kept in `S.story.photosPending` and joins the album, dated, when the art is supplied):** `jill_dylan_valentine` (first post-reveal Valentine's), `wang_anniv` (王家's anniversary), `staff_meal` (ensemble). Note: the supplied sheets carry captions inside the image; the crops were taken inside the panel frames so no caption text is in a photo.

## 8. Reviews / Social / Marketing (I / T / O)
Topic vocabulary shared by reviews, posts, campaigns and demand (`TOPICS`). Reviews carry the topics their text is about (glass / Lounge / dessert pools added; recovery line for a named guest whose sell-out or wait was remembered). Social page (shop tab 社群與宣傳): guest posts only from their own evening (Momo's cat by this save's name, 小琪's dish → demand ×1.6 for 3 days, guests say 「是不是那一道？」), Jill's candidates only from things that happened (a dish added these days, an album photo, a new room, the wine list, the second Signature), one post each, ≤3 a day, no follower counter. Five campaigns (在地 / 料理 / 側廳 / 店貓 / 晚餐酒單), 3 days, real cost, guests marked `via:'camp'`, counted results (first-timers, ordered the dish, came for the campaign, returning guests in the window, most-mentioned topics). O: `p8_social_page.png`, `p8_campaigns.png`, `p8_reviews_topics.png`.

## 9. Save migration (T)
`S.story` / `S.social` / `S.gearN` created lazily; no top-level read at load time (TDZ rule kept). `tools/sims/migration_sweep.py`: Day 30/33/35/39/42/44/46 fixtures each load three times identically, play a full lazy day, save, reload — day/money unchanged, story state starts empty, no page errors. Fresh save covered by the golden scenario. Nothing is inferred from before v2.3 (visits of named guests, tenure, first visits all count from now).

## 10. Tests and simulations (T)
Suite: **107 tests, all passing** after the last fixes (`tests/run_tests.py` 82 + `tests/v23_tests.py` 25). New v2.3 tests: story foundation/reload, hooks, Sophie × 寶寶, Lounge identity/payment, Lounge origin, Lounge I content, staff growth, Phase 7 arcs (one long test driving every arc through real conditions, save/reload, no re-fire), Phase 8, Phase 9. Goldens: `golden_scenario` re-recorded once (day 3 only; named guests became persons with a usual table — legitimate); `golden_frames`, `cat_personality_fingerprint` unchanged. Sims: `tools/sims/story_days.py`, `social_days.py` (30/40/50/60 days, several seeds), `migration_sweep.py`.

## 11. Balance findings (T)
Level-5 nights: 80–110 guests, Lounge 9–18 tabs / $4–7k (small share of ~$50k). Named VIPs at level 5 are frequent (weight 9 vs office 30): with the one-visit-a-day rule 周董 / Madame Lin / Mr. Hart each come most nights — acceptable but worth a look in play. Sophie × Mia needs ~50–60 days from a save with no shared history (schedule nudges their hours once they have met); Ken × 杜 ~20–30 days; 晴 × 阿拓 ~25 days. Angry leaves 2–3/night with or without the Lounge (staffing of that save).

## 12. Deferred
- Final art for the three pending Story Photo slots (§7).
- Critic reveal is still immediate at checkout (v2.2 behaviour); the 2–5-day Records reveal was not rebuilt.
- 小琪 / Momo visits are rare (blogger event days), so their posts are rare; Mia's 3–4-friend dinner not added.
- Wine familiarity for Lounge servers affects nothing mechanical beyond labels.
- Balance of VIP frequency (§11) left as-is.

## 13. What needs your iPhone / normal play
- Lounge darkness and light pools on a real screen; the bag on the held stool; the quiet corner (bottom-left) not hidden by staff bubbles.
- Story Photo lightbox and the 故事 pin; the Social / campaign page scrolling and the dish selector.
- Whether the arcs are *perceivable* at your pace: Ken × 杜 at the bar, Sophie's seat choice, 晴 asking about 阿拓 — sims say they happen; only play says they read.
- Event density over a normal week (target 0–1 major, 0–2 minor).
- Save from your real phone: load into the RC and confirm Day/money/crew unchanged (the sweep only used the fixtures you gave me).
