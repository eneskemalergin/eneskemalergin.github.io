# eneskemalergin.github.io

Personal professiona/academic website, built with [Zola](https://www.getzola.org). Not a theme. Not a CMS. Markdown in, static HTML out.

## Quick start

```sh
make build   # pre-process + zola build → public/
make serve   # local preview at localhost:1111
```

Requires Python 3 (for tag frequency and star color preprocessing) and Zola 0.19+.

## Structure

| Path         | Role                                                                       |
| ------------ | -------------------------------------------------------------------------- |
| `content/`   | Markdown for blog posts, section index files                               |
| `data/`      | Structured TOML: projects, publications, news, presentations, teaching     |
| `templates/` | Jinja2-style Zola templates + 5 shortcodes                                 |
| `sass/`      | SCSS: design tokens, layout, component styles                              |
| `tools/`     | Python scripts: tag frequency aggregation, GitHub star color normalization |
| `plan/`      | Design system, writing rules, markdown reference (private)                 |

At build time, `build.sh` also mirrors the latest CV PDF from `eneskemalergin/My_CV` into `static/cv/` (single source of truth — see `content/cv/` and `templates/cv.html`) and writes a `data/cv_meta.toml` sentinel so the `/cv/` page can fall back to a GitHub link when offline. Zola's built-in search index (`build_search_index`) powers the `/search/` page via `templates/search.html` + `static/js/search.js`.

## Shortcodes

Custom shortcodes that extend markdown: callout boxes (Notion-style with emoji icons), margin sidenotes, captioned figures, language-labeled code blocks, and collapsible details. Rendered server-side, zero client JavaScript.

## Design

Muted backgrounds, Inter at weight 300, teal accent, first-class dark mode. 20 static pages, ~92ms build, page weight comparable to a single Medium article sans framework.

## License

Content and design are my own. The underlying Zola project is MIT. Do what you want with the structure, leave my writing and face alone.
