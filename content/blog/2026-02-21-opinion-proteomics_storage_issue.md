+++
title = "The Storage Crisis Nobody Budgets For"
date = 2026-02-21
description = "Proteomics data is growing faster than storage budgets. AI demand is driving up hardware prices. The format debate is a distraction. Compression tools exist but nobody uses them. The real problem is that storage is an unaccounted line item, and the field optimizes for generation, not retention."
[taxonomies]
tags = ["proteomics", "mass-spectrometry", "storage", "compression", "infrastructure", "open-science", "mzML"]
[extra]
kind = "opinion"
+++

{% callout(type="note") %}

**TLDR:** Proteomics data is growing faster than the storage budgets that are supposed to hold it. New instruments produce deeper coverage per run. Single-cell work multiplies the sample count. AI demand is driving up the cost of storage hardware. The format debate between XML and binary is a distraction. Total data volume is the real problem, and nobody is accountable for it.

{% end %}

I built a storage server for the lab six months ago. 86 TB of RAID capacity. An Orbitrap Astrals and a timsTOF Ultra 2 feed into it. It is already 60% full.

There is cold storage for older runs. We also lost data there, so it is not quite a solution.

This is not an isolated story. A Reddit user processing Astral data put it bluntly: "You'll need to find a data storage solution because buying 10TB hard drives isn't sustainable." This is from someone who just bought a multi-million dollar instrument. The storage problem was an afterthought.

This is not a dramatic story. It is math.

## The numbers are not on our side

Per-run depth is increasing fast. The Orbitrap Astral can identify over 8,000 protein groups from a single HeLa run and over 15,000 from a fractionated sample in under 5 hours{% sidenote() %}Thermo's <a href="https://assets.thermofisher.com/TFS-Assets/CMD/Specification-Sheets/ps-001728-ms-orbitrap-astral-ms-ps001728.pdf" target="_blank">Orbitrap Astral datasheet</a> claims >8,000 protein groups from a 5.5-min HeLa run. Confirmed independently by <a href="https://www.nature.com/articles/s41467-024-51274-0" target="_blank">Nature Communications (2024)</a> mapping ~30,000 phosphosites in 30 minutes. The "eight proteomes per day" figure cites Jesper Olsen's group at the Copenhagen CP.{% end %}. The timsTOF Ultra 2 is competitive on coverage.

More spectra per run means larger files. An Astral DIA file is around 15 GB{% sidenote() %}Confirmed by multiple user reports. A <a href="https://github.com/vdemichev/DiaNN/discussions/973" target="_blank">DIA-NN GitHub discussion (#973, March 2024)</a> documents an Exploris 480 DIA file at 2-3 GB versus an Astral DIA file at ~15 GB. The jump is roughly 5-7x per file between generations.{% end %}. The previous generation (Exploris 480) produced files in the 2-3 GB range. Same experiment. Five times the storage.

{% code(ln="bash", caption="CS1: How 15 GB per run becomes a problem nobody planned for.") %}

# One Astral run

15 GB  experiment_01.raw

# 100 runs per month

1500 GB  monthly_raw

# With converted mzML (uncompressed, ~10x expansion)

15000 GB  monthly_mzML

# After a year (uncompressed mzML)

180 TB  annual_mzML
{% end %}

Sample counts are exploding. A single-cell proteomics experiment can produce thousands of individual measurements across many acquisitions. Terabytes from one study. The field is moving from dozens of samples to hundreds, to thousands. The storage footprint tracks every run linearly.

Multi-omics compounds the problem. Genomics has its own storage crisis. When the same study collects proteomics, transcriptomics, and metabolomics, the storage demand multiplies across modalities.

The result: a single large study can produce 50 terabytes of raw data. Most of it will never be looked at again after the paper is published. All of it has to be stored somewhere.

The PRIDE repository{% sidenote() %}<a href="https://doi.org/10.1093/nar/gkae1011" target="_blank">Perez-Riverol et al., NAR 53(D1), 2025</a>. PRIDE receives 534 new datasets per month. 47% of all datasets were submitted in the last three years. Growth is accelerating.{% end %} receives 534 new datasets per month. Globus was added as a transfer protocol because FTP could not handle the file sizes.

Less than 10% of PRIDE's public datasets are ever reanalyzed{% sidenote() %}From the <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC11701690/" target="_blank">2025 PRIDE update paper</a>: "Overall, the number of datasets mentioned as reanalyzed is <10% of the PRIDE public datasets." Measured by counting dataset accession mentions in EuropePMC.{% end %}.

## The conversion penalty

Converting vendor formats to open formats is the right thing to do. The default conversion settings also make your storage problem measurably worse.

The mzML format is verbose by design. The MS-Numpress paper{% sidenote() %}<a href="https://doi.org/10.1074/mcp.RA119.001624" target="_blank">Teleman et al., MCP (2019)</a>. A naive mzML representation can be 4-fold to 18-fold larger than the vendor original. The paper also developed the MS-Numpress compression schemes that fix this.{% end %} documented this: a naive mzML conversion grows the file by 4x to 18x compared to the vendor original.

That expansion is not uniform. It depends on the vendor format. Thermo .raw files are compact binary containers. Converting them to uncompressed mzML creates the largest expansion. Bruker timsTOF .d files are already a directory of binary files (TDF/TSF). The expansion from Bruker .d to mzML is less dramatic, and many tools{% sidenote() %}<a href="https://fragpipe.nesvilab.org/docs/tutorial_convert.html" target="_blank">FragPipe's docs</a> explicitly recommend against converting .d: "we recommend using the raw .d format for Bruker data." <a href="https://github.com/vdemichev/DiaNN" target="_blank">DIA-NN</a> and <a href="https://msfragger.nesvilab.org/" target="_blank">MSFragger/IonQuant</a> all read .d natively. Thermo .raw users do not have this option.{% end %} can read .d natively anyway. The problem is most acute for Thermo users, which is still the majority of the installed base.

{% code(ln="bash", caption="CS2: The same data, two conversion paths.") %}

# Default conversion (no compression)

wine msconvert experiment.raw --mzML

# Result: 150 GB mzML from a 15 GB raw

# With MS-Numpress + zlib

wine msconvert experiment.raw --mzML \
  --zlib --numpress linear \
  --numpress short logged

# Result: ~20 GB mzML, comparable to original raw

{% end %}

This is not an argument against open formats. It is an argument that open formats need to be compact by default. mzMLb{% sidenote() %}<a href="https://doi.org/10.1021/acs.jproteome.0c01006" target="_blank">Bhamber et al., JPR (2021)</a>. HDF5-based format storing spectra as compressed datasets with XML metadata. Achieves file sizes comparable to vendor formats. Published, standardized, included in ProteoWizard. Rarely used.{% end %} solves the compression problem while keeping metadata accessible. MS-Numpress reduces mzML size by roughly 61% alone, up to 87% with zlib, and improves read speed by 21% in some configurations.

The tools exist. They are not the default.

## The AI tax

Storage has historically gotten cheaper. That long trend is not guaranteed to continue.

AI demand is disrupting the hardware supply chain in ways that hit labs buying storage right now. NAND flash prices increased by roughly 246% during 2025 according to Kingston's end-of-year report{% sidenote() %}<a href="https://nand-research.com/memory-flash-crisisc-update-march-2026/" target="_blank">Kingston's Cameron Crandall reported NAND wafer pricing up 246% from Q1 2025</a>. <a href="https://www.forbes.com/sites/tomcoughlin/2026/01/02/digital-storage-and-memory-projections-for-2026-part-2/" target="_blank">Forbes (January 2026)</a> confirmed some NAND prices more than doubled in under six months. <a href="https://www.elinfor.com/knowledge/nand-flash-prices-are-surging-in-2026-what-it-means-for-your-supply-chain-and-how-to-prepare-p-11312" target="_blank">TrendForce projects</a> NAND prices rising another 33-38% QoQ in Q1 2026. This is structural, not cyclical.{% end %}. SSDs that were $175 are now $379. 1TB drives that were $40-50 are more than double.

Cloud providers buy drives by the exabyte. GPU manufacturers allocate supply to the AI market first. The downstream effect: the same components proteomics labs depend on cost more than they did two years ago.

A qualified objection: most proteomics archives live on HDD arrays or tape, not high-performance SSDs. NAND prices affect the active storage layer (SSD caching, high-speed analysis nodes) more directly than cold archives. A lab storing everything on spinning disk is partially insulated from NAND volatility.

The broader point stands. Storage infrastructure of all types is getting more expensive. HDD prices are also rising as manufacturers shift factory capacity to meet AI demand. Cloud pricing is complex. Egress and retrieval fees often dwarf storage costs{% sidenote() %}<a href="https://leanopstech.com/blog/aws-s3-glacier-pricing-2026/" target="_blank">S3 Glacier Deep Archive is ~$0.00099/GB/month</a>, but restoring large datasets costs $0.02-0.03/GB in retrieval fees plus hours of wait time. A 10 TB restore costs ~$200 before egress. As LeanOps puts it: "$1/TB to store, $20K to retrieve" a petabyte.{% end %}. The headline storage rate understates the true cost of keeping data accessible.

A lab buying a storage server in February 2026 is paying more for less capacity than they would have in 2024. That is not speculation. It is the NAND spot price.

## Nobody is accountable

Instrument vendors sell instruments. They do not pay for the storage that holds the data their instruments produce. Software vendors sell analysis tools. They do not pay for storage of intermediate and output files. Grant budgets include line items for instruments and compute. They rarely include realistic line items for long-term data retention.

{% details(summary="How the NIH policy handles storage costs") %}
The NIH Data Management and Sharing Policy (effective January 2023) requires a DMS plan for all grant applications. Storage costs can be budgeted during the project period. After the grant ends, the data must persist. The funding does not.

Some institutions provide repository funding, core facility support, or infrastructure grants. The gap is not absolute. It is structural and widespread enough that most labs feel it.
{% end %}

To put numbers on the silence: the UAB Targeted Metabolomics and Proteomics Laboratory estimated that their TripleTOF 5600 generated 1-2 TB of raw data per month{% sidenote() %}<a href="https://www.uab.edu/medicine/tmpl/services/data-storage" target="_blank">UAB TMPL data storage page</a>. At their quoted price ($0.15/GB/month), projected cost was $80,000/year. At modern S3 pricing (~$0.023/GB/month), raw storage drops to ~$550/year. The real costs are elsewhere: backup, replication, metadata, retrieval, and the sysadmin time to maintain it all.{% end %}. Their projected cost was $80,000 per year. At modern cloud rates, the raw storage is cheap. The real cost is everything around it.

The hidden expense is operations. Sysadmin time. Backup validation. Data migrations across storage generations. Security compliance. These costs scale with data volume and easily exceed hardware. A facility generating 50 TB/year might spend more on the person managing it than on the disks holding it.

The incentive structure reinforces the gap. Nobody gets a paper for efficient storage. The MS-Numpress authors published their work and the tools are available in ProteoWizard. The default conversion settings most researchers use do not enable compression. Journals require data deposition but do not fund the infrastructure. A handful of datasets get most of the download traffic. The rest sit.

> The field optimizes for generation. Not retention.

## The problem nobody wants to talk about

Deletion is politically harder than storage.

Every dataset has an owner. Nobody wants to approve deletion. Nobody wants responsibility if the data becomes useful later. The result is a hoarding equilibrium: keep everything because the cost of deleting the wrong thing is higher than the cost of keeping it.

This is exactly why storage crises emerge gradually. No single decision creates them. They are the accumulated weight of decisions deferred. The server fills up not because someone chose poorly, but because no one chose at all.

Retention policies exist on paper. Enforcement is rare. The field has no culture of intentional deletion. We keep everything until the server forces a decision.

## What would actually help

The format debate between XML and binary is a distraction. Total data volume is the real problem, and it grows regardless of encoding choice. A 50-terabyte study is large in any format.

Compression tooling is the most direct lever. MS-Numpress{% sidenote() %}<a href="https://doi.org/10.1074/mcp.RA119.001624" target="_blank">Teleman et al., MCP (2019)</a>. Reduces mzML by ~61% alone, up to 87% with zlib. Also improves read speed by 21%. Ships with ProteoWizard, enabled by a single flag.{% end %} already works. mzMLb matches vendor format sizes. StackZDPD{% sidenote() %}<a href="https://www.nature.com/articles/s41598-022-16812-y" target="_blank">StackZDPD, Nature Scientific Reports (2022)</a>. Alternative encoding using difference encoding + zstd. Reduces mzML volume by ~80% with faster decompression than zlib.{% end %} offers similar ratios. The gap is not invention. It is adoption. Making compressed, indexed formats the default rather than a niche option would reduce storage pressure across the entire field.

Will Kryder's Law save us? Probably not this time. Storage density improvements have slowed. The transition from PMR to HAMR has been slow. Meanwhile, instrument throughput is accelerating faster than density improvements. Retention obligations never expire. Raw files are rarely deleted. Reprocessing requirements preserve originals. The old pattern of "storage will catch up" is not keeping pace with how fast this field generates data.

Retention policies need to become explicit. Not every file lives forever. Raw instrument data that has been processed and verified could move to cold storage after a defined window. Search engine intermediates can be regenerated.

{% code(ln="bash", caption="CS3: A lifecycle policy for proteomics data.") %}

# S3 lifecycle rule: raw to cold to delete

{
    "Rules": [
        {
            "Id": "proteomics-retention",
            "Status": "Enabled",
            "Transitions": [
                {"Days": 90,  "StorageClass": "STANDARD_IA"},
                {"Days": 365, "StorageClass": "GLACIER"}
            ],
            "Expiration": {"Days": 1825}
        }
    ]
}
{% end %}

Cloud storage tiers make this practical. AWS S3 Glacier Deep Archive costs roughly $0.001/GB/month, compared to $0.023/GB/month for Standard. 20x difference for data accessed once a year or less. The field has no standard for retention. Every lab reinvents the policy, or more often, has no policy at all.

## Where I land

Storage is not a glamorous problem. It is a maintenance problem. The kind that gets ignored until the server is full and someone has to spend a day deciding what to delete.

The cost is real and growing. Instruments produce more data per run. Experiments include more runs. AI demand pushes hardware prices up. Open formats are necessary but inflate storage requirements when used without compression.

The solutions exist. Compression works. Tiered storage policies work. What is missing is the incentive to adopt them, the tooling to make them easy, and the willingness to treat storage as a first-class budget item rather than an afterthought.

This problem will get worse before it gets better. There are opportunities to build tools that make it better. Small, fast, format-aware compression. Indexed access without full decompression. Retention automation that does not require a human to decide what to delete.

Some of those ideas feel worth exploring further.
