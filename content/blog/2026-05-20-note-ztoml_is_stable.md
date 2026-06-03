+++
title = "z-toml Is Stable and Passing"
date = 2026-05-20
description = "z-toml reached a stable, tested version with TOML v1.1 support, writer support, and passing validation against the toml-test corpus."
[taxonomies]
tags = ["zig", "toml", "parser", "configuration", "tooling", "ztoml"]
[extra]
kind = "note"
+++

{% callout(type="tip") %}
**z-toml v0.4.0.** TOML v1.1 parser and writer for Zig 0.16. Struct mapping and raw access, in-place rewriter, passes the toml-test corpus. Small enough to understand, stable enough to depend on.
{% end %}

z-toml has reached the point where I am comfortable calling it stable for my own use. That does not mean finished forever. It means the main shape is there, the important pieces are tested, and I can start depending on it without feeling like every small change may break the whole design.

{% code(ln="zig", caption="CS1: Parse a TOML string and access values.") %}
const src =
    \\title = "My App"
    \\[server]
    \\port = 8080
;
const root = try toml.parseSlice(gpa, src, null);
defer toml.deinit(root, gpa);

const port = root.get("server").?.table.get("port").?.integer.value;
{% end %}

I started z-toml because I wanted a TOML library I could understand, maintain, and use inside other Zig projects. I did not want configuration parsing to become a fragile side problem every time I worked on something that needed config files.

The main milestones: it parses TOML v1.1, writes TOML back out, supports typed parsing into Zig structs, and has an in-place rewriter for changing values without rebuilding the whole file{% sidenote() %}The in-place rewriter is the feature I use most. It preserves comments and formatting for the parts of the file it does not touch, which means I can update a config value programmatically without blowing away the hand-written annotations around it.{% end %}. It also passes the toml-test validation suite{% sidenote() %}toml-test is the official TOML validation corpus maintained by the TOML project. Passing it means the parser handles edge cases like inline tables, array-of-tables, dotted keys, and the various datetime formats correctly. It is the closest thing to a conformance guarantee a TOML library can have.{% end %}.

> The library is starting to feel boring in the good way. I can parse a file, map it into a struct, write it back out, or rewrite one value by path. The tests pass. The behavior is documented enough that future me should not have to rediscover the whole project from scratch.

{% callout(type="note") %}
**What is next.** Better documentation, a small CLI, typed serialization, more examples. The library has crossed the line from experiment to usable dependency. The rest is polish, not discovery.
{% end %}

The project is small and it should stay small. It is not trying to become a full configuration framework. It parses, writes, preserves enough formatting for practical edits, and reports useful errors with line and column information. That is enough for now.
