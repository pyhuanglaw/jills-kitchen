# v2.2.1 B1 — the stock recommendation on a mature restaurant (#1)

What the player saw (Day 33): the prep screen's suggestion filled the fridge, and by the second half of the evening some dishes were sold out while others had plenty left. "Per-dish distribution, not just capacity."

## What the suggestion was doing (v2.2)

`suggestStock()` estimated the day's demand per dish with the game's own order model (`expectDemand`, seeded per day), blended it with a sales history (`S.salesHist`, an EMA of what actually sold), added a flat +15 % and, when the total did not fit the fridge, scaled everything down to the cap.

Three things about that, measured on the Day 33 save:

1. **The model is not the problem.** For every dish the model's mean and what a lazy-bot day actually sells agree within the day's own noise (three seeds, Day 33 menu, model mean vs ordered):

   | dish | model | ordered |
   |---|---|---|
   | fruitsoda | 24.0 / 28.1 / 23.4 | 23 / 17 / 19 |
   | blacktea | 21.8 / 20.2 / 19.9 | 21 / 21 / 23 |
   | sparkling | 18.4 / 15.8 / 19.7 | 17 / 17 / 17 |
   | signature | 14.7 / 14.2 / 15.3 | 17 / 13 / 17 |
   | steak | 9.8 / 11.1 / 10.5 | 11 / 12 / 9 |
   | duck | 9.0 / 10.3 / 9.8 | 5 / 12 / 5 |
   | coffee | 9.4 / 9.7 / 9.4 | 7 / 7 / 15 |
   | pudding | 7.3 / 7.6 / 7.4 | 4 / 4 / 7 |
   | risotto | 5.3 / 4.7 / 5.8 | 8 / 3 / 8 |

   The day-to-day swing per dish is ±30 % and more (duck 5 / 12 / 5, coffee 7 / 7 / 15). A flat +15 % buffer covers a dish like blacktea (steady) and not a dish like coffee (spiky).

2. **The fridge is the binding constraint at Day 33.** Fridge LV5 + 冷藏庫 = 260 portions. The 18-dish menu sells ~190 portions a day; means + any honest buffer exceed 260, so the cap shaves the buffers of every dish and the last hour of the evening runs some of them dry. This is the same on every seed and is not something the recommendation can fix without a bigger fridge.

3. **A vicious circle.** v2.2's A2 sold-out filter made a table order only what was in stock, and the sales history recorded what sold. A dish that ran out at 21:00 was recorded as "sold 12" instead of "wanted 18", so the next day's blended mean was *lower*, the suggestion for it fell, and it ran out earlier. Regulars' favourites (seafood, pudding, sparkling) were the usual victims.

## What changed (v2.2.1)

- The buffer is per dish and grows with the square root of the mean: `ceil(mean + 1.2·√mean + 1)`, never below 2. A 24-a-day drink gets +7, a 5-a-day side gets +4 — bigger sellers get a bigger buffer and a smaller relative one, which is what a Poisson-ish daily demand needs.
- When the total does not fit the fridge, the **buffers give first**: every dish keeps its mean when the means fit; only when even the means do not fit does everything scale. The rounding's leftovers are handed to the dishes that lost the most to the floor, so the fridge is filled to the last portion (v2.2.1's first cut left 11 portions unused).
- The prep screen says when the fridge could not hold the day ("冰箱裝不下…") instead of silently shaving.
- **The demand that met an empty shelf is counted.** When a table sits down and something on the menu is sold out, what it would have ordered with a full fridge (`orderItems(g, true)`) is tallied in `R.st.unmet`; the summary shows "賣完・估計少賣 N" for that dish, and the sales history blends sales + short + unmet, so a sold-out dish is recommended *higher* tomorrow, not lower.
- Demand itself, prices, customer counts: untouched. The suggestion's total on Day 33 is the same 260 (the cap).

## Before / after — the Day 33 save, a lazy day (staff work, the player only restocks to the suggestion), 8 seeds each

| | v2.2 | v2.2.1 |
|---|---|---|
| suggestion total | 260 (cap) | 260 (cap) |
| dishes sold out before closing, per day (mean) | **5.0** (2 / 5 / 5 / 3 / 6 / 8 / 6 / 5) | **3.6** (3 / 1 / 4 / 4 / 2 / 9 / 3 / 3) |
| first sell-out, minutes into the 250-minute evening (mean) | 162 | 175 |
| portions sold (mean) | 193 | 188 |
| portions left at closing (mean) | 67 | 71 |
| guests who left because their dish was gone | 0 | 0 |
| most often out | seafood 5×, sparkling 5×, pudding 4×, fruitsoda 4× | seafood 3×, signature 3×, prosciutto 3×, pudding 3× |

Sold-outs per day fall by about a quarter and happen later; nobody leaves hungry in either build (a table whose dish is gone orders something else — the cost of a sell-out is a guest's second choice, not a lost guest). The rest is the fridge: 260 portions for an 18-dish menu that sells ~190 leaves ~70 of buffer, ~4 per dish, against a daily swing of ±3 on a 10-a-day dish. Seed 5 is the reminder — a heavy day sells out nine dishes in both builds.

Scripts: `tools/sims/stock_ab.py` (both builds via `JK_GAME_JS`), logs `stock_before8.log` / `stock_after8.log`; the model-vs-sales table from `tools/sims/demand_model_vs_sales.py`.

## What it does not do, on purpose

- It does not raise the fridge cap or the 冷藏庫's +80 — that is a purchase, and at Day 33 the player owns the largest. A second cold room would be the honest lever for a menu this size; it is listed under deferred items in the report (it is capacity, i.e. economy, not a recommendation fix).
- It does not touch demand, prices or customer counts.

Regression: `stock_suggestion_follows_each_dish_and_counts_the_demand_it_missed` (the shape, the cap behaviour on the Day 33 save, the unmet tally, the summary line, the history blend).
