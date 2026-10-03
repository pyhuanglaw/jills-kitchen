# Jill's Kitchen 2.1 — Food & Life: what changed, and how it was checked

Foundation: 2.0 (`v2.0`, commit `6a757c2`) with every system intact. 2.1 adds nothing the player has to manage; it adds
things the player sees, in the food and in the life around it. Every item below was judged by one question: can the
player see, feel or experience it during normal play?

## 1. Food
- **特製版** (`SPECIALS`, eight of them). A dish at mastery LV3 can be researched on the 菜單研發 page into its finer version:
  the same recipe and the same cooking (`DISHES[sp.id]` is the base with `special:base`; every renderer that keys on the
  dish goes through `baseOf()`), its own name, price, cost and stock, a `fin` topping the plate carries, and a painted finish
  the player recognises without a label — crab on the fried rice, a burrata on the tomato pasta, mushroom sauce oozing at
  the seam of the burger, truffle on the pumpkin soup, a roasted marrow bone beside the ribeye, cherries under the duck, uni
  lobes on the risotto, matcha dusted over the soufflé (`paintTopping`). 1.8k–7k to research; a special is +10% pull and
  needs LV3 to exist. Two achievements (`special`, `specials4`). The original and the special can both be on the menu.
- **The signature grows** (`sigLv()` from lifetime sold, `SIG_EVO=[0,40,110]`): a second plating at 40 sold (a swoosh of
  the sauce, a tuft of microgreens) and a third at 110 (an edible flower, flakes of gold leaf), +$30 each; the prep screen
  says it happened, the 招牌菜 page says how far to the next one; achievements `sig2`, `sig3`; a Dylan scene.
- **Plates**: the food fills more of the plate and casts a soft shadow; the plates on the tables are bigger (20/22 px); the
  meal goes down while they eat (the plate shows through from the middle out) and sits empty until the bill.
- Guests notice a special on the table (a word, sometimes a photo — 「先拍再吃」 in the album); the first special plated
  is 「第一道特製版」.

## 2. Life
- **The street** (`STREET`, `streetUpd`): while the restaurant is open, people walk the pavement — neighbours, students,
  couples, someone with a dog; umbrellas in the rain (arriving guests carry them too); a scooter (sometimes a delivery
  box) or a bicycle on the road. Some stop at a window or the door and read (the street pieces and the evening lights make
  it likelier: `streetStopP`), think for a moment, and one who likes what they see walks in **as the next scheduled party**
  (`streetJoin`): demand is unchanged, but the guest visibly comes from the street, from where they stood. The summary
  counts 路過進來; achievement `walkin` at 20.
- **The cooks' quiet minutes** (`cookIdleTick`): an idle cook wipes the counter, drinks some water, tastes from a spoon,
  reads the rail, or turns to the cook beside him for a word (a bubble passes between them). Nothing to manage.
- **The pickup side is furnished** on tall screens (`drawKitchenFill`): wire shelving with the plates, jars and the rice
  sack, a work table with the dish rack and glasses by the fridge, the mop and bucket by the door. The oven and bar cooks
  stand apart.
- **Families** (`TYPES.family`): two grown-ups and a child, drawn small (`L.kid`), take a four-top from Day 4 (double on
  weekend evenings); the child watches the cats (「小朋友與貓」 in the album); a word at the table; achievement `families`.
- **Table talk**: a party of two or more passes a little bubble between them while they wait. On a hot day someone at
  the table fans themselves. The child sits in a high chair.
- **The dog waits**: when a passer-by with a dog walks in, the dog waits by the planter on a leash and leaves with them.
- **員工餐**: before opening (看店裡 on the prep screen) the staff eat together at the big table — a pot in the middle,
  bowls and chopsticks, whoever does not fit stands with a bowl (`staffMealList`).
- Dylan: two scenes about the specials and one about the new plating.
- A one-time 2.1 news line on the prep screen.

## 3. Save compatibility
- New save fields are all optional and defaulted on read: `S.firstSpecial`, `S.sigEvoNews`, `S.news21`, `S.stats.walkins`,
  `S.stats.families`; special dishes live in `S.unlocked/S.menu/S.stock/S.xp` like any dish. A pre-2.1 save owns no special
  (the mature fixture in the tests asserts this) and loads unchanged.

## 4. Tests (`tests/run_tests.py`, 55)
- New: `specials_are_a_finer_version_of_a_mastered_dish` (shop offer and the LV3 hint, prices charged, menu/stock/xp,
  achievements, the icons differ from the base, the cooks cook and serve three different specials, tickets name them),
  `the_street_has_passers_by_and_some_walk_in` (walkers, lookers and a vehicle appear; a walk-in replaces the next
  scheduled party and starts on the pavement; walkers keep to the pavement, vehicles to the road).
- Goldens (scenario / frames / cat fingerprint) re-recorded for 2.1: the street draws from the same random stream.

## 5. Performance
- Headless Chromium 390×800, mature save, rain, measured back to back on the same machine: dining room 15.4–15.8 ms of
  JS per frame vs the 2.0 baseline's 15.9–16.1 (the 12.6 in the 2.0 report was a quieter machine); kitchen 5.3–5.8 (5.1–5.7);
  side 3.1–3.8 (4.1–4.3); street with five walkers and a scooter in the rain 3.2 (3.1). Nothing 2.1 adds is per-frame
  heavy: the street is a handful of persons, the toppings are painted once into the dish cache.

## 6. Real-speed smoke (`playtest21.py`)
- A grown 2.0 restaurant (every project, 18 tables, 10 staff), three days at real speed with the person-like actor:
  researching specials on the evenings, looking at the street, the kitchen and the side room. See the report.
