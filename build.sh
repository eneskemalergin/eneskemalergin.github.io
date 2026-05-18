#!/bin/bash
# Pre-process data files, then run zola build/serve.
# Usage: ./build.sh [build|serve]
set -e
cd "$(dirname "$0")"

python3 tools/tag-freq.py
python3 tools/tag-freq.py data/publications.toml data/pub_tag_frequencies.json --table publications
python3 tools/star-colors.py

cmd="${1:-build}"
zola "$cmd"
