+++
title = "QuEStVar v0.1.0 is out"
date = 2026-05-22
description = "Release note for QuEStVar v0.1.0. Python package for paired equivalence and difference testing, now stable on PyPI."
[taxonomies]
tags = ["proteomics", "statistics", "equivalence-testing", "bioinformatics", "python", "questvar"]
[extra]
kind = "note"
+++

{% callout(type="tip") %}
`pip install questvar[plot,yaml]`

[PyPI](https://pypi.org/project/questvar/) · [Docs](https://eneskemalergin.github.io/QuEStVar/) · [GitHub](https://github.com/eneskemalergin/QuEStVar) · [Paper](https://doi.org/10.1021/acs.jproteome.4c00131)
{% end %}

The package grew out of the [2024 J. Proteome Res. paper](https://doi.org/10.1021/acs.jproteome.4c00131). The analysis lived in a monolithic GitHub archive until last week. v0.1.0 is the clean API extraction of that work.

The core point is one that keeps getting missed in omics: a non-significant t-test is not evidence of equivalence. It is a failure to reject. QuEStVar runs a [TOST (two-one-sided t-test)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5502906/) alongside the standard test so the result is always one of three states: differential, equivalent, or genuinely indeterminate. The indeterminate case is important to surface explicitly rather than letting it collapse into "not significant."

The other thing I spent time on is the exclusion tracking. Features excluded before testing (bad CV, missing values, zero variance) appear in their own panel with a breakdown by reason. Most tools drop them silently. Knowing _why_ a feature was excluded matters when you are interpreting the overall result counts.

{% code(ln="python", caption="CS1: Minimal single-comparison run.") %}
import polars as pl
from questvar import QuestVar

df = pl.read_csv("data/demo_realistic.tsv", separator="\t")
qv = QuestVar(cv_thr=1.0, eq_thr=0.5, df_thr=1.0, p_thr=0.05, correction="fdr")
results = qv.test(df, cond_1=["c1_0","c1_1","c1_2"], cond_2=["c2_0","c2_1","c2_2"])
print(results.summary())
{% end %}

Power analysis is included from the start because sample size planning under equivalence constraints is different from planning under difference constraints, and I kept getting that question after the paper.

The `.plot()` call on any results object produces an eight-panel figure. Panel G is the exclusion breakdown.

{{ figure(
  src="https://raw.githubusercontent.com/eneskemalergin/QuEStVar/main/assets/summary_plot.png",
  alt="Eight-panel summary figure from QuEStVar",
  alt_badge="QuEStVar v0.1.0",
  caption="**Figure 1.** Summary plot from a single comparison."
  label="Figure 1"
) }}

v0.1.0 is single-comparison only. Multi-comparison support (metadata-driven pair generation, batch execution) is next.
