#!/usr/bin/env python3
"""
Custom GitHub Contribution Snake Generator.

Generates animated SVGs where a snake traverses the contribution grid
and changes contribution block colors to random vibrant colors instead
of eating them. Supports light and dark themes.

Usage (requires env vars):
    GITHUB_TOKEN=ghp_xxx GITHUB_USER=YourUsername python generate_snake.py
"""

import json
import os
import sys
import random
import urllib.request

# ── Visual Configuration ─────────────────────────────────────────
CELL_SIZE = 11
CELL_GAP = 3
CELL_RX = 2
PAD_L, PAD_T, PAD_R, PAD_B = 16, 16, 16, 16
ROWS = 7  # days of the week

DURATION = 25       # total animation cycle (seconds)
TRAVEL_PCT = 85     # percent of cycle for traversal

SNAKE_COLOR = "#FF4757"

VIBRANT = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFEAA7", "#DDA0DD",
    "#FF9FF3", "#54A0FF", "#5F27CD", "#FF6348", "#FFC312",
    "#C4E538", "#ED4C67", "#B53471", "#F97F51", "#55E6C1",
    "#25CCF7", "#FD7272", "#58B19F", "#EA8685", "#B8E994",
    "#78E08F", "#38ADA9", "#82CCDD", "#FDA7DF", "#EAB543",
]

THEMES = {
    "light": {"bg": "#ffffff", "empty": "#ebedf0"},
    "dark":  {"bg": "#0d1117", "empty": "#161b22"},
}


# ── GitHub GraphQL API ───────────────────────────────────────────
def fetch_contributions(user, token):
    """Fetch contribution calendar data from GitHub's GraphQL API."""
    query = (
        "query($u:String!){user(login:$u){contributionsCollection"
        "{contributionCalendar{totalContributions weeks{contributionDays"
        "{contributionCount date color weekday}}}}}}"
    )
    payload = json.dumps({"query": query, "variables": {"u": user}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "contribution-snake-generator",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API error: {e.code} {e.reason}")

    if "errors" in data:
        sys.exit(f"GraphQL errors: {data['errors']}")

    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["weeks"], cal["totalContributions"]


# ── Grid Helpers ─────────────────────────────────────────────────
def build_grid(weeks):
    """Convert weeks data into a grid dict: (row, col) -> cell info."""
    grid = {}
    for col_idx, week in enumerate(weeks):
        for day in week["contributionDays"]:
            grid[(day["weekday"], col_idx)] = {
                "count": day["contributionCount"],
                "color": day["color"],
            }
    return grid, len(weeks)


def cell_xy(row, col):
    """Get top-left pixel position of a grid cell."""
    return (PAD_L + col * (CELL_SIZE + CELL_GAP),
            PAD_T + row * (CELL_SIZE + CELL_GAP))


def cell_center(row, col):
    """Get center pixel position of a grid cell."""
    x, y = cell_xy(row, col)
    return x + CELL_SIZE / 2, y + CELL_SIZE / 2


def snake_path(cols):
    """Generate zigzag path through the grid (like reading/scanning)."""
    path = []
    for row in range(ROWS):
        rng = range(cols) if row % 2 == 0 else range(cols - 1, -1, -1)
        path.extend((row, c) for c in rng)
    return path


# ── SVG Generator ────────────────────────────────────────────────
def make_svg(weeks, theme_name):
    """Generate the full animated SVG string."""
    theme = THEMES[theme_name]
    grid, cols = build_grid(weeks)
    path = snake_path(cols)
    total_cells = len(path)

    # Canvas dimensions
    svg_w = PAD_L + cols * (CELL_SIZE + CELL_GAP) - CELL_GAP + PAD_R
    svg_h = PAD_T + ROWS * (CELL_SIZE + CELL_GAP) - CELL_GAP + PAD_B

    # Deterministic random color assignments for contribution cells
    rng = random.Random(42)
    color_map = {}
    for r, c in path:
        cell = grid.get((r, c))
        if cell and cell["count"] > 0:
            color_map[(r, c)] = rng.choice(VIBRANT)

    # Build motion path string for snake head
    motion_parts = []
    for i, (r, c) in enumerate(path):
        cx, cy = cell_center(r, c)
        cmd = "M" if i == 0 else "L"
        motion_parts.append(f"{cmd}{cx:.0f},{cy:.0f}")
    motion_d = " ".join(motion_parts)

    # Animation timing sync values
    dur = f"{DURATION}s"
    tp = TRAVEL_PCT / 100        # 0.85
    kp = "0;1;1;0;0"
    kt = f"0;{tp};{tp + 0.02};0.96;1"

    # ── Start building SVG ──
    lines = []
    add = lines.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}"'
        f' viewBox="0 0 {svg_w} {svg_h}">')
    add(f'<rect width="{svg_w}" height="{svg_h}" fill="{theme["bg"]}" rx="6"/>')

    # Glow filter for snake
    add('<defs>')
    add('  <filter id="glow">')
    add('    <feGaussianBlur stdDeviation="2.5" result="blur"/>')
    add('    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>')
    add('  </filter>')
    add('</defs>')

    # ── CSS Animations ──
    add('<style>')

    # Per-cell color-change keyframes
    for idx, (r, c) in enumerate(path):
        if (r, c) not in color_map:
            continue
        original = grid[(r, c)]["color"]
        target = color_map[(r, c)]
        # Calculate when this cell activates (as % of total animation)
        act = (idx / total_cells) * TRAVEL_PCT
        # Keyframes: original → white flash → vibrant → hold → reset to original
        add(f'@keyframes c{r}_{c}{{'
            f'0%,{act:.1f}%{{fill:{original}}}'
            f'{act + 0.3:.1f}%{{fill:#fff}}'
            f'{act + 0.8:.1f}%,{TRAVEL_PCT + 3}%{{fill:{target}}}'
            f'92%,100%{{fill:{original}}}}}')
        add(f'.c{r}_{c}{{animation:c{r}_{c} {dur} ease infinite}}')

    # Snake visibility (hide during reset/snap-back)
    add(f'@keyframes svis{{'
        f'0%,{TRAVEL_PCT}%{{opacity:1}}'
        f'{TRAVEL_PCT + 2}%,96%{{opacity:0}}'
        f'98%,100%{{opacity:1}}}}')
    add(f'.snake{{animation:svis {dur} ease infinite}}')

    add('</style>')

    # ── Grid Cells ──
    for col_idx in range(cols):
        for row_idx in range(ROWS):
            x, y = cell_xy(row_idx, col_idx)
            cell = grid.get((row_idx, col_idx))
            if cell and cell["count"] > 0:
                cls = f' class="c{row_idx}_{col_idx}"' if (row_idx, col_idx) in color_map else ''
                add(f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}"'
                    f' rx="{CELL_RX}" fill="{cell["color"]}"{cls}/>')
            else:
                add(f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}"'
                    f' rx="{CELL_RX}" fill="{theme["empty"]}"/>')

    # ── Snake ──
    motion_attrs = (
        f'dur="{dur}" repeatCount="indefinite" calcMode="linear"'
        f' keyPoints="{kp}" keyTimes="{kt}" path="{motion_d}"'
    )

    add(f'<g class="snake" filter="url(#glow)">')
    # Snake head with eyes
    add(f'  <g>')
    add(f'    <animateMotion {motion_attrs}/>')
    add(f'    <circle r="5.5" fill="{SNAKE_COLOR}" opacity="0.9"/>')
    add(f'    <circle cx="-1.8" cy="-2" r="1.4" fill="#fff"/>')
    add(f'    <circle cx="1.8" cy="-2" r="1.4" fill="#fff"/>')
    add(f'    <circle cx="-1.8" cy="-2.2" r="0.6" fill="#1a1a2e"/>')
    add(f'    <circle cx="1.8" cy="-2.2" r="0.6" fill="#1a1a2e"/>')
    add(f'  </g>')
    add(f'</g>')

    add('</svg>')
    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────
def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    user = os.environ.get("GITHUB_USER", "")

    if not token:
        sys.exit("Error: GITHUB_TOKEN environment variable is not set.")
    if not user:
        sys.exit("Error: GITHUB_USER environment variable is not set.")

    print(f"🐍 Fetching contribution data for @{user}...")
    weeks, total = fetch_contributions(user, token)
    print(f"   Found {len(weeks)} weeks, {total:,} total contributions\n")

    os.makedirs("dist", exist_ok=True)

    for theme in ("light", "dark"):
        svg = make_svg(weeks, theme)
        suffix = "-dark" if theme == "dark" else ""
        out_path = f"dist/github-contribution-grid-snake{suffix}.svg"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"   ✓ {out_path} ({len(svg):,} bytes)")

    print("\n✅ Snake SVGs generated successfully!")


if __name__ == "__main__":
    main()
