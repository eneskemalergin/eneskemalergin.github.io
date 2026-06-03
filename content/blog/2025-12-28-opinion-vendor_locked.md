+++
title = "Vendor-Locked MS Files and Open Formats, a Collision"
date = 2025-12-28
description = "Thermo locks its format behind Windows DLLs. Bruker does better. Spectronaut adds its own proprietary layer on top. Open formats are inevitable, but the real bottleneck is proprietary converters in the middle."
[taxonomies]
tags = ["proteomics", "mass-spectrometry", "vendor-formats", "file-formats", "reverse-engineering", "open-science", "open-data", "conversion", "mzML"]
[extra]
kind = "opinion"
+++

{% callout(type="note") %}
**TLDR:** Instrument vendors use proprietary file formats. Thermo is the most locked down. Bruker ships an SDK. The problem is not that proprietary formats exist. It is that accessing them requires proprietary converters that gate everything downstream. Open formats are necessary, and they can be binary, compressed, and fast. mzML proved the model works. The next step is making open formats the default, not the conversion target.
{% end %}

I should be fair to start. Vendors make instruments. Instruments generate data. The data is theirs to format as they see fit. Nobody owes me a CSV.

The gap between how instrument data is stored and how it is used has become a bottleneck. Not in theory. In practice. Every proteomics pipeline I work with starts by converting files before any analysis can begin.

{% code(ln="bash", caption="CS1: The first step in every pipeline is a toll booth.") %}

## Convert Thermo .raw to mzML before anything else

mono ThermoRawFileParser.exe \
 -i=PXD000001.raw \
 -o=PXD000001.mzML

## Now the real pipeline can start

{% end %}

That conversion step is the bottleneck I want to talk about.

## The landscape, not the villain

Vendors sit on a spectrum. It is more useful than singling out one company.

| Model                                        | Example     | Can you read the data?          |
| -------------------------------------------- | ----------- | ------------------------------- |
| Proprietary format + proprietary reader only | Thermo .raw | Only through vendor's DLLs      |
| Proprietary format + documented SDK          | Bruker .d   | Through SDK, restricted license |
| Proprietary format + public specification    | Rare in MS  | Anyone can implement a reader   |
| Open format + multiple independent readers   | mzML, mzMLb | Fully open                      |

The gap between the first two rows and the last two is where the ecosystem cost lives. Not in the format itself. In the access layer.

## Thermo: the door is now cross-platform, but still locked

Thermo Fisher Scientific is the largest manufacturer of mass spectrometers used in proteomics. Their .raw format is a binary blob readable only through proprietary Windows DLLs. For a long time, that meant Linux users needed a Windows VM or Mono to read their own data.

That has improved. Thermo now ships RawFileReader{% sidenote() %}Thermo's RawFileReader is a group of .NET assemblies wrapping the ThermoFisher.CommonCore C# libraries. It officially supports Windows, Linux, and macOS through .NET. [GitHub](https://github.com/thermofisherlsms/RawFileReader){% end %}, a cross-platform .NET library. ThermoRawFileParser{% sidenote() %}Hulstaert N et al. "ThermoRawFileParser: Modular, Scalable, and Cross-Platform RAW File Conversion." _J. Proteome Res._ 19(1):537-542, 2020. [GitHub](https://github.com/CompOmics/ThermoRawFileParser){% end %} builds on top of it and runs on Linux at scale through .NET Core. You no longer need a Windows VM.

The framing matters here. Linux access arrived late. The original RawFileReader required Windows, and the community spent years building workarounds before Thermo provided a cross-platform path. It is also still dependent on Thermo's proprietary stack. If Thermo changed their DLL interface tomorrow, every downstream converter would break. That is not a theoretical risk. It is a structural dependency.

The community keeps finding creative ways to work around the same door. There is a Rust reader that hosts the .NET runtime in-process to call RawFileReader{% sidenote() %}[thermorawfilereader.rs](https://github.com/mobiusklein/thermorawfilereader.rs) embeds the .NET runtime inside a Rust process. Clever engineering that still depends on Thermo's DLLs.{% end %}. Another project, ThermoRawRead, provides a GUI and CLI for extracting spectra{% sidenote() %}[ThermoRawRead](https://thermorawread.ctarn.io/) by ctarn is a cross-platform tool built on RawFileReader with a pipeline processing model.{% end %}. All of them route through Thermo's reader.

A vendor engineer would say: "We are not protecting a file format. We are protecting correct interpretation of instrument data." New instruments introduce new detector modes, ion mobility dimensions, and acquisition schemes. If a third-party reader misinterprets the data, users blame the instrument. That concern is legitimate. It also does not require proprietary readers forever. A public specification with conformance tests would serve the same goal.

## Bruker: easier to use, not truly open

Bruker ships the TDF-SDK{% sidenote() %}Bruker TDF-SDK provides C++ and Python bindings on Windows and Linux for reading .tdf and .tsf files. [Bruker TDF-SDK page](https://www.bruker.com/en/products-and-solutions/mass-spectrometry/ms-software/mass-spectrometry-software-updates.html){% end %} with documentation, examples, and cross-platform support. Their timsTOF stores data in SQLite and HDF5 containers. That is more accessible than Thermo's binary blob.

But accessible is not the same as open.

The TDF ecosystem still revolves around proprietary Bruker libraries (`timsdata.dll` / `libtimsdata.so`) in many tools. OpenTIMS{% sidenote() %}[OpenTIMS](https://github.com/gtluu/OpenTIMS) parses portions of the .tdf format directly, including the SQLite components. It exists because people wanted access that was less dependent on Bruker's SDK.{% end %} emerged because the community wanted a path that did not require Bruker's SDK. pyTDFSDK{% sidenote() %}[pyTDFSDK](https://github.com/gtluu/pyTDFSDK) provides a Python wrapper around the TDF-SDK DLL. Still depends on the proprietary library.{% end %} wraps the SDK DLL.

Bruker protects intellectual property. TIMS is proprietary ion mobility technology that differentiates their instruments. I am not asking them to give that away. The difference from Thermo is real and worth crediting: Bruker decided that making data accessible to third-party tools is better for customers, and by extension better for business. But the dependency is still on a vendor-controlled SDK, not an open specification. That distinction matters.

## Not just vendors: the software middleman problem

Vendors are not the only offenders. Biognosys's Spectronaut uses a proprietary format called HTRMS{% sidenote() %}HTRMS is a pre-processed binary format for Spectronaut. Biognosys recommends converting to it for timsTOF data. The converter is free but closed-source. The format specification is not public.{% end %}. The converter is free but closed-source. The format spec is not public.

I should be precise about the harm here. A proprietary internal format that speeds up a specific tool is an engineering choice. The problem is not that HTRMS exists. It is that the format specification is not public, which means the processed data exists in a form only one tool can read. If Spectronaut published the HTRMS layout and documented the encoding, the performance argument would remain and the lock-in would disappear.

DIA-NN{% sidenote() %}Demichev V et al. "DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput." _Nat. Methods_ 17:41-44, 2020. [GitHub](https://github.com/vdemichev/DiaNN){% end %} demonstrates that a proprietary intermediate format is not necessary for performance. It processes Thermo .raw, Bruker .d, and Sciex .wiff files{% sidenote() %}DIA-NN supports these formats directly from a user perspective. Some of this support may route through vendor SDKs internally. The point is not that DIA-NN is fully independent of vendor code. It is that the workflow does not require a separate conversion step and a proprietary intermediate layer.{% end %} without requiring users to manage a separate conversion step. Speed and openness are compatible.

## The reverse-engineering graveyard

The history of people trying to read Thermo files without Thermo's permission is long and mostly sad. Unfinnigan{% sidenote() %}[Unfinnigan](https://code.google.com/archive/p/unfinnigan/) was a Google Code project for "painless extraction of mass spectra from Thermo raw files." The name is a jab at the Thermo Finnigan lineage. Archived.{% end %} was one of the early attempts. It tried to read raw spectra without a proprietary library. It died.

OpenChrom reads vendor formats natively through reverse-engineered binary readers. ProteoWizard's msconvert is the workhorse most pipelines depend on. None of these are small projects. All exist because vendors will not publish their formats.

The cost is not measured in lines of code. It is measured in abandoned projects, wasted grant cycles, and formats that change without warning.

I should be precise about the risk. Thermo has not, to my knowledge, deliberately broken downstream tools by changing their DLL. The risk is subtler. Instrument firmware evolves. New scan modes, new detectors, new ion optics. The format tracks the hardware. When a new instrument ships, the format changes, and every downstream converter chases the update. That is not malice. It is the natural consequence of a closed format that the community cannot maintain independently.

## The legal uncertainty is itself a cost

This is where the argument lands hardest for me.

I have an early-stage idea for reading Thermo .raw files natively. No RawFileReader. No .NET. No Windows. A single static binary that you copy to a cluster node and run.

I do not know if it is legal to try.

Reverse engineering for interoperability exists in a legal gray area that varies by jurisdiction{% sidenote() %}In the US, reverse engineering for interoperability may be protected as fair use under certain conditions (Sony v. Connectix, Sega v. Accolade). The EU explicitly permits reverse engineering to achieve interoperability under the Software Directive (2009/24/EC). Canadian law is less clear. In all cases, the specifics of how the reverse engineering is done and what license agreements govern the software matter enormously.{% end %}. Thermo's RawFileReader license{% sidenote() %}RawFileReader ships with a proprietary license document. The license terms around reverse engineering, decompilation, and competitive use are standard for vendor SDKs but deliberately restrictive. The exact boundaries are unclear without legal review, which itself costs money most researchers do not have.{% end %} restricts what you can do with their reader. Whether analyzing the format independently through clean-room reverse engineering is permitted depends on who you ask and where you are.

The uncertainty itself is a burden. A researcher who wants to build a better, faster, more open reader has to either accept legal risk or spend resources on legal review that could go to the actual work. The person most motivated to solve the problem is also the person with the least clarity on whether trying is allowed.

That is the structural failure in its purest form.

## mzML is not the whole answer, and that is fine

mzML is the HUPO-PSI standard{% sidenote() %}The Proteomics Standards Initiative unified mzXML and mzData into mzML in 2008. It has been the community interchange format for nearly two decades.{% end %}. It is XML-based, verbose, and designed for interoperability over compactness. It solved the problem of having a common format for processed data.

I am not arguing against mzML. I am arguing that open formats are bigger than mzML.

mzMLb exists{% sidenote() %}Bhamber RS et al. "mzMLb: A Future-Proof Raw Mass Spectrometry Data Format." _J. Proteome Res._ 20(1):172-183, 2021. [DOI](https://doi.org/10.1021/acs.jproteome.0c00192). Reference implementation in ProteoWizard.{% end %}. It compresses spectra into HDF5 datasets while keeping metadata as XML. File sizes comparable to vendor formats. Reference implementation in ProteoWizard. The path forward exists. It needs adoption, not invention.

An open format can be binary, compressed, and optimized for random access. What makes it open is not the serialization choice. It is whether you can read it without asking permission. The specification is public. A reference reader exists that does not depend on proprietary libraries. The format does not change in breaking ways without notice.

mzML satisfies these. mzMLb improves on the performance dimension. The fight is not about XML versus binary. It is about the conversion layer between the instrument and the analysis.

## The middleman is the bottleneck

The problem is not that vendors have proprietary formats. Every instrument vendor has one. The problem is that accessing the data requires proprietary libraries controlled entirely by a single company.

The dependency chain is real. RawFileReader depends on Thermo's DLLs. ThermoRawFileParser depends on RawFileReader. Every downstream pipeline depends on ThermoRawFileParser. A proprietary format with an open, maintained reader is workable. A proprietary format with no public specification and a proprietary reader gating all access is a structural failure.

The stronger argument is not about Thermo specifically. It is that the ecosystem should not depend on any single vendor's reader implementation. That criticism applies equally to Thermo, Bruker, Waters, and Sciex.

## Where I land

Open formats tend to become dominant when interoperability creates enough economic value. In proteomics, the value is clear: pipelines that cross labs, instruments, and software stacks without a conversion tax. The transition takes time, and the wasted effort accumulates in the meantime.

Thermo is the most visible obstacle because they have the largest installed base and the most locked-down access model. They feel like the old guard that has not noticed the world changed. Bruker shows you can sell instruments, protect IP, and make your data more accessible. Neither is fully open, but the gap between them shows the range of possible choices, and Thermo's position is a choice.

The software layer matters too. Spectronaut makes a speed argument for HTRMS. DIA-NN shows performance does not require a closed format. If your tool is fast and your format is open, you win on both axes. If your tool is fast and your format is closed, only one of those things ages well.

I will keep converting .raw files with ThermoRawFileParser like everyone else. It works. It solved the Linux problem, and I am grateful to the people who built it. But the next generation of proteomics tools should not start with a toll booth.
