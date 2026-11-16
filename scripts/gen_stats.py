#!/usr/bin/env python3
"""Generate the two GitHub stat cards for the profile README.

It writes assets/stats.svg and assets/top-langs.svg.
It uses only the Python standard library.

Environment:
  GITHUB_TOKEN  required. A token with the `repo` scope counts private repositories.
  STATS_LOGIN   optional. The GitHub login. The default is sojoudian.
  STATS_OUT     optional. The output directory. The default is assets.
"""

import json
import math
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com/graphql"

# tokyonight theme of anuraghazra/github-readme-stats
THEME = {
    "title": "#70a5fd",
    "icon": "#bf91f3",
    "text": "#38bdae",
    "bg": "#1a1b27",
    "border": "#2f3146",
}

FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Helvetica,Arial,sans-serif"

# The stats card and the streak card sit side by side on one line.
# CARD_W is the width of each one. WIDE_W is the width of the pair, with the
# 4 px gap that Markdown puts between the two images.
CARD_W = 400
WIDE_W = CARD_W * 2 + 4

# Fallback colors for languages that the API gives no color for.
FALLBACK_COLOR = "#858585"


def gql(query, variables, token):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Authorization": "bearer " + token,
            "Content-Type": "application/json",
            "User-Agent": "profile-stats-generator",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        sys.exit("GitHub API error %s: %s" % (exc.code, exc.read()[:400].decode("utf-8", "replace")))
    if "errors" in payload:
        sys.exit("GraphQL error: " + json.dumps(payload["errors"])[:600])
    return payload["data"]


STATS_QUERY = """
query($login:String!,$after:String){
  user(login:$login){
    name
    login
    followers{totalCount}
    contributionsCollection{
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestReviewContributions
    }
    repositoriesContributedTo(first:1,contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]){totalCount}
    pullRequests(first:1){totalCount}
    openIssues:issues(states:OPEN){totalCount}
    closedIssues:issues(states:CLOSED){totalCount}
    repositories(first:100,after:$after,ownerAffiliations:OWNER,isFork:false){
      totalCount
      pageInfo{hasNextPage endCursor}
      nodes{
        name
        stargazerCount
        languages(first:12,orderBy:{field:SIZE,direction:DESC}){
          edges{size node{name color}}
        }
      }
    }
  }
}
"""


def collect(login, token):
    after = None
    stars = 0
    langs = {}
    head = None
    while True:
        data = gql(STATS_QUERY, {"login": login, "after": after}, token)["user"]
        if data is None:
            sys.exit("No such user: " + login)
        if head is None:
            head = data
        repos = data["repositories"]
        for node in repos["nodes"]:
            stars += node["stargazerCount"]
            for edge in node["languages"]["edges"]:
                name = edge["node"]["name"]
                entry = langs.setdefault(name, {"size": 0, "color": edge["node"]["color"]})
                entry["size"] += edge["size"]
                if entry["color"] is None:
                    entry["color"] = edge["node"]["color"]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]

    contrib = head["contributionsCollection"]
    stats = {
        "name": head["name"] or head["login"],
        "stars": stars,
        "commits": contrib["totalCommitContributions"] + contrib["restrictedContributionsCount"],
        "prs": head["pullRequests"]["totalCount"],
        "reviews": contrib["totalPullRequestReviewContributions"],
        "issues": head["openIssues"]["totalCount"] + head["closedIssues"]["totalCount"],
        "contributed": head["repositoriesContributedTo"]["totalCount"],
        "repos": head["repositories"]["totalCount"],
        "followers": head["followers"]["totalCount"],
    }
    return stats, langs


# ---------------------------------------------------------------- drawing ---


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def card(width, height, title, body, title_x=20, title_y=28, title_size=16):
    return """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{t}">
  <rect x="0.5" y="0.5" width="{w1}" height="{h1}" rx="4.5" fill="{bg}" stroke="{border}"/>
  <text x="{tx}" y="{ty}" font-family="{font}" font-size="{ts}" font-weight="600" fill="{title}">{t}</text>
{body}
</svg>
""".format(
        w=width,
        h=height,
        w1=width - 1,
        h1=height - 1,
        t=esc(title),
        tx=title_x,
        ty=title_y,
        ts=title_size,
        bg=THEME["bg"],
        border=THEME["border"],
        font=FONT,
        title=THEME["title"],
        body=body,
    )


def scaled(markup, x, y, factor):
    """Scale markup around the point (x, y)."""
    return '<g transform="translate(%.2f,%.2f) scale(%s)">%s</g>' % (
        x * (1 - factor),
        y * (1 - factor),
        factor,
        markup,
    )


def star_path(cx, cy, outer, inner):
    pts = []
    for i in range(10):
        r = outer if i % 2 == 0 else inner
        angle = math.radians(-90 + i * 36)
        pts.append("%.2f,%.2f" % (cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return '<polygon points="%s" fill="%s"/>' % (" ".join(pts), THEME["icon"])


def icon(kind, x, y):
    """A small glyph, drawn from plain shapes only. (x, y) is its centre."""
    c = THEME["icon"]
    if kind == "star":
        return star_path(x, y, 8, 3.4)
    if kind == "commit":
        return (
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>'
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>'
            '<circle cx="%s" cy="%s" r="3.6" fill="none" stroke="%s" stroke-width="2"/>'
            % (x - 8, y, x - 4, y, c, x + 4, y, x + 8, y, c, x, y, c)
        )
    if kind == "pr":
        return (
            '<circle cx="%s" cy="%s" r="2.6" fill="%s"/>'
            '<circle cx="%s" cy="%s" r="2.6" fill="%s"/>'
            '<circle cx="%s" cy="%s" r="2.6" fill="%s"/>'
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>'
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>'
            % (
                x - 6, y - 6, c,
                x - 6, y + 6, c,
                x + 6, y - 6, c,
                x - 6, y - 4, x - 6, y + 4, c,
                x - 4, y - 6, x + 4, y - 6, c,
            )
        )
    if kind == "issue":
        return (
            '<circle cx="%s" cy="%s" r="7" fill="none" stroke="%s" stroke-width="2"/>'
            '<circle cx="%s" cy="%s" r="2.2" fill="%s"/>' % (x, y, c, x, y, c)
        )
    if kind == "repo":
        return (
            '<rect x="%s" y="%s" width="13" height="14" rx="2" fill="none" stroke="%s" stroke-width="2"/>'
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>'
            % (x - 7, y - 7, c, x - 3, y - 7, x - 3, y + 7, c)
        )
    if kind == "review":
        return (
            '<rect x="%s" y="%s" width="16" height="11" rx="2" fill="none" stroke="%s" stroke-width="2"/>'
            '<polyline points="%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="2"/>'
            % (x - 8, y - 7, c, x - 4, y - 2, x - 1, y + 1, x + 5, y - 5, c)
        )
    return ""


def stats_card(stats):
    rows = [
        ("star", "Total Stars Earned", stats["stars"]),
        ("commit", "Total Commits", stats["commits"]),
        ("pr", "Total PRs", stats["prs"]),
        ("review", "Total PR Reviews", stats["reviews"]),
        ("issue", "Total Issues", stats["issues"]),
        ("repo", "Contributed to", stats["contributed"]),
    ]
    # The height matches the streak card, so the two sit level on one line.
    width, height, top, step = CARD_W, 195, 58, 23
    parts = []
    for i, (kind, label, value) in enumerate(rows):
        y = top + i * step
        parts.append("  <g>")
        parts.append("    " + scaled(icon(kind, 28, y - 4), 28, y - 4, 0.72))
        parts.append(
            '    <text x="44" y="%s" font-family="%s" font-size="13" font-weight="600" fill="%s">%s:</text>'
            % (y, FONT, THEME["text"], esc(label))
        )
        parts.append(
            '    <text x="%s" y="%s" font-family="%s" font-size="13" font-weight="600" fill="%s" text-anchor="end">%s</text>'
            % (width - 20, y, FONT, THEME["text"], f"{value:,}")
        )
        parts.append("  </g>")
    title = "%s's GitHub Stats" % stats["name"]
    return card(width, height, title, "\n".join(parts))


def langs_card(langs, limit=8):
    items = sorted(langs.items(), key=lambda kv: kv[1]["size"], reverse=True)[:limit]
    total = sum(entry["size"] for _, entry in items) or 1
    width, bar_x, bar_y = WIDE_W, 20, 48
    bar_w = width - 2 * bar_x
    parts = ['  <g>', '    <rect x="%s" y="%s" width="%s" height="8" rx="4" fill="#2f3146"/>' % (bar_x, bar_y, bar_w)]
    offset = 0.0
    for name, entry in items:
        share = entry["size"] / total
        seg = max(share * bar_w, 2.0)
        if offset + seg > bar_w:
            seg = bar_w - offset
        parts.append(
            '    <rect x="%.2f" y="%s" width="%.2f" height="8" fill="%s"/>'
            % (bar_x + offset, bar_y, seg, entry["color"] or FALLBACK_COLOR)
        )
        offset += seg
    parts.append('    <rect x="%s" y="%s" width="%s" height="8" rx="4" fill="none" stroke="%s"/>'
                 % (bar_x, bar_y, bar_w, THEME["bg"]))
    parts.append("  </g>")

    columns = 4
    rows_per_col = math.ceil(len(items) / columns)
    col_w = (width - 2 * bar_x) // columns
    for i, (name, entry) in enumerate(items):
        x = bar_x + (i // rows_per_col) * col_w
        y = 80 + (i % rows_per_col) * 24
        pct = entry["size"] / total * 100
        parts.append("  <g>")
        parts.append('    <circle cx="%s" cy="%s" r="5" fill="%s"/>'
                     % (x + 5, y - 4, entry["color"] or FALLBACK_COLOR))
        parts.append(
            '    <text x="%s" y="%s" font-family="%s" font-size="12" font-weight="400" fill="%s">%s %.2f%%</text>'
            % (x + 16, y, FONT, THEME["text"], esc(name), pct)
        )
        parts.append("  </g>")
    height = 80 + rows_per_col * 24 - 10
    return card(width, height, "Most Used Languages", "\n".join(parts))


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("STATS_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set.")
    login = os.environ.get("STATS_LOGIN", "sojoudian")
    out = os.environ.get("STATS_OUT", "assets")
    os.makedirs(out, exist_ok=True)

    stats, langs = collect(login, token)
    files = {
        os.path.join(out, "stats.svg"): stats_card(stats),
        os.path.join(out, "top-langs.svg"): langs_card(langs),
    }
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        print("wrote %s (%d bytes)" % (path, len(content.encode())))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
