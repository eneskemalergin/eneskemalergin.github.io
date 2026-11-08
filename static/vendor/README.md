# Vendored browser assets

These assets are served locally. The website does not request them from third-party CDNs at runtime.

- Font Awesome Free 6.7.2: icons are CC BY 4.0, fonts are SIL OFL 1.1, and code is MIT. The upstream license is in `fontawesome/LICENSE.txt`.
- Academicons 1.9.4: fonts are SIL OFL 1.1 and CSS is MIT. The upstream README is in `academicons/README.md`.

No page loads the Font Awesome or Academicons fonts and stylesheets: `data/icons.toml` holds the outlines of the icons the site uses, drawn from these two releases, and `templates/macros.html` renders them as inline SVG.
- Highlight.js 11.10.0: BSD-3-Clause. The upstream license is in `highlightjs/LICENSE`.
- KaTeX 0.16.21: MIT. The upstream license is in `katex/LICENSE`.
- Inter 4.001 (from `@fontsource-variable/inter` 5.3.0, the Latin subsets with the weight axis): SIL OFL 1.1. The license is in `inter/LICENSE`.

Update these assets deliberately by version. Do not replace them with unversioned CDN URLs.
