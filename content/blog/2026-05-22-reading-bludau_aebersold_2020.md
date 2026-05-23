+++
title = "Reading: Bludau & Aebersold (2020) — Proteomic and interactomic insights into the molecular basis of cell functional diversity"
date = 2026-05-22
[taxonomies]
tags = ["proteomics", "proteoforms", "mass-spectrometry", "bioinformatics"]
[extra]
kind = "reading"
+++

**Paper:** Bludau, I. & Aebersold, R. (2020). Proteomic and interactomic insights into the molecular basis of cell functional diversity. *Nature Reviews Molecular Cell Biology*, 21, 327–340. [doi:10.1038/s41580-020-0231-2](https://doi.org/10.1038/s41580-020-0231-2)

---

This is a review, not a methods paper, which is why it was easy to deprioritize and then very useful once I finally read it. Bludau and Aebersold lay out the argument that cell-type specificity is largely encoded not at the genome level but at the level of protein abundance, modification state, and interaction context. The framing is not new, but the synthesis is tight.

The most useful section for my work is the treatment of proteoforms. They distinguish three layers: sequence diversity (splice isoforms, single amino acid variants), modification diversity (PTMs), and structural diversity (conformational states that affect binding partners without changing sequence). Most tools, including the ones I work on, handle at best two of those three. Structural diversity is nearly invisible to standard bottom-up workflows.

The discussion of protein complexes and how complex stoichiometry shifts between cell types is well-cited and points toward several experimental strategies I had not connected before. The SEC-SWATH-MS approach for co-fractionation gets a good treatment here as a complement to AP-MS.

**Things I want to follow up:**
- The Malioutov et al. work on protein complex stoichiometry estimation from abundance data
- Complexome profiling in the context of mitochondrial disease, which is touched on briefly
- Whether the "protein states" framing maps cleanly onto the proteoform database efforts from the Kelleher group

**One tension the paper does not resolve:** if proteoform-level resolution requires top-down MS, and top-down MS still struggles with large proteins and complex mixtures, what is the practical scope of the claims being made? The review is optimistic about near-term technological convergence. That optimism may be warranted by 2026 instrument generations, but the 2020 framing reads somewhat ahead of where the field actually was at the time.

Overall worth reading before writing anything that invokes "proteoforms" in a claims context.
