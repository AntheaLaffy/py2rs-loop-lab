# py2rs-loop-lab

> A skill-driven loop engineering lab for human-constrained Python-to-Rust rewrites.

`py2rs-loop-lab` 收录一组 Codex/Claude skills，用来把 Python -> Rust 或 legacy -> Rust 的渐进式重写变成可运行、可审核、可回滚的工程循环。

它不是“Python 自动翻译成 Rust”的工具，而是一套 loop engineering 方法论：用 manifest、依赖展开、迁移单元、writer/reviewer 分离、R0 行为门禁和项目专属 skills，把 AI 写代码的循环约束在人的工程判断之内。

## Why

最近 vibecoding / loop engineering 很火，但常见做法有一个核心问题：规划、书写、审核、演进方向都交给 AI 后，人能发挥创意的地方被压缩到很少。

py2rs 的取向不同：

- 人在初始化时给出架构 seam、依赖策略、粒度偏好和项目约束。
- AI 负责在这些约束内执行 writer/reviewer loop。
- 每个迁移单元必须能独立验证、独立审查、独立回滚。
- 审核不是一句“看起来没问题”，而是 durable report 和可重复行为证据。
- 项目可以发展自己的实践 skills，而不是照搬 py2rs 的目录结构。

In English: py2rs is a human-constrained loop engineering discipline. The AI can plan, write and review, but the human defines the boundaries, tradeoffs and project-specific rules.

## What Is Included

Core py2rs skills:

- [`skills/py2rs`](skills/py2rs/SKILL.md): 总协调思想。
- [`skills/py2rs-dep-align`](skills/py2rs-dep-align/SKILL.md): 依赖能力对齐、源码展开、crate/adapter/造轮子取舍。
- [`skills/py2rs-runtime`](skills/py2rs-runtime/SKILL.md): manifest、控制面、manifest shards、迁移单元粒度。
- [`skills/py2rs-env-bootstrap`](skills/py2rs-env-bootstrap/SKILL.md): seam bootstrap。
- [`skills/py2rs-review-r0-behavior`](skills/py2rs-review-r0-behavior/SKILL.md): 行为一致性门禁。
- [`skills/py2rs-review-r1-rust-style`](skills/py2rs-review-r1-rust-style/SKILL.md) to [`skills/py2rs-review-r6-ergonomics`](skills/py2rs-review-r6-ergonomics/SKILL.md): 独立质量门。

Practice skills:

- [`skills/practices/mvsep-rs-rewrite`](skills/practices/mvsep-rs-rewrite/SKILL.md): Tauri backend facade seam 的实践。
- [`skills/practices/vocal2midi-rs-rewrite`](skills/practices/vocal2midi-rs-rewrite/SKILL.md): Python 依赖展开 + Rust library rewrite seam 的实践。

Supporting docs:

- [`docs/philosophy.md`](docs/philosophy.md): 方法论和 loop engineering 批判。
- [`docs/architecture.md`](docs/architecture.md): 架构术语和控制面。
- [`docs/usage.md`](docs/usage.md): 如何使用这些 skills 初始化或推进重写。
- [`docs/practices.md`](docs/practices.md): 两个实践案例的差异。

## Core Ideas

1. **Project truth first**: 先读项目事实，不从模板出发。
2. **Granularity calibration**: 初始化时和用户确认单元切多细。更细意味着更多审核和 token 成本，也意味着更少幻觉、更少死代码和更高质量。
3. **Capability coverage, not package parity**: 依赖对齐按能力，不按包名一一对应。
4. **Source expansion with boundaries**: 一层直接依赖可以作为本地 reference corpus；二层更深依赖必须有 public-seam call-path evidence。
5. **Writer/reviewer separation**: 写代码的人不能审自己的代码。
6. **R0 before elegance**: 行为一致性先于 Rust 优雅。
7. **Project-specific skills**: py2rs 是纪律，不是固定架构。项目可以保留自己的 seam 和控制面。

## Usage

Copy the skills you want into your agent skill directory, or use this repository as a reference when designing project-specific skills.

Minimal flow:

1. Read [`skills/py2rs/SKILL.md`](skills/py2rs/SKILL.md).
2. Initialize or identify a manifest/control-plane using [`skills/py2rs-runtime/SKILL.md`](skills/py2rs-runtime/SKILL.md).
3. Calibrate migration unit size with the user.
4. Run dependency alignment using [`skills/py2rs-dep-align/SKILL.md`](skills/py2rs-dep-align/SKILL.md).
5. Implement one unit with a writer role.
6. Run R0 behavior review before promotion.
7. Add additional review gates based on risk.

See [`docs/usage.md`](docs/usage.md) for a more concrete workflow.

## License

MIT. See [`LICENSE`](LICENSE).
