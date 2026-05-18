#!/usr/bin/env python3
"""Count tag frequencies from a Zola projects.toml and write a sorted JSON array.

Usage:
    python3 tools/tag-freq.py [INPUT] [OUTPUT]

    INPUT   - Path to projects.toml   (default: data/projects.toml)
    OUTPUT  - Path to output JSON     (default: data/tag_frequencies.json)

Output format (sorted descending by count):
    [
      {"name": "cli",        "count": 7},
      {"name": "proteomics", "count": 6},
      ...
    ]
"""

import json
import re
import sys
from pathlib import Path


def parse_tags(path: str) -> list[dict]:
    """Read projects.toml and return a flat list of all tag strings."""
    content = Path(path).read_text(encoding="utf-8")
    tags = []
    for m in re.finditer(r'tags = \[(.*?)\]', content, re.DOTALL):
        tags.extend(re.findall(r'"([^"]+)"', m.group(1)))
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
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/projects.toml"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/tag_frequencies.json"
    tags = parse_tags(inp)
    freqs = count_frequencies(tags)
    write_json(freqs, out)


if __name__ == "__main__":
    main()
