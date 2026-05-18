#!/usr/bin/env python3
"""Compute log-normalised star-badge colours from a Zola projects.toml.

Reads all projects, applies log normalisation so extreme values
(high or low) don't compress the rest into a narrow band, then
writes a JSON map keyed by project title.

Usage:
    python3 tools/star-colors.py [INPUT] [OUTPUT]

    INPUT   - Path to projects.toml   (default: data/projects.toml)
    OUTPUT  - Path to output JSON     (default: data/project_stars.json)

Output format:
    {
      "SQuAPP": {
        "count": 10,
        "clr":   "#b91c1c",              # light‑mode text / border
        "bdr":   "rgba(185,28,28,0.4)",   # light‑mode border (with alpha)
        "bg":    "rgba(185,28,28,0.08)",  # light‑mode background
        "clr-d": "#dc2626",              # dark‑mode text / border
        "bdr-d": "rgba(220,38,38,0.35)",  # dark‑mode border
        "bg-d":  "rgba(220,38,38,0.08)"   # dark‑mode background
      },
      ...
    }

Colour scale:
    Light mode   #fca5a5  →  #b91c1c   (red‑300 → red‑700)
    Dark mode    #fecaca  →  #dc2626   (red‑100 → red‑600)
"""

import json
import math
import re
import sys
from pathlib import Path


# ── Gradient endpoints (RGB tuples) ──────────────────────────────────────
LIGHT_MIN = (252, 165, 165)   # red-300  #fca5a5
LIGHT_MAX = (185, 28, 28)     # red-700  #b91c1c
DARK_MIN  = (254, 202, 202)   # red-100  #fecaca
DARK_MAX  = (220, 38, 38)     # red-600  #dc2626


def _lerp(a: int, b: int, t: float) -> int:
    """Linearly interpolate between a and b by t in [0, 1]."""
    return int(a + (b - a) * t)


def _interpolate_rgb(c0: tuple[int, int, int],
                     c1: tuple[int, int, int],
                     t: float) -> tuple[int, int, int]:
    """Interpolate two RGB tuples by factor t."""
    return (
        _lerp(c0[0], c1[0], t),
        _lerp(c0[1], c1[1], t),
        _lerp(c0[2], c1[2], t),
    )


def parse_projects(path: str) -> list[dict]:
    """Return [{title, stars}, ...] for every [[projects]] entry."""
    content = Path(path).read_text(encoding="utf-8")
    projects = []
    for section in content.split("[[projects]]")[1:]:
        title = re.search(r'title = "([^"]+)"', section)
        stars = re.search(r'stars = (\d+)', section)
        if title and stars:
            projects.append({
                "title": title.group(1),
                "stars": int(stars.group(1)),
            })
    return projects


def log_intensity(count: int, min_s: int, max_s: int) -> float:
    """Log-normalised intensity in [0, 1] for a star count.

    Uses log(count) to spread low values while preventing a single
    high outlier from compressing the rest of the range.
    Returns 0.5 when all counts are identical (no spread).
    """
    if max_s == min_s:
        return 0.5
    log_min = math.log(min_s) if min_s > 0 else 0
    log_max = math.log(max_s) if max_s > 0 else 1
    log_c = math.log(count) if count > 0 else 0
    return max(0.0, min(1.0, (log_c - log_min) / (log_max - log_min)))


def compute_colors(projects: list[dict]) -> dict:
    """Build a title → colour-data map with light and dark mode values."""
    counts = [p["stars"] for p in projects if p["stars"] > 0]
    if not counts:
        return {}
    min_s, max_s = min(counts), max(counts)

    result: dict[str, dict] = {}
    for p in projects:
        if p["stars"] <= 0:
            continue
        t = log_intensity(p["stars"], min_s, max_s)
        rl, gl, bl = _interpolate_rgb(LIGHT_MIN, LIGHT_MAX, t)
        rd, gd, bd = _interpolate_rgb(DARK_MIN, DARK_MAX, t)

        result[p["title"]] = {
            "count": p["stars"],
            "clr":   f"#{rl:02x}{gl:02x}{bl:02x}",
            "bdr":   f"rgba({rl},{gl},{bl},0.4)",
            "bg":    f"rgba({rl},{gl},{bl},0.08)",
            "clr-d": f"#{rd:02x}{gd:02x}{bd:02x}",
            "bdr-d": f"rgba({rd},{gd},{bd},0.35)",
            "bg-d":  f"rgba({rd},{gd},{bd},0.08)",
        }
    return result


def write_json(data: dict, path: str) -> None:
    """Write data as pretty-printed JSON."""
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {path} ({len(data)} projects)")


def main() -> None:
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/projects.toml"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/project_stars.json"
    projects = parse_projects(inp)
    colors = compute_colors(projects)
    write_json(colors, out)


if __name__ == "__main__":
    main()
