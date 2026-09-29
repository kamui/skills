"""Render a scoreboard scatter chart as a standalone SVG for bench/SCOREBOARD.md.

Imported by scoreboard.py; standard library only. Colors are the dataviz reference palette's
first three categorical slots, validated all-pairs in both modes, with the chrome and ink tokens
of that palette. Every point carries a direct label and a <title> tooltip, and the page pairs each
chart with a table, so no value depends on color or hover alone.
"""

from __future__ import annotations

import math
from typing import NamedTuple
from xml.sax.saxutils import escape

THEMES = {
    "light": {"surface": "#fcfcfb", "primary": "#0b0b0b", "secondary": "#52514e", "muted": "#898781",
              "grid": "#e1e0d9", "axis": "#c3c2b7",
              "methods": {"claude-builtin": "#2a78d6", "review-code": "#eb6834", "codex": "#1baf7a"}},
    "dark": {"surface": "#1a1a19", "primary": "#ffffff", "secondary": "#c3c2b7", "muted": "#898781",
             "grid": "#2c2c2a", "axis": "#383835",
             "methods": {"claude-builtin": "#3987e5", "review-code": "#d95926", "codex": "#199e70"}},
}
METHOD_NAMES = {"claude-builtin": "Claude Code built-in", "review-code": "/review-code", "codex": "Codex review"}
WIDTH, HEIGHT = 720, 440
LEFT, RIGHT, TOP, BOTTOM = 64, 150, 84, 60
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"
CHAR_WIDTH = 6.4


class Point(NamedTuple):
    label: str
    method: str
    current: bool
    x: float
    y: float
    tooltip: str


class Axis(NamedTuple):
    title: str
    log: bool
    lo: float
    hi: float
    ticks: tuple
    fmt: object


def position(axis: Axis, value: float, start: float, length: float) -> float:
    if axis.log:
        share = (math.log10(value) - math.log10(axis.lo)) / (math.log10(axis.hi) - math.log10(axis.lo))
    else:
        share = (value - axis.lo) / (axis.hi - axis.lo)
    return start + max(0.0, min(1.0, share)) * length


def frontier(points: list) -> list:
    """Points no other point beats on both axes: lower x and higher y."""
    return sorted((p for p in points if not any(q.x <= p.x and q.y >= p.y and q != p and (q.x < p.x or q.y > p.y)
                                                 for q in points)), key=lambda p: p.x)


def place_labels(anchors: list, bounds: tuple) -> list:
    """Greedy label placement: right of the dot, then left, then above or below, avoiding earlier labels."""
    placed, boxes = [], [(cx - 8, cy - 8, cx + 8, cy + 8) for (cx, cy), _ in anchors]
    x0, y0, x1, y1 = bounds
    for (cx, cy), text in anchors:
        width = len(text) * CHAR_WIDTH
        for dx, dy, anchor in ((10, 4, "start"), (-10, 4, "end"), (10, -12, "start"), (10, 18, "start"),
                               (-10, -12, "end"), (-10, 18, "end"), (10, 32, "start"), (10, -26, "start")):
            left = cx + dx if anchor == "start" else cx + dx - width
            box = (left, cy + dy - 11, left + width, cy + dy + 3)
            inside = box[0] >= x0 and box[2] <= x1 and box[1] >= y0 and box[3] <= y1
            clear = all(box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3] for b in boxes)
            if inside and clear:
                break
        boxes.append(box)
        placed.append((cx + dx, cy + dy, anchor))
    return placed


def scatter(title: str, subtitle: str, points: list, x: Axis, y: Axis, theme: str) -> str:
    t = THEMES[theme]
    plot_w, plot_h = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM
    px = lambda v: position(x, v, LEFT, plot_w)
    py = lambda v: TOP + plot_h - (position(y, v, 0, plot_h))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" '
           f'font-family="{FONT}" role="img" aria-label="{escape(title)}">',
           f"<title>{escape(title)}</title>",
           f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{t["surface"]}"/>',
           f'<text x="{LEFT}" y="24" font-size="15" font-weight="600" fill="{t["primary"]}">{escape(title)}</text>',
           f'<text x="{LEFT}" y="42" font-size="12" fill="{t["secondary"]}">{escape(subtitle)}</text>']
    for value in y.ticks:
        yy = py(value)
        out.append(f'<line x1="{LEFT}" x2="{LEFT + plot_w}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{t["grid"]}" stroke-width="1"/>')
        out.append(f'<text x="{LEFT - 8}" y="{yy + 4:.1f}" font-size="11" text-anchor="end" fill="{t["muted"]}" '
                   f'font-variant-numeric="tabular-nums">{escape(y.fmt(value))}</text>')
    for value in x.ticks:
        xx = px(value)
        out.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{TOP}" y2="{TOP + plot_h}" stroke="{t["grid"]}" stroke-width="1"/>')
        out.append(f'<text x="{xx:.1f}" y="{TOP + plot_h + 18}" font-size="11" text-anchor="middle" fill="{t["muted"]}" '
                   f'font-variant-numeric="tabular-nums">{escape(x.fmt(value))}</text>')
    out.append(f'<line x1="{LEFT}" x2="{LEFT + plot_w}" y1="{TOP + plot_h}" y2="{TOP + plot_h}" stroke="{t["axis"]}" stroke-width="1"/>')
    out.append(f'<text x="{LEFT + plot_w / 2:.1f}" y="{HEIGHT - 18}" font-size="12" text-anchor="middle" '
               f'fill="{t["secondary"]}">{escape(x.title)}</text>')
    out.append(f'<text transform="translate(18 {TOP + plot_h / 2:.1f}) rotate(-90)" font-size="12" text-anchor="middle" '
               f'fill="{t["secondary"]}">{escape(y.title)}</text>')
    out.append(f'<text x="{LEFT + 8}" y="{TOP + 16}" font-size="12" fill="{t["muted"]}">better ↖</text>')
    best = frontier(points)
    if len(best) > 1:
        path = " ".join(f"{'M' if i == 0 else 'L'}{px(p.x):.1f},{py(p.y):.1f}" for i, p in enumerate(best))
        out.append(f'<path d="{path}" fill="none" stroke="{t["muted"]}" stroke-width="1"/>')
    anchors = [((px(p.x), py(p.y)), p.label) for p in points]
    labels = place_labels(anchors, (LEFT, TOP, LEFT + plot_w + RIGHT - 12, TOP + plot_h))
    for p, ((cx, cy), _), (lx, ly, anchor) in zip(points, anchors, labels):
        color = t["methods"][p.method]
        fill = color if p.current else t["surface"]
        out.append(f"<g><title>{escape(p.tooltip)}</title>"
                   f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="transparent"/>'
                   f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{fill}" stroke="{color}" stroke-width="2"/></g>')
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="11" text-anchor="{anchor}" fill="{t["primary"]}">'
                   f"{escape(p.label)}</text>")
    out += legend(t, [m for m in METHOD_NAMES if any(p.method == m for p in points)],
                  any(p.current for p in points) and any(not p.current for p in points))
    return "\n".join(out + ["</svg>", ""])


def legend(t: dict, methods: list, both_kinds: bool) -> list:
    """One row under the subtitle: a swatch per method, then filled against hollow for the run."""
    x, y, out = LEFT, 64, []
    for method in methods:
        name = METHOD_NAMES[method]
        out.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{t["methods"][method]}"/>')
        out.append(f'<text x="{x + 15}" y="{y}" font-size="11" fill="{t["secondary"]}">{escape(name)}</text>')
        x += 15 + len(name) * CHAR_WIDTH + 18
    if both_kinds:
        x += 6
        out.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{t["muted"]}"/>')
        out.append(f'<text x="{x + 15}" y="{y}" font-size="11" fill="{t["secondary"]}">this run</text>')
        x += 15 + 8 * CHAR_WIDTH + 12
        out.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="4" fill="{t["surface"]}" stroke="{t["muted"]}" stroke-width="2"/>')
        out.append(f'<text x="{x + 15}" y="{y}" font-size="11" fill="{t["secondary"]}">earlier run</text>')
    return out
