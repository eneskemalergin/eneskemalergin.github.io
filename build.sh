#!/bin/bash
# Pre-process data files, then run zola build/serve.
# Usage: ./build.sh [build|serve]
set -e
cd "$(dirname "$0")"

# ─── Mirror CV PDF from My_CV repo (single source of truth) ───
# The site renders the CV inline via an <iframe> pointing at this local copy,
# which GitHub Pages serves as application/pdf (same-origin, frameable).
# raw.githubusercontent.com can't be framed (X-Frame-Options: deny), so the
# PDF is mirrored at build time instead. Skipped silently offline/CI network
# blips keep any previously fetched copy.
CV_SRC="https://raw.githubusercontent.com/eneskemalergin/My_CV/master/Full_CV_Resonance.pdf"
CV_DIR="static/cv"
CV_DST="$CV_DIR/Full_CV_Resonance.pdf"
mkdir -p "$CV_DIR"
if command -v curl >/dev/null 2>&1; then
    if curl -fsSL --retry 2 "$CV_SRC" -o "$CV_DST.tmp"; then
        mv "$CV_DST.tmp" "$CV_DST"
        echo "Synced CV: $CV_DST"
    else
        rm -f "$CV_DST.tmp"
        if [ -f "$CV_DST" ]; then
            echo "CV sync failed; keeping previous copy at $CV_DST"
        else
            echo "CV sync failed and no local copy exists; /cv/ will show the fallback link"
        fi
    fi
fi

# Sentinel consumed by templates/cv.html to decide iframe vs. fallback link.
if [ -f "$CV_DST" ]; then
    printf 'available = true\nsrc_url = "%s"\n' "$CV_SRC" > data/cv_meta.toml
else
    printf 'available = false\nsrc_url = "%s"\n' "$CV_SRC" > data/cv_meta.toml
fi

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
