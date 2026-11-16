# Report: Vertical alignment of the three analytics cards

**Date**: 2026-11-15
**Sequence**: #03 for the day

## Summary

The three cards in the Analytics section had three different widths and two different themes. The language card was 340 px wide, the stats card 495 px, and the streak card used the light default theme. I set all three to 495 px and to the tokyonight theme. The three cards now stack as one aligned column.

## What Changed

- `scripts/gen_stats.py` — modified. The language card width is 495 instead of 340. The progress bar is 445 wide instead of 290. The second text column starts at x=260 instead of x=182.
- `assets/top-langs.svg` — regenerated at the new width.
- `assets/stats.svg` — regenerated. The commit count changed from 2,057 to 2,059.
- `README.md` — modified. The streak card URL now has `theme=tokyonight`, `background=1A1B27`, `border=2F3146` and `card_width=495`.
- `reports/report-2026-11-15-03-card-alignment.md` — created. This report.

## Technical Details

The stats card width of 495 px is the reference. It matches the width the original github-readme-stats project uses, so the layout keeps its familiar proportion. I widened the language card to the same value instead of making the stats card narrower. A narrower stats card would push the right-aligned numbers toward the labels.

The streak-stats service accepts a `card_width` parameter, so no fork is necessary. Its `tokyonight` theme uses the same palette as the two generated cards: background `#1a1b27`, title `#70A5FD`, text `#38BDAE`, ring `#BF91F3`. I added explicit `background` and `border` values to protect the look if the service changes its theme definition.

Before the rebase, the local branch was behind. The workflow had committed the two refreshed SVGs directly to `origin/main`. I stashed the local edit, rebased onto `origin/main`, then restored the edit.

## Results

Success. Verification:

| Check | Result |
|---|---|
| Generator runs | Pass. `assets/stats.svg` 3,774 bytes, `assets/top-langs.svg` 3,007 bytes. |
| Both generated cards are 495 px | Pass. Their edges align in a stacked render. |
| Streak card responds at the new URL | Pass. HTTP 200, 7,063 bytes, viewBox `0 0 495 195`. |
| Streak card colors | Pass. The SVG contains `#1a1b27`, `#70A5FD`, `#38BDAE`, `#BF91F3`. |

## Issues / Notes

- The streak card looks empty in a headless Chrome screenshot. Its text starts at `opacity: 0` and fades in with a CSS animation that the screenshot does not wait for. In a real browser it renders correctly. The user's own screenshot of the profile confirms this.
- The changes are not committed. The repository is at commit `03919b9`.
- The push triggers the workflow, because `scripts/gen_stats.py` is in its `paths` filter. The workflow then commits the regenerated SVGs. Pull before your next local change, or the next push is rejected again.
