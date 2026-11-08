# eneskemalergin.github.io

Personal professional/academic website, built with [Zola](https://www.getzola.org). Not a theme. Not a CMS. Markdown in, static HTML out.

## Quick start

```sh
mise install
make build   # pre-process + zola build → public/
make serve   # local preview at localhost:1111
```

Requires Python 3.12 for preprocessing and Zola 0.22.1. The repository's `mise.toml` pins Zola for local builds; `build.sh` checks both tool versions before doing any work.

## Structure

| Path         | Role                                                                       |
| ------------ | -------------------------------------------------------------------------- |
| `content/`   | Markdown for blog posts, section index files                               |
| `data/`      | Structured TOML: projects, publications, news, presentations, teaching     |
| `static/`    | Site assets, local browser scripts, and pinned third-party assets          |
| `templates/` | Jinja2-style Zola templates + 5 shortcodes                                 |
| `sass/`      | SCSS: design tokens, layout, component styles                              |
| `tools/`     | Python scripts: tag frequencies, star colors, internal link check          |

At build time, `build.sh` also downloads the CV PDF from `eneskemalergin/My_CV` at the commit pinned in `data/cv.toml` into `static/cv/` (single source of truth; see `content/cv/` and `templates/cv.html`), checks that it is a PDF, and writes a `data/generated/cv_meta.toml` sentinel. Without network access a local build falls back to a GitHub link on `/cv/`, while CI fails instead. To publish a new CV, update the commit in `data/cv.toml`. All derived data (tag frequencies, star colors, CV status) goes to `data/generated/`, which is not committed; `make check` builds the site and checks its internal links. Zola's built-in search index (`build_search_index`) powers the `/search/` page via `templates/search.html` + `static/js/search.js`.

## Shortcodes

Custom shortcodes that extend markdown: callout boxes (Notion-style with emoji icons), margin sidenotes, captioned figures, language-labeled code blocks, and collapsible details. Their markup is rendered server-side; small local scripts handle theme selection, code highlighting, and math rendering.

## Design

Muted backgrounds, restrained sans-serif typography, teal accent, first-class dark mode, and no client framework. Generated page counts vary with content and taxonomy output.

## License

Content and design are my own. The underlying Zola project is MIT. Do what you want with the structure, leave my writing and face alone.
