# v2.4 rc5 — the release check on the published page

Version 39 of https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (version id `1790862876-a1d4`), read back from the
artifact service after the publish and checked with `tools/sims/live_check.py`:

```
python3 tools/sims/live_check.py LIVE.html v2.4-rc5 tests/saves/player_day61.json docs/evidence/v24_rc5_release
```

- The page built from the tag sits inside the live HTML byte for byte; `js/game.js` appears once; the host adds only
  its document skeleton (552 bytes).
- Played at 390×844 with touch, the player's Day 61 save, the way a player would. The screenshots are listed one line
  each in `live_check.txt`:
  - the title, then OPEN and the prep screen;
  - a whole day with the lazy bot, the five rooms photographed through their tabs;
  - the summary, then the staff page;
  - the next day, then the page reloaded.
- No page errors.

This is T evidence: Chromium on this machine, not a phone, and not the claude.ai frame the player opens it in.

The summary's 4.13 → 3.30 comes from the lazy bot's evening, not from rc5. The same save and seeds on rc4's
`js/game.js` give the same walk-outs. Over five seeds:

| Build | Groups that left angry |
|---|---|
| rc4 | 19 / 18 / 25 / 26 / 25 |
| rc5 | 20 / 21 / 26 / 21 / 20 |

On both builds, the side room fills only after the dining room, near the middle of the evening.
