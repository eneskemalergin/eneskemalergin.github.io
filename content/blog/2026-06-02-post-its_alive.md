+++
title = "It's Alive!"
date = 2026-06-02
description = "After months on a feature branch, the new Zola-based website finally merged to main. Custom shortcodes, migrated old posts, 90ms build times, and a dark mode that actually looks good."
[taxonomies]
tags = ["personal", "website", "zola", "meta", "design"]
[extra]
kind = "post"
+++

{% callout(type="tip") %}

**TLDR:** This site is now built with <a href="https://www.getzola.org" target="_blank" rel="noopener noreferrer">Zola</a>, a static site generator that turns markdown into HTML in under 100ms. Custom shortcodes for callouts, sidenotes, code blocks, figures, and collapsible details. Old posts migrated from an obsolete platform with retroactive commentary added through sidenotes. Dark mode included. No JavaScript framework required.

{% end %}

## The branch that would not die

For months, this site existed as a branch on my machine. I would open it on weekends. Tweak the CSS. Write a shortcode. Close it again. The branch grew opinions about font weights.

Today I merged it to main.

The old site was on a platform I do not want to name because it is not their fault I outgrew it{% sidenote() %}That part bothered me more than the performance. Writing a post should mean opening a file, writing, and running a command. Not fighting a WYSIWYG editor that keeps rearranging your paragraph breaks.{% end %}. It worked. It was also slow, locked into a database, and required logging into a browser to publish a 200-word note.

I needed something I could edit in vim and deploy with a single command. Zola does both. Markdown files in, static HTML out. No database. No login screen. No build step that outlasts my attention span.

{% code(ln="bash", caption="CS1: The entire deployment pipeline.") %}

./build.sh    # pre-process tags, generate star colors, build site
git push      # GitHub Pages picks it up automatically

{% end %}

That is the whole thing. Three files to publish a post, one push to deploy it. I spent months building what amounts to a very opinionated markdown renderer with nice CSS.

## Shortcodes that do one thing

Zola calls them shortcodes. They are template fragments you invoke from markdown{% sidenote() %}Block shortcodes use the bracket-percent syntax and wrap content. Inline shortcodes use the double-brace syntax. Both are Zola-specific. Other static site generators handle this differently.{% end %}. A file in `templates/shortcodes/`, a parameter or two, and suddenly you have Notion-style formatting in a static site.

I built callouts, sidenotes, code blocks, figures, and collapsible details. Each one because I kept wanting that thing and it did not exist. The callout gives me colored boxes with emoji icons for tip, note, warning, and danger. The sidenote floats commentary into the right margin so it does not break the reading flow. The code block adds a language badge so you know what you are looking at. Small things. They add up.

The post kind system came from the same place. I wanted the blog listing to tell you what you were clicking into before you clicked. Technical deep dives get a table of contents and reading time. Short observations get neither. Opinion pieces and paper notes get their own presentation. The badge in the header and on the listing page handles the rest.

## Design that stays out of the way

The design brief was short: make it look like I wrote it. Not like a template got filled in.

Muted backgrounds. Inter at weight 300 for body text. A teal accent that appears exactly where you need it and nowhere else. Monospace for code, metadata, and dates. Dark mode that is not an afterthought{% sidenote() %}There is something absurd about spending this much time on CSS for a personal blog. And also something satisfying about getting the teal accent exactly right in both light and dark mode.{% end %}.

The site fits a lot of information into a small space without feeling crowded. That balance took the longest to get right.

The build produces 20 static pages and completes in 92ms. Total page weight, including fonts and CSS, is about the same as a single Medium article loaded with their JavaScript framework, analytics tracker, and cookie consent banner{% sidenote() %}I checked. The difference is two orders of magnitude. This is not a flex. It is an observation about what we accepted as normal.{% end %}.

## The old posts live here now

I migrated most of the old content. Some posts did not make the cut. Unfinished drafts, notes that no longer applied, a few early pieces that did not fit what I want this site to be. The ones that stayed are organized by kind and retroactively tagged to cross-link with current projects.

The oldest surviving post is from 2018, a fuzzy C-means clustering write-up from my Master's{% sidenote() %}I re-read it before migrating and added a note where my understanding of the math had changed. Young me was enthusiastic if not always precise.{% end %}. The content is untouched. The commentary is new.

{% details(summary="Posts that made the journey") %}
- Fuzzy C-Means clustering on the Iris dataset (2018)
- Prosit spectral prediction (2019)
- PRODA: proteoform detection (2020)
- ProteoForge deep dive (2025)
- Opinion pieces on Zig, vendor formats, search engines, storage (2025-2026)
- z-fasta, mzarc, zigR, HarmonizePy, and all the Zig experiments (2026)
{% end %}

Each migrated post got the same treatment: convert the frontmatter, assign the right kind, add shortcodes where they improved readability. The ones that needed correction got retroactive sidenotes. The ones that still hold up got left alone.

## What is next

Several things I want to add before I call this finished. A comments section, if I can find one that does not require a JavaScript framework. Analytics that count visits without counting visitors. Cloudflare if I move the DNS there. A proper RSS template. Per-page meta tags for social previews. And the presentations and teaching pages need the same treatment the blog just got.

The blog itself will keep growing. The project page needs a compression benchmark comparison. I want to write up the SQuAPP workflow properly. There is a half-finished post about why I keep building things in Zig instead of using existing tools.

But mostly I want to use this thing. The site is built, the branch is merged, and the publishing pipeline is a single push away.

The rest is just writing.
