#!/usr/bin/env python3
"""Count tag frequencies from a TOML data file and write a sorted JSON array.

Tags are counted by slug, the way Zola builds tag URLs, so `mzML` and `mzml`
count as one tag under the first spelling seen.

Usage:
    python3 tools/tag-freq.py [INPUT] [OUTPUT] [--table TABLE]

    INPUT   - Path to TOML file           (default: data/projects.toml)
    OUTPUT  - Path to output JSON         (default: data/generated/tag_frequencies.json)
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

from slug import slugify

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
    """Tally tags by slug and return sorted descending by count."""
    counts: dict[str, int] = {}
    names: dict[str, str] = {}
    for t in tags:
        slug = slugify(t)
        counts[slug] = counts.get(slug, 0) + 1
        names.setdefault(slug, t)
    return sorted(
        [{"name": names[s], "count": c} for s, c in counts.items()],
        key=lambda x: -x["count"],
    )


def write_json(data: list[dict], path: str) -> None:
    """Write data as pretty-printed JSON, creating the output directory."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {path} ({len(data)} tags)")


def main() -> None:
    args = sys.argv[1:]
    inp = "data/projects.toml"
    out = "data/generated/tag_frequencies.json"
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
