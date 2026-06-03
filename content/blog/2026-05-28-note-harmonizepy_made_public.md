+++
title = "HarmonizePy: HarmonizR's Approach, in Python"
date = 2026-05-28
description = "A note on making HarmonizePy public, and why we wanted a Python version of HarmonizR's missing-value-aware batch correction."
[taxonomies]
tags = ["proteomics", "batch-effect-correction", "harmonization", "statistics", "multi-omics", "biostatistics", "python", "tooling", "harmonizepy"]
[extra]
kind = "note"
+++

{% callout(type="tip") %}
**HarmonizePy is public.** Pure-Python batch correction for omics data, built around HarmonizR's core idea: handle structural missingness by grouping features by observed batch support, correcting compatible subsets, and reassembling without imputation. `pip install harmonizepy`.
{% end %}

HarmonizR's idea is simple once you see it. Standard ComBat and limma need dense matrices. Real proteomics data has structured missingness (a peptide might be quantifiable in batches 1 and 2 but absent from batch 3 for reasons that have nothing to do with zero abundance). Most approaches impute first or drop features. Voß et al.{% sidenote() %}Voß H et al. "HarmonizR enables data harmonization across independent proteomic datasets with appropriate handling of missing values." *Nature Communications* 13:3523, 2022.{% end %} asked a different question: what if you let the missingness structure tell you which features should be corrected together?

> Split the matrix by batch-presence patterns. Each feature joins only the batches that observed it. Correct those sub-matrices independently. Reassemble. No imputation.

That is the idea. Schlumbohm et al.{% sidenote() %}Schlumbohm S, Neumann JE, Neumann P. "HarmonizR: blocking and singular feature data adjustment improve runtime efficiency and data preservation." *BMC Bioinformatics*, 2025.{% end %} later added blocking and singular-feature rescue. The core approach is the same and it is worth having in Python.

We used HarmonizR in the lab. It worked. The friction was not the algorithm. It was reaching across languages every time. Move data to R, correct, bring it back. Once is fine. When the workflow needs to be shared or automated, that extra hop becomes a reason to skip the correction.

HarmonizePy keeps the pipeline inside Python.

{% code(ln="python", caption="CS1: The harmonize() entry point.") %}
from harmonizepy import harmonize

result = harmonize("data.tsv", "batch.csv")
{% end %}

That is the main thing. A single call. Same shape as the input. No imputation. No R installation.

The implementation was rebuilt from the method descriptions, not ported from the R source line by line{% sidenote() %}Direct ports carry assumptions from the original language without forcing a real understanding of the algorithm. Rebuilding from the papers meant testing against expected outputs, not copying code.{% end %}. It uses NumPy for the core engines, has 628 tests validated against `sva::ComBat`, `limma::removeBatchEffect`, and HarmonizR v1.10.0, and is numerically concordant within documented tolerances.

The performance works out well for pure Python{% sidenote() %}On a Ryzen 3950X, HarmonizePy runs 54x to 266x faster than single-core HarmonizR across the benchmarked datasets. The largest gaps are on non-parametric ComBat and SCP-scale data. Details in the Benchmarks wiki page.{% end %}. NumPy's BLAS-backed operations avoid R's per-iteration overhead, but that was never the goal. The goal was keeping the workflow in one language.

{% callout(type="note") %}
**What this changes.** A script that the lab used internally is now a public package with tests, docs, a CLI, and a stable API. The work was making it independent of the original author, of the R runtime, and of the private repository, so the next person who needs to correct batch effects in Python has something to start from.
{% end %}

Making it public does not mean it is finished. Diagnostics, better guidance on when correction is working, and more real-world validation are still useful. What it means is the implementation is open, inspectable, and usable without asking for access.

That was the handoff I wanted.
