# 实践案例

[English version](practices.md)

本仓库收录了两组从 py2rs 纪律发展出的具体实践 skills。

## mvsep-rs

Skills：

- `skills/practices/mvsep-rs-rewrite`
- `skills/practices/mvsep-rs-batch-writer`
- `skills/practices/mvsep-rs-review-gate`

mvsep-rs 借鉴 py2rs 纪律，但不采用 py2rs 架构。

关键形态：

- Tauri command -> backend facade seam。
- 保留现有 command names 和 progress events。
- writer 和 reviewer 角色分离。
- behavior review 是第一门。
- 不引入 Python router，不强制 `py/` / `rs/` 目录形态。

这是 py2rs 作为迁移纪律而不是固定模板的例子。

## Vocal2Midi / v2m

Skills：

- `skills/practices/vocal2midi-rs-rewrite`
- `skills/practices/vocal2midi-rs-dep-bootstrap`
- `skills/practices/vocal2midi-rs-unit-writer`
- `skills/practices/vocal2midi-rs-review-gate`

Vocal2Midi 是依赖很重的 Python 项目重写。

关键形态：

- 大体量第三方源码库作为本地 reference material。
- 第一层直接 Python 依赖适合支撑高级语言层面的造轮子。
- 第二层或更深依赖必须有 public-seam call-path evidence。
- Rust crates 和手写 replacement 是互补关系。
- 低层 native/compiler/runtime 细节默认忽略，除非影响 public behavior、memory/ABI、persistence、security 或 model/numeric correctness。

这是 py2rs 应用于胶水语言项目和重依赖对齐场景的例子。
