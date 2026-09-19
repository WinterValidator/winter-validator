#!/usr/bin/env python3
"""Refresh Mina Foundation uptime leaderboard data for validators.win.

Fetches the Block Producers Uptime Tracker (https://uptime.minaprotocol.com/),
finds our block producer key, writes uptime.json into the repo root and
commits+pushes to GitHub Pages when the data changed.

The site cannot query uptime.minaprotocol.com client-side (no CORS headers),
so this script runs from ops cron and the site reads same-origin uptime.json.
Exit 0 = success (with or without push), non-zero = failure.
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.request

BP_KEY = "B62qn3aPKv9vuoU1oJdT785bYLbbU1TTrNAXyEfycA17Kx7Miao4whM"
URL = "https://uptime.minaprotocol.com/getPageDataForSnark.php?pageNumber={page}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_PAGES = 8


def fetch_rows():
    rows = []
    for page in range(1, MAX_PAGES + 1):
        req = urllib.request.Request(
            URL.format(page=page), headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        chunk = data.get("row", [])
        if not chunk:
            break
        rows.extend(chunk)
    return rows


def main():
    rows = fetch_rows()
    if not rows:
        print("FAIL: leaderboard returned no rows")
        return 1
    rank, me = None, None
    for i, row in enumerate(rows, 1):
        if row.get("block_producer_key") == BP_KEY:
            rank, me = i, row
            break
    if me is None:
        print(f"FAIL: BP key not found among {len(rows)} rows")
        return 1

    payload = {
        "score": me.get("score"),
        "score_percent": me.get("score_percent"),
        "rank": rank,
        "total": len(rows),
        "updated": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "source": "https://uptime.minaprotocol.com/",
    }
    path = os.path.join(ROOT, "uptime.json")
    new = json.dumps(payload, indent=2) + "\n"
    old = open(path).read() if os.path.exists(path) else None
    if old == new:
        print(f"OK no change: {payload['score_percent']}% rank #{payload['rank']}/{payload['total']}")
        return 0

    with open(path, "w") as fh:
        fh.write(new)
    for args in (
        ["git", "add", "uptime.json"],
        ["git", "commit", "-m", "chore: refresh uptime.json"],
        ["git", "push", "origin", "main"],
    ):
        subprocess.run(args, cwd=ROOT, check=True)
    print(f"OK pushed: {payload['score_percent']}% rank #{payload['rank']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
