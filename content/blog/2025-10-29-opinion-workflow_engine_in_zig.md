+++

title = "Workflow Engines and the Case for a Zig-Based One"

date = 2025-10-29

description = "Nextflow and Snakemake both get the big things right and the small things wrong. A bioinformatics-specific engine with no runtime and a single static binary might fix the part that actually costs time."

[taxonomies]

tags = ["zig", "bioinformatics", "workflow-engines", "tooling", "opinion"]

[extra]

kind = "opinion"

+++

{% callout(type="note") %}

**TLDR:** I have used Snakemake, Nextflow, and GNU Make to run real proteomics pipelines. All three solve the big problem. Reproducible execution graphs. And all three make the small things harder than they should be. Container overhead, JVM startup, and general-purpose design add friction that a domain-specific engine could remove. This is not a plan. It is a direction I am curious about.

{% end %}

I keep coming back to an idea I have not built.

A workflow engine for bioinformatics. No runtime. No JVM. No Conda environments to maintain. A single static binary that knows what mzML and FASTA are, because those are the files we actually work with. Copy it to a cluster node and run it.

I know how that sounds. The space already has Nextflow, Snakemake, CWL, WDL{% sidenote() %}And Cromwell, Toil, Luigi, Prefect, Airflow, Parsl. The design space is wider than the bioinformatics corner. I name the ones I have used.{% end %}. They all have real users and real papers. Adding one more sounds like hubris.

The idea will not leave me alone. I want to explain why, and where it is probably wrong.

## The tools I actually use

My first workflow engine was a Makefile. It resolved dependencies, skipped completed steps, and parallelized across cores. For a single-machine analysis with a few dozen samples, it was enough.

{% code(ln="make", caption="CS1: What most of my workflows actually look like.") %}
results/%.mzML: raw/%.raw
    wine msconvert $< --mzML -o $@

results/%.pep.xml: results/%.mzML
    tide-search $< $@

results/%.tsv: results/%.pep.xml
    percolator $< $@
{% end %}

Then the data grew. I moved to Snakemake because it understood glob patterns and could distribute to a cluster. I moved to Nextflow because the lab standardized on it.

Both are good. Both frustrate me.

## Snakemake: great rules, heavy environments

Snakemake is the most natural fit for a Python-native bioinformatician. Rules extend Python syntax. The DAG is built before execution so you see what will run before it starts. I liked using it.

The pain is the environment layer. Snakemake's `conda:` directive pins environments per rule. For a pipeline with twenty steps, that is twenty environments to maintain. When one Conda solve hangs or a container pulls the wrong tag, you spend an afternoon fixing infrastructure. The Python runtime is not the problem. What sits on top of it is.

I also wonder if per-rule environments are solving the wrong problem. My pipelines depend on maybe four tools plus Python. Twenty Conda environments means I have managed the same numpy install twenty times.

## Nextflow: channels are good, startup is not

Nextflow's channel model is genuinely good{% sidenote() %}DSL2 channels handle per-sample branching in a way that Snakemake's rule-level scoping does not. When a pipeline step decides what to run next based on the previous output, that matters.{% end %}. Data flows asynchronously. You branch, merge, and filter without writing explicit orchestration code. For hundreds of samples with per-sample variability, this model makes hard things manageable.

The startup cost is what I notice most. Even with `NXF_JVM_ARGS` tuned, there is a visible delay before the pipeline begins doing useful work. The JVM heap overhead{% sidenote() %}The head process uses hundreds of megabytes. For pipelines running massive tools like MSFragger or DIA-NN, that overhead is negligible. The stronger problem is startup latency and the extra layer of abstraction when debugging.{% end %} is rarely the dominant resource cost in pipelines where the tools themselves use tens of gigabytes.

> I have debugged a Nextflow pipeline at 2 AM. I do not recommend it.

Here is where I go back and forth. The channel model solves a real problem. The startup latency and debugging friction are taxes. Are they coupled? Nextflow does not need the JVM for the channel model. It needs the JVM because it is written in Groovy. That is a historical choice, not a technical necessity.

## The container tax

Both engines lean on containers for reproducibility. The idea is sound. Modern HPC clusters cache container layers effectively{% sidenote() %}Apptainer and Singularity make this viable: pull once, run hundreds of jobs from the cached copy. Container startup drops dramatically after the first pull.{% end %}.

The friction I feel is less about startup and more about maintenance. Image registries go down. Dependency rebuilds break cached layers. Provenance across container versions requires discipline that a shared cluster rarely enforces. The problem is not "containers are slow." It is "containers add a maintenance surface between me and the science."

Containers exist because shared environments drift. That is a real problem and I do not have a better answer. I want reproducibility without managing a container registry on every invocation. I do not know if that tension resolves.

## What bioinformatics workflows actually need

Here is the honest truth about where the time goes. In most proteomics pipelines, roughly 95% of wall-clock time is in search and quantification tools, 4% is data movement, and 1% is orchestration{% sidenote() %}Even eliminating all JVM and container overhead cuts the 1%, not the 95%. Speed is not the argument for a different engine. The argument is about deployment, debugging, and cognitive load.{% end %}. Eliminating JVM and container overhead changes the total runtime by barely a rounding error.

Speed is not the argument. The argument is that the orchestration layer should not add cognitive overhead that exceeds its runtime contribution. A fast, simple engine that I can understand and debug without a specialized DSL is worth having even if the pipeline runs the same wall-clock time.

## What would a format-aware engine actually do?

This is the question the idea keeps dodging. What does it mean for an engine to know mzML and FASTA?

It means the engine can validate inputs before the pipeline starts. A malformed mzML file is caught before it reaches the search tool, not during the fifth hour of a search run. It means the engine can extract metadata (instrument type, precursor tolerance, sample annotations) and propagate it through the DAG without manual wiring. It means the engine can construct parts of the pipeline graph automatically: if the input is mzML and the tool expects FASTA, the engine knows to insert a conversion step.

Current engines treat file formats as opaque strings. That is correct for general-purpose tools. For a domain-specific engine, format awareness means the engine understands the data, not just the file paths.

I do not know how far this stretches. It might be a small advantage that does not justify a new engine. It might open pipeline patterns that are awkward in current systems. This is where the novelty lives, not in the language choice.

## Why Zig keeps coming up

I should say this plainly: the language is not the hard part of a workflow engine. The hard parts are error recovery, checkpointing, cloud integration, and provenance tracking. C would work. Rust would work. Go works well and already has excellent concurrency and networking for orchestration workloads{% sidenote() %}Go is understated in most Zig comparisons. It has mature networking, stable concurrency, large ecosystem, and cross-compiles to static binaries. Many workflow tools are written in Go for good reason. Zig's advantage over Go for this problem is C interop, and even that matters less if the engine mostly orchestrates external processes.{% end %}.

What keeps me coming back to Zig is the combination of properties.

Zig produces a single static binary with no runtime. Deploy the engine with a file copy. No Python environment. No JVM. No Conda.

Zig calls C directly{% sidenote() %}`@cImport` on a C header and the functions are available. No binding layer, no FFI ceremony. ProteoWizard is C++ (needs a C ABI wrapper), but zlib, netCDF, and most compression libraries are straight C.{% end %}. For reading mzML through existing C libraries and compressing output, that integration path is short.

Zig has explicit memory. No garbage collector. For a long-running pipeline on a shared cluster node, predictable memory behavior matters more than peak throughput.

These are not unique to Zig. The difference is C interop. Rust needs `bindgen` and FFI safety wrappers. Go needs cgo. Both work, both add ceremony. For a tool that wraps other tools, ceremony compounds.

## What I have not figured out

I have not built this. The idea is still a question mark.

Zig is pre-1.0{% sidenote() %}This is the biggest practical concern. A workflow engine is infrastructure software. Infrastructure values stability, ecosystem, and backwards compatibility more than language elegance. Starting an engine on a pre-1.0 language means accepting that every release may break the build.{% end %}. It will break my code between releases. The ecosystem is tiny compared to anything in the workflow space. If the engine needs a feature that Nextflow already has, the gap is not weeks of work. It is the accumulated years of edge cases that existing engines have already absorbed.

I also have not settled the most basic question: should this be a new engine, or a library, or a set of Zig tools that slot into an existing engine? A library that generates Makefiles solves deployment without solving the DAG problem. A Zig plugin for Nextflow gives format awareness without the JVM, if that is even possible.

## Where I land

Here is the honest version. A production workflow engine to replace Nextflow is probably a bad idea. The existing tools have absorbed too many edge cases. Even if I got the architecture right, the gap in real-world testing would take years to close.

But building a small one, not to ship but to understand? That is worth doing. The value is not the engine. It is the understanding of what makes workflow orchestration hard, what tradeoffs are real, and where current tools make choices that a domain-specific approach could avoid.

I will keep using Nextflow and Snakemake for production work. They work. They have communities. They ship reproducible pipelines that produce real results.

And I will probably build something small in this direction. Not to replace Nextflow. To understand the problem space well enough to know whether the idea has anything in it.
