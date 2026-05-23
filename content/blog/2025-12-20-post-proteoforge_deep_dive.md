+++
title = "ProteoForge: What Happens When You Stop Averaging Your Peptides"
date = 2025-12-20
description = "The story behind ProteoForge, a framework for finding differential proteoforms in bottom-up proteomics data. Why protein-level averages hide biology, how missing data broke every tool we tried, and what we found when we applied it to a hypoxia dataset."
[taxonomies]
tags = ["proteoforge", "proteomics", "proteoforms", "statistics", "bioinformatics", "mass-spectrometry"]
[extra]
kind = "post"
katex = true
+++

I spent the better part of my PhD staring at peptide intensity matrices. Thousands of rows, dozens of columns, lots of missing values. The standard workflow says: roll those peptides up into protein-level quantities, run your differential expression, make a volcano plot, write the paper{% sidenote() %}If you have never seen a peptide intensity matrix, imagine a spreadsheet where most of the cells in columns 5 through 12 are empty, and the ones that are not empty disagree with each other about what the protein is doing. That is bottom-up proteomics.{% end %}. I did that. Multiple times. It always felt like we were throwing away information.

This post is about ProteoForge, the framework that came out of that frustration. It is not a summary of the paper (you can [read the preprint](https://www.biorxiv.org/content/10.64898/2025.12.12.694008v1) for that). It is about the problem as I experienced it, the decisions we made while building the tool, and what surprised us when we finally applied it to real data.

## The averaging problem

The human genome codes for roughly 20,000 proteins. But the actual number of distinct protein forms in a cell is orders of magnitude larger[^1]. Alternative splicing, post-translational modifications, proteolytic processing: these create proteoforms[^2], and proteoforms from the same gene can have opposing biological functions.

{% callout(type="note") %}

**The KRAS example.** Different proteoforms of the KRAS oncogene have opposing effects on MAPK signalling[^3]. KRAS4A and KRAS4B are splice variants with different membrane targeting, different interactomes, and different downstream effects. A protein-level average across both would hide the biology entirely. KRAS is not an edge case. It is the rule at scale.

{% end %}

Bottom-up proteomics measures peptides, not intact proteins. The field has lived with this trade-off for years: you get broad coverage but you lose proteoform identity. The standard fix is to group peptides by protein accession, average their intensities, and call it a protein quantity.

That averaging step is where the information dies.

If three peptides from a protein go up under treatment and two go down, the protein-level average might show no change at all. A flat line on your volcano plot. You move on. You never see that the protein was actually doing something complicated at the proteoform level.

## What already existed (and where it broke)

| Feature | PeCorA | COPF | ProteoForge |
| --- | --- | --- | --- |
| Discordant peptide detection | Yes | No | Yes |
| Peptide grouping into proteoforms | No | Yes | Yes |
| Missing data tolerance | Poor (degrades early) | Poor (needs complete data) | Good (stable to 60%) |
| Statistical model | Per-peptide linear model | Peptide correlation matrix | RLM with interaction terms |
| Minimum requirement | 2+ treatment groups | Many replicates, low missingness | 4+ peptides per protein |

The core issue with both tools, and really with every method we tested: missing data{% sidenote() %}A typical DIA dataset from an Orbitrap will have about 25% missing values at the precursor level. By the time you filter for valid peptides per protein, that number often exceeds 40%. Most statistical methods assume complete data and crash or bias badly when confronted with this.{% end %}. In a typical DIA proteomics experiment, 20 to 40 percent of peptide measurements are missing. Some are missing at random (instrument did not pick them up). Some are missing because the peptide is genuinely absent in that condition. The distinction matters enormously, and most tools either ignore it or require you to delete incomplete cases.

That was the gap.

## The idea behind ProteoForge

ProteoForge does four things, in order. I will walk through each one, not with equations (the paper has those), but with the reasoning.

*Figure 1: The four-module ProteoForge pipeline. (A) Framework schematic. (B) Effect of normalization steps on peptide distributions. (C) Three example proteins showing peptide profiles, distance heatmaps, and final dPF assignments.*

### Module 1: Normalize relative to a control

Raw peptide intensities are noisy and have different baselines across samples. We log-transform, z-score, and then subtract the mean control intensity for each peptide. After this step, every value represents the deviation of that peptide from its own control baseline. Sounds simple. It is. But it makes the downstream models much cleaner because you are comparing changes, not absolute values.

{% callout(type="tip") %}

**See Figure 1B.** The control-adjusted values collapse the four condition-specific distributions into a shared zero-centered space. This is the input for everything that follows.

{% end %}

### Module 2: Find discordant peptides

This is the statistical core. For each protein, we fit a linear model that asks: does this peptide behave differently from its siblings across conditions?

{% code(ln="r", caption="CS1: The interaction model used by ProteoForge for each protein.") %}

Intensity ~ Condition * Peptide

{% end %}

The interaction term (`Condition * Peptide`) captures the discordance. If a peptide responds to the condition differently than the other peptides from the same protein, the interaction term will be significant.

We tested several model types. Ordinary least squares, weighted least squares with custom imputation-aware weights, generalized linear models, and robust linear models (RLM) with Huber M-estimation[^6].

{% details(summary="Why we chose RLM over other models") %}

Supplementary Note 1 in the paper contains the full model comparison across OLS, WLS with custom weights, GLM, and RLM. RLM with Huber weights gave the best balance between performance and ease of use. The custom-weighted WLS models can outperform RLM at extreme missingness (above 60%), but they require you to correctly specify the weight matrix, which is error-prone in practice.

At moderate missingness (under 50%), all models performed similarly. The differences emerged at the edges: high missingness, many imputed values, unbalanced group sizes. RLM handled all of these without requiring the user to configure anything beyond the default.

{% end %}

We settled on RLM as the default because of a property that turned out to be exactly what we needed: it automatically down-weights outliers. Imputed values, especially the down-shifted low values used for condition-complete missingness, look like outliers to the model. RLM treats them accordingly. No manual weight specification needed. The user does not have to think about which values were imputed and which were real.

The p-values from the interaction terms go through a two-step Benjamini-Hochberg FDR correction[^7]: first within each protein, then globally{% sidenote() %}The first correction accounts for multiple peptides per protein. The second accounts for multiple proteins genome-wide. A miscleaved peptide or technical artifact would have to survive both rounds, which is why we use this approach despite it being conservative.{% end %}. Peptides that pass the threshold (we used adjusted p < 0.001) are flagged as significantly discordant.

### Module 3: Cluster the discordant peptides

Finding discordant peptides is not enough. You need to know which discordant peptides move together, because a proteoform is defined by a group of co-varying peptides, not a single one.

We compute the Euclidean distance between median adjusted intensity profiles and cluster with Ward linkage[^8]. The default cut method (`hybrid_outlier_cut`) determines the number of clusters automatically.

This is the part that separates ProteoForge from PeCorA. PeCorA stops at "this peptide is different." ProteoForge goes further: "these three peptides are different in the same way, and they likely belong to the same proteoform."

### Module 4: Build proteoforms

The naming convention tells the story:

| Label | Meaning | Composition |
| --- | --- | --- |
| `dPF_0` | Canonical proteoform | All non-discordant peptides. Your "clean" protein signal. |
| `dPF_1`, `dPF_2`, ... | Differential proteoforms | Clusters with 2+ peptides and 1+ significantly discordant. |
| `dPF_-1` | Singleton PTM flag | Significantly discordant peptides in singleton clusters. Likely single-site modifications. |

{% callout(type="tip") %}

**See Figure 1C.** Three example proteins with their peptide profiles, distance heatmaps, and final dPF assignments. Protein 2 is the interesting one: three peptides cluster into a dPF while a fourth ends up as a singleton PTM.

{% end %}

The result is a peptide-to-dPF mapping table. Each protein can have zero, one, or multiple differential proteoforms, plus a canonical form.

## Benchmarking: what we actually learned

Benchmarking a proteoform discovery tool is tricky because there is no ground truth for proteoforms in most real datasets. We used two approaches: real data with in-silico perturbations (the COPF benchmark approach, using a SWATH-MS interlab HEK293 dataset[^4][^5]), and controlled simulations.

*Figure 2: Benchmark results across real and simulated data. (A) SWATH-MS interlab test. (B-E) Simulations 1-4: imputation impact, missingness tolerance, signal strength, multi-condition complexity.*

Four simulation scenarios tested the things that matter in practice:

| Scenario | What was varied | ProteoForge | PeCorA | Takeaway |
| --- | --- | --- | --- | --- |
| 1. Imputation impact | Up to 35% data removed, imputed | MCC dropped 0.005 | MCC dropped 0.158 | 30x less sensitive to imputation |
| 2. Missingness tolerance | 0% to 80% missing values | Stable MCC 0.46-0.57 to 60% | Degraded sharply from start | Hard cliff at 60% for ProteoForge |
| 3. Signal strength | Fold change from low to high | 0.91 MCC at high FC | 0.52 MCC at high FC | Nearly 2x better at strong signal |
| 4. Multi-condition | 2 to 6 conditions | Flat performance | Variable | Scales to complex designs |

{% callout(type="note") %}

**The key visual is Figure 2C.** ProteoForge's MCC line stays flat across increasing missingness while PeCorA's drops linearly. Panels A through E map to the SWATH-MS interlab test and simulations 1 through 4 respectively.

{% end %}

For peptide grouping (which PeCorA cannot do), ProteoForge consistently hit MCC around 0.45 to 0.61, while COPF hovered around 0.27. At a p-value cutoff of 0.001, COPF's grouping MCC was near zero in most simulated conditions.

One result surprised us. In the imputation simulation, ProteoForge's *grouping* performance actually improved slightly after imputation (MCC from 0.60 to 0.61). Why? When a peptide is completely missing in one condition and gets imputed with a down-shifted low value, it creates a strong, unambiguous signal. The clustering picks it up correctly.

{% details(summary="What about AlphaQuant and MSstatsWeightedSummary?") %}

Two other tools address related problems in this space. AlphaQuant uses tree-based quantification to organize peptide data hierarchically and can infer proteoform groups from bottom-up data. MSstatsWeightedSummary handles the shared peptide problem through weighted summarization with Huber loss. Both are complementary to ProteoForge rather than direct competitors. ProteoForge focuses specifically on the interaction between missing data, discordant peptide detection, and proteoform grouping. The three tools answer different questions and could be used in combination on the same dataset.

{% end %}

## The hypoxia application

Benchmarks are one thing. Real biology is another.

We applied ProteoForge to a published dataset from Tomin et al. (2025)[^9], who measured the proteome of H358 lung cancer cells under normoxia (21% O2) and hypoxia (1% O2) at 48 and 72 hours. The data came from DIA-NN[^10] as precursor-level quantities. After filtering and imputation, we had 95,369 peptides across 7,161 proteins.

The numbers alone tell a story. At 48 hours, about 15% of proteins had multiple discordant peptides. At 72 hours, that jumped to 36%. Hypoxia is not a subtle perturbation, and the proteoform-level response grows over time in a way that protein-level analysis completely misses. **Figure 3A** shows this distribution shift from 48 to 72 hours. The fraction of proteins with multiple significantly discordant peptides more than doubles.

The original study by Tomin et al.[^9] reported increased levels of S-lactoylglutathione (a GLO1 product) under hypoxia, but no change in GLO1 protein abundance. That is a contradiction. If the product goes up, something about the enzyme should be different.

ProteoForge resolved it.

At 48 hours, one peptide in GLO1 (harboring a known phosphorylation site at T35 and a mutagenesis site at Q34) showed elevated intensity under hypoxia while the other peptides stayed flat. By 72 hours, this expanded into a multi-peptide dPF (three peptides, including one with ubiquitination/acetylation at K148). The protein average saw nothing because the canonical peptides diluted the signal.

{% callout(type="tip") %}

**Figures 3D and 3E** show the GLO1 story in full. 3D has the peptide intensity profiles across conditions. 3E maps each peptide against known PTMs and protein features. The phosphorylation at T35 is particularly interesting: it sits near GLO1's active site, and the discordance emerges before the multi-peptide dPF forms at 72 hours.

{% end %}

This is what I mean by "the averaging problem." GLO1 was regulated. The original analysis just could not see it.

### FPGT: catching isoform-driven variance

Fucose-1-phosphate guanylyltransferase (FPGT) provided a different kind of example. At 48 hours, all peptides behaved the same. At 72 hours, two peptides spanning amino acids 60 to 95 dropped under hypoxia while the rest stayed stable.

**Figures 3F and 3G** show the FPGT peptide profiles and protein schematic, with the two discordant peptides highlighted in the N-terminal region and isoform boundaries marked.

### What happens to your pathway analysis

This was, for me, the most striking result.

We ran four different protein-level quantification strategies through QuEStVar[^11] (our equivalence testing framework from the earlier paper) and then into pathway enrichment with g:Profiler[^12]:

| Quantification strategy | % Proteins regulated at 72h | GO:BP terms found |
| --- | --- | --- |
| DIANN Original | 2% | Near zero |
| Mean (top 3 peptides) | ~3% | Minimal |
| Mean (all peptides) | ~4% | Minimal |
| ProteoForge dPFs | 23% | 87 elevated + 181 reduced |

That is not a marginal improvement. That is the difference between "hypoxia did almost nothing to this proteome" and "hypoxia restructured a quarter of the proteome at the proteoform level."

{% callout(type="note") %}

**Figures 4C and 5 tell this story visually.** Figure 4C shows the stacked bar charts of regulatory classifications. The contrast between "Original" and "dPFs" bars is startling. Figure 5 shows the downstream pathway enrichment: "Original" finds almost no elevated or reduced GO terms at 72 hours while "dPFs" finds hundreds, including canonical hypoxia response pathways.

{% end %}

The pathway results were telling. The original analysis found broad equivalence across GO categories at 72 hours. The dPF analysis found canonical hypoxia response pathways correctly classified as elevated. Cell cycle terms were reduced. Metabolic terms showed complex, time-dependent shifts. Signaling terms appeared elevated.

The "Original" analysis missed all of this. Not because the data was bad. Because the quantification averaged it away.

## Things I wish I had known earlier

A few practical notes for anyone thinking about using ProteoForge.

{% callout(type="warning") %}

**The 60% missingness cliff.** ProteoForge handles missing data better than anything else we tested, but there is a hard limit around 60%. Past that, RLM starts treating imputed values as the majority signal rather than outliers, and performance drops sharply. If your dataset has more than 60% missing values, consider using the WLS model with custom imputation weights instead of RLM (see Supplementary Note 1). Or consider whether the dataset is salvageable at all.

{% end %}

{% callout(type="warning") %}

**Minimum four peptides per protein.** ProteoForge requires at least four peptides per protein. This is not arbitrary. The interaction model needs enough peptides to estimate the protein-level consensus and detect deviations from it. Proteins with fewer peptides are excluded. This means ProteoForge is best suited for DIA or deep DDA datasets. Shallow experiments with 1 to 2 peptides per protein will not benefit.

{% end %}

**It is not a package yet.** The analysis repository on [GitHub](https://github.com/LangeLab/ProteoForge_Analysis) contains the scripts and notebooks used for the manuscript. A standalone Python package is under development but not released. If you use the current code, expect some rough edges.

## Why this matters (to me)

I started this work because of pediatric cancer. My PhD focused on computational proteomics for childhood leukemia, and the proteoform question kept coming up. In our leukemia data, we would see proteins where the overall level looked stable between diagnosis and relapse, but specific peptides shifted dramatically. We could not make sense of it with protein-level tools.

ProteoForge came from that frustration. The hypoxia application in the paper is a clean, well-controlled dataset that made for a good proof of concept. But the motivation was always translational: can we find proteoform-level changes in disease that protein-level analysis misses?

The GLO1 result gives me confidence that the answer is yes.

## What comes next

The preprint is currently under review at the *Journal of Proteome Research*. The standalone Python package is in development.

If you want to try it on your data, the [analysis repository](https://github.com/LangeLab/ProteoForge_Analysis) has everything. The Zenodo snapshot ([doi:10.5281/zenodo.17795845](https://doi.org/10.5281/zenodo.17795845)) freezes the exact version used in the manuscript.

---

**Paper:** Ergin, E. K., Conrrero, A., Ferguson, K. M., Lange, P. F. (2025). ProteoForge: An Imputation-Aware Framework for Differential Proteoform Discovery in Bottom-Up Proteomics. *bioRxiv*. [doi:10.64898/2025.12.12.694008](https://www.biorxiv.org/content/10.64898/2025.12.12.694008v1)

**Code:** [github.com/LangeLab/ProteoForge_Analysis](http://github.com/LangeLab/ProteoForge_Analysis)

**Data:** PRIDE repository, [PXD062503](https://www.ebi.ac.uk/pride/archive/projects/PXD062503) (Tomin et al. hypoxia dataset)

[^1]: Smith, L.M. et al. (2021). The Human Proteoform Project: Defining the human proteome. *Science Advances*, 7(46). [doi:10.1126/sciadv.abk0734](https://doi.org/10.1126/sciadv.abk0734)

[^2]: Smith, L.M. & Kelleher, N.L.; Consortium for Top Down Proteomics (2013). Proteoform: a single term describing protein complexity. *Nature Methods*, 10(3), 186-187. [doi:10.1038/nmeth.2369](https://doi.org/10.1038/nmeth.2369)

[^3]: Comparative analysis of KRAS4a and KRAS4b splice variants reveals distinctive structural and functional properties (2024). *Science Advances*. [doi:10.1126/sciadv.adj4137](https://doi.org/10.1126/sciadv.adj4137). See also: Mapping the KRAS proteoform landscape in colorectal cancer identifies truncated KRAS4B that decreases MAPK signaling (2023). [PMC9808003](https://pmc.ncbi.nlm.nih.gov/articles/PMC9808003/).

[^4]: Peptide Correlation Analysis (PeCorA) Reveals Differential Proteoform Regulation (2021). *Journal of Proteome Research*, 20(4). [doi:10.1021/acs.jproteome.0c00602](https://doi.org/10.1021/acs.jproteome.0c00602)
[^5]: Bludau, I. et al. (2021). Systematic detection of functional proteoform groups from bottom-up proteomic datasets. *Nature Communications*, 12, 3810. [doi:10.1038/s41467-021-24030-x](https://doi.org/10.1038/s41467-021-24030-x)

[^6]: Huber, P.J. (1964). Robust Estimation of a Location Parameter. *Annals of Mathematical Statistics*, 35(1), 73-101. [doi:10.1214/aoms/1177703732](https://doi.org/10.1214/aoms/1177703732)

[^8]: Ward, J.H. Jr. (1963). Hierarchical Grouping to Optimize an Objective Function. *Journal of the American Statistical Association*, 58(301), 236-244. [doi:10.1080/01621459.1963.10500845](https://doi.org/10.1080/01621459.1963.10500845)

[^7]: Benjamini, Y. & Hochberg, Y. (1995). Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289-300. [doi:10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)

[^9]: Tomin, T. et al. (2025). Increased antioxidative defense and reduced advanced glycation end-product formation by metabolic adaptation in non-small-cell-lung-cancer patients. *Nature Communications*. [doi:10.1038/s41467-025-60326-y](https://doi.org/10.1038/s41467-025-60326-y)

[^10]: Demichev, V. et al. (2020). DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput. *Nature Methods*, 17, 41-44. [doi:10.1038/s41592-019-0638-x](https://doi.org/10.1038/s41592-019-0638-x)

[^11]: Ergin, E.K., Myung, J.J.K., Lange, P.F. (2024). Statistical Testing for Protein Equivalence Identifies Core Functional Modules Conserved across 360 Cancer Cell Lines. *Journal of Proteome Research*, 23(6), 2169-2185. [doi:10.1021/acs.jproteome.4c00131](https://doi.org/10.1021/acs.jproteome.4c00131)

[^12]: Raudvere, U. et al. (2019). g:Profiler: a web server for functional enrichment analysis and conversions of gene lists (2019 update). *Nucleic Acids Research*, 47(W1), W191-W198. [doi:10.1093/nar/gkz369](https://doi.org/10.1093/nar/gkz369)
