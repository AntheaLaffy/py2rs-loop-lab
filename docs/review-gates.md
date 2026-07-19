# Review Gates R0-R6

[中文版本](review-gates.zh.md)

py2rs separates writing from reviewing. A writer can prepare code and fixtures, but review evidence must come from a separate role. Each unit first selects one R0 oracle in the manifest.

Independent review does not have to start after every writer pass. The
manifest's `review_policy` may select per-unit review, one aggregate review every
N units, or an end-of-scope review for a small project. The default is a
three-unit batch when the user does not choose.

## R0 Behavior

Skill: [`py2rs-review-r0-behavior`](../skills/py2rs-review-r0-behavior/SKILL.md)

Purpose: prove that the rewritten implementation preserves the selected public behavior.

R0 behavior checks public inputs, outputs, errors, side effects, persistence and user-visible payloads through the accepted project seam. A batch also checks integration. It applies only to `behavior_parity`.

## R0 Compatibility

Skill: [`py2rs-review-r0-compatibility`](../skills/py2rs-review-r0-compatibility/SKILL.md)

Purpose: prove that a new Rust unit remains application-compatible with already
behavior-verified canonical Rust contracts.

Use it only for predeclared `rust_compatibility` units, such as tensor handoff,
codecs, model artifacts and model loading in a deep inference chain. It does not
compare excluded Python framework internals or claim Python parity, but any
difference that reaches a declared application contract must fail.

## R1 Rust Style

Skill: [`py2rs-review-r1-rust-style`](../skills/py2rs-review-r1-rust-style/SKILL.md)

Purpose: check Rust module shape and maintainability.

R1 looks at ownership, visibility, warnings, clippy-style concerns, test structure and whether the Rust code is understandable to future maintainers.

## R2 Error Tracing

Skill: [`py2rs-review-r2-error-tracing`](../skills/py2rs-review-r2-error-tracing/SKILL.md)

Purpose: make failures diagnosable without leaking sensitive data.

R2 checks structured errors, context propagation, logs, trace IDs, redaction and whether source errors remain visible enough to debug.

## R3 IO Concurrency

Skill: [`py2rs-review-r3-io-concurrency`](../skills/py2rs-review-r3-io-concurrency/SKILL.md)

Purpose: check runtime and operational behavior around IO.

R3 covers blocking IO, async boundaries, cancellation, retries, concurrency limits, repeated calls and runtime nesting risks.

## R4 Algorithm Complexity

Skill: [`py2rs-review-r4-algo-complexity`](../skills/py2rs-review-r4-algo-complexity/SKILL.md)

Purpose: keep algorithm changes evidence-based.

R4 only supports algorithmic changes when there is complexity analysis, theory or benchmark evidence. It is not a license to optimize before behavior is proven.

## R5 Architecture

Skill: [`py2rs-review-r5-architecture`](../skills/py2rs-review-r5-architecture/SKILL.md)

Purpose: check data ownership and API boundaries.

R5 reviews ownership, canonical storage, data structures, module depth and whether the selected seam remains clean.

## R6 Ergonomics

Skill: [`py2rs-review-r6-ergonomics`](../skills/py2rs-review-r6-ergonomics/SKILL.md)

Purpose: inspect the migration from a user and operator perspective.

R6 checks CLI/help text, recovery, batching, cache behavior, error readability, configuration, accessibility and operational workflow.

## Gate Selection

R0 is mandatory before promotion: each unit selects exactly one of behavior or compatibility. R1-R6 are selected by risk, manifest policy and granularity. Failed parity cannot trigger an ad hoc compatibility switch.

## Batch Rules

- Each unit must pass writer verification and remain `reimplemented` before it
  enters an open batch.
- Flush the batch at its configured size, scope completion or a promotion
  request. `risk_override` controls high-risk boundaries and defaults to an
  early flush.
- Run the behavior/compatibility R0 selected by each unit first, then the union
  of additional roles.
- Each role may write one batch report, but it must list unit ids and per-unit
  verdicts. `not_required` is valid only when that unit's manifest does not
  require the role.
- One failed unit does not erase valid evidence for the others; promote only
  units whose required verdicts all pass.
- After remediation, rerun R0 and any other gates affected by the fix.
