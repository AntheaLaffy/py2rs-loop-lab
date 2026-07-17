---
name: "py2rs-review-r4-algo-complexity"
description: "[DRAFT] 第 4 轮算法复杂度审查。只在有复杂度分析、理论依据和 benchmark 证据时建议或实施算法改变；默认审查不改生产代码。"
---

# R4 Algorithm Complexity Review

R4 只处理算法和复杂度。Rust 代码不因为“看起来更 Rust”就改算法。

## Preconditions

- R0 behavior report exists.
- Earlier required reviews are complete or explicitly deferred.
- Representative input sizes and hot paths are known or can be measured.

## Review Focus

- O(n^2) or worse loops on realistic large inputs.
- Repeated parsing, sorting, serialization or regex work.
- Hot-path allocations and string concatenation.
- Missing indexes/maps for repeated lookup.
- Python C-extension behavior that Rust does not automatically beat.
- Memory growth from proposed optimizations.

## Evidence Rule

Any algorithm change requires all three:

1. Complexity analysis: old vs new.
2. Theoretical basis: why the new structure improves cost.
3. Benchmark or measured fixture: before/after numbers.

Without the three, write a finding or recommendation; do not change the algorithm.

## Workflow

1. Confirm unit id and performance-relevant public behavior.
2. Identify hot paths from code, tests, profiles or realistic workload notes.
3. Classify findings as required, optional or no-change.
4. Run or request benchmarks where practical.
5. Save a report with decision.

## Code Changes

Default review-gate mode does not edit production code. If explicitly asked to remediate:

- Apply only changes backed by the evidence rule.
- Keep public behavior stable.
- Record benchmark numbers.
- Rerun R0 behavior after changes.
- Do not approve your own final R4 report.

## Report

Use project convention or:

```text
reviews/YYYY-MM-DD-<unit-id>-data-algorithm.md
```

Include:

- Scope reviewed
- Hot paths inspected
- Complexity findings
- Benchmark/checks run
- Residual risk
- Promotion decision

## Non-Negotiables

- No speculative "probably faster" changes.
- No behavior change without explicit migration-unit policy.
- No benchmark-free algorithm rewrite.
