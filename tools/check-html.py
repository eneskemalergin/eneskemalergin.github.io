#!/usr/bin/env python3
"""Check the structure of a built site: landmarks, IDs, link policy, scripts, indexing, search.

Each HTML page in the build output must have:
  - exactly one <main> and one <h1>, and the skip link as its first focusable element
  - unique id values, and every aria-controls, aria-labelledby, and label "for"
    pointing at an id on the same page
  - rel="noopener noreferrer" on every target="_blank" link
  - no inline executable script (JSON and JSON-LD data blocks are allowed), which
    the Content Security Policy relies on
  - scripts, stylesheets, images, and frames from the site itself

Across the site:
  - sitemap.xml lists only built pages, and no page marked noindex
  - the search index on /search/ parses, every record links to a built page
    and fragment, every record type appears, and every project and publication
    in data/ has a record

Usage:
    python3 tools/check-html.py [SITE_DIR] [--base-url URL]

    SITE_DIR   - Built site directory          (default: public)
    --base-url - Site base URL                  (default: base_url in zola.toml)

Output: one line per problem, sorted, then a summary. Exits with status 1 when
any check fails, or when SITE_DIR is missing or holds no HTML pages.

    blog/index.html: 2 <h1> elements
    search/index.html: search record "zigR" links to a missing fragment
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

try:
    import tomllib
except ImportError:
    import tomli as tomllib

DATA_BLOCK_TYPES = {"application/json", "application/ld+json"}
RESOURCE_ATTRS = {"script": "src", "img": "src", "iframe": "src", "source": "src"}
FOCUSABLE = {"a", "button", "input", "select", "textarea", "summary"}
SEARCH_TYPES = {"Page", "Post", "Note", "Opinion", "Reading", "Project", "Publication", "Talk", "Teaching", "News"}


class PageParser(HTMLParser):
    """Collect what the checks need from one HTML page."""

    def __init__(self) -> None:
        super().__init__()
        self.counts = {"main": 0, "h1": 0}
        self.ids: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.blank_links: list[str] = []
        self.inline_scripts = 0
        self.resources: list[str] = []
        self.first_focusable: dict | None = None
        self.noindex = False
        self.data_blocks: dict[str, str] = {}
        self._data_id: str | None = None
        self._data_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = {k: (v or "") for k, v in attrs}
        if tag in self.counts:
            self.counts[tag] += 1
        if a.get("id"):
            self.ids.append(a["id"])
        for key in ("aria-controls", "aria-labelledby", "aria-describedby"):
            for target in a.get(key, "").split():
                self.references.append((key, target))
        if tag == "label" and a.get("for"):
            self.references.append(("for", a["for"]))
        if tag == "a" and a.get("target") == "_blank":
            rel = set(a.get("rel", "").split())
            if not {"noopener", "noreferrer"} <= rel:
                self.blank_links.append(a.get("href", ""))
        if tag == "script":
            if a.get("type") in DATA_BLOCK_TYPES:
                self._data_id, self._data_text = a.get("id", a["type"]), []
            elif not a.get("src"):
                self.inline_scripts += 1
        attr = RESOURCE_ATTRS.get(tag)
        if attr and a.get(attr):
            self.resources.append(a[attr])
        if tag == "link" and "stylesheet" in a.get("rel", "").split() and a.get("href"):
            self.resources.append(a["href"])
        if tag == "meta" and a.get("name") == "robots" and "noindex" in a.get("content", ""):
            self.noindex = True
        if self.first_focusable is None and tag in FOCUSABLE and (tag != "a" or a.get("href")):
            self.first_focusable = a

    def handle_data(self, data: str) -> None:
        if self._data_id is not None:
            self._data_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._data_id is not None:
            self.data_blocks[self._data_id] = "".join(self._data_text)
            self._data_id = None


def page_path(site: Path, file: Path) -> str:
    """Return the root-relative URL path that serves a built file."""
    rel = file.relative_to(site).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def check_page(rel: str, page: PageParser, local, problems: list[str]) -> None:
    """Structure, link policy, and resource checks for one page."""
    for tag, count in page.counts.items():
        if count != 1:
            problems.append(f"{rel}: {count} <{tag}> elements")
    first = page.first_focusable or {}
    if "skip-link" not in first.get("class", "").split():
        problems.append(f"{rel}: the first focusable element is not the skip link")
    seen: set[str] = set()
    for i in page.ids:
        if i in seen:
            problems.append(f"{rel}: duplicate id \"{i}\"")
        seen.add(i)
    for key, target in page.references:
        if target not in seen:
            problems.append(f"{rel}: {key} points at missing id \"{target}\"")
    for href in page.blank_links:
        problems.append(f"{rel}: target=_blank link without noopener noreferrer: {href}")
    if page.inline_scripts:
        problems.append(f"{rel}: {page.inline_scripts} inline script(s)")
    for url in page.resources:
        if not local(url):
            problems.append(f"{rel}: resource from another origin: {url}")


def check_sitemap(site: Path, pages: dict, problems: list[str]) -> None:
    """Every sitemap URL is a built page that search engines may index."""
    sitemap = site / "sitemap.xml"
    if not sitemap.is_file():
        problems.append("sitemap.xml: missing")
        return
    by_path = {page_path(site, f): p for f, p in pages.items()}
    listed = set()
    for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8")):
        path = urlsplit(loc).path or "/"
        listed.add(path)
        if path not in by_path:
            problems.append(f"sitemap.xml: {loc} is not a built page")
        elif by_path[path].noindex:
            problems.append(f"sitemap.xml: {loc} is marked noindex")
    for path, page in by_path.items():
        if path.endswith("/") and not page.noindex and path not in listed and path != "/404.html":
            problems.append(f"sitemap.xml: indexable page {path} is missing")


def check_search(site: Path, pages: dict, problems: list[str]) -> None:
    """The embedded search index covers every record type and every data record."""
    search = site / "search" / "index.html"
    if search not in pages:
        problems.append("search/index.html: missing")
        return
    raw = pages[search].data_blocks.get("search-data")
    if raw is None:
        problems.append("search/index.html: no search-data block")
        return
    try:
        records = json.loads(raw)
    except json.JSONDecodeError as err:
        problems.append(f"search/index.html: search index does not parse: {err}")
        return
    ids_by_path = {page_path(site, f): set(p.ids) for f, p in pages.items()}
    names = set()
    for r in records:
        if not r.get("n") or not r.get("u") or r.get("t") not in SEARCH_TYPES:
            problems.append(f"search/index.html: malformed search record {r!r:.80}")
            continue
        names.add(r["n"])
        target = urlsplit(r["u"])
        path = target.path or "/"
        if path not in ids_by_path:
            problems.append(f"search/index.html: search record \"{r['n']}\" links to a missing page {path}")
        elif target.fragment and unquote(target.fragment) not in ids_by_path[path]:
            problems.append(f"search/index.html: search record \"{r['n']}\" links to a missing fragment #{target.fragment}")
    missing_types = {"Page", "Project", "Publication", "Talk", "Teaching", "News"} - {r.get("t") for r in records}
    if missing_types:
        problems.append(f"search/index.html: no search records of type {', '.join(sorted(missing_types))}")
    for data_file, table in (("data/projects.toml", "projects"), ("data/publications.toml", "publications")):
        with open(data_file, "rb") as f:
            for entry in tomllib.load(f).get(table, []):
                title = re.sub(r"<[^>]+>", "", entry.get("title", ""))
                if title and title not in names:
                    problems.append(f"search/index.html: no search record for {table[:-1]} \"{title}\"")


def main() -> None:
    args = sys.argv[1:]
    site = Path("public")
    base_url = None
    if args and not args[0].startswith("--"):
        site = Path(args.pop(0))
    if "--base-url" in args:
        base_url = args[args.index("--base-url") + 1]
    if base_url is None:
        with open("zola.toml", "rb") as f:
            base_url = tomllib.load(f)["base_url"]
    base = urlsplit(base_url)

    if not site.is_dir():
        sys.exit(f"Site directory not found: {site}")
    pages: dict[Path, PageParser] = {}
    for file in sorted(site.rglob("*.html")):
        parser = PageParser()
        parser.feed(file.read_text(encoding="utf-8"))
        pages[file] = parser
    if not pages:
        sys.exit(f"No HTML pages in {site}; build the site first.")

    def local(url: str) -> bool:
        target = urlsplit(urljoin(base_url.rstrip("/") + "/", url))
        return target.scheme in ("http", "https") and target.netloc == base.netloc

    problems: list[str] = []
    for file, page in pages.items():
        check_page(file.relative_to(site).as_posix(), page, local, problems)
    check_sitemap(site, pages, problems)
    check_search(site, pages, problems)

    for line in sorted(set(problems)):
        print(line)
    print(f"Checked {len(pages)} pages: {len(set(problems))} problems.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
