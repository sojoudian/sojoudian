# Report: Self-hosted GitHub stat cards

**Date**: 2026-11-15
**Sequence**: #02 for the day

## Summary

The two statistics images in the profile README used `github-readme-stats.vercel.app`. That public deployment is paused and gives HTTP 503. I replaced it with a generator that runs inside this repository. A Python script calls the GitHub GraphQL API and writes two SVG cards into `assets/`. A GitHub Actions workflow runs the script each day and commits the new SVGs. The README now points to those two files. There is no third-party runtime host, so the images cannot break again from an external outage. I ran the generator locally and rendered the result to confirm the cards look correct.

## What Changed

- `scripts/gen_stats.py` — created. The card generator. Standard library only, no dependencies.
- `.github/workflows/stats.yml` — created. A daily cron workflow that regenerates and commits the cards.
- `assets/stats.svg` — created. The statistics card, 3.7 KB.
- `assets/top-langs.svg` — created. The language card, 3.0 KB.
- `README.md` — modified. The Analytics section now uses `./assets/top-langs.svg` and `./assets/stats.svg`.
- `reports/report-2026-11-15-02-stat-cards.md` — created. This report.

## Technical Details

**Data.** One GraphQL query gets the user node, with repositories paginated 100 at a time. Stars are the sum of `stargazerCount` over the owned, non-fork repositories. Commits are `totalCommitContributions` plus `restrictedContributionsCount`, which is the same formula the original project uses. Languages are the sum of `languages.edges.size` over all owned repositories, with the color the API supplies for each language.

**Rendering.** The script writes SVG text directly. It does not use a template engine or a drawing library. The icons are plain shapes — circles, lines, rectangles and one computed five-point polygon — instead of copied Octicon path data. A hand-copied path can be malformed and is hard to verify; generated geometry is always valid. The theme is the tokyonight palette of the original project, so the cards match the former look: background `#1a1b27`, title `#70a5fd`, text `#38bdae`, icons `#bf91f3`.

**Authorship.** The workflow does not use `git commit`. It uploads each file with `gh api --method PUT .../contents/<path>`. This avoids `git config user.*`, which your global instructions forbid. The commit author is the owner of the token. With a `STATS_TOKEN` secret the author is you; with the default `GITHUB_TOKEN` the author is `github-actions[bot]`.

**Private repositories.** The old URLs had `count_private=true`. That parameter has an effect only when the token can read private data. The workflow reads `secrets.STATS_TOKEN` first and falls back to `secrets.GITHUB_TOKEN`. Add `STATS_TOKEN` as a classic personal access token with the `repo` scope to include private repositories.

## Results

Success. Local run output:

```
wrote assets/stats.svg (3774 bytes)
wrote assets/top-langs.svg (3005 bytes)
{
  "name": "Maziar",
  "stars": 198,
  "commits": 2057,
  "prs": 2,
  "reviews": 0,
  "issues": 6,
  "contributed": 53,
  "repos": 266,
  "followers": 884
}
```

Verification:

| Check | Result |
|---|---|
| Generator runs with a real token | Pass |
| Both SVGs render in headless Chrome | Pass. Bar, colors, icons and numbers are correct. |
| Workflow YAML parses | Pass |
| Commit step shell syntax (`bash -n`) | Pass |

The card shows six rows: stars 198, commits 2,057, PRs 2, PR reviews 0, issues 6, contributed to 53. The language card shows eight languages with a stacked bar: Go 44.45%, HTML 18.44%, Python 16.24%, JavaScript 6.30%, Java 6.28%, TypeScript 3.12%, CSS 2.93%, Shell 2.24%.

## Issues / Notes

- The files are not committed. The images stay broken until you push `assets/`, `scripts/` and `.github/`.
- GitHub proxies README images through camo, which caches them. A refreshed card can take some minutes to appear.
- The generator counts only non-fork repositories you own. Forks would distort the language shares.
- `STATS_TOKEN` is optional. Without it the cards show public data only, and the commits come from `github-actions[bot]`.
- The cron time is 04:17 UTC. GitHub delays scheduled workflows under load, so the exact minute is not guaranteed.
- The old Vercel URLs are deleted from the README, not commented out.
