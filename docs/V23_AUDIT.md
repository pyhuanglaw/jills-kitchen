# v2.3 Phase 0 — architecture audit (from `js/game.js` at `v2.2.1`, 2026-09-30)

Answers A–P of `docs/v23/go_2026-09-30_v23_start.txt`, read from the code. Line numbers are `v2.2.1` (`7dbcaff`).
Verdict at the end: **no architectural blocker; implementation starts with the story/relationship foundation.**

## What exists (the systems the brief names)

| brief's name | in the code | notes |
|---|---|---|
| restaurant clock / one loop | `R.t`, `update(dt)` (1565), `frame()`; one `R` per service day; `phase` title/prep/service/summary/shop | the only simulation |
| customer identity | a group `g` in `R.groups` (`spawn`, 1029): `id`, `type`, `size`, `reg`/`regs` (regular ids), `name`, `looks`, `state` (arrive→queue→toTable→reading→order→wait→eat→check→leave), `table`, `room/troom`, `ticket`, `pat` | one object for the whole visit; nothing is cloned |
| tickets / payment | `createTicket(g)` (1140) → `R.tickets`; `collect(g)` (1276) pays **once**, counts `S.regulars[id]++`, `S.catFam`, reviews (`addReview`), then `leaveGroup` | the single place a visit becomes history |
| regular history | `S.regulars{id:visits}`, `regMem(id)` = `{seats,orders,facts[6],flags,last}` (1311), `regTier(v)` 0/.5/1/2, `regGate(id,key,gapDays)` cooldowns, `momentsLeft()` (1351) = the day's budget for "something happened" | already a facts + gates + budget shape, but only for the 7 `REGS` + Dylan |
| named guests (Ken, 杜, 周董…) | `NAMED` (157): fixed looks + portrait, drawn from `NAMES[type]` at spawn; **no history at all** — nothing counts their visits | the Ken arc needs this (I) |
| World Memory | `WORLD_MEM` (1327): reads days the save already keeps (`newRooms`, `records`, `dylan.reveal`) and lets a regular mention them once in a window; `S.worldMem{k:day}`, one a day | a read-only callback layer: the pattern the arbiter's ambient lane should reuse |
| regular story beats | `regPlanVisit` (1359) decides a visit's `moment` when the day is scheduled (weighted, gated, budgeted); `regSeatMoment` (1379) says it; `regGift` (1404) leaves objects (`propSet`); `REG_PAIRS`/`regMeet` (1414) two regulars who know each other | this *is* a small story system; v2.3 generalises it rather than replacing it |
| Dylan | `S.dylan{stage,stay,reveal,clues,orders,seen,trace}`; `dylanStageCheck` at day start, `DYLAN_SCENES` (each once, `seen`), `DYLAN_ACT`, evening `LIFE` | stays as is (brief §41); story facts can *read* it |
| speech log | `logLine` → `R.log` / `S.dayLog` (90 lines) | scenes log every spoken line |
| Reviews | `S.reviews[80]` `{s,txt,name,day,w,tags,cat}`; `rating()` = last 40 | Phase B material |
| Restaurant Records / journal | `S.records`, `showBook` tabs; `storyEvents()` (4007) builds the album's week timeline from days the save keeps | the surface for "event history visible" (slice item 8) |
| Life Album | `albumList()` `{id,kind,day,clock,cap,txt,keep}`; picture in IndexedDB (`photoPut`), inline fallback; `memo()` → `flushMem()` captures the canvas | Story Photos = a second kind of entry with an authored picture instead of a capture (N) |
| achievements | `ach(id)` once, day stamped | not reused for story state (a save through an update stamps them late — comment at 4004) |
| daily event / weather | `planToday` → `S.today{weather,event,groups,tasks,reco}`; `EVENTS` | untouched |
| staff | `S.crew[{id,role,name,lv,duty,duties}]`; the board (`boardHTML`, `bdAdd/bdRm`), `FLOOR_DUTIES` per area | Lounge = one more area on the board (J) |
| kitchen | `R.slots` by station (`buildSlots`), `startCook`, `chefAuto`, tickets route by `DISH(d).st` | Bar Food = dishes with existing stations (M) |
| save / migration | flat `S`; `newState()` defaults; `fillDefaults` adds missing top-level keys and merges 10 sub-objects; one-shot migrations (`legacyCrew/legacyWang/mainHallMig/crewNameFix`) run inside `parseSave`'s try; `SAVE_V=1`, `MIGRATE{}` unused | the TDZ trap: anything a migration reads must be declared above line 438 |
| checkpoint | `snapshotService` keeps `CP_KEYS` of `R` and the groups' `G_STATES` | a new guest state must be added to `G_STATES` or it is dropped on resume |
| RNG | `Math.random` (seedable in the harness); `hash()` for per-day determinism | deterministic tests = seed + fixture |

## A. One restaurant, not two
The Lounge is a fourth `room` in `ROOMS`/`ROOM_ORDER` with its own `LH`/layout constants (the side hall already does this: `SIDE_L`, `roomOpen('side')` gated by `S.rooms.side`). Tables carry `room` (`buildTables` gives `'main'|'side'|'front'`); a Lounge seat is a table with `room:'lounge'` and a `kind` (bar/small/sofa). Guests, tickets, staff, the kitchen, reviews, the album, the economy: all the same objects. Nothing is duplicated.

## B. One guest through WAITING → Lounge → dining → Lounge → out
`g` already moves rooms (`troom`, `stepTo` walks a doorway chain, 517–523). The transitions are new **states of the same `g`** (added to `G_STATES` for the checkpoint):
- waiting → Lounge: `pickSpot(g)` gets a fourth spot kind `{k:'lounge',i}` (like bench/stand); `requeue()` moves the group; `freeTableFor` + the queue's `notice` timer already seat a waiting group when a table frees — unchanged, so no duplicate customer.
- dinner → Lounge: `collect(g)` pays the dinner ticket once (it already sets `g.ticket=null`); a group that stays gets `state:'lounge'`, a Lounge seat, and a *second* ticket (`tk.room='lounge'`), paid by a `collectLounge(g)` that adds revenue but **does not** touch `S.regulars`/`catFam`/reviews: the visit-count line in `collect` moves behind `if(!g.counted){g.counted=1;…}`. One visit, two phases, one identity, one review eligibility (`addReview` is already once per `collect`).
- Lounge → dinner: the group leaves the Lounge seat and takes the normal `seatGroup` path.
- The `co-presence` fact (D) is keyed by `g.id` per visit, so a guest who changes rooms is one presence.

## C. Story facts in the save
One new top-level key `S.story` (defaulted by `newState()`; `fillDefaults` adds it to every old save; nothing else changes):
```
S.story = { v:1,
  facts:{key:{d:firstDay,n:count,l:lastDay}},          // world/character facts, idempotent by key
  rel:{ 'a|b':{f:{fact:{d,n,l}}} },                     // relationship facts between two ids, pair-keyed (sorted)
  ev:{ key:{d:doneDay,n:times,miss:overdueCount,last:day} },   // story events fired / eligible-but-not-chosen
  day:{d,major,minor},                                  // today's lane budget
  photos:{key:day},                                     // Story Photos unlocked (album entries carry kind 'story:'+key)
  named:{name:{v,last,dishes:{}}}                       // named guests' real history (Ken, 杜 …), from now on
}
```
Ids: regulars by `REGS` id, Dylan `'dylan'`, named guests by `'n:'+name` (their `NAMED` key), staff by `'s:'+crew.id`, cats by cat id, Jill `'jill'`. No id is renamed. Old saves have no `S.story` → everything starts empty; **nothing is inferred from the past** (no fabricated history), the next visit begins it.

## D. Facts → familiarity → behaviour, no N×N
Facts are written only where the game already handles the pair: `seatGroup` (co-presence with the other seated regulars — at most the handful in the room), `collect`, cat `visit`/`pet` events, staff actions. Familiarity is **computed** from the pair's facts (`famOf(a,b)` → 0 stranger / 1 recognize / 2 familiar / 3 comfortable), never stored, never shown. Behaviour pools check `famOf` when they run. Cost: O(regulars in the room) at a seating, ~5.

## E. Arbiter = the existing shape, generalised
`storyTick(boundary, ctx)` is called at the same points the game already evaluates regular moments: day start (`startService`), `seatGroup`, `createTicket`, serve, `collect`, `startClosing`, the evening (`lifeEnsureEvening`), `endDay`. Each story event is data: `{k, lane, when(ctx), can(), w(ctx), cd, present:[...], run(ctx)}`. `run` writes facts/consequences through idempotent helpers (`factSet`, `evDone`). Never per frame.

## F. Lanes
`S.story.day` counts today's `major` (cap 1) and `minor` (cap 2); `ambient` events have no budget but their own cooldowns (`regGate`-style, in `S.story.ev[k].last`). An ambient line never consumes the major slot; a major event's `can()` never depends on an ambient one.

## G. Weighted eligibility + overdue
At every boundary the eligible events of a lane are weighted (`w(ctx)` × `(1+.6·miss)`) and one is drawn (`wpick`); every eligible event not drawn gets `miss++` that day (once per day). Class A events (Ken origin beats, the Lounge project, Sophie's gift) also get a hard floor: after `miss>=N` they are chosen first when eligible. `miss` resets when the event fires.

## H. Presentation fallback
An event's `present` list is ordered; the first variant whose `can()` holds is used (crowded → "share a table", else "stops at her table"). The fact written is the same. If no variant can run, the event stays eligible (`miss++`) — it is never faked: the cat must be there (`catBy('mei')` position checked), the guest must be seated, the staff member must be employed today.

## I. Ken's arc on fresh / Day 30 / Day 35 saves
Named guests get history from now: `collect` records `S.story.named[name]` (visits, last day, dishes). Ken's beats require `named['品酒師 Ken'].v>=3` and a suitable dish eaten (`dishes` has a main); on the Day 35 save that is empty → his arc starts at his next visits, honestly. His spawn weight is raised while the arc is open (`buildSchedule` adds a Ken visit with p≈.35 when eligible — a scheduling weight, not a teleport). 杜 is enrichment: beat 2's preferred variant needs both seated; the fallback is Ken talking pairing with Jill alone. The Lounge project (Phase 4) requires the tasting fact, not 杜.

## J. Lounge staffing = the board
`ROLES` gains `bartender`; the board gets a `lounge` area row (like main/side) and the bar station; `bdAdd/bdRm` unchanged. `homeSpot` for the new area. No second staff manager.

## K. Station familiarity
`m.fam={main,side,lounge,kitchen}` days worked, incremented at `endDay` for the area the member was assigned to; coarse labels at 0/3/10 days (新/熟悉/熟練) computed, shown as one line on the crew card. Wine familiarity the same way (`m.wine`), Phase 3+.

## L. Staff-dependent stories
Every staff-bound event's `can()` requires the member in `S.crew` today; absence → not eligible (no miss penalty for optional arcs); firing → the arc goes inactive (`S.story.ev` keeps what happened). Nothing blocks restaurant progression: no event is a prerequisite of a purchase.

## M. Bar Food = the Main Kitchen
Bar dishes are `DISHES` entries with existing stations (`prep`/`stove`/`bar`), unlocked with Lounge I; Lounge tickets are `R.tickets` with `tk.room='lounge'`; the kitchen does not know the difference; waiters deliver to `t.room` as they do for the side hall. Kitchen pressure is the real consequence. No second kitchen.

## N. Story Photos in the album
`albumAdd(kind='story:'+key, img, info)` with `keep:true` and a `story:1` flag; the picture is an authored asset (`js/story_art.js`, like `portraits.js`) when one exists, else a staged render of the actual sprites at the actual place (still canonical). Unlock is a consequence of a story event (`storyPhoto(key)`), idempotent through `S.story.photos[key]`; the event itself needs the real milestone facts. Ordinary captures stay `memo()`/`flushMem()`.

## O. Save migration
No migration step is needed for the foundation (a new defaulted key). Rule kept from v2.2.1: anything read at load time is declared above `S=load()`. Tests: fresh, Day 30, Day 33, Day 35 through two reloads each, `S.story` identical after the second.

## P. Performance
Story evaluation only at boundaries (E); familiarity computed on demand from a pair's few facts; no matrix, no per-frame scan. Tests protect identity, payment, idempotence, budgets, migration — not pixels.

## Risks found
1. `momentsLeft()`/`regPlanVisit` and the new arbiter both spend "moments": the arbiter's minor lane **replaces** `momentsLeft` for new events; the existing regular moments keep their own budget so v2.2.1 behaviour is unchanged.
2. `NAMES.gourmet` draws 杜 and Ken at random for any gourmet — two Kens in one evening are possible today; the story layer treats a named guest as one person (a second same-name group in a day is renamed at spawn when the story is on).
3. The checkpoint (`G_STATES`) must learn every new guest state or a resumed day loses those groups.
4. `flushMem` only photographs the room on screen; Story Photos bypass the camera (authored image), so they never depend on which room the player is watching.
