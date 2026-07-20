---
name: "py2rs-review-r6-ergonomics"
description: "[DRAFT] 第 6 轮产品、CLI、UX 与运维人体工学审查。对一个迁移单元或已收批的 review batch，从用户和维护者视角检查恢复、批处理、缓存、错误可读性、配置、可访问性和 workflow；只产出报告。"
---

# R6 Ergonomics Review

R6 是 report-only gate。它不写代码，产出下一轮可排期的产品/体验/运维改进建议。

## Preconditions

- The R0 behavior report exists.
- Required engineering reviews are complete or explicitly deferred.
- Every in-scope unit is usable through its intended public interface.

## Review Focus

- High-frequency workflow: how many steps, where users wait, where retries happen.
- Batch behavior: queueing, partial failure, resume and export.
- Cache behavior: invalidation, refresh, corruption recovery and clear-cache path.
- Error readability: user-facing message vs maintainer log detail.
- Config/defaults: missing config, help/version, sane defaults and migration messages.
- Recovery: app/process crash, network loss, DB/file errors and interrupted downloads/jobs.
- Internationalization and long text: non-ASCII paths, translated strings, text overflow.
- Frontend/GUI only when relevant: focus, accessibility, progress, narrow viewport and untrusted HTML escaping.

## Workflow

1. Confirm the unit or closed review batch, included unit ids and target audience.
2. Exercise or inspect the intended workflow.
3. Read relevant logs, help text, UI, CLI output or docs.
4. Rank findings by impact and cost.
5. Save a report. Do not edit production code.

## Report

Use project convention or:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-ergonomics.md
```

Required sections:

- Current workflow summary
- Included unit ids and per-unit verdicts (`not_required` only when the manifest
  does not require R6 for that unit)
- Findings ordered by severity or impact/cost
- Recommended follow-up units
- Checks or manual scenarios run
- Residual risk
- Promotion decision or product-readiness note

## Boundaries

- Do not change behavior under R6.
- Do not use UX preference to override R0 behavior without defining a new migration unit.
- Do not mix visual redesign with backend protocol migration unless the unit explicitly includes it.
- If suggestions require code, hand them to a writer/architect pass and require fresh R0 evidence.
