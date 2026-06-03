+++
title = "pxseek: From a Selenium Script to a PyPI Package"
date = 2026-05-26
description = "The story of a small ProteomeXchange metadata tool that started as a fragile Selenium parser and became a PyPI package the lab can actually depend on."
[taxonomies]
tags = ["proteomics", "metadata", "proteomexchange", "python", "cli", "tooling", "pxseek"]
[extra]
kind = "note"
+++

{% callout(type="tip") %}
**pxseek is on PyPI.** CLI and Python library for querying ProteomeXchange metadata. Filter by species, repository, keywords, date range, instruments. Local caching, JSON and table output. `pip install pxseek`.
{% end %}

The first version was not a package. It was a small parser from 2024, built to help hunt down pediatric cancer proteomics datasets on ProteomeXchange. I worked on it with a co-op student. The goal was practical: find datasets faster, collect enough metadata to decide what was worth looking at, and avoid doing the same manual search again and again.

It worked, but it relied on Selenium{% sidenote() %}Browser automation is the kind of dependency you accept for a prototype and regret in production. Chrome versions change. Driver versions change. Pages change. A tool that helps you today can fail silently tomorrow and you will not know why until you debug the browser.{% end %}. I did not want the lab to depend on that long term.

Before I left my post in Lange Lab, I rewrote the core to use ProteomeCentral metadata directly. No browser. No driver. Just HTTP requests and structured data.

{% code(ln="bash", caption="CS1: Fetch, filter, and lookup in three commands.") %}
pxseek fetch -o px_datasets.tsv
pxseek filter -i px_datasets.tsv -s "Homo sapiens" -k "cancer" -o shortlist.tsv
pxseek lookup --input shortlist.tsv -o detailed.tsv
{% end %}

The rewrite also added local caching, multiple output formats, a Python API, and a CLI that works in scripts. It does not download raw files or process spectra. It finds metadata so you can decide what to download.

Publishing to PyPI changes what the tool is. Instead of "there is a script somewhere," it becomes `pip install pxseek`. That matters for documentation. It matters for the next student, analyst, or lab member who needs to ask: "Which human cancer proteomics datasets are available?"

{% callout(type="note") %}
**Why this mattered.** I wanted to leave behind something the lab could keep using without needing me to explain a private script, a browser setup, or a set of manual steps. Small tools that sit between a research need and a little software care are worth packaging properly.
{% end %}

That is what the PyPI release is. A fragile script turned into something installable, repeatable, and independent of whoever wrote the first version.
