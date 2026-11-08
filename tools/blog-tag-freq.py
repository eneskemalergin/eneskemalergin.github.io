#!/usr/bin/env python3
"""Count how many blog posts carry each tag, for the tag bar on the blog page.

Tags are counted by slug, the way Zola builds tag URLs, so `mzML` and `mzml`
count as one tag under the first spelling seen.

Usage:
    python3 tools/blog-tag-freq.py [OUTPUT]

    OUTPUT - Path to output JSON (default: data/generated/blog_tag_frequencies.json)

Reads the front matter of content/blog/*.md.

Output format (sorted descending by count, then by name):
    [
      {"name": "proteomics", "count": 18},
      {"name": "tooling",    "count": 11},
      ...
    ]
"""

import json
import re
import sys
from pathlib import Path

from slug import slugify

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def post_tags(path: Path) -> list[str]:
    """Return the taxonomy tags from a post's TOML front matter."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\+\+\+\n(.*?)\n\+\+\+", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing +++ front matter")
    front = tomllib.loads(match.group(1))
    return front.get("taxonomies", {}).get("tags", [])


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/generated/blog_tag_frequencies.json")

    counts: dict[str, int] = {}
    names: dict[str, str] = {}

    def add(tag: str) -> None:
        slug = slugify(tag)
        counts[slug] = counts.get(slug, 0) + 1
        names.setdefault(slug, tag)

    for path in sorted(Path("content/blog").glob("*.md")):
        if path.name == "_index.md":
            continue
        for tag in post_tags(path):
            add(tag)

    freqs = sorted(({"name": names[s], "count": c} for s, c in counts.items()),
                   key=lambda x: (-x["count"], x["name"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(freqs, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(freqs)} tags)")


if __name__ == "__main__":
    main()
