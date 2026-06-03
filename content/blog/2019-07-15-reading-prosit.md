+++
title = "Prosit"
date = 2019-07-15
description = "Deep learning for MS2 spectrum and retention time prediction. Accurate enough for rescoring and library generation."
[taxonomies]
tags = ["proteomics", "mass-spectrometry", "deep-learning", "spectral-prediction", "bioinformatics", "rescoring"]
[extra]
kind = "reading"
featured_image = "/blog/images/reading/prosit_mirror.jpg"
edited_date = "2026-06-02"
+++

> **Note:** I first wrote this note in the summer of 2019, right after the Nature Methods paper dropped. When I rebuild my webside and migrate the posts I had an oppurtunity to provide edits in June 2026 with proper citation details and a check on where the models live now, since the original code repository was retired in favor of newer tooling.

{% callout(type="note") %}
**Paper:** [Prosit: proteome-wide prediction of peptide tandem mass spectra by deep learning](https://www.nature.com/articles/s41592-019-0426-7)  
**Authors:** Siegfried Gessulat, Tobias Schmidt, Daniel P. Zolg, and colleagues (Mathias Wilhelm and Bernhard Kuster labs)  
**Published:** *Nature Methods* (2019), published online 27 May 2019{% sidenote() %}The Nature Methods version is the one to cite. The preprint history is messy but the final paper is solid. — EKE, June 2026{% end %}  
**Tool:** [Prosit on ProteomicsDB](https://www.proteomicsdb.org/prosit/) | [Koina model server](https://koina.wilhelmlab.org/){% sidenote() %}The original kusterlab/prosit GitHub repository was archived in August 2023. The models moved to Koina, the training code moved to dlomix, and the rescoring/library generation moved to Oktoberfest. The method did not die, it grew up and got integrated into real workflows. — EKE, June 2026{% end %}

**Citation:**  
Gessulat, S. *et al.* Prosit: proteome-wide prediction of peptide tandem mass spectra by deep learning. *Nat. Methods* **16**, 509–518 (2019).
{% end %}

---

## Why this one stuck

I had filed spectral prediction under "neat demo" and left it there. Prosit moved it off that shelf. It predicts fragment intensities and indexed retention time from peptide sequence alone, and the predictions are good enough to feed a rescorer or build a DIA library without measuring a single real spectrum.

The shift was not in the math. Predicting spectra from sequence is a straightforward supervised learning problem if you have enough training data. The shift was in the accuracy. The predictions crossed the threshold where people started using them in production pipelines instead of publishing them and moving on.

{{ figure(src="/blog/images/reading/prosit_mirror.jpg", alt="Mirror plot comparing a Prosit-predicted MS2 spectrum against an observed spectrum, showing close agreement of fragment intensities", caption="Predicted fragment intensities sit close enough to observed spectra to be used as features for rescoring and as the basis for spectral libraries. From Gessulat et al., 2019.") }}

## What you actually get

The practical impact shows up in two places. First, rescoring gets better. When you give a rescorer predicted spectra as features, it can actually distinguish good matches from noise instead of gambling on search engine scores alone. Second, you can generate spectral libraries for organisms or proteases nobody has measured. Just predict from sequence.

The interesting part is the architecture. It is not complicated. A bidirectional LSTM with attention, nothing exotic. The win came from scale. Enough training data, enough compute, and suddenly predictions that were too noisy to trust become informative.

## When it matters

This matters when you need spectral libraries for something outside the standard human/mouse/yeast space, or when rescoring database searches. It matters less if your peptides sit far from the training set. Early models struggle with unusual modifications or nontryptic cleavage. The newer models on Koina handle more, but the boundaries are still real.

The other place it matters is as proof of concept. Prosit showed that deep learning could do more in proteomics than classify spectra. It could generate them. That opened doors. Since 2019, whole workflows have been built around predicted spectra. The method did not stay in papers. It moved into tools people actually run.

{% callout(type="note") %}
**Final thought:** I never used Prosit directly in my own work. What stuck with me was watching spectral prediction go from "interesting idea" to "thing people depend on." The math is not mysterious. The training data and engineering are what made it work. It is a good example of how deep learning earns its place in proteomics: not by being clever, but by being useful enough that the field builds around it. — EKE, June 2026
{% end %}
