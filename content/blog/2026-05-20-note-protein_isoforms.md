+++
title = "Protein Isoforms Are Not the Same as Proteoforms"
date = 2026-05-20
[taxonomies]
tags = ["proteomics", "proteoforms", "bioinformatics"]
[extra]
kind = "note"
+++

These two terms get conflated constantly, including in papers from groups that should know better.

**Isoforms** are distinct protein sequences that arise from the same gene. The canonical sources are alternative splicing, alternative transcription start sites, and alternative polyadenylation. The key point is that the distinction is at the sequence level and is captured in the reference proteome (UniProt canonical + isoform entries).

**Proteoforms** are all the distinct molecular forms that a single gene product can take, including isoforms, but also every combination of post-translational modifications, signal peptide cleavages, propeptide processing, and sequence variants. Smith & Kelleher (2013) coined the term precisely to separate the PTM layer from the sequence layer.

The practical difference matters when you are analyzing mass spectrometry data. Isoform-aware database search is a proteomics database question. Proteoform-level inference is a different, harder problem that requires top-down or middle-down MS, and even then probabilistic assignment.

When someone says their tool does "isoform detection" from bottom-up MS, they almost always mean they can differentiate a handful of sequence-distinguishing peptides. That is useful but it is not proteoform resolution. The word choice matters because it sets the expectation for what the tool can and cannot do.
