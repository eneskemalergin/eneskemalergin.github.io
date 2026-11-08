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

import sys
import tomllib

from common import slugify, write_json


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
    write_json(freqs, out, "tags")


if __name__ == "__main__":
    main()
