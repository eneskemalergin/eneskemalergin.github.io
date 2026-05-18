#!/usr/bin/env python3
"""Count tag frequencies from a TOML data file and write a sorted JSON array.

Usage:
    python3 tools/tag-freq.py [INPUT] [OUTPUT] [--table TABLE]

    INPUT   - Path to TOML file           (default: data/projects.toml)
    OUTPUT  - Path to output JSON         (default: data/tag_frequencies.json)
    --table - TOML array table name       (default: projects)

Output format (sorted descending by count):
    [
      {"name": "cli",        "count": 7},
      {"name": "proteomics", "count": 6},
      ...
    ]
"""

import json
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def parse_tags(path: str, table: str) -> list[str]:
    """Read a TOML file and return a flat list of all tag strings."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    tags = []
    for entry in data.get(table, []):
        tags.extend(entry.get("tags", []))
    return tags


def count_frequencies(tags: list[str]) -> list[dict]:
    """Tally tags and return sorted descending by count."""
    counts: dict[str, int] = {}
    for t in tags:
        counts[t] = counts.get(t, 0) + 1
    return sorted(
        [{"name": n, "count": c} for n, c in counts.items()],
        key=lambda x: -x["count"],
    )


def write_json(data: list[dict], path: str) -> None:
    """Write data as pretty-printed JSON."""
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {path} ({len(data)} tags)")


def main() -> None:
    args = sys.argv[1:]
    inp = "data/projects.toml"
    out = "data/tag_frequencies.json"
    table = "projects"

    if len(args) > 0 and not args[0].startswith("--"):
        inp = args[0]
        args = args[1:]
    if len(args) > 0 and not args[0].startswith("--"):
        out = args[0]
        args = args[1:]
    for i, a in enumerate(args):
        if a == "--table" and i + 1 < len(args):
            table = args[i + 1]

    tags = parse_tags(inp, table)
    freqs = count_frequencies(tags)
    write_json(freqs, out)


if __name__ == "__main__":
    main()
