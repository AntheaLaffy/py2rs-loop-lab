---
name: "py2rs-review-r1-rust-style"
description: "[DRAFT] 第 1 轮 Rust 工程化审查。对一个迁移单元或已收批的 review batch 检查 Rust 模块结构、可见性、所有权、lint 和可维护性；默认审查不改生产代码，修复需单独实现并重跑 R0。"
---

# R1 Rust Style Review

R1 检查 Rust 代码是否从“行为等价但直译”走向可维护的 Rust。它不重新定义项目架构 seam。

## Preconditions

- The R0 behavior report exists and is `pass` or accepted `pass-with-followups`.
- Every in-scope manifest unit is at least `reimplemented`.
- The R0 behavior baseline can be rerun after any remediation.

## Review Focus

- Module shape: entrypoint, library boundary, domain modules and test modules are understandable.
- Visibility: `pub` surface is minimal and matches the project seam.
- Types: business concepts are named types instead of loose maps/strings where practical.
- Ownership: unnecessary clones and broad ownership transfer are flagged.
- Borrowing: APIs accept `&str`, `&[T]` or borrowed data where that fits the seam.
- Panics: no production `unwrap`/`expect` without explicit justification.
- Lints: `cargo fmt`, `cargo clippy` or project lint policy are considered.

## Workflow

1. Confirm this is one review role for one unit or one closed review batch.
2. Inspect only Rust code and public adapter surface needed for style/maintainability.
3. Run non-mutating checks where useful.
4. Report findings first with file/line references.
5. Save a report with `pass`, `pass-with-followups` or `fail` for each in-scope unit.

## Code Changes

Default review-gate mode does not edit production code. If the user explicitly asks this skill to fix issues:

- Make only style/structure changes that preserve R0 behavior.
- Do not author the final R1 pass report for your own patch.
- Require the R0 behavior gate to be rerun after the patch.

## Report

Use project convention or:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-rust-style.md
```

Include:

- Scope reviewed
- Included unit ids and per-unit verdicts (`not_required` only when the manifest
  does not require R1 for that unit)
- Rust files/interfaces inspected
- Findings ordered by severity
- Checks run
- Residual risk
- Promotion decision

## Non-Negotiables

- Do not change behavior semantics in a style review.
- Do not introduce async/concurrency work here; that is R3.
- Do not make data-structure redesigns here unless they are small and style-local; larger changes belong to R5.
