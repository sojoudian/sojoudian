# Report: Stats card and streak card on one line

**Date**: 2026-11-15
**Sequence**: #04 for the day

## Summary

The stats card and the streak card each used a full row. The Analytics section was three cards tall. I made both cards 400 px wide and 195 px high, then put them on one Markdown line. They now sit side by side. The language card is 804 px wide, which is the width of the pair, so the section is one aligned block of two rows instead of three. The section is about 250 px shorter.

## What Changed

- `scripts/gen_stats.py` — modified.
  - New constants `CARD_W = 400` and `WIDE_W = 804` (two cards plus the 4 px Markdown space).
  - `card()` takes `title_x`, `title_y` and `title_size`. The title is 16 px instead of 18 px.
  - New helper `scaled()`. It scales a glyph around its own centre.
  - `stats_card()`: width 495 → 400, height fixed at 195, row spacing 30 → 23, text 14 px → 13 px, icons at 72%.
  - `langs_card()`: width 495 → 804, two text columns → four, bar is the full card width.
- `assets/stats.svg` — regenerated. 400 x 195.
- `assets/top-langs.svg` — regenerated. 804 x 118.
- `README.md` — modified. The stats image and the streak image are on one line, separated by a space. The streak URL uses `card_width=400`.
- `reports/report-2026-11-15-04-horizontal-cards.md` — created. This report.

## Technical Details

Two images on one Markdown line render as inline elements in one paragraph. GitHub puts one space between them. In the README body font at 16 px that space is about 4 px wide. `WIDE_W = CARD_W * 2 + 4` uses that value, so the language card above ends level with the streak card.

The streak-stats service fixes its height at 195 px at any `card_width`. I therefore fixed the stats card height at 195 as well, instead of computing it from the row count. The two cards now sit level. The row geometry (top 58, step 23, six rows) ends at y=173, which leaves 22 px below the last row.

The language card holds eight languages. Four columns of two rows fit the new width better than two columns of four. The card is 118 px high, down from 190 px.

The icons keep their original geometry. A `transform="translate(…) scale(0.72)"` wrapper shrinks each one around its centre. This avoids a second set of coordinates for the small size.

## Results

Success. Sizes after regeneration:

| File | Size | Before |
|---|---|---|
| `assets/stats.svg` | 400 x 195 | 495 x 252 |
| `assets/top-langs.svg` | 804 x 118 | 495 x 190 |
| streak card (service) | 400 x 195 | 495 x 195 |

A headless Chrome render of the new layout confirms it: the language card spans the full width, and the stats card and streak card sit on one line at equal height. The streak URL returns HTTP 200 with `viewBox='0 0 400 195'`.

Section height: about 500 px, down from about 750 px.

## Issues / Notes

- The changes are not committed.
- The streak card looks empty in a headless screenshot. Its text fades in with a CSS animation. A real browser shows it correctly.
- GitHub camo caches the old images. The new layout can take some minutes to appear after the push.
- On a narrow window GitHub wraps the two images onto separate lines. This is normal reflow, not a layout error.
- The 4 px gap is the width of a space in the GitHub body font. A different font would shift the right edge of the pair by one or two pixels.
