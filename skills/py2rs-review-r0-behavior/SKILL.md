---
name: "py2rs-review-r0-behavior"
description: "[DRAFT] 第 0 轮行为一致性门禁。独立证明旧实现与新实现在选定 public seam 后行为一致；不写生产代码，只运行/补充对比证据并输出报告。"
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

1. Confirm unit id and current manifest state.
2. Confirm public interface policy and rollback route.
3. Build a behavior comparison matrix: normal, boundary, error, side effect and persistence cases.
4. Run existing comparison tests or add non-production fixtures/tests if the repo convention allows reviewer-owned test artifacts.
5. Compare old/new outputs, errors, logs, side effects and user-visible payloads.
6. Report findings first, ordered by severity.
7. Write a durable report.
8. Use decision `pass`, `pass-with-followups` or `fail`.

## Boundaries

- Do not edit production code.
- Do not approve behavior changes as "close enough" unless the public interface policy explicitly allows the change.
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
- Do not mark the unit `verified`; the orchestrator updates manifest after required reports pass.
- If behavior differs, write the diff and send it back to the writer.

## Report

Use the project report convention. If none exists:

```text
reviews/YYYY-MM-DD-<unit-id>-behavior.md
```

Required sections:

- Scope reviewed
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
