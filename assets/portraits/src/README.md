# Portrait source sheets (supplied by the player)

Each sheet is the player's original. The cut portraits are produced by the tools named here, into
`assets/portraits/<id>.png` (full size) and `assets/portraits/web/<id>.webp` (display size). `tools/portraits.py`
then packs `js/portraits.js`.

| Sheet | Supplied | What is on it | Cut by |
|---|---|---|---|
| `sheet_jill_dylan_8.png` | v2.2 | Top row: Jill — default/warm, cheerful, teasing, gentle. Bottom row: Dylan — default, friendly, playful, gentle | `tools/portraits.py` |
| `sheet_regulars_staff_13.png` | v2.2 | Top row: the regulars 陳伯伯, Mia, 小林, Leo, Sophie, 王先生, 王太太. Bottom row: six named-staff designs (appearance only; the game data stays authoritative for identity) | `tools/portraits.py` (陳伯伯, 小林, Leo, 王先生 and 王太太 still come from here) |
| `sheet_named_staff_18.png` | v2.2.1 | The named guests and staff as cards | `tools/portraits_named.py` |
| `sheet_named_staff_20.png` | v2.2.1 | A twenty-card version of the same sheet | not used (kept as supplied) |
| `sheet_staff_12_v23.png` | v2.3 follow-up | Twelve staff redrawn: 阿德師傅, Marco, 小林師傅, 阿珠姐, Hugo, 阿勇, 小茉, Kai, Nina, 阿哲, 秀琴阿姨, 小彤 | `tools/portraits_staff_v23.py` |
| `sheet_staff_8_v23.png` | v2.3 follow-up | The other eight staff: 老周師傅, 小魏, Momo, 小威, 阿芳, 阿明, Yuki, 阿桂 | `tools/portraits_staff_v23.py` |
| `sophie_mia_sheet_anime_v23.png` | v2.3 follow-up | Sophie × Mia, illustrated; each one's main panel became her portrait | `tools/portraits_regulars_v23.py` |

Also:

- `../jill.png` and `../jill-relaxed.png` are the two single Jill portraits supplied first (clipboard = default, chin-on-hand = relaxed).
- The Lounge four (Evan, 沈晴, 安安, 阿拓) are cut from `docs/v23/lounge_cast_concept.png` and `docs/v23/qing_tuo_ken_du_concept.png` by `tools/portraits_lounge.py`.

Do not redraw, stretch or recolour. Do not use any of these for procedural customers.
