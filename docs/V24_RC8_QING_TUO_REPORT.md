# JILL'S KITCHEN rc8 — 晴 × 阿拓 after work: report (2026-10-03)

The five after-work scenes of 沈晴 and 阿拓, on top of Checkpoint C (a95fcd2). Sources, newest first where they differ:
the player's message of 2026-10-03 (phase 3 canon), the handover's §AI/§19 and «CURRENT ENGINEERING STATE» §十二, the
2026-10-03 brief 「沈晴 × 阿拓後續故事」 with its revised 第五幕, and 19:19 §18–§19. Not published.

I / T / O as in the release reports: nothing here is O.

## 0. Where the briefs differ, and what was built

| | Older text | Built (newer canon) |
|---|---|---|
| 《今天喝？》 opening | 「第一次來這邊吧？」「我倒是聽過你。」 | 「今天喝？」「稀奇。」 — Evan has known Dylan since the signing (19:19 §18; 2026-10-03 message) |
| 《晚點回去》 | Jill: 「你不走？」 | Jill does not appear in any of the five (§19; 2026-10-03 message) |
| Dylan's husband reveal | 「不要做正式的老公身分揭露事件」 | The restaurant's reveal is kept (19:19 §14; handover §N) — nothing in these scenes says he is her husband |
| 《講完》 | 「我喜歡妳。」「要不要跟我在一起？」, 「你不要鼓掌。」 | The revised 第五幕: 「那妳要不要……在……」「在什麼？」「……好啊。」; Dylan claps twice, nobody scolds him; Evan, 予安, Dylan go; the two are left |
| 《講完》 ending | — | The revised brief's own example: 「你什麼時候學的？」「妳回家的時候。」「予安教你的？」「嗯。」「難怪。」「什麼難怪？」 she smiles, no answer (the 「難怪」 picture, `qt_alone`) |

Written here where the brief only describes: 《晚點回去》's four lines of work talk (「今天沙發那四個，炸雞點了三次。」
「四次。」「第四次是外帶。」「外帶也算。」) and short narration lines that stage what the brief describes (who stays,
where they sit, the light). They are the player's to change.

## 1. Story beats (I)

`js/game.js`, one block after the Ken stand-ins (`qaS` … `drawIllusQt`):

| Key | Kind | What |
|---|---|---|
| `qt_drink` 《今天喝？》 | held, major | Dylan's first drink at The Lounge, at the bar |
| `qx_pay` | unheld, minor | his first bill: 「這杯算了。」「不用。」「你還真的付喔。」「不然呢？」 — the bill is the evening's own, paid once |
| `qx_dylan` | unheld, ambient | his later drinks there; Evan: 「一樣？」「嗯。」 |
| `qt_late` 《晚點回去》 | held, major | after closing: Evan, 沈晴, 阿拓 stay; Dylan stays on; the bottle handed over; his money under the glass |
| `qt_often` 《最近比較常》 | held, major | 予安 stays for one: 「你們下班都會留下來？」「偶爾。」「最近比較常。」; 沈晴's look; 予安 sees it, says nothing |
| `qx_after` | unheld, ambient | the evenings after closing, different people on different nights |
| `qx_home` | unheld, ambient | 沈晴 goes home to her parents for two days |
| `qt_ya` 《你喜歡予安？》 | held, major | the question, Dylan's wrong guess, 「是沈晴」, the piano, 予安 knows, five notes |
| `qt_said` 《講完》 | held, major | he plays them himself; the unfinished sentence; 「……好啊」; two claps; the two of them left |

Changed elsewhere: the story page 「晴 & 阿拓」 lists the five after 「有你在的晚班」; `qt_extra` (「多的。」 repeats) stays
quiet on an evening one of the five has; illustration slots `qt_first`, `qt_more`, `qt_lesson`, `qt_play`, `qt_alone`
with drawn stand-ins until the player's pictures; a planned Lounge visit for a regular keeps its retry for a full bar
(`v24Visits`); Jill does not walk over to Dylan's table when he is at The Lounge; **Dylan never walks next door after
dinner to Madame Lin's bar** (`barNextP` — before this he could, one evening in eight; Evan must not have met him before the
signing, §11C, and he hardly drinks, §18). While one of the five is on screen, The Lounge shows only its cast
(`qaSolo`): the evening's guests and crew are not drawn under it.

## 2. Each scene's prerequisites and the scheduler (I, T)

All five are held (the restaurant, its clock and its orders stop; one line a tap; it resumes where it was), staged in The
Lounge, on an ordinary Lounge night (not Ken's tasting, not the chef's night), Evan on. One major story step a day: when
the day's slot is another line's, the scene comes on a later evening.

| Scene | When |
|---|---|
| 《今天喝？》 | Evan knows Dylan (the signing), The Lounge open ten days or more; planned as Dylan's evening at The Lounge (half the eligible evenings); fires when he sits down |
| 《晚點回去》 | 「多的。」 done; 《今天喝？》 five days back or more; Dylan has had two more drinks there, on two evenings; 沈晴 and 阿拓 in; she is not away |
| 《最近比較常》 | 《晚點回去》 four days back or more; 予安 the pianist ten days or more; one of her nights (she is still there at closing); 沈晴 and 阿拓 in |
| 《你喜歡予安？》 | 《最近比較常》 five days back or more; 沈晴 at her parents' (`qx_home`); one of 予安's nights; 阿拓 in |
| 《講完》 | 沈晴 back two days or more (not the day she is back); one of 予安's nights; 沈晴 and 阿拓 in |

`qx_home` (daystart) sends 沈晴 home for two days, on one of 予安's nights, five days or more after 《最近比較常》 — her
life, not anyone's plan; if the evening goes to another story both days, she goes home again a week later.

**《你喜歡予安？》 is one scene**: the question, the wrong guess, 「是沈晴」, Evan seeing the piano, going over, 予安's
「沈晴？」 and the lesson are the lines of one held beat on one evening — nothing is split into stages.

## 3. Who knows what

- 沈晴 does not know until 「……好啊」: no line of hers before then says or denies anything; 《最近比較常》 gives her a look.
- 予安: `ya_sees_qt`, set as she sees 沈晴's look in 《最近比較常》 (and kept even if the scene is not shown). Nobody tells
  her: in 《你喜歡予安？》 Evan only asks 「教他一個最簡單的。」, and she says 「沈晴？」 herself.
- Dylan: `dylan_knows_qt`, set at 「……沈晴？」 — he learns it there, his wrong guess first. Nothing before it (no
  narration either) says he noticed.
- Evan has seen it all along; he joins in only when 阿拓 asks.

## 4. Mature saves

Nothing to migrate: the five are new beats with prerequisites from what a save already has (「多的。」, The Lounge,
Evan, 予安's line). A save past those enters at the earliest step whose conditions hold; one step an evening at most; no
earlier 晴 × 阿拓 beat is replayed and none is marked as history.

## 5. Tests (T)

- New: `v24_rc8_qing_tuo_after_work_five_scenes` (the player's Day 74 save) — PASS. It drives the five on evenings with a
  free story slot and checks: every line of 《今天喝？》 (no exam named); his bill counted once and the 「這杯算了。」
  exchange; the cast of each scene (no Jill; 沈晴 absent from 《你喜歡予安？》); the order of the key lines; Dylan's
  knowledge flag false through 「……沈晴？」 and true after; no line telling 予安; her lines only about the piano; one
  hand, five notes, not a piece; 《講完》 not while 沈晴 is away nor on the day she is back; 阿拓 plays, 予安 does not;
  the lines the briefs forbid absent (「我喜歡妳」「跟我在一起」「你不要鼓掌」, any 「空間」/「不打擾」, 「司法官」…);
  only 沈晴 and 阿拓 on stage at the end; the after-hours line changes no story step; the five on five different days, in
  order; the story page lists them.
- Regression on 0d3ab73: the 111 tests whose names touch Dylan, The Lounge, the stories, 予安, Ken, the bar, Madame Lin,
  saves and migration, staff and Evan, regulars, the scenes and the album, with the two goldens — **110 passed, 1 failed**
  (`docs/evidence/v24_rc8/qing_tuo/regression.txt`). The one failure is `jill_rests_when_staff_cover_the_floor`, the
  same as at Checkpoint C and with the same numbers (sit 517 of 5907 frames): Checkpoint A's, not this line's (Checkpoint
  C report §3). From the 52nd test on, the tree also had 2c1d303's two pictures (data only); the illustration and signing
  tests ran on them and pass. The full regression (232) belongs to the release gate.

## 6. Simulations (T) — `docs/evidence/v24_rc8/qing_tuo/chain/qt_chain_d74.log`

`tools/sims/qt_chain.py` (lin_chain's loop with this line's facts) from the player's Day 74 save, the lazy bot, scenes
unseen: 予安's own line runs alongside (ya_1 Day 80 … ya_join Day 87); 《今天喝？》 Day 81 (his bill the same night),
《晚點回去》 94, 《最近比較常》 99, 沈晴 home and 《你喜歡予安？》 113, 《講完》 118 — one an evening, in order, 0 page
errors.

## 7. Evidence (T) — `docs/evidence/v24_rc8/qing_tuo/`

`shot_qt.py`: the five scenes' key lines at 390×844 (q1–q5) and the story page (q6); `log.txt` has every line of each.

## 8. Known limitations

- Pictures: all ten of the player's pictures are in — `lin_hello` and `dylan_book` with this line's commit; `lin_viewing`,
  `lin_sign`, `lin_guest`, `qt_first`, `qt_more`, `qt_lesson`, `qt_play` and `qt_alone` in the commits after. The drawn
  stand-ins stay in the code as the fallback.
- The Lounge does not dim to 「只剩吧台那一區的燈」 on screen; the narration says it, the stand-in picture shows it.
- The five-note phrase plays as a simple tone sequence.
- Nothing here has been played by the player (O).
