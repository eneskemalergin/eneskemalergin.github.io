#!/usr/bin/env python3
"""Compute log-normalised star-badge levels from a Zola projects.toml.

Reads all projects, applies log normalisation so extreme values (high or low)
don't compress the rest into a narrow band, and maps each star count to a
level from 1 to 5. The stylesheet draws the levels: the badge text keeps one
readable color, and a higher level gets a stronger fill and border.

Usage:
    python3 tools/star-levels.py [INPUT] [OUTPUT]

    INPUT   - Path to projects.toml   (default: data/projects.toml)
    OUTPUT  - Path to output JSON     (default: data/generated/project_stars.json)

Output format:
    {
      "SQuAPP": 4,
      ...
    }
"""

import math
import sys
import tomllib

from common import write_json

LEVELS = 5


def parse_projects(path: str) -> list[dict]:
    """Return [{title, stars}, ...] for every [[projects]] entry."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return [
        {"title": p["title"], "stars": p["stars"]}
        for p in data.get("projects", [])
        if "title" in p and "stars" in p
    ]


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


def compute_levels(projects: list[dict]) -> dict:
    """Build a title -> level map for projects with stars."""
    counts = [p["stars"] for p in projects if p["stars"] > 0]
    if not counts:
        return {}
    min_s, max_s = min(counts), max(counts)
    return {
        p["title"]: 1 + round(log_intensity(p["stars"], min_s, max_s) * (LEVELS - 1))
        for p in projects
        if p["stars"] > 0
    }


def main() -> None:
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/projects.toml"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/generated/project_stars.json"
    write_json(compute_levels(parse_projects(inp)), out, "projects")


if __name__ == "__main__":
    main()
