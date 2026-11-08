"""Helpers shared by the build tools: tag slugs, JSON output, and reading a built site."""

import json
import re
import sys
import tomllib
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


def slugify(text: str) -> str:
    """Approximate Zola's default slug: ASCII, lowercase, runs of other characters become '-'.

    Templates match tags to tag pages by this slug, so the tools count tags by it too.
    """
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def write_json(data, path: str | Path, unit: str) -> None:
    """Write data as pretty-printed JSON, creating the output directory."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {path} ({len(data)} {unit})")


def site_args(argv: list[str]) -> tuple[Path, str]:
    """Parse `[SITE_DIR] [--base-url URL]`; the base URL defaults to zola.toml's."""
    args = list(argv)
    site = Path("public")
    if args and not args[0].startswith("--"):
        site = Path(args.pop(0))
    if "--base-url" in args:
        return site, args[args.index("--base-url") + 1]
    with open("zola.toml", "rb") as f:
        return site, tomllib.load(f)["base_url"]


def read_site(site: Path, parser_class: type[HTMLParser]) -> dict[Path, HTMLParser]:
    """Parse every HTML page in a built site; exit when there is no build to check."""
    if not site.is_dir():
        sys.exit(f"Site directory not found: {site}")
    pages = {}
    for file in sorted(site.rglob("*.html")):
        parser = parser_class()
        parser.feed(file.read_text(encoding="utf-8"))
        pages[file] = parser
    if not pages:
        sys.exit(f"No HTML pages in {site}; build the site first.")
    return pages


def page_path(site: Path, file: Path) -> str:
    """Return the root-relative URL path that serves a built file."""
    rel = file.relative_to(site).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel
