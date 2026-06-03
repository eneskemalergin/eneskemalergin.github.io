+++
title = "proDA"
date = 2020-05-05
description = "Probabilistic dropout analysis for label-free proteomics. Handles missing values by modeling dropout curves instead of imputing."
[taxonomies]
tags = ["proteomics", "statistics", "quantification", "differential-abundance"]
[extra]
kind = "reading"
featured_image = "/blog/images/proda/proDA_fig2.jpg"
edited_date = "2026-06-02"
+++

> **Note:** This reading note was originally written in 2020 when I first encountered the preprint. I have expanded and updated it in June 2026 with proper citation details (the paper was published in *Journal of Proteome Research* after the initial bioRxiv version) and verified that the proDA package remains actively maintained on Bioconductor.

{% callout(type="note") %}
**Paper:** [Probabilistic dropout analysis for identifying differentially abundant proteins in label-free mass spectrometry](https://www.biorxiv.org/content/10.1101/661496v2)  
**Authors:** Constantin Ahlmann-Eltze, Simon Anders  
**Published:** bioRxiv (2019), later published in *Journal of Proteome Research* (2020){% sidenote() %}I originally read the bioRxiv preprint, but if you are citing this in a paper, use the JPR version. — EKE, June 2026{% end %}  
**Tool:** [proDA R package](https://bioconductor.org/packages/proDA) | [GitHub](https://github.com/const-ae/proDA){% sidenote() %}As of June 2026, the GitHub repo shows recent commits and the Bioconductor package is in active release (version 1.26.0). This is not abandonware. The method has held up and the implementation is maintained. — EKE, June 2026{% end %}

**Citation:**  
Ahlmann-Eltze, C. & Anders, S. proDA: Probabilistic Dropout Analysis for Identifying Differentially Abundant Proteins in Label-Free Mass Spectrometry. *J. Proteome Res.* **19**, 1761–1774 (2020).
{% end %}

---

## Why this one stuck

proDA does offer an option to do testing with missing values. Missing values in label-free data are not always random. You miss the low-intensity stuff systematically. Drop in a median or some small constant and you've quietly invented data points. Your matrix looks complete. Your downstream code runs without complaints. Your p-values are confident. They're also biased.

proDA refuses the shortcut. Instead of filling holes, it fits a sigmoidal dropout curve per sample. If a value is missing, the model says "this protein was probably below detection, here's the probability distribution for where it might have been." Then it carries that uncertainty through to the differential abundance test. The error bars grow. The significant hits shrink. The ones that survive are real.

{{ figure(src="/blog/images/reading/proDA.jpg", alt="proDA's probabilistic dropout model showing how missing values are modeled as censored observations below detection threshold", caption="The dropout model fits a curve describing missingness probability as a function of intensity. Proteins with all missing values (blue) have wide uncertainty. Proteins with some observations (orange, green) combine observed data with modeled dropout probability. From Ahlmann-Eltze & Anders, 2019.") }}

## What you actually get

The practical difference is honest uncertainty. If you have a protein with 5 missing values and 1 weak observation, traditional imputation fills those 5 holes with guesses and pretends you measured 6 data points. proDA says "you measured one marginal signal, the rest fell below detection, here's how uncertain your mean estimate actually is."

Your significantly differentially abundant list gets shorter. That's the point. The proteins you lose were riding on invented data. The ones you keep passed a test that acknowledges how little you actually saw.

## When it matters

This matters most when you're running differential abundance tests and your FDR depends on accurate variance estimates. If you're just making a heatmap for a figure or doing quick exploratory clustering, imputation is fine. The problem is when you impute for visualization and then forget you did it before running statistics.

{% callout(type="note") %}
**Final thought:** proDA is a reminder that the data we don't see can be just as important as the data we do. Since 2020, there have been many methods have been developed around this idea, I myself even have been using limma with weighted testing and robust linear models to go around imputing missing values. Imputation can give us a false sense of confidence. Modeling missingness explicitly keeps us honest about what our data can actually tell us. — EKE, June 2026
{% end %}
