# Report: Visitor badge moved to the contact row

**Date**: 2026-11-15
**Sequence**: #05 for the day

## Summary

The visitor counter was the first item of the Analytics section. It used a line of its own. I moved it into the centered contact row of "How to reach me", after the LinkedIn badge. The three badges — Twitter, LinkedIn, Visitors — now sit on one horizontal line. The Analytics section starts with the language card.

## What Changed

- `README.md` — modified.
  - Added the visitor image to the second `<p align='center'>` block, after the LinkedIn link, with `&nbsp;&nbsp;` spacing and an `alt` attribute.
  - Deleted the `![Profile Views](...)` line under the Analytics heading.
- `reports/report-2026-11-15-05-visitor-badge-move.md` — created. This report.

## Technical Details

The contact row is an HTML `<p>` with `align='center'`. Images inside it are inline elements, so a new `<img>` joins the same line. The spacing pattern `&nbsp;&nbsp;` is the one the other badges use, so the gaps stay equal.

The counter keeps the same URL and the same `countColor=%23025a5f`. The Azure function renders it in the shields.io `for-the-badge` style, which matches the Twitter and LinkedIn badges beside it.

The badge is not wrapped in an `<a>`. It is a counter, not a link, so it has no target.

## Results

Success. The contact row now holds three badges in one line. The Analytics heading is followed directly by the language card, then by the stats and streak pair.

The row is about 30 px shorter than before, because the counter no longer uses a line of its own.

## Issues / Notes

- The changes are not committed.
- The counter increases on each view of the profile. Its width grows by a few pixels when the number passes 100,000. The centered row absorbs this.
- `estruyf-github.azurewebsites.net` is a third-party Azure Function. It has no availability guarantee.
- On a narrow window the three badges wrap onto two lines. This is normal reflow.
