# Philosophy

[中文版本](philosophy.zh.md)

py2rs is a loop engineering discipline for controlled rewrites.

It is not trying to maximize creativity. It is trying to preserve engineering control while AI agents perform repetitive migration work. If the work needs free-form invention, product taste or open-ended exploration, this repository is the wrong tool. If the work needs bounded rewrites, behavior parity, review gates and rollback, it fits.

The skills in this repository are architecture and thinking skills. They are primarily skills for creating other skills. A project should not start by blindly running them. It should start by understanding the project, writing project-specific skills, initializing the rewrite workspace, and then entering the loop.

## Borrowed From teach

py2rs borrows a large part of its progression model from the [`teach`](../skills/foundations/teach/SKILL.md) skill, originally from Matt Pocock's [`mattpocock/skills`](https://github.com/mattpocock/skills) repository.

In `teach`, learning is not a single answer. It is a stateful workspace:

- `MISSION.md` keeps the reason for learning visible.
- `RESOURCES.md` makes the agent ground work in sources instead of memory.
- records capture non-obvious lessons for future sessions.
- notes preserve user preferences and working context.
- each lesson is small, self-contained and tied to the mission.
- progress happens through feedback loops, not one-shot output.

py2rs maps those ideas into rewrite work:

- mission becomes the reason and constraints for the rewrite.
- resources become source-of-truth docs, dependency sources and high-confidence references.
- learning records become rewrite records and review reports.
- lessons become migration units.
- retrieval/feedback becomes behavior fixtures, R0 checks and reviewer gates.
- stateful learning becomes a manifest-driven rewrite workspace.

This is why py2rs is not just "ask AI to rewrite it". It is a way to keep the loop grounded across many sessions.

## Human Constraints

The human owns the constraints that define the loop:

- the reason for the rewrite
- accepted architecture seams
- public behavior that must not change
- which units target Python behavior parity and which deep boundaries target verified-Rust compatibility
- migration unit granularity
- review budget, review cadence and token budget
- dependency source expansion policy
- crate reuse, adapter or hand-written replacement tradeoffs
- manifest partitioning and serial or explicitly coordinated-parallel execution
- project-specific rules that deserve their own skills

The AI operates inside those constraints.

## AI Work Inside The Loop

The AI can still do substantial work:

- inspect project facts
- propose or re-cut manifest units
- use one writer in dependency order by default, even when the manifest is sharded
- add fixtures and tests
- accumulate writer-verified units according to the user's review cadence
- produce batch reports with shared context and per-unit verdicts
- maintain migration state
- record reusable lessons

The point is to make fast loops produce code that can be understood, reviewed and rolled back. Strict behavior parity is the default; at a boundary where the whole external framework cannot be rewritten, explicit verified-Rust compatibility is more rigorous than pretending to match framework internals.

## Why Skills

Skills are the reusable boundary between human intent and AI execution. A good skill records:

- when it should be used
- what context must be read first
- which architecture is accepted
- which decisions are out of scope
- how evidence is produced
- what counts as completion

py2rs is the general discipline. Project-specific skills are where the discipline becomes real.
