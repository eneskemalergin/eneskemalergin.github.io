+++

title = "The Landscape of Proteomics Search Engines, and Does a Zig-Based One Make Sense?"

date = 2026-01-02

description = "The search engine space is crowded, fast-moving, and genuinely competitive. DIA-NN, Spectronaut, FragPipe, MaxQuant, and Sage each carved a niche. A Zig-based search engine is not the right next step. The gap between engines might be."

[taxonomies]

tags = ["proteomics", "search-engines", "dda", "dia", "open-science", "zig", "opinion"]

[extra]

kind = "opinion"

+++

{% callout(type="note") %}

**TLDR:** The proteomics search engine space is crowded and genuinely competitive. DIA-NN, Spectronaut, FragPipe, MaxQuant, and Sage each occupy a real niche. Sage proved a systems language can win on throughput, but features lag behind the decade-old tools. Pipeline projects like quantms and nf-core are already solving the integration problem by wrapping engines in reproducible workflows. A Zig-based search engine is not the right next step. A Zig-based workflow engine built around composable libraries might be.

{% end %}

I kept asking myself whether a Zig-based proteomics search engine makes sense. The answer is probably no. The space is crowded, the incumbents are improving fast, and the hard problems are not about search speed. Why that is the case is more interesting than a simple yes or no.

## The landscape as of early 2026

DDA is not dead, but DIA is where the field is heading. The engines that matter most right now are the ones handling DIA data well.

On the open-source side, DIA-NN{% sidenote() %}DIA-NN is built primarily by Vadim Demichev. Supports GPU and CPU, library-based and library-free modes, reads most vendor formats. Free for academic and commercial use. [GitHub](https://github.com/vdemichev/DiaNN){% end %} reset expectations for DIA processing. MaxQuant with MaxDIA handles DIA within the Quant ecosystem. FragPipe{% sidenote() %}FragPipe wraps MSFragger (DDA and DIA search) with DIA-NN (quantification), MSBooster, Percolator, and ProteinProphet in one pipeline. [fragpipe.nesvilab.org](https://fragpipe.nesvilab.org){% end %} combines MSFragger and DIA-NN in a single platform. Skyline remains the targeted quantification workhorse.

On the commercial side, Spectronaut{% sidenote() %}Biognosys. Polished UI, library-based and directDIA modes, subscription licensing. Pushes users toward the proprietary HTRMS format. [biognosys.com](https://biognosys.com/software/spectronaut){% end %} has the best UI and turnkey analysis. Proteome Discoverer is Thermo's bundled solution, Windows-bound and slower than alternatives. Mascot still exists but feels like legacy infrastructure.

On DDA, MSFragger{% sidenote() %}MSFragger uses fragment ion indexing for fast database search. Open-source, Nesvizhskii lab. Published in *Nature Methods* (2017). Integrated into FragPipe.{% end %} changed the speed equation years ago. Sage{% sidenote() %}Sage by Michael Lazear. Rust-based, MIT-licensed. Benchmarks faster than MSFragger on most DDA benchmarks. LFQ and TMT quantification, RT prediction, FDR control. Published in *JPR* (2023). [GitHub](https://github.com/lazear/sage){% end %} is a newer Rust-based engine that benchmarks faster still. One developer, limited development depth. That is not a criticism. It is the reality of a project that started as a personal learning exercise.

## The space is crowded, and that is a good thing

This is worth saying plainly. The search engine landscape is not broken. It is competitive, fast-moving, and full of genuine innovation. New tools appear regularly. Old tools improve. Benchmarking papers compare them{% sidenote() %}For example, the 2023 *Nature Communications* benchmarking of DIA-NN, Spectronaut, MaxDIA, and Skyline across Orbitrap and timsTOF data. More recently, comparisons of Spectronaut vs DIA-NN on lung adenocarcinoma biopsies (Yu & Siu, *JPR* 2026).{% end %}. The community debates them. This is what a healthy software ecosystem looks like.

If you need to analyze proteomics data today, you have good options. Free ones, fast ones, well-documented ones. The problem is not a lack of tools. The problem is stitching them together.

## DIA-NN and Spectronaut: two models, both working

DIA-NN is remarkable. Built mostly by one person, now one of the most-used DIA tools in the field. Free for academic and commercial use. No license wall between institutions. Fast.

Spectronaut has a polished interface, excellent documentation, and dedicated support. It also has a subscription fee, proprietary HTRMS format lock-in, and academic/commercial license tiers. The results are good. The cost, the tiering, and the format lock-in are the parts that frustrate me. If a graduate student learns on Spectronaut and moves to a lab that cannot afford the license, their tool stack breaks.

Both models work. DIA-NN proved you do not need a company to build a widely adopted tool. Spectronaut proves commercial polish still commands a market. Neither is going away.

## Speed is solved. Scale is not

MSFragger solved raw search speed. Sage pushed it further. Search throughput is no longer what keeps people up at night.

The new bottleneck is cohort scale. At 20 samples, most tools work. At 500, the ones designed for workstations start creaking. At 1,000, the ones not built for headless environments become painful.

{% code(ln="bash", caption="CS1: The gap between tools is where the real work lives.") %}

## Run DIA-NN on 500 .raw files

diann --dir data/ \
      --lib spectral_library.speclib \
      --out report.tsv

## Convert FragPipe output for downstream analysis

python -c "
import pandas as pd
combined = []
for f in glob('combined_protein.tsv'):
    combined.append(pd.read_csv(f, sep='\t'))
pd.concat(combined).to_csv('all_results.tsv', sep='\t')
"
{% end %}

The problems are not CPU cycles. They are memory management across thousands of identifications, file I/O patterns that assume local disk when data lives on network storage, and quantification workflows that break silently when scaled.

Spectronaut handles large cohorts if you pay for the server license. DIA-NN handles them if configured correctly. FragPipe works but the Java GUI adds friction on headless servers. MaxQuant will run, but slowly.

## Feature fragmentation: everyone owns a corner

Nobody does everything well. Each tool has a signature strength.

MaxQuant owns label-free quantification. MaxLFQ is the algorithm papers cite without thinking. FragPipe bridges DDA and DIA with MSFragger speed. Spectronaut has the best UI and directDIA mode. DIA-NN has speed, openness, and format support. Skyline owns targeted quantification and method building. Sage has raw throughput and cloud-native design but lacks the quantification depth and PTM analysis of tools that have been evolving for a decade.

The niches are deep but narrow. If you need LFQ on a DIA dataset with PTM analysis and batch correction, you are stringing together multiple tools. That works. It is also where the friction lives.

The field rewards novelty. A new quantification method gets a paper. A new search algorithm gets a paper. Nobody gets a paper for making tools work together. The incentive structure produces fragmentation.

## Sage, and what it taught me

I followed Sage from its earliest days. It started as a blog post and a simple repository. Michael Lazear was learning Rust and proteomics at the same time. The project grew from a learning exercise into a *JPR* publication and a tool people actually use in production{% sidenote() %}Lazear MR. "Sage: An Open-Source Tool for Fast Proteomics Searching and Quantification at Scale." *J. Proteome Res.* 22(11):3652-3659, 2023. [DOI](https://doi.org/10.1021/acs.jproteome.3c00486). MIT-licensed. [GitHub](https://github.com/lazear/sage){% end %}.

Sage proved two things. First, a modern systems language can enter a mature space and win on raw performance. Second, the gap between a fast search engine and a full-featured platform is enormous. Sage is faster than most tools on clean benchmarks. It also has fewer features, less community testing, and narrower format support than the tools it competes with. {% sidenote() %}That is not a criticism. It is the reality of a project that started as a personal learning exercise. And hasn't had the time to evolve into mature tool. The point is the gap between a fast search engine and a complete analysis platform is measured in years of domain-specific development, not in CPU cycles.{% end %}

> A fast search engine is not the same as a complete analysis platform. The distance between them is measured in years of domain-specific development, not in CPU cycles.

I watched that trajectory. It made me think about what I could learn by building something similar in Zig. The conclusion I arrived at is not the one I expected.

## People are already solving the integration problem

The gap between tools is real, but groups are working on it.

quantms{% sidenote() %}Dai C, Pfeuffer J, Wang H et al. "quantms: a cloud-based pipeline for quantitative proteomics enables the reanalysis of public proteomics data." *Nature Methods* 21:1603-1607, 2024. [GitHub](https://github.com/bigbio/quantms). Wraps search engines into reproducible Nextflow pipelines with containers. quantmsdiann wraps DIA-NN for DIA.{% end %} wraps search engines and quantification tools into reproducible Nextflow pipelines with containerized environments. It supports DDA and DIA workflows and follows nf-core standards.

nf-core/proteomicslfq provides LFQ analysis using OpenMS and MSstats. The nf-core community now has dozens of pipelines and thousands of contributors, with a dedicated Mass Spectrometry Proteomics Special Interest Group.

These projects show the path forward. The integration problem is being solved by workflow engines wrapping existing tools in reproducible containers. You do not need to rebuild the search engine. You need to make the engines work together at scale.

## A Zig-based engine? Probably not. Something adjacent

Sage answered the question of whether a new language can produce a competitive search engine. It can. It also answered the question of whether speed alone wins. It does not.

The hard problems in search engines are quantification algorithms tuned for a decade, FDR control and protein inference that depend on deep domain knowledge, and PTM localization that is as much biochemistry as computation. Building a new engine means rebuilding all of that. The field does not need another fast searcher. It has several.

What I keep coming back to is the workflow engine idea from my earlier thinking{% sidenote() %}See [Workflow Engines and the Case for a Zig-Based One](@/blog/2025-10-29-opinion-workflow_engine_in_zig.md).{% end %}. A Zig-based workflow engine, not a search engine. Something that treats search engines and quantification tools as composable libraries, OpenMS-style{% sidenote() %}OpenMS is a C++ framework for mass spectrometry data analysis with Python bindings (pyOpenMS). Provides modular tools (TOPP) for building custom workflows. [openms.de](https://openms.de). BSD-licensed. Nearly two decades of continuous development.{% end %}, but built from the start for the scale and deployment constraints of modern proteomics.

The value would not be in beating DIA-NN on identifications. It would be in making the glue between tools more reliable and less fragile.

This is a library project, not an engine project. It is also a multi-year effort with uncertain demand. I am not starting it tomorrow. But watching Sage grow from a blog post to a real tool makes the idea feel less abstract.

## Where I land

The search engine landscape is crowded. It is also healthy. Genuine competition, genuine open-source options, and genuine innovation. The problems are not a lack of good engines. The problems are feature fragmentation, scale challenges, and the integration work of stitching tools together.

Pipeline projects like quantms and nf-core are solving integration with Nextflow and containers. That is probably the right approach for production work. A Zig-based workflow engine that treats proteomics tools as composable building blocks might be a better fit for exploration, for learning, and for the kind of custom pipelines where Makefiles still work until they do not.

I will keep using DIA-NN for most things. I will keep watching Sage grow. I will keep wishing the tools talked to each other better.

And I will probably keep wondering what a modular proteomics toolkit in Zig would look like, even if I never build it.
