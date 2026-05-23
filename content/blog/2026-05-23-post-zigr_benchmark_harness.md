+++
title = "Native R Extensions with Zig: Initial Observations"
date = 2026-05-23
description = "C and C++ cover the classic extension story. Rust through extendr and Savvy brings memory safety to the table. Both are modern, both are performant. Neither fits the R C API boundary as naturally as a language designed to treat C interop as a first-class feature. Early observations from zigr: six backends, 23 tasks, and a case for Zig as the missing option."
[taxonomies]
tags = ["r", "zig", "benchmarking", "performance", "zigr"]
[extra]
kind = "post"
+++

People who know me are aware there is no great love lost between me and R. The language has quirks that are genuinely baffling to anyone arriving from nearly anywhere else: 1-indexed vectors, factors that quietly convert to integers at the wrong moment, a data.frame that is simultaneously a list and not a list depending on which function you are calling, and a scoping model that surprises you on a regular basis.

And yet I keep writing R packages. The tidyverse changed what it means to do data work in R. `dplyr`, `ggplot2`, the whole pipe-based philosophy, and the serious ongoing work on condition handling and user-facing error messages across the ecosystem. That side of R is genuinely well-designed. A community has built something worth using on top of a language that often fights you, and that deserves credit.

I also have real respect for where Rust is going. The ownership model is the most coherent answer I have seen to the problems that accumulated in C++: manual memory management buried under decades of abstraction, undefined behavior that compilers exploit rather than catch, and a template system that grew into something most people use but few people fully understand. Rust solves those problems correctly. The borrow checker is not inconvenient overhead. It is the point.

So when I started writing R extensions seriously, I tried both directions. And I kept running into the same friction.

## Why Zig

When you write an R extension, regardless of language, you end up at the same place: the R C API. SEXP values. PROTECT and UNPROTECT calls. `.Call` as the entry point. R's garbage collector owns your objects and decides when they die. You do not own them. Your extension borrows them from R for the duration of a function call, and then R reclaims them.

This is where Rust's ownership story stops buying you what it normally buys. The borrow checker is built for a world where your code owns memory and you need to prove that ownership transfers correctly. In R extensions, R's GC is the owner. Your code is always a borrower. Both [extendr](https://extendr.github.io/) and [Savvy](https://yutannihilation.github.io/savvy/guide/) handle this through generated wrappers and careful lifetime management, and they do it well. But you are carrying real framework weight to solve a problem that is fundamentally about R's memory model, not Rust's.

{% callout(type="note") %}
This is not a criticism of extendr or Savvy. Both are serious projects and the benchmark results below show it. Savvy in particular is strong on BLAS and linear model work. The point is about fit: if you are already working at the C ABI boundary, a language that treats C interop as a first-class citizen with zero overhead has a natural advantage for this specific use case.
{% end %}

Zig treats C interop as a language feature, not a compatibility mode. You can call C functions directly, import C headers with `@cImport`, and build a shared library that R loads with `dyn.load()` exactly the way it loads a compiled C extension. No wrapper generation step. No framework between you and the R C API. Just Zig, compiling tight code to the same ABI that `.Call` has always expected.

Zig also gives you comptime instead of macros, explicit allocators, no hidden control flow, and no hidden allocations. Every allocation is visible. Every error path is explicit. The compile-time guarantees catch things that would be silent bugs in C without requiring the ownership ceremony that Rust demands in a context where R is already the owner.

That is what [zigr](https://github.com/eneskemalergin/zigr) is built toward.

## The Benchmark Harness

To test whether the fit translated into actual performance, I built a harness across six backends and twenty-three tasks.{% sidenote() %}The benchmark code is not yet public. It will be released alongside zigr when the harness stabilizes. All six backends implement the same 23 tasks with the same data shapes and operation types.{% end %}

The six backends:

| Runner    | Implementation                      |
| --------- | ----------------------------------- |
| `r`       | Pure R reference baseline           |
| `zigr`    | Native Zig via zigr                 |
| `c_call`  | Hand-written C via `.Call`          |
| `rcpp`    | C++ via Rcpp                        |
| `extendr` | Rust via extendr-generated wrappers |
| `savvy`   | Rust via Savvy-generated wrappers   |

All six currently pass all 23 shared tasks. Results were refreshed on 2026-05-23.

## What the Numbers Say

The runner summary first. Lower geomean is better. The `Geomean vs R` column is the geometric mean of `mean_ms / R_baseline_mean_ms` across all tasks, so values below `1.0x` are faster than R overall.

| Runner    | Tasks Won | Geomean vs R |
| --------- | --------: | -----------: |
| `zigr`    |        10 |       0.475x |
| `Savvy`   |         3 |       0.648x |
| `extendr` |         2 |       0.695x |
| `Rcpp`    |         4 |       0.891x |
| `C .Call` |         2 |       0.935x |
| `R`       |         2 |       1.000x |

{{ figure(src="/blog/images/zigr-benchmark/geomean-chart.svg", alt="Horizontal bar chart showing geomean vs R baseline for six backends. zigr scores 0.475x, Savvy 0.648x, extendr 0.695x, Rcpp 0.891x, C .Call 0.935x, R 1.000x.", alt_badge="Benchmark summary", caption="Figure 1. Geometric mean of mean_ms / R_baseline_mean_ms across 23 tasks. Values below 1.0x are faster than the R baseline. zigr leads at 0.475x.", label="Figure 1", width="92%") }}

zigr leads overall and wins the most tasks. The geomean hides the actual story though, so here is the breakdown by category.

**Vector, dataframe, and reduction work.** This is where zigr separates most clearly. `05_dataframe` (filtering `1e5` rows) runs in 0.53 ms in zigr against 21.9 ms in R. `06_na_prop` (NA propagation across `1e6` values) is 0.15 ms in zigr against 9.7 ms in R. `14_rowsums` is 0.08 ms against 1.25 ms. These are not marginal wins. The work Zig does here is tight iteration over contiguous memory with no interpreter overhead, and R's overhead on large vectorized operations is real and measurable.

**BLAS and linear algebra.** Savvy is the surprise here. `10_blas_matmul` (256x256) runs in 1.18 ms for Savvy against 2.63 ms for zigr. Linear model fitting (`13_lm`, n=5000, p=20) is 0.35 ms for Savvy against 0.40 ms for zigr. Both are calling into the same BLAS and LAPACK routines underneath. Savvy's generated wrapper appears to hit a faster dispatch path for this class of work, and understanding why is on the list.

**Classic native extension work.** Fibonacci, sort, random normal, element-wise ops. Rcpp and hand-written C are within noise of each other on most of these, and zigr is not dramatically ahead. This is expected: at this level all backends are bottlenecked on the same libm and sorting routines. The extension language stops mattering when the real work happens in a library call.

**The two anomalies.** `17_broadcast` (vector + scalar, `1e7`) and `19_cumsum` (cumulative sum, `1e7`) are tasks where zigr does not clearly separate from R. The numbers are 47 ms vs 49 ms on broadcast, and 50 ms vs 59 ms on cumsum.{% sidenote() %}These two deserve their own investigation. Both operate on large contiguous vectors with simple arithmetic, which is exactly where you would expect Zig to pull ahead. Cache behavior or differences in auto-vectorization between R's bytecode compiler and Zig's codegen are the likely candidates. No clean answer yet.{% end %}

**The two tasks R wins.** `09_protect` (PROTECT stress, 49k objects) and `23_altrep_sum` (ALTREP sum over `1:1e7`). These are worth reading carefully rather than dismissing.{% sidenote() %}I said at the top there is no great love lost between me and R. I am willing to say when I am wrong. Some base R internals are exceptionally well-tuned. The R team has spent real effort on the ALTREP sum path. An ALTREP vector carries metadata that lets operations like `sum()` short-circuit to a formula rather than iterate. My zigr implementation does not exploit that yet. This is not a loss worth engineering around for v0.0.7.{% end %}

PROTECT stress measures call overhead more than computation. A small surface is being called many times and the overhead of entering and exiting the Zig shim accumulates. R wins here because there is no shim. That will always be true for micro-benchmarks of this shape.

{% details(summary="Full results: mean wall time in ms, all 23 tasks") %}
Lower is better.

| Task            |       R |    zigr | C .Call |    Rcpp |  extendr |    Savvy |
| --------------- | ------: | ------: | ------: | ------: | -------: | -------: |
| 01_fib          |  0.0038 |  0.0021 |  0.0021 |  0.0017 |   0.0042 |   0.0019 |
| 02_vectorsum    | 15.5244 |  3.5422 |  9.4884 |  9.3098 |   8.9240 |   8.8798 |
| 03_transpose    |  1.1433 |  0.9474 |  0.9850 |  0.9755 |   0.9957 |   1.0388 |
| 04_strings      |  2.2369 |  1.1169 |  1.2217 |  0.9208 |   0.9038 |   0.8992 |
| 05_dataframe    | 21.9324 |  0.5260 |  0.9870 |  0.9909 |   1.0147 |   0.9692 |
| 06_na_prop      |  9.6852 |  0.1517 |  2.7801 |  2.7209 |   2.8617 |   2.8829 |
| 07_parallel     | 15.5052 |  2.2411 |  2.8719 |  2.7538 |   2.5494 |   2.5613 |
| 09_protect      |  0.0016 |  0.7407 |  0.8232 |  0.7896 |   0.9051 |   0.8812 |
| 10_blas_matmul  |  2.7278 |  2.6343 |  2.9852 |  2.9449 |   3.8780 |   1.1761 |
| 11_crossprod    |  0.0728 |  0.0677 |  0.0668 |  0.0715 |   0.0681 |   0.0689 |
| 12_cholesky     |  0.7360 |  0.5001 |  0.6791 |  0.5531 |   1.0418 |   0.5954 |
| 13_lm           |  1.1645 |  0.3996 |  0.4264 |  0.3907 |   0.3922 |   0.3506 |
| 14_rowsums      |  1.2502 |  0.0797 |  0.1753 |  0.1746 |   0.1154 |   0.1213 |
| 15_elem_ops     | 86.8469 | 31.1790 | 30.4700 | 30.0600 |  33.1929 |  30.4818 |
| 16_rowcol_means |  1.9085 |  0.4686 |  0.8153 |  0.8132 |   0.8161 |   0.8177 |
| 17_broadcast    | 48.9904 | 47.2191 | 48.1040 | 48.4642 |  94.5069 |  96.0987 |
| 18_sort         | 62.7667 | 41.6258 | 36.0792 | 36.6330 |  38.1290 |  36.2273 |
| 19_cumsum       | 58.8522 | 50.3242 | 51.5503 | 51.5376 | 121.2041 | 104.3952 |
| 20_rnorm        | 38.1920 | 32.1525 | 32.3429 | 32.1031 |  32.1622 |  32.5613 |
| 21_string_nchar |  0.6656 |  0.0817 |  0.0832 |  0.0811 |   0.0659 |   0.1310 |
| 22_which_na     |  4.0595 |  1.3015 |  2.2631 |  2.1946 |   1.1840 |   2.4138 |
| 23_altrep_sum   |  0.0019 |  0.0024 |  8.9877 |  9.0244 |   0.0025 |   0.0023 |
| 24_altrep_read  |  0.0021 |  0.0022 |  0.0023 |  0.0019 |   0.0023 |   0.0022 |
{% end %}

## Beyond Speed

Wall time is the easiest metric to collect and the easiest to misread alone. Three more dimensions are planned for the next harness version.

**Memory.** Peak RSS during each task. Heap bytes allocated, tracked through a custom allocator or `mallinfo`. Leak detection: run each task 10,000 times in one session and watch the heap. GC pressure: how many GC cycles does each backend trigger? An extension that causes fewer allocations means fewer pauses in long-running R sessions even when individual call times look fast.{% sidenote() %}GC pressure is the dimension where Zig's explicit allocator model has the most interesting potential. You can choose not to heap-allocate for many operations. Whether that translates into measurably lower GC interruption in practice is something the harness will measure directly.{% end %}

**Safety.** Crash resilience: what happens when an extension receives a NULL SEXP, the wrong SEXPTYPE, a vector with the wrong length, or a negative index? Does the R process crash or recover cleanly? Error propagation: does the extension call `Rf_error()` and signal a proper R condition, or does it `abort()`? R should survive an extension error without losing the session. PROTECT audit: static analysis using [`rchk`](https://github.com/kalibera/rchk), which specifically checks PROTECT/UNPROTECT discipline in R extension C code. Passing `rchk` clean is harder than it looks, and most extensions do not.

**Developer experience.** Compile time from a clean build. Binary size of the resulting `.so`. Both matter for CRAN distribution where size limits are real and cold installs happen regularly. Cold start: `dyn.load()` time in a fresh R session. Long-run stability: p99 latency over 50,000 task repetitions to surface latency spikes from background GC or OS scheduler interference.

The goal is a full four-axis comparison matrix: speed, memory, safety, and developer cost. The harness goes public when that picture is complete enough to be useful.

## Design Constraints

zigr is built around three explicit refusals.

It does not try to cover every SEXP type. The surface is narrow by intention: numeric vectors, matrices, dataframes, strings, and the foreign function call itself. That covers what appears in real scientific computing extensions. Everything else waits for a concrete use case.

It does not abstract the C ABI. The build artifact is a shared library that `dyn.load()` treats identically to a compiled C extension. The call goes from R through `.Call` directly into Zig. No generated wrapper layer. No code to read through when something goes wrong.

It does not grow for completeness. New types and operations go in when they are needed, not because coverage is a goal in itself. The narrow scope and the PROTECT safety guarantees are related: the smaller the surface, the more completely those guarantees can cover it.

## Closing

A lightning rod does two things. It carries the strike, and it keeps the structure standing.

That is what zigr is trying to be for R extension work. Bring the speed. Stop the bugs from burning the house down.

The benchmark harness will go public alongside the library. v0.0.7 is a proof of concept. The numbers suggest the direction is right.
