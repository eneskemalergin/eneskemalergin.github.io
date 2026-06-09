+++
title = "ProteoForge published in J. Proteome Res."
date = 2026-06-09
description = "ProteoForge is out in Journal of Proteome Research. What changed during review, what is still broken, and where the package is headed."
[taxonomies]
tags = ["proteomics", "proteoforms", "proteoforge"]
[extra]
kind = "note"
+++

{% callout(type="tip") %}
**Paper:** [doi:10.1021/acs.jproteome.5c01235](https://pubs.acs.org/doi/10.1021/acs.jproteome.5c01235) · **Preprint:** [bioRxiv](https://www.biorxiv.org/content/10.64898/2025.12.12.694008v1) · **Analysis:** [GitHub](https://github.com/LangeLab/ProteoForge_Analysis) · **Zenodo:** [doi:10.5281/zenodo.17795845](https://doi.org/10.5281/zenodo.17795845) · **Package (WIP):** [GitHub](https://github.com/eneskemalergin/ProteoForge)
{% end %}

ProteoForge is finally out in *Journal of Proteome Research*. The review process took a couple of rounds and added a ton of supplementary material. Better benchmarking, cleaner validation of the statistics, proper boundary conditions on the missing-data tolerance claims. I will not pretend the extra rounds were fun, felt like it was too much, but the paper is better after it. However around 85 pages long, I just hope that readers can find what they are looking for.

Unfortunately, the proof-reading stage was (and weirdly still at the time of writing, still) a mess. Figure legends got scrambled in the production pipeline and the published version still has errors. I am still figuring out what to do about that. Keeping the bioRxiv preprint updated with corrections might be the practical answer. It is versionable, not locked after publication, and anyone who finds the paper through search will land on the JPR page anyway.

The [analysis repository](https://github.com/LangeLab/ProteoForge_Analysis) is the real record of this work. Every script and notebook needed to reproduce the results lives there, organized to guide you through each step. The [Zenodo snapshot](https://doi.org/10.5281/zenodo.17795845) freezes the input data and HTML renders at the manuscript version. The GitHub repo stays live and collects updates.

What is next: the standalone Python package. The published analysis is a collection of scripts. Usable, but not pleasant. I am actively building a proper `pip install` package with a CLI, an API, and a dashboard for exploring results interactively. The core methods already show meaningful speed and memory improvements over the analysis scripts. What remains is the ergonomic layer: sensible defaults, clear output formats, and a way to inspect dPF assignments without digging through notebooks.

No release date yet. Soon.
