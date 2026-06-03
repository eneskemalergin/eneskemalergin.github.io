#!/bin/bash
# Pre-process data files, then run zola build/serve.
# Usage: ./build.sh [build|serve]
set -e
cd "$(dirname "$0")"

python3 tools/tag-freq.py
python3 tools/tag-freq.py data/publications.toml data/pub_tag_frequencies.json --table publications
python3 tools/star-colors.py

python3 << 'PYEOF'
import json, re, os, tomllib
from collections import Counter

counts = Counter()

# Collect all blog post tags into a set for matching
blog_tags_set = set()
blog_dir = "content/blog"
for fname in os.listdir(blog_dir):
    if not fname.endswith(".md"):
        continue
    with open(os.path.join(blog_dir, fname)) as f:
        content = f.read()
    m = re.search(r'\[taxonomies\]\s*\n(.*?)\n\+\+\+', content, re.DOTALL)
    if m:
        tags = re.findall(r'tags\s*=\s*\[(.*?)\]', m.group(1), re.DOTALL)
        for t in tags:
            for tag in re.findall(r'"([^"]+)"', t):
                blog_tags_set.add(tag)
                counts[tag] += 1

# For each linked project (its "tag" field matches a blog tag), count its "tags"
if os.path.exists("data/projects.toml"):
    with open("data/projects.toml", "rb") as f:
        data = tomllib.load(f)
    for entry in data.get("projects", []):
        if entry.get("tag") and entry["tag"] in blog_tags_set:
            for tag in entry.get("tags", []):
                counts[tag] += 1

# For each linked publication, count its "tags"
if os.path.exists("data/publications.toml"):
    with open("data/publications.toml", "rb") as f:
        data = tomllib.load(f)
    for entry in data.get("publications", []):
        if entry.get("tag") and entry["tag"] in blog_tags_set:
            for tag in entry.get("tags", []):
                counts[tag] += 1

freqs = sorted([{"name": n, "count": c} for n, c in counts.items()], key=lambda x: -x["count"])
with open("data/blog_tag_frequencies.json", "w") as f:
    json.dump(freqs, f, indent=2)
print(f"Generated data/blog_tag_frequencies.json ({len(freqs)} tags)")
PYEOF

cmd="${1:-build}"
if [ "$cmd" = "serve" ]; then
    zola build
    zola serve
else
    zola "$cmd"
fi
