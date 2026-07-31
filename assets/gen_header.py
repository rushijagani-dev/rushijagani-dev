#!/usr/bin/env python3
"""Generate the profile header SVGs: an agent loop drawn as a ring of
GitHub contribution cells, with a pulse of 'contributions' rotating through
observe -> decide -> act -> validate."""

import math
import sys

CX, CY, R = 980, 160, 92
N = 36                 # cells around the ring
DUR = 6.0              # seconds per full rotation
CARDINALS = {0: "OBSERVE", 9: "DECIDE", 18: "ACT", 27: "VALIDATE"}

THEMES = {
    "dark": dict(
        bg="#0B1220", grid="#1E293B",
        accent="#3FB950", name="#E8EEF7", tagline="#8FA0B8",
        sub="#5C6B84", label="#5C6B84", center="#46556F",
        # GitHub dark contribution scale: L0 (empty) -> L4 (most)
        cells=["#151B23", "#033A16", "#196C2E", "#2EA043", "#56D364"],
    ),
    "light": dict(
        bg="#FFFFFF", grid="#E3E9F1",
        accent="#1A7F37", name="#0B1220", tagline="#475569",
        sub="#7C8BA1", label="#7C8BA1", center="#B8C2D0",
        # GitHub light contribution scale: L0 (empty) -> L4 (most)
        cells=["#EFF2F5", "#ACEEBB", "#4AC26B", "#2DA44E", "#116329"],
    ),
}


def cell_xy(i):
    """Position of cell i, starting at 12 o'clock, going clockwise."""
    a = math.radians(-90 + i * (360.0 / N))
    return CX + R * math.cos(a), CY + R * math.sin(a)


def build(theme_name, preview_head=None):
    t = THEMES[theme_name]
    c = t["cells"]
    out = []

    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" '
        'width="1200" height="320" role="img" '
        'aria-label="Rushi Jagani, senior front-end engineer building agents '
        'that delete manual work">'
    )
    out.append("  <defs>")
    out.append(f'    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">')
    out.append(f'      <path d="M48 0V48M0 48H48" fill="none" stroke="{t["grid"]}" stroke-width="1"/>')
    out.append("    </pattern>")
    out.append('    <radialGradient id="vig" cx="40%" cy="50%" r="80%">')
    out.append(f'      <stop offset="0" stop-color="{t["bg"]}" stop-opacity="0"/>')
    out.append(f'      <stop offset=".5" stop-color="{t["bg"]}" stop-opacity=".5"/>')
    out.append(f'      <stop offset="1" stop-color="{t["bg"]}" stop-opacity="1"/>')
    out.append("    </radialGradient>")
    out.append('    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">')
    out.append(f'      <stop offset="0" stop-color="{t["accent"]}"/>')
    out.append(f'      <stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>')
    out.append("    </linearGradient>")
    out.append("  </defs>")
    out.append("")
    out.append(f'  <rect width="1200" height="320" fill="{t["bg"]}"/>')
    out.append('  <rect width="1200" height="320" fill="url(#grid)" opacity=".5"/>')
    out.append('  <rect width="1200" height="320" fill="url(#vig)"/>')
    out.append("")

    mono = "ui-monospace,Menlo,Consolas,monospace"
    sans = "system-ui,-apple-system,Helvetica,Arial,sans-serif"
    out.append(f'  <text x="80" y="112" font-family="{mono}" font-size="11" letter-spacing="3.2" fill="{t["accent"]}">SENIOR FRONT-END ENGINEER</text>')
    out.append(f'  <text x="80" y="178" font-family="{sans}" font-size="56" font-weight="700" letter-spacing="-1" fill="{t["name"]}">Rushi Jagani</text>')
    out.append('  <rect x="80" y="202" width="160" height="2" fill="url(#rule)"/>')
    out.append(f'  <text x="80" y="240" font-family="{sans}" font-size="18" fill="{t["tagline"]}">Building agents that delete manual work.</text>')
    out.append(f'  <text x="80" y="268" font-family="{mono}" font-size="12" letter-spacing=".4" fill="{t["sub"]}">12 years  ·  React  ·  TypeScript  ·  agents that touch real systems</text>')
    out.append("")

    # --- the loop: a ring of contribution cells ---
    out.append("  <g>")
    step = DUR / N
    # brightness decay of the trailing comet, in fractions of one rotation
    key_times = "0;0.02;0.06;0.10;0.15;1"

    for i in range(N):
        x, y = cell_xy(i)
        size = 11 if i in CARDINALS else 8
        rx = x - size / 2.0
        ry = y - size / 2.0

        if preview_head is not None:
            # bake a static comet for offline rendering checks
            d = (preview_head - i) % N
            lvl = [4, 3, 2, 1][d] if d < 4 else 0
            fill = c[lvl]
            out.append(f'    <rect x="{rx:.1f}" y="{ry:.1f}" width="{size}" height="{size}" rx="2" fill="{fill}"/>')
            continue

        begin = i * step
        values = f'{c[0]};{c[4]};{c[3]};{c[2]};{c[1]};{c[0]}'
        out.append(f'    <rect x="{rx:.1f}" y="{ry:.1f}" width="{size}" height="{size}" rx="2" fill="{c[0]}">')
        out.append(f'      <animate attributeName="fill" values="{values}" keyTimes="{key_times}" dur="{DUR:g}s" begin="{begin:.3f}s" repeatCount="indefinite"/>')
        out.append("    </rect>")

    out.append("")
    out.append(f'    <g font-family="{mono}" font-size="9" letter-spacing="1.8" fill="{t["label"]}">')
    out.append('      <text x="980" y="42" text-anchor="middle">OBSERVE</text>')
    out.append('      <text x="1094" y="164" text-anchor="start">DECIDE</text>')
    out.append('      <text x="980" y="283" text-anchor="middle">ACT</text>')
    out.append('      <text x="866" y="164" text-anchor="end">VALIDATE</text>')
    out.append("    </g>")
    out.append("")
    out.append(f'    <g font-family="{mono}" font-size="10" letter-spacing="2.4" fill="{t["center"]}" text-anchor="middle">')
    out.append('      <text x="980" y="156">AGENT</text>')
    out.append('      <text x="980" y="174">LOOP</text>')
    out.append("    </g>")
    out.append("  </g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    outdir = sys.argv[1]
    for name in THEMES:
        suffix = "-preview" if preview else ""
        path = f"{outdir}/header-{name}{suffix}.svg"
        with open(path, "w") as f:
            f.write(build(name, preview_head=14 if preview else None))
        print("wrote", path)
