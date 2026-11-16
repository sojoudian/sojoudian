# Report: README.md error fixes

**Date**: 2026-11-15
**Sequence**: #01 for the day

## Summary

I found 15 errors in the GitHub profile README (`sojoudian/sojoudian`) and corrected all of them in the local clone at `/Users/maziar/sojoudian/README.md`. The errors were spelling and grammar mistakes, malformed shields.io query parameters, dead or paused image hosts, and style inconsistencies between badges. I also found the cause of the two broken statistics images: the public `github-readme-stats.vercel.app` deployment is paused. The changes are in the working tree. I did not commit or push them.

## What Changed

- `README.md` — modified. 19 insertions, 16 deletions. All 15 fixes are listed below.
- `reports/report-2026-11-15-01-readme-fixes.md` — created. This report.

## Technical Details

Approach: I read the file from GitHub with `gh api repos/sojoudian/sojoudian/contents/README.md`, then compared it with the local clone. I tested each embedded URL with `curl -s -o /dev/null -w '%{http_code}'` to separate real link rot from cosmetic errors. I applied the edits with one Python script that asserts each search string occurs exactly once. This prevents a silent partial replacement.

Fixes applied:

| # | Error | Fix |
|---|---|---|
| 1 | "Faviorite" in the heading | "Favorite" |
| 2 | "Parallel and Distributing" | "Parallel and Distributed Computing" |
| 3 | "on twitter anf" in an HTML comment | "and" |
| 4 | "Pronouns: mɑziɑr" is a pronunciation | Label changed to "Pronunciation" |
| 5 | Visitor badge had `countColorcountColor` with no value | `countColor=%23025a5f` |
| 6 | mongoDB badge had `&logoColor` with no value | `logo=mongodb&logoColor=ADD8E6` |
| 7 | Twitter badge had `countColor`, not a shields.io parameter | Removed |
| 8 | Blog badge used `logo=Maziar`, which does not exist | `logo=hugo` |
| 9 | Four badge URLs started with `?&` (empty first parameter) | `?` |
| 10 | Both `github-readme-stats.vercel.app` images gave HTTP 503 | Commented out with a note (see Issues) |
| 11 | Streak stats used the retired `herokuapp.com` host | `streak-stats.demolab.com` |
| 12 | Nginx badge used `style=flat-square` | `style=flat` |
| 13 | `&nbsp;` missing after the RHEL and Ubuntu badges | Added |
| 14 | AWS badge used `logo=Amazon` (the retail logo) | `logo=amazonwebservices&logoColor=FF9900` |
| 15 | Two links to near-identical repos | Kept `testdome_python` only |

Decision on the blog badge logo: shields.io accepts any Simple Icons slug. `Maziar` is not one, so the logo area stayed empty. I used `hugo` because the badge links to a blog. Any valid slug works here.

Decision on items 10: I did not substitute a third-party fork of github-readme-stats. The community forks are unmaintained and can disappear or leak traffic data. A commented block with instructions is safer than a mirror that may break again.

## Results

Success. All 15 errors are fixed. Verification by HTTP status code after the edits:

| URL | Status |
|---|---|
| `streak-stats.demolab.com/?user=sojoudian&hide_border=true` | 200 |
| Blog badge with `logo=hugo` | 200 |
| AWS badge with `logo=amazonwebservices` | 200 |
| Visitor counter with `countColor=%23025a5f` | 200 |
| mongoDB badge with `logoColor=ADD8E6` | 200 |

Cause of the two broken statistics images: the upstream host returns HTTP 503 with body `The deployment is currently unavailable / DEPLOYMENT_PAUSED`. This is a Vercel platform response, not a GitHub or camo problem. The camo URLs in the question are only GitHub's image proxy. Camo caches the upstream failure, so the images appear broken in the rendered README. The cause is the paused upstream deployment. The public demo instance of `anuraghazra/github-readme-stats` is rate-limited and is paused from time to time.

## Issues / Notes

- The two statistics images stay disabled until a private instance exists. To restore them: fork `anuraghazra/github-readme-stats`, deploy it to Vercel, add a `PAT_1` environment variable with a GitHub personal access token, then put the new host in the commented block in the Analytics section.
- `count_private=true` has an effect only on a private instance with a personal access token. On the public instance the parameter is ignored.
- The changes are not committed. The repository is at commit `d1c4246` ("fix title").
- `streak-stats.demolab.com` is the maintained host of the streak-stats project. The `herokuapp.com` host stopped with the end of the Heroku free tier.
- The `estruyf-github.azurewebsites.net` visitor counter is a personal Azure Function of a third party. It responds now, but it has no availability guarantee.
