+++
title = "Benchmarks Without Negative Controls Are Not Benchmarks"
date = 2026-05-21
[taxonomies]
tags = ["bioinformatics", "statistics", "proteomics"]
[extra]
kind = "opinion"
+++

A pattern I keep seeing in computational proteomics papers: a new method is evaluated by comparing its output against one or two existing tools on a handful of published datasets. The new method performs better on most metrics. The paper is accepted. The method is released.

The problem is that none of these evaluations include a meaningful negative control. By "negative control" I mean something that deliberately does the wrong thing: a method that ranks proteins randomly, a normalization strategy known to introduce bias, a clustering run on permuted labels. If your new method cannot beat a random baseline on any dataset, the benchmark is not distinguishing signal from noise.

This is not a new observation. The field has discussed benchmark inflation in genomics for years. But proteomics, and especially PTM proteomics, seems to have quietly decided the issue does not apply to it. I suspect this is because ground-truth data is genuinely hard to construct. Phosphorylation atlases are incomplete, gold-standard interactomes are sparse, and most "reference" datasets were themselves produced by methods you might want to evaluate.

That difficulty is real, but it is an argument for more careful experimental design around negative controls, not an excuse to skip them. Simulated data with known properties is not perfect, but it is better than implicitly trusting that three real datasets from three different labs constitute rigorous evaluation.

The minimal thing every benchmarking paper should include: show that your method beats a reasonable dummy. If it cannot, say so, explain why, and narrow the claim. Narrower honest claims are more useful than broad ones that do not survive contact with a negative control.
