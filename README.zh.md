# py2rs-loop-lab

> 用于受控 Python-to-Rust 和 legacy-to-Rust 重写的 loop engineering skill 实验室。

[English README](README.md)

`py2rs-loop-lab` 收录一组 Codex/Claude skills，用来把 Python -> Rust 或 legacy -> Rust 的渐进式重写变成可运行、可审核、可回滚的工程循环。

这个项目不是反对 loop engineering。它本身就是一个 loop engineering 项目。它的定位更窄：当你需要受控工程推进、行为门禁、依赖对齐、审核报告和持久迁移状态时使用它。如果你的主要目标是开放式创意探索，不要使用这个项目，因为这套流程会有意牺牲一部分创意自由来换取质量控制。

## 项目定位

py2rs 承认 AI 可以承担大量迁移工作：读代码、写代码、补 fixture、跑检查、写审核报告、维护迁移状态。

但人仍然负责关键约束：

- 项目为什么要重写。
- 哪些公共行为不能变。
- 哪个架构 seam 被接受。
- 迁移单元应该切多细。
- 什么时候复用依赖、写 adapter、局部造轮子或全量造轮子。
- 哪些项目实践应该固化成可复用 skill。

一句话：py2rs 是带有人类显式约束的 loop engineering。

## 仓库内容

py2rs 核心 skills：

- [`skills/py2rs`](skills/py2rs/SKILL.md)：总协调思想和路由 skill。
- [`skills/py2rs-runtime`](skills/py2rs-runtime/SKILL.md)：manifest、控制面、状态机、manifest shards 和粒度配置。
- [`skills/py2rs-dep-align`](skills/py2rs-dep-align/SKILL.md)：按能力做依赖对齐、源码展开、crate/adapter/造轮子取舍。
- [`skills/py2rs-env-bootstrap`](skills/py2rs-env-bootstrap/SKILL.md)：业务迁移前证明 seam 可用。

审核门 skills：

- [`R0 behavior`](skills/py2rs-review-r0-behavior/SKILL.md)：promotion 前先证明公共行为一致。
- [`R1 Rust style`](skills/py2rs-review-r1-rust-style/SKILL.md)：Rust 模块结构、所有权、可见性、warning 和可维护性。
- [`R2 error tracing`](skills/py2rs-review-r2-error-tracing/SKILL.md)：结构化错误、日志、上下文和脱敏。
- [`R3 IO concurrency`](skills/py2rs-review-r3-io-concurrency/SKILL.md)：阻塞 IO、async 边界、取消、重试和运行时人体工学。
- [`R4 algorithm complexity`](skills/py2rs-review-r4-algo-complexity/SKILL.md)：算法修改、复杂度声明和 benchmark 证据。
- [`R5 architecture`](skills/py2rs-review-r5-architecture/SKILL.md)：数据 ownership、API 边界、canonical storage 和模块深度。
- [`R6 ergonomics`](skills/py2rs-review-r6-ergonomics/SKILL.md)：产品、CLI、UX 和运维人体工学。

实践 skills：

- [`mvsep-rs`](skills/practices/mvsep-rs-rewrite/SKILL.md)：Tauri backend facade seam 的实践。
- [`Vocal2Midi / v2m`](skills/practices/vocal2midi-rs-rewrite/SKILL.md)：依赖复杂的 Python 项目重写实践。

## 文档

英文：

- [`docs/philosophy.md`](docs/philosophy.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/review-gates.md`](docs/review-gates.md)
- [`docs/usage.md`](docs/usage.md)
- [`docs/practices.md`](docs/practices.md)

中文：

- [`docs/philosophy.zh.md`](docs/philosophy.zh.md)
- [`docs/architecture.zh.md`](docs/architecture.zh.md)
- [`docs/review-gates.zh.md`](docs/review-gates.zh.md)
- [`docs/usage.zh.md`](docs/usage.zh.md)
- [`docs/practices.zh.md`](docs/practices.zh.md)

## 核心思想

1. **Project truth first**：先读项目事实，不从模板出发。
2. **Granularity calibration**：切 manifest 前先和用户确认单元粒度、审核成本和质量目标。
3. **Capability coverage, not package parity**：依赖对齐按行为和能力，不按包名一一对应。
4. **Bounded source expansion**：第一层直接 Python 依赖可以作为本地参考；更深依赖必须有 public-seam call-path evidence。
5. **Writer/reviewer separation**：写代码的 agent 不审核自己的代码。
6. **R0 before elegance**：行为一致性先于 Rust 风格或优化。
7. **Project-specific skills**：py2rs 是纪律，不是强制架构。

## 快速开始

1. 阅读 [`skills/py2rs/SKILL.md`](skills/py2rs/SKILL.md)。
2. 用 [`skills/py2rs-runtime/SKILL.md`](skills/py2rs-runtime/SKILL.md) 建立或复用 manifest/control plane。
3. 和用户校准迁移单元粒度。
4. 用 [`skills/py2rs-dep-align/SKILL.md`](skills/py2rs-dep-align/SKILL.md) 做依赖对齐。
5. 由 writer role 实现一个已确认的迁移单元。
6. 运行 [`R0 behavior review`](skills/py2rs-review-r0-behavior/SKILL.md)。
7. 根据风险和 promotion 要求增加 R1-R6 门禁。

## License

MIT. See [`LICENSE`](LICENSE).
