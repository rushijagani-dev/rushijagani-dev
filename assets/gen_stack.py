#!/usr/bin/env python3
"""Compose the 'tools of the trade' icon grid.

Brand marks and their official colours come from simple-icons (CC0-1.0);
each is laid on a tile and dropped to 50% opacity so the row reads as one
muted band rather than a bag of competing logos.
"""

import os
import re
import subprocess
import sys

TILE, GAP, PAD, ICON = 52, 12, 8, 26

# grouped for visual rhythm: interface first, then runtime / data / tooling
ROWS = [
    ["typescript", "javascript", "react", "nextdotjs", "html5", "css", "tailwindcss", "mui", "vite"],
    ["nodedotjs", "python", "postgresql", "git", "githubactions", "prettier", "vercel", "ollama"],
]

# brands whose mark is pure black; needs a per-theme stand-in
MONO = {"#000000", "#000"}

THEMES = {
    # compositing toward white mutes much harder than toward dark, so the
    # light grid needs a higher alpha to land at the same perceived weight
    "dark":  dict(tile="#0F172A", stroke="#1E293B", mono="#E8EEF7", opacity=0.5),
    "light": dict(tile="#F6F8FA", stroke="#E2E8F0", mono="#0B1220", opacity=0.68),
}


CACHE = "/tmp/si-cache"


def fetch(slug):
    """Pull the mark from simple-icons, caching locally."""
    os.makedirs(CACHE, exist_ok=True)
    dest = f"{CACHE}/{slug}.svg"
    if not os.path.exists(dest) or os.path.getsize(dest) == 0:
        subprocess.run(
            ["curl", "-sSf", "-o", dest, f"https://cdn.simpleicons.org/{slug}"],
            check=True,
        )
    svg = open(dest).read()
    color = re.search(r'fill="(#[0-9A-Fa-f]{3,6})"', svg)
    path = re.search(r'<path[^>]*\sd="([^"]+)"', svg)
    title = re.search(r"<title>([^<]*)</title>", svg)
    if not path:
        raise SystemExit(f"no path found for {slug}")
    return {
        "slug": slug,
        "color": (color.group(1) if color else "#000000").upper(),
        "d": path.group(1),
        "title": title.group(1) if title else slug,
    }


def build(icons, theme_name):
    t = THEMES[theme_name]
    op = t["opacity"]
    width = PAD * 2 + max(len(r) for r in ROWS) * TILE + (max(len(r) for r in ROWS) - 1) * GAP
    height = PAD * 2 + len(ROWS) * TILE + (len(ROWS) - 1) * GAP

    names = ", ".join(icons[s]["title"] for row in ROWS for s in row)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{names}">'
    ]

    for ri, row in enumerate(ROWS):
        # centre a short row against the longest one
        span = len(row) * TILE + (len(row) - 1) * GAP
        full = max(len(r) for r in ROWS) * TILE + (max(len(r) for r in ROWS) - 1) * GAP
        x0 = PAD + (full - span) / 2.0
        y = PAD + ri * (TILE + GAP)

        for ci, slug in enumerate(row):
            ic = icons[slug]
            x = x0 + ci * (TILE + GAP)
            fill = t["mono"] if ic["color"] in MONO else ic["color"]

            out.append(
                f'  <rect x="{x:g}" y="{y:g}" width="{TILE}" height="{TILE}" rx="10" '
                f'fill="{t["tile"]}" stroke="{t["stroke"]}"/>'
            )
            # simple-icons ship on a 24x24 grid
            scale = ICON / 24.0
            tx = x + (TILE - ICON) / 2.0
            ty = y + (TILE - ICON) / 2.0
            out.append(
                f'  <g transform="translate({tx:g} {ty:g}) scale({scale:g})" '
                f'fill="{fill}" opacity="{op:g}">'
                f'<title>{ic["title"]}</title><path d="{ic["d"]}"/></g>'
            )

    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    outdir = sys.argv[1]
    icons = {}
    for row in ROWS:
        for slug in row:
            icons[slug] = fetch(slug)
            print("fetched", slug, icons[slug]["color"])
    for theme in THEMES:
        path = f"{outdir}/stack-{theme}.svg"
        with open(path, "w") as f:
            f.write(build(icons, theme))
        print("wrote", path)
