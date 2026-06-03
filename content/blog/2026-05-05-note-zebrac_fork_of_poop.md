+++
title = "zebrac: Why I Forked poop"
date = 2026-05-05
description = "A note on why I forked Andrew Kelley's poop into zebrac, what I have added so far, and the direction I want to take it next."
[taxonomies]
tags = ["zig", "benchmarking", "linux", "performance", "tooling", "poop", "hyperfine", "note", "zebrac"]
[extra]
kind = "note"
+++

zebrac is my fork of poop, Andrew Kelley's Linux benchmarking tool written in Zig. Andrew also created Zig, which is worth saying out loud because none of this exists without the language. I want to be clear about that from the start. poop already does the main interesting thing: it reports CPU performance counters and memory information for command benchmarks.

I did not fork it because I thought the original missed the point. I forked it because I started needing workflow features while comparing versions of my own tools.

{% callout(type="tip") %}
**What zebrac adds on top of poop.** JSON output, configurable sample counts, warmup iterations, failure tolerance, better error messages, multi-architecture CI, and a cleaned-up build system. The core is still poop's. The additions are the parts I needed day to day.
{% end %}

The first thing I wanted was JSON output. Terminal output is good when I am watching the benchmark run. JSON is better when I want to save results, inspect them later, or feed them into a script. I do not want to manually copy numbers from the terminal every time I benchmark something.

I added warmups because the first few runs of a command can be strange. Cold caches, unloaded files, initial allocations. The first measurement is rarely representative. A `--warmup` flag lets me discard those early iterations.

The other flags came from real use. `--min-samples` and `--max-samples` control how many measurements to collect. `--allow-failures` lets me benchmark commands that sometimes return non-zero. Better error messages surface when a command cannot be executed at all instead of failing silently{% sidenote() %}The error message improvements seem small, but they matter when you are benchmarking across a dozen command variants and one of them has a typo. You want to know which one failed and why, not guess.{% end %}.

{% code(ln="bash", caption="CS1: Typical zebrac invocation.") %}
zebrac --json results.json \
       --warmup 3 --min-samples 5 \
       './my_tool --input data.bin'
{% end %}

The build and CI side also got attention. zebrac tracks Zig through 0.12.0, 0.15.0, and now 0.16.0. The CI cross-compiles for x86-linux, x86_64-linux, aarch64-linux, and riscv64-linux. The `build.zig` supports `-Dstrip` and `zig build release` for multi-target binary releases. None of this changes the benchmark output, but it means the tool can live where the data lives, not just on my machine.

---

There is more I want to do. The current version works for my workflow, but the gaps are visible.

I want better shell quoting support. Passing a command with pipes, redirects, or quoted arguments to a benchmarking tool is surprisingly fragile. The shell, the flag parser, and the command string all interact in ways that break on realistic input. I want zebrac to handle the common cases without wrapping everything in a script.

I want better support for comparing two or more commands side by side. Right now I run them separately and compare JSON outputs by hand. A built-in comparison mode would make the workflow tighter.

I want cleaner export formats. Markdown tables, CSV, maybe something that pastes cleanly into a project README or a release note.

I want baseline comparisons. Run a benchmark today, save it as a baseline, run again next week, and see what changed.

I also want better labels and result organization. When you are benchmarking five variants of the same tool across three inputs, keeping the results straight is its own problem.

{% callout(type="note") %}
**What zebrac is not.** It is not a replacement for hyperfine or a general benchmarking framework. It is a focused Linux tool built around performance counters. The additions I want to make are about workflow, not scope. I am trying to make the tool I reach for when I need to know whether my code got faster or slower.
{% end %}

The credit belongs to poop for proving that this could be a small Zig tool built around Linux performance counters. zebrac keeps that starting point, then adds the pieces I wanted for my own benchmarking. The next pieces are the ones I still reach for manually.

And thank you to Andrew for Zig. It makes projects like this one fun to build, and that matters.
