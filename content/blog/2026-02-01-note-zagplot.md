+++
title = "ZagPlot: An Experiment in Learning Zig Through Plotting"
date = 2026-02-01
description = "A note on what I am doing with ZagPlot, a small private Zig plotting project. Not a finished tool, just an excuse to learn graphics, API design, and Zig's systems story from the inside."
[taxonomies]
tags = ["zig", "plotting", "visualization", "learning", "tooling", "note", "zagplot"]
[extra]
kind = "note"
+++

{% callout(type="tip") %}
**What this is (and is not).** ZagPlot is a private Zig project for learning how plotting libraries work. It is early, messy, and may never be a finished tool. That is fine. The point is what I learn along the way.
{% end %}

I wanted to understand what happens between "I have some numbers" and "I have a figure." That can sound simple.. well it apprentely is not.

Even a small plot has more parts than you notice until you have to build them yourself: scales, axes, ticks, labels, margins, colors, data parsing, output formats, and sensible defaults. Each one is a design decision you normally inherit from a library. I wanted to see those decisions surface{% sidenote() %}The exercise is similar to writing a parser to understand parsing, or implementing a hash table to understand hash tables. You do not do it because the world needs another hash table. You do it because the implementation teaches you things the interface hides.{% end %}.

I am not building this because the world needs another plotting library. There are good ones already, across multiple languages. Zig alone has several plotting projects, including ones that draw in the terminal, which is genuinely impressive. ZagPlot is not competing with any of them. It would not make sense to try.

I am building it because I want to learn a few things that keep coming up in my work.

> How do you map data into a visual space? How do you design an API that is flexible enough for real use but simple enough that someone else can read it? How do you keep a library path separate from a CLI path? How do allocators flow through a real system instead of a toy example?

Those questions are the point. The library is the excuse.

I chose SVG for the output format because it keeps the scope contained. SVG is text. You write it, inspect it, diff it, and open it in a browser. You do not need PNG encoders, font renderers, canvas APIs, or GUI frameworks before you can see whether your axis labels line up. The fewer dependencies I pull in, the more I learn about the actual problem I am trying to understand.

For now, ZagPlot lives on GitHub as a private repository. I expect it to stay that way for a while. The API will change. Names will get renamed. Parts will get deleted. I want room to make mistakes without pretending the project is ready for anyone else.

{% details(summary="The rough shape of what I am aiming for") %}
This is not implemented yet. This is the direction I am thinking about.

```zig
const zag = @import("zagplot");
var plot = zag.Scatter.init(allocator);
try plot.load_csv("data.csv");
try plot.render(stdout);
```

Simple, explicit about allocation, works from CLI or as a library. Whether the final API looks anything like this is something I expect to learn by getting it wrong first.
{% end %}

If the library becomes genuinely useful for my own work later, I will expand it. More chart types. Better CSV handling. Cleaner defaults. Proper tests. If it does not, teaching me how plotting libraries think is still a good outcome for a project of this size.

That is enough. A small thing to learn from, not a thing to ship.

{% callout(type="note") %}
**The honest version.** I do not know whether ZagPlot becomes something I use, something I throw away, or something I learn from and leave behind. All three are fine outcomes for a project whose main goal is understanding.
{% end %}
