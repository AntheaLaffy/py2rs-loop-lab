---
name: "py2rs-review-r5-architecture"
description: "[DRAFT] 第 5 轮架构与数据结构审查。对一个迁移单元或已收批的 review batch 检查 ownership、API 边界、canonical storage、data structures 和 seam 深度；默认审查不改生产代码，架构修改需独立实现与复审。"
---

# R5 Architecture And Data Structures Review

R5 审视迁移后的结构是否适合长期维护。它尊重项目已经接受的架构 seam，不把 py2rs router 强行套进去。

## Preconditions

- The manifest-selected behavior or Rust-compatibility R0 report exists.
- Required earlier reviews are complete or explicitly deferred.
- Project architecture/source-boundary docs have been read.

## Review Focus

- Accepted seam is preserved and deep enough.
- Public API area is small and stable.
- Ownership model is clear: who owns state, cache, DB rows, files and task identity.
- Canonical store is explicit when legacy and rewritten stores overlap.
- Data structures match access patterns.
- Shared mutable state is minimized and justified.
- Rollback path remains possible.
- Cross-module dependencies do not expose storage internals to callers.

## Workflow

1. Confirm the unit or closed review batch, included unit ids, source-boundary rules and accepted architecture.
2. Inspect data structures, ownership and public APIs.
3. Check whether implementation leaked new internals across the seam.
4. Check storage conflict and migration rules.
5. Save findings and promotion decision.
6. Add or request a rewrite record when a reusable source-boundary lesson appears.

## Code Changes

Default review-gate mode does not edit production code. If explicitly asked to remediate:

- Keep changes inside the selected migration unit or define a new unit.
- Preserve public behavior and rollback.
- Record source-boundary changes before broad implementation.
- Rerun the selected R0 gate after changes.
- Do not author the final pass report for your own architecture patch.

## Report

Use project convention or:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-architecture.md
```

Include:

- Scope reviewed
- Included unit ids and per-unit verdicts (`not_required` only when the manifest
  does not require R5 for that unit)
- Architecture/data interfaces inspected
- Findings ordered by severity
- Checks run
- Residual risk
- Promotion decision

## Non-Negotiables

- Do not replace the project's accepted seam without an ADR or equivalent decision record.
- Do not let callers depend on repository/database internals.
- Do not mark a broad refactor verified without fresh evidence from its selected R0 gate.
