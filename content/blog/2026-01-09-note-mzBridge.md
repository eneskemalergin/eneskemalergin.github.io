+++
title = "mzBridge: An Early Attempt to Go from Vendor to Open"
date = 2026-01-09
description = "Why vendor mass spectrometry formats bother me, why a small native bridge might matter, and why Zig feels like the right place to test the idea."
[taxonomies]
tags = ["proteomics", "mass-spectrometry", "vendor-formats", "zig", "open-data", "mzbridge"]
[extra]
kind = "note"
+++

Mass spectrometry data often starts in the least convenient place possible: inside a vendor format. Before I can think about models, statistics, compression, search engines, or nice downstream tooling, I first need to ask a boring question. Can I read the file without dragging half a runtime, a vendor DLL, or a fragile conversion chain behind me? {% sidenote() %}That question bothers me more than it probably should, but for someone who cares about performance and optimization it makes sense.{% end %}

{% callout(type="note") %}
**The mzML reality:** mzML is the format I want to see at the end of the conversion step. It is documented, supported by many tools, and much easier to move between workflows than vendor raw files. The problem is that mzML is often not where the data starts.
{% end %}

If the original files are Thermo `.raw`, Bruker `.d`, or some other vendor format, then the first step is still conversion. That step can take a long time when cohort size grows. It can also come with annoying practical constraints: operating system assumptions, vendor libraries, large runtimes, and tools that are useful but not as simple as they should be.

This is not me saying those tools are bad. ThermoRawFileParser, ProteoWizard, and mzdata-converter exist because people needed a way through the mess. I have used them. They are part of the reason this ecosystem works at all.

> Reading the file should not feel like the fragile part.

For Thermo files, the common path depends on the vendor API or tools built around it. For Bruker `.d`, things are more open in practice because parts of the format are organized around SQLite{% sidenote() %}Bruker's `.d` format uses SQLite databases for some metadata structures, which means you can inspect parts of it with standard SQL tools. This is more open than Thermo's binary format, but it is still not the same as having a small reader that treats the data as plain infrastructure.{% end %}. There is a gap between "we can convert this" and "this is boring enough to build on."

I want the boring version.

---

mzBridge is my early attempt to test that idea. The goal is not to build a search engine, a complete replacement for every converter, or a grand universal mass spectrometry platform. The goal is smaller and more annoying: read vendor data directly, turn it into open data, and make the path small enough that it can live inside real workflows.

{% callout(type="tip") %}
**What I envising mzBridge to be.** A small native tool that reads vendor mass spectrometry formats and writes open data. Not a search engine. Not a universal converter. A bridge between the format you have and the format you need.
{% end %}

Zig feels interesting for this because the problem is close to the metal. This is binary parsing, file offsets, buffers, compression, validation, and memory layout. It is not the kind of problem where I want a garbage collector making decisions. It is also not the kind of problem where I want to write C and manually hold every sharp edge with my bare hands. I want a small, simple binary that works on any platform.

Zig gives me a middle place that I enjoy.

Explicit allocation. Small binaries. Easy cross-compilation. Good control over structs and bytes. Enough safety checks that I do not feel like every mistake becomes silent memory corruption. Enough directness that I can still see what the program is doing. That is the appeal.

I do not think Zig magically makes this easy. The hard part is not syntax. The hard part is that vendor formats are not designed for independent readers. Some parts can be inferred. Some parts can be validated. Some parts will probably be weird because instrument models, firmware versions, acquisition methods, and software versions all leave their fingerprints in the file.

{% callout(type="warning") %}
**The legal constraint.** I cannot reverse engineer this from vendor source code. I do not want to touch anything that makes the legal or ethical situation messy. The only version of this project that makes sense is a clean one: public files, observed behavior, independent parsing, documented assumptions, and validation against outputs produced by accepted tools. I may not make this public for a while. I may not put it on GitHub until I understand the risks better. I do not want a DMCA problem over a tool whose purpose is to make scientific data easier to access.
{% end %}

---

The practical suspicion is simple. A lot of conversion feels slower and heavier than it needs to be because the path is too layered. Vendor API, managed runtime, wrapper, converter, XML writer, then maybe another tool that reads the XML back in. Each layer makes sense historically. Together they make the first step of analysis feel more expensive than it should.

I want to know how much of that cost is necessary.

Maybe the answer is most of it. Maybe direct parsing runs into too many edge cases. Maybe the format differences across versions make the maintenance burden too high. Maybe the safe public version of this project ends up much smaller than the private experiment. That would still teach me something.

> Downstream tools inherit the shape of the input step. If the first step is slow, fragile, platform-specific, or legally awkward, then everything after it starts with that friction. Search engines, compression formats, public repositories, automated pipelines, and reproducible analysis all depend on reading the data first. That should be the least dramatic part of the workflow.

I do not know yet whether mzBridge becomes a public tool, a private experiment, or just a set of lessons for future projects like mzArc and mzValidate. I know the question is worth testing. Vendor data is where a lot of proteomics begins, and pretending that open science starts only after conversion feels incomplete.

So this is the early note to myself. Try the bridge. Keep it clean. Validate everything. Do not overpromise.
