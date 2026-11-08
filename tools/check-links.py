#!/usr/bin/env python3
"""Check that every internal link, asset, and fragment in a built site resolves.

Scans each HTML file in the build output and checks every href and src that
points into the site: relative paths, root-relative paths, and absolute URLs
that start with the site's base_url. External URLs are not fetched.

Usage:
    python3 tools/check-links.py [SITE_DIR] [--base-url URL]

    SITE_DIR   - Built site directory          (default: public)
    --base-url - Site base URL                  (default: base_url in zola.toml)

Output: one line per broken reference, sorted, then a summary. Exits with
status 1 when any reference is broken, or when SITE_DIR is missing or holds no
HTML pages, so CI can stop a deployment.

    missing page: /tags/fair/  (from projects/index.html)
    missing fragment: /blog/post-x/#results  (from blog/index.html)
"""

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from common import page_path, read_site, site_args

# Paths on this domain that other repositories publish (their own GitHub Pages
# sites), so they are absent from this build by design.
EXTERNAL_PREFIXES = ("/QuEStVar/",)

# Images missing from two older reading notes. Remove an entry once its image
# is restored, so the check guards it again.
KNOWN_MISSING = {
    "/blog/images/reading/proDA.jpg",
    "/blog/images/reading/prosit_mirror.jpg",
}

LINK_ATTRS = {"a": "href", "link": "href", "img": "src", "script": "src",
              "iframe": "src", "source": "src"}


class PageParser(HTMLParser):
    """Collect element IDs and outgoing references from one HTML page."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attrs = dict(attrs)
        for key in ("id", "name"):
            if attrs.get(key):
                self.ids.add(attrs[key])
        attr = LINK_ATTRS.get(tag)
        if attr and attrs.get(attr):
            self.refs.append(attrs[attr])


def resolve(site: Path, path: str) -> Path | None:
    """Map a URL path to the built file that serves it, if any."""
    candidate = site / unquote(path).lstrip("/")
    if path.endswith("/"):
        candidate = candidate / "index.html"
    if candidate.is_file():
        return candidate
    if (candidate / "index.html").is_file():
        return candidate / "index.html"
    return None


def main() -> None:
    site, base_url = site_args(sys.argv[1:])
    base = urlsplit(base_url)
    pages = read_site(site, PageParser)

    problems: set[str] = set()
    checked = 0
    for file, parser in pages.items():
        source = file.relative_to(site).as_posix()
        here = page_path(site, file)
        for ref in parser.refs:
            target = urlsplit(urljoin(base_url.rstrip("/") + here, ref))
            if target.scheme not in ("http", "https") or target.netloc != base.netloc:
                continue
            if target.path.startswith(EXTERNAL_PREFIXES) or target.path in KNOWN_MISSING:
                continue
            checked += 1
            built = resolve(site, target.path or "/")
            if built is None:
                problems.add(f"missing page: {target.path}  (from {source})")
            elif target.fragment and built.suffix == ".html":
                ids = pages[built].ids if built in pages else set()
                if unquote(target.fragment) not in ids:
                    problems.add(f"missing fragment: {target.path}#{target.fragment}  (from {source})")

    for line in sorted(problems):
        print(line)
    print(f"Checked {checked} internal references in {len(pages)} pages: {len(problems)} broken.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
