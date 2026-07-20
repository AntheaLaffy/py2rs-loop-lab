---
name: "py2rs-review-r0-behavior"
description: "[DRAFT] 第 0 轮行为一致性门禁。对一个迁移单元或已收批的 review batch，独立证明旧实现与新实现在选定 public seam 后行为一致；不写生产代码，只运行/补充对比证据并输出报告。"
---

# R0 Behavior Review

R0 是所有后续优化的前置 gate。目标不是让 Rust 更好看，而是证明：

```text
legacy behavior == rewritten behavior
```

## Required Context

Read first:

- project mission/architecture/resources/manifest/records
- selected migration unit or batch
- public interface policy
- rollback route
- old and new implementation paths or adapters
- existing tests/fixtures/logs for the behavior
- `behavior_verification`, including the legacy public seam, observations,
  comparison policy and fixture evidence

Do not rely on the writer's explanation when code, tests or docs can answer.

## Scope

Review through the project's accepted seam:

- Python module/function if that is the seam.
- CLI arguments/stdin/stdout/exit codes for CLI migration.
- HTTP payloads/status/errors for service migration.
- Tauri command/event/payload contracts for desktop migration.
- Pipeline input/output fixtures for data migration.

Do not force `py/` and `rs/` paths if the project uses another architecture.

## Workflow

1. Confirm `behavior_verification` names an independently comparable legacy
   public seam. Reject missing seams and evidence that substitutes Rust-only or
   circular output for legacy behavior.
2. Confirm the unit id, or confirm the review batch is closed to new units and
   record every included unit id and manifest state.
3. Confirm each public interface policy and rollback route.
4. Build a behavior comparison matrix covering every unit plus cross-unit
   integration: normal, boundary, error, side effect and persistence cases. For
   model or framework boundaries, include observable tensor shape/dtype/layout,
   codecs, artifacts, model loading, schemas, handoffs and error projection.
5. Run existing comparison tests or add non-production fixtures/tests if the repo convention allows reviewer-owned test artifacts.
6. Compare old/new outputs, errors, logs, side effects and user-visible payloads.
7. Report findings first, ordered by severity.
8. Write a durable report.
9. Use decision `pass`, `pass-with-followups` or `fail` for each unit.

## Boundaries

- Do not edit production code.
- Do not approve behavior changes as "close enough" unless the public interface policy explicitly allows the change.
- Do not replace a failed parity review with a Rust-only oracle. Re-cut the unit,
  move the seam outward, or keep the legacy owner.
- Comparison is exact unless the manifest records a tolerance from an existing
  public contract or explicit pre-implementation user approval.
- Review the selected public seam, not every transitive dependency or native
  implementation detail below it.
- Do not chase low-level compiler/runtime/native-library differences such as
  NaN bit payloads, internal table layouts, allocator behavior, struct padding,
  SIMD branches or kernel selection unless they affect public outputs, errors,
  serialization, persistence, memory/ABI contracts, security, or model/numeric
  correctness.
- High-level/domain-visible data structures are in scope when the unit depends
  on them: parser state, tokenizer output, tensor shape/dtype policy, model
  runner payloads, business DTOs, cache keys, schema, and user-visible error
  projection.
- Do not mark units `verified`; the orchestrator updates manifest after required reports pass.
- If behavior differs, write the diff and send it back to the writer.

## Report

Use the project report convention. If none exists:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-behavior.md
```

Required sections:

- Scope reviewed
- Included unit ids and per-unit verdicts
- Public interfaces inspected
- Comparison cases and results
- Findings ordered by severity
- Tests/checks run
- Residual risk
- Promotion decision

## Exit Criteria

- Behavior evidence is repeatable.
- Any mismatch has file/line or fixture references.
- The report is saved.
- Later R1-R6 work has a clear behavior baseline to rerun.
- A batch report covers integration behavior and gives every included unit an
  explicit verdict.
