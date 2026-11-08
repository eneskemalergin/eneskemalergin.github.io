#!/bin/bash
# Pre-process data files, then run zola build/serve.
# Usage: ./build.sh [build|serve]
set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3.12}"
# mise.toml pins the Zola version; the build refuses any other.
ZOLA_VERSION="$(sed -n 's/^zola = "\(.*\)"$/\1/p' mise.toml)"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python 3.12 is required. Set PYTHON to its executable if needed." >&2
    exit 1
fi

PYTHON_MAJOR_MINOR="$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [ "$PYTHON_MAJOR_MINOR" != "3.12" ]; then
    echo "Python 3.12 is required; found $PYTHON_MAJOR_MINOR." >&2
    exit 1
fi

if command -v mise >/dev/null 2>&1; then
    ZOLA=(mise exec -- zola)
elif command -v zola >/dev/null 2>&1; then
    ZOLA=(zola)
else
    echo "Zola $ZOLA_VERSION is required. Run 'mise install' or install that exact version." >&2
    exit 1
fi

ZOLA_ACTUAL_VERSION="$("${ZOLA[@]}" --version 2>/dev/null || true)"
case "$ZOLA_ACTUAL_VERSION" in
    "zola $ZOLA_VERSION"*) ;;
    *)
        echo "Zola $ZOLA_VERSION is required; found $ZOLA_ACTUAL_VERSION." >&2
        exit 1
        ;;
esac

# Derived data goes to data/generated/, which Git ignores.
mkdir -p data/generated

# CV PDF, pinned to a commit of its source repository.
# data/cv.toml names the repository, commit, and file. The site renders the
# CV inline via an <iframe> pointing at a local copy, which GitHub Pages serves
# same-origin; raw.githubusercontent.com can't be framed (X-Frame-Options:
# deny). A download is used only if it is a PDF under CV_MAX_BYTES. A local
# copy of the pinned commit is reused, so offline rebuilds keep working.
# In CI a failed or invalid download stops the build; locally the /cv/ page
# falls back to a GitHub link and the build prints a warning.
CV_FIELDS="$("$PYTHON" -c '
import re, tomllib
cv = tomllib.load(open("data/cv.toml", "rb"))
assert re.fullmatch(r"[\w.-]+/[\w.-]+", cv["repo"]), "data/cv.toml: repo must be OWNER/NAME"
assert re.fullmatch(r"[0-9a-f]{40}", cv["commit"]), "data/cv.toml: commit must be a full SHA"
assert re.fullmatch(r"[\w./-]+", cv["path"]) and ".." not in cv["path"], "data/cv.toml: bad path"
print(cv["repo"], cv["commit"], cv["path"])')"
read -r CV_REPO CV_COMMIT CV_PATH <<< "$CV_FIELDS"
CV_SRC="https://raw.githubusercontent.com/$CV_REPO/$CV_COMMIT/$CV_PATH"
CV_DIR="static/cv"
CV_DST="$CV_DIR/$(basename "$CV_PATH")"
CV_META="data/generated/cv_meta.toml"
CV_MAX_BYTES=10000000
mkdir -p "$CV_DIR"

cv_valid() {
    [ -s "$1" ] && [ "$(head -c 5 "$1")" = "%PDF-" ] && [ "$(wc -c < "$1")" -le "$CV_MAX_BYTES" ]
}

cv_ok=false
if [ -f "$CV_DST" ] && [ -f "$CV_META" ] \
    && grep -qx 'available = true' "$CV_META" \
    && grep -qx "commit = \"$CV_COMMIT\"" "$CV_META" \
    && cv_valid "$CV_DST"; then
    cv_ok=true
    echo "CV: using local copy of $CV_COMMIT"
elif command -v curl >/dev/null 2>&1 \
    && curl -fsSL --retry 2 "$CV_SRC" -o "$CV_DST.tmp" \
    && cv_valid "$CV_DST.tmp"; then
    mv "$CV_DST.tmp" "$CV_DST"
    cv_ok=true
    echo "CV: downloaded $CV_COMMIT"
else
    rm -f "$CV_DST.tmp"
    if [ "${CI:-}" = "true" ]; then
        echo "CV download failed or is not a PDF under $CV_MAX_BYTES bytes: $CV_SRC" >&2
        exit 1
    fi
    echo "WARNING: CV download failed or invalid; /cv/ will show the GitHub link fallback" >&2
fi

# Sentinel consumed by templates/cv.html to decide iframe vs. fallback link.
printf 'available = %s\ncommit = "%s"\n' "$cv_ok" "$CV_COMMIT" > "$CV_META"

"$PYTHON" tools/tag-freq.py
"$PYTHON" tools/tag-freq.py data/publications.toml data/generated/pub_tag_frequencies.json --table publications
"$PYTHON" tools/star-levels.py
"$PYTHON" tools/blog-tag-freq.py

cmd="${1:-build}"
if [ "$cmd" = "serve" ]; then
    "${ZOLA[@]}" build
    "${ZOLA[@]}" serve
else
    "${ZOLA[@]}" "$cmd"
fi
