---
name: "py2rs-review-r2-error-tracing"
description: "[DRAFT] 第 2 轮错误与追踪审查。对一个迁移单元或已收批的 review batch 检查结构化错误、上下文、日志、trace 传播和敏感信息保护；默认审查不改生产代码，修复后必须重跑行为门禁。"
---

# R2 Error And Tracing Review

R2 确认新 Rust path 在失败时可诊断、可映射、可审计，并且不会泄露敏感信息。

## Preconditions

- The manifest-selected behavior or Rust-compatibility R0 report exists.
- R1 style review is complete or explicitly deferred by the manifest.
- Every in-scope unit's public error contract is known.

## Review Focus

- Public errors preserve the selected R0 error contract until protocol changes are explicitly approved.
- Internal errors carry operation, path/endpoint/resource id, source error and useful context.
- Errors stay structured until the public seam requires stringification.
- Logs/traces include operation and correlation id where the project supports it.
- Sensitive values such as tokens, passwords, headers and credential-like config are redacted.
- Panic paths are absent from normal error handling.

## Workflow

1. Confirm the unit or closed review batch, included unit ids, seams and public error policies.
2. Inspect error types, adapter mapping and logging paths.
3. Trigger at least one representative error path when practical.
4. Check whether logs let a maintainer locate the failing operation.
5. Report findings first and save a durable report.

## Code Changes

Default review-gate mode does not edit production code. If explicitly asked to remediate:

- Add context/redaction/error mapping without changing public behavior.
- Do not approve your own remediation report.
- Rerun the selected R0 gate after changes.

## Report

Use project convention or:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-error-tracing.md
```

Required sections:

- Scope reviewed
- Included unit ids and per-unit verdicts (`not_required` only when the manifest
  does not require R2 for that unit)
- Error/log interfaces inspected
- Findings ordered by severity
- Error cases/checks run
- Residual risk
- Promotion decision

## Non-Negotiables

- Do not flatten errors early inside business modules.
- Do not log secrets.
- Do not replace behavior differences with generic error strings.
