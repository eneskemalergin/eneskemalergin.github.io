#!/bin/bash
# Pre-process data files, then run zola build/serve.
# Usage: ./build.sh [build|serve]
set -e
cd "$(dirname "$0")"

python3 tools/tag-freq.py
python3 tools/star-colors.py

python3 << 'PYEOF'
import json, re
with open('data/publications.toml') as f:
    content = f.read()
counts = {}
for m in re.finditer(r'tags = \[(.*?)\]', content, re.DOTALL):
    for t in re.findall(r'"([^"]+)"', m.group(1)):
        counts[t] = counts.get(t, 0) + 1
freqs = sorted([{"name": n, "count": c} for n, c in counts.items()], key=lambda x: -x["count"])
with open('data/pub_tag_frequencies.json', 'w') as f:
    json.dump(freqs, f, indent=2)
print(f"Generated data/pub_tag_frequencies.json ({len(freqs)} tags)")
PYEOF

cmd="${1:-build}"
zola "$cmd"
