# Philosophy

[中文版本](philosophy.zh.md)

py2rs is a loop engineering discipline for controlled rewrites.

It is not trying to maximize creativity. It is trying to preserve engineering control while AI agents perform repetitive migration work. If the work needs free-form invention, broad product ideation or creative taste, this repository is the wrong tool. If the work needs bounded rewrites, behavior parity, review gates and rollback, this repository is the intended tool.

## Human Constraints First

The human owns the constraints that define the loop:

- the reason for the rewrite
- accepted architecture seams
- public behavior that must not change
- migration unit granularity
- review budget and token budget
- dependency source expansion policy
- crate reuse, adapter or hand-written replacement tradeoffs
- project-specific rules that deserve their own skills

The AI operates inside those constraints.

## AI Loop Work

The AI can still do substantial work:

- inspect project facts
- propose or re-cut manifest units
- implement one unit at a time
- add fixtures and tests
- produce review reports
- maintain migration state
- record reusable lessons

The point is not to slow the loop down. The point is to make sure fast loops keep producing code that can be understood, reviewed and rolled back.

## Why Skills

Skills are the reusable boundary between human intent and AI execution. A good skill records:

- when it should be used
- what context must be read first
- which architecture is accepted
- which decisions are out of scope
- how evidence is produced
- what counts as completion

py2rs is the general discipline. Project-specific skills are where the discipline becomes real.
