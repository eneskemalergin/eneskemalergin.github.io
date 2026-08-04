+++
title = "Why I'm Learning Zig Instead of Doubling Down on Rust"
date = 2025-05-27
description = "I already knew Rust. I'm learning Zig anyway. Not because it's better, but because it fits a specific kind of work: small, fast tools that live forever in pipelines. An early take, not a manifesto."
[taxonomies]
tags = ["zig", "systems-programming", "bioinformatics", "tooling"]
[extra]
kind = "opinion"
+++

{% callout(type="note") %}
**TLDR:** Zig excels at the boring foundation layer. Small parsers, validators, indexers. Tools with no runtime, explicit memory, direct C interop, and a single static binary. Not replacing Rust for serious projects. Just occupying a different niche.
{% end %}

---

## How I got here

I defended my PhD in April 2025. I took a month and a half off, after it I will start as a staff bioinformatician in the same lab where I did my PhD. Same place, new role, to continue excited projects that we still haven’t finalized.

I care a lot about performance. I am the kind of person who profiles code that already runs fine, just to see if it can run faster. In academia the most important part is if the logic is sound and output is valid, the speed, memory, overall resource usage comes later. Unless you are not working with extremely large data or in a pipeline where every resource usage counts, optimizing things is secondary. Well, I spent my time with making my tools optimized anyway. Likely gotten my PhD 1-2 years longer than it should be. Slow code bothers me more than it probably should.

I already knew Rust. I had used it a bit, mostly small binders to speed up slow Python loops. It worked well and I respected it, I’ve definetly seen how it can actually modern toolkit for performant and safe language.

During my time off apart from gaming and enjoying my time off and out of the high that I finished my PhD, I’ve learned about Zig’s existence. It did peak my interest, it was relatively less known with a very particular philosophy that resonated with me.

## What caught me

I am not going to list version numbers or changelogs. The Zig website covers all of that. What I liked was how the language works day to day. Also will mention Rust a lot since there are obvious similarities and there are big differences to mention…

Zig is explicit. There is no hidden control flow, and nothing allocates memory unless I ask it to. When I read a function, I can see exactly what it does. For someone who spends a lot of time tracking down where an allocation came from, that matters to me. Also it is not as heavy or strict as Rust that I know. Which hits a well balanced with providing memory safety, and lightweightnes.

It also works with C directly. Zig treats C as a first-class citizen, which is the phrasing the Zig people like to use, and it fits. As far as motto or selling phrases it is appropriate. A lot of bioinformatics runs on C libraries, and Zig can call them without a separate binding layer.{% sidenote() %}You can @cImport a C header and the functions just work. No FFI ceremony, no bindgen step, no build system wrestling.{% end %}. At the end you get one small static binary that you can copy to a cluster and run. That is a nice thing to have.

## Rust is winning. So what?

I want to be fair here, because I am not trying to argue against Rust. It is brilliant. It is providing support for Python like I don't think we've seen before.{% sidenote() %}Polars is a great example: DataFrame operations at Rust speed with a clean Python API.{% end %}

Rust is winning in bioinformatics. It is everywhere, and it is being pushed hard for good reasons. The I/O libraries are mature, the format parsers are solid, and even in proteomics there are strong Rust tools in real use. If you are starting a serious project today and ask me what to use, I would tell you Rust.

It is also the better career choice, and I know that. Rust is the thing on the resume and the keyword in the job post. Picking it is the sensible decision.

But where is the fun in that.

## The boring tools niche

I should be clear about one thing: I have not built anything real in Zig yet. I am putting my thoughts at a very early on stage, at a stage where I am learning a language that I decided to invest in so some bias could be expected.

Everthing I talk about Zig is based on what I’ve seen so far and a personal “Hunch”. But my hunch is specific though. The work I keep coming back to is the boring foundation. Parsers, indexers, validators. Small tools that hold a pipeline together and cause real problems when they break. They tend to be small, they stick around for years, and they have to be fast and predictable on whatever machine the data is on.

That is what Zig looks good for. Small, no runtime, explicit about memory, and easy to use with existing C code. For that kind of tool, it feels like a good fit rather than a compromise.

And it is fun to write. It makes me want to build things on my own time again, which I had not felt much during the PhD.

## The honest caveats

I guess I have to honestly mention caveats, much like most Zig early adapters have to disclose. It goes without saying a language that is pre 1.0 will break your code between releases. That is the plan, not an accident, so if you build on it now you should expect to do migrations.

The ecosystem is small compared to Rust. Fewer libraries, fewer examples, and fewer people who have already solved your problem. Sometimes you have to work it out yourself. There is also no bioinformatics presence, which I might work on closing in the future…???

So I am not telling anyone to skip Rust and bet their career on Zig. Learn Rust and use Rust. It is the smart choice. I just want to spend some of my own time on Zig because I think I will enjoy it, and I think it might have a good adoption in the future.

## Where I land

I think Zig is a good fit for the foundational tools in bioinformatics, the small fast pieces everything else sits on. I cannot prove that yet, because I have not built it yet.

For now, I will use Rust when the work calls for it, and Zig when I get to choose.

---
