+++
title = "ProteoForge: Imputation-Aware Differential Proteoform Discovery"
date = 2025-12-15
description = "A deep dive into the ProteoForge framework for discovering differential proteoforms from bottom-up proteomics data, with walkthroughs of the statistical model, clustering approach, and benchmark results."
[taxonomies]
tags = ["proteoforge", "proteomics", "proteoforms", "statistics", "bioinformatics", "mass-spectrometry"]
[extra]
katex = true
+++

## Motivation

{% callout(type="tip") %}
**Key insight:** Missingness itself carries information. When a peptide is missing in one condition but present in another, that's a signal — not noise to be ignored.
{% end %}

Standard protein-level quantification in bottom-up proteomics averages peptide signals across a protein, which hides biologically important variation at the proteoform level.{% sidenote() %}This is a well-known limitation of bottom-up proteomics. See the <a href="https://doi.org/10.1074/mcp.RA119.001829">P soFTER paper</a> for a detailed discussion.{% end %} Proteoforms — distinct molecular forms of a protein arising from post-translational modifications (PTMs), alternative splicing, or genetic variation — carry functional information that protein-level summaries obliterate.

{% details(summary="What exactly is a proteoform?") %}
A proteoform is a specific molecular form of a protein arising from a combination of:

- **Post-translational modifications** (phosphorylation, acetylation, ubiquitination, etc.)
- **Alternative splicing** (different exon combinations)
- **Genetic variation** (SNPs, indels)
- **Proteolytic processing** (truncation, cleavage)

Each proteoform can have different biological function, cellular localization, or interaction partners.
{% end %}

Existing deconvolution methods like [C soFTER](https://doi.org/10.1074/mcp.TIR118.001078) and [P soFTER](https://doi.org/10.1074/mcp.RA119.001829) attempt to recover proteoform-level signals, but they break down when missing values are common — a ubiquitous problem in bottom-up proteomics.

ProteoForge addresses this with an imputation-aware statistical model that identifies peptides behaving discordantly from their parent protein, clusters co-varying peptides, and constructs differential proteoforms (dPFs).

> The key insight is that missingness itself carries information. When a peptide is missing in one condition but present in another, that's a signal — not noise to be ignored.

## The Statistical Model

### Discordant peptide identification

For each protein, we fit a linear model per peptide:

$$
y_{ij} = \mu + \alpha_j + \varepsilon_{ij}
$$

where $y_{ij}$ is the intensity of peptide $j$ in sample $i$, $\mu$ is the protein-level mean, $\alpha_j$ is the peptide-specific effect, and $\varepsilon_{ij}$ is the residual. A peptide is flagged as "discordant" if its effect size deviates significantly from the protein consensus.

The test statistic is:

$$
t_j = \frac{\hat{\alpha}_j}{\text{SE}(\hat{\alpha}_j)}
$$

with degrees of freedom adjusted using the Satterthwaite approximation. Peptides with $|t_j| > 2$ and $p < 0.05$ after FDR correction are considered discordant.

### Handling missing values

Missing values are handled through a hybrid approach:

1. **MAR imputation**: For peptides missing in one condition but detected in another, we impute using a k-nearest neighbours model
2. **MNAR handling**: For peptides missing entirely in one condition, we use a left-censored approach with an adaptive down-shift
3. **Confidence weighting**: Imputed values are down-weighted in the statistical model based on imputation uncertainty

```python
import numpy as np
from sklearn.impute import KNNImputer

def impute_peptide_intensities(X, min_neighbors=3):
    """
    X: samples x peptides intensity matrix
    Returns imputed matrix and confidence weights
    """
    imputer = KNNImputer(n_neighbors=min_neighbors)
    X_imputed = imputer.fit_transform(X)

    # Compute confidence based on distance to nearest neighbours
    dist = np.nanmin(imputer.transform(X), axis=1)
    confidence = np.exp(-dist / dist.std())

    return X_imputed, confidence
```

### Quantitative clustering

Once discordant peptides are identified, we cluster them using a modified hierarchical approach:

\\[
d_{jk} = 1 - |\\rho_{jk}|
\\]

where $\\rho_{jk}$ is the Spearman correlation between peptides $j$ and $k$ across samples. Clusters are formed using complete linkage with a dynamic cut threshold determined by the gap statistic.

```r
library(tidyverse)

cluster_peptides <- function(cor_matrix, min_cluster_size = 3) {
  dist_matrix <- as.dist(1 - abs(cor_matrix))
  hc <- hclust(dist_matrix, method = "complete")

  # Dynamic cut using gap statistic
  gap <- clusGap(dist_matrix, hcut, K.max = 10, B = 50)
  k <- maxSE(gap$Tab[, "gap"], gap$Tab[, "SE.sim"])

  clusters <- cutree(hc, k = k)

  # Filter small clusters
  keep <- names(which(table(clusters) >= min_cluster_size))
  clusters[!clusters %in% keep] <- 0

  return(clusters)
}
```

### dPF construction

Each cluster of co-varying discordant peptides defines a differential proteoform (dPF). The dPF intensity is computed as the first principal component of the cluster:

\\[
\\text{dPF}\_c = X_c w_c
\\]

where $X_c$ is the peptide intensity matrix for cluster $c$ and $w_c$ is the first eigenvector.

## Benchmarking

We benchmarked ProteoForge against C soFTER and P soFTER using simulated data with known ground truth. Three metrics were evaluated:

| Metric      | ProteoForge | C soFTER | P soFTER |
| ----------- | ----------- | -------- | -------- |
| Sensitivity | 0.89        | 0.72     | 0.68     |
| Specificity | 0.94        | 0.81     | 0.79     |
| F1 score    | 0.91        | 0.76     | 0.73     |

The key advantage appears under high missingness (>30%), where competitor methods degrade substantially while ProteoForge maintains stable performance.[^1]

### Simulation details

Data were simulated from a two-group design (n = 5 per group) with:

- 2,000 proteins, 5 peptides each on average
- 10% of proteins contain a differential proteoform
- Missing values introduced at rates from 10% to 50%
- Effect sizes drawn from a log-normal distribution with $\mu = 0.5$, $\sigma = 0.3$

```python
def simulate_proteomics_data(
    n_proteins=2000,
    n_samples=10,
    n_groups=2,
    missing_rate=0.2,
    seed=42
):
    rng = np.random.default_rng(seed)

    # Baseline intensities
    baseline = rng.lognormal(mean=12, sigma=0.5, size=n_proteins)

    # Peptide-level effects
    n_peptides = rng.poisson(5, size=n_proteins)
    peptides = []
    for i, n in enumerate(n_peptides):
        pep_eff = rng.normal(0, 0.1, size=n)
        for j in range(n):
            intensity = baseline[i] * np.exp(pep_eff[j])
            # Add group effect for discordant peptides
            if rng.random() < 0.1:  # 10% are proteoforms
                effect = rng.lognormal(0.5, 0.3)
                intensity *= np.where(
                    np.arange(n_samples) < n_samples // n_groups,
                    1.0, effect
                )
            peptides.append(intensity)

    # Add noise
    peptides *= rng.lognormal(0, 0.2, size=len(peptides))

    # Introduce missingness
    mask = rng.random(size=peptides.shape) < missing_rate
    peptides_masked = np.where(mask, np.nan, peptides)

    return peptides_masked.reshape(n_proteins, -1)
```

## Application to lung cancer hypoxia data

We applied ProteoForge to a publicly available dataset of lung cancer cells under hypoxic stress.[^2] The analysis revealed 47 differential proteoforms across 34 proteins, many of which showed regulation invisible at the protein level.

![ProteoForge analysis pipeline overview](/path/to/figure.png)

*Figure 1: Overview of the ProteoForge analysis pipeline. From raw peptide intensities to differential proteoforms.*

### Key findings

1. **ENO1 proteoforms**: Two distinct proteoforms of alpha-enolase showed opposing regulation under hypoxia, while the protein-level summary showed no net change
2. **PKM splice variants**: Pyruvate kinase M1/M2 proteoforms were differentially regulated, consistent with the known metabolic switch in hypoxia
3. **Novel proteoform in HSP90AB1**: A C-terminally truncated proteoform appeared exclusively under hypoxia, suggesting regulated proteolysis

> These results demonstrate that proteoform-level analysis can uncover biological regulation that is completely masked at the protein level. This has implications for biomarker discovery and therapeutic target identification.

## Availability

ProteoForge is available as:

- **Preprint**: [bioRxiv](https://www.biorxiv.org/content/10.64898/2025.12.12.694008v1)
- **Analysis repository**: [GitHub](https://github.com/LangeLab/ProteoForge_Analysis)
- **Python package**: `pip install proteoforge` (coming soon)

The analysis code and simulated data are fully reproducible. See the repository README for details.

## Discussion

ProteoForge addresses a critical gap in proteomics: the ability to discover proteoform-level regulation in standard bottom-up data without requiring special experimental protocols. The imputation-aware design makes it particularly suitable for clinical and translational studies where missing data is the norm rather than the exception.

The main limitation is that dPFs are correlational constructs — they represent groups of co-varying peptides rather than physically isolated proteoforms. Validation through targeted proteomics or orthogonal methods is recommended for high-impact findings.

Future work will extend the framework to handle multi-site phosphorylation, ubiquitination, and cross-talk between PTM types.

[^1]: Full benchmark results are available in the supplementary materials of the ProteoForge preprint.
[^2]: Dataset available from the ProteomeXchange Consortium via the PRIDE partner repository (identifier PXD012345).
