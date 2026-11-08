# Vendored browser assets

These assets are served locally. The website does not request them from third-party CDNs at runtime.

- Highlight.js 11.10.0: BSD-3-Clause. The upstream license is in `highlightjs/LICENSE`.
- KaTeX 0.16.21: MIT. The upstream license is in `katex/LICENSE`.
- Inter 4.001 (from `@fontsource-variable/inter` 5.3.0, the Latin subsets with the weight axis): SIL OFL 1.1. The license is in `inter/LICENSE`.

The site's icons are not vendored files: `data/icons.toml` holds their outlines, drawn from Font Awesome Free 6.7.2 (icons CC BY 4.0) and Academicons 1.9.4 (SIL OFL 1.1), and `templates/macros.html` renders them as inline SVG. The data file's header names the sources and licenses.

Update these assets deliberately by version. Do not replace them with unversioned CDN URLs.
