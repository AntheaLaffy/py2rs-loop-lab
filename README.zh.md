# py2rs-loop-lab

> 用来创造项目专属重写 skills 的架构 skills。

[English README](README.md)

`py2rs-loop-lab` 是一个用于受控 Python-to-Rust 和 legacy-to-Rust 重写的 loop engineering 仓库。

它不是可以直接套到任意项目的通用 skill 包。正确用法是：让 AI 借鉴这个仓库的思想和架构，再为你的具体项目创造具体 skills。真正的 loop 只能在项目已经有自己的事实、约束、manifest、records、依赖策略和审核门之后开始。

如果你的目标是开放式创意探索，这不是合适工具。这个项目适合有边界的工程工作：迁移状态、行为证据、依赖对齐、审核报告和回滚。

## 怎么使用

1. 先有一个真实项目仓库。
2. 让 AI 研究这个仓库的思想和架构。
3. 让 AI 为真实项目设计项目专属 skills：coordinator、dependency/bootstrap、writer 和 review gates。
4. 初始化重写工作区：mission、resources、notes、records、manifest、依赖源码策略和 granularity profile。
5. 再进入 loop：依赖对齐、实现一个单元、运行 R0，再按需要增加 R1-R6。

核心产物不是 Rust 代码。核心产物是一个能持续产出已审核 Rust 代码的项目专属 loop。

如果你只是想先把 skills 装进 Codex，见 [`docs/installation.zh.md`](docs/installation.zh.md)。教程包含“让 AI 安装”的提示词，以及 macOS/Linux 和 Windows 手动安装命令。

## 核心 Skills

- [`py2rs`](skills/py2rs/SKILL.md)：总重写纪律和路由。
- [`py2rs-runtime`](skills/py2rs-runtime/SKILL.md)：控制面、manifest、状态机、shards 和粒度。
- [`py2rs-dep-align`](skills/py2rs-dep-align/SKILL.md)：依赖源码展开和能力对齐。
- [`py2rs-env-bootstrap`](skills/py2rs-env-bootstrap/SKILL.md)：业务迁移前证明 seam 可用。

## 审核门

- [`R0 behavior`](skills/py2rs-review-r0-behavior/SKILL.md)：公共行为一致性。
- [`R1 Rust style`](skills/py2rs-review-r1-rust-style/SKILL.md)：Rust 结构和可维护性。
- [`R2 error tracing`](skills/py2rs-review-r2-error-tracing/SKILL.md)：错误、日志、上下文和脱敏。
- [`R3 IO concurrency`](skills/py2rs-review-r3-io-concurrency/SKILL.md)：阻塞 IO、async 边界和运行时人体工学。
- [`R4 algorithm complexity`](skills/py2rs-review-r4-algo-complexity/SKILL.md)：算法声明和 benchmark 证据。
- [`R5 architecture`](skills/py2rs-review-r5-architecture/SKILL.md)：ownership、API、storage 和数据边界。
- [`R6 ergonomics`](skills/py2rs-review-r6-ergonomics/SKILL.md)：CLI、UX、恢复和运维。

详见 [`docs/review-gates.zh.md`](docs/review-gates.zh.md)。

## 思想来源

py2rs 结合了：

- **teach 式渐进思想**：mission-grounded、resources before memory、durable records、notes、小单元和反馈循环。
- **重写纪律**：行为先于架构、可逆状态、manifest 驱动进度、独立审核门。
- **项目专属适配**：真实项目保留自己接受的 seam，不强制采用 py2rs 固定目录结构。

来源 skill 已收录在 [`skills/foundations/teach`](skills/foundations/teach/SKILL.md)。它来自 Matt Pocock 的 [`mattpocock/skills`](https://github.com/mattpocock/skills) 仓库；见 [`THIRD_PARTY.md`](THIRD_PARTY.md)。

## 实践 Skills

- [`mvsep-rs`](skills/practices/mvsep-rs-rewrite/SKILL.md)：[`AntheaLaffy/mvsep-rs`](https://github.com/AntheaLaffy/mvsep-rs) 的 Tauri backend facade 重写实践。
- [`Vocal2Midi / v2m`](skills/practices/vocal2midi-rs-rewrite/SKILL.md)：[`AntheaLaffy/Vocal2Midi-for-linux`](https://github.com/AntheaLaffy/Vocal2Midi-for-linux) 的重依赖 Python 项目重写实践。

它们是从同一套架构创造出来的项目专属 skills，不是通用模板。

## 文档

英文：

- [`docs/philosophy.md`](docs/philosophy.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/review-gates.md`](docs/review-gates.md)
- [`docs/usage.md`](docs/usage.md)
- [`docs/practices.md`](docs/practices.md)

中文：

- [`docs/installation.zh.md`](docs/installation.zh.md)
- [`docs/philosophy.zh.md`](docs/philosophy.zh.md)
- [`docs/architecture.zh.md`](docs/architecture.zh.md)
- [`docs/review-gates.zh.md`](docs/review-gates.zh.md)
- [`docs/usage.zh.md`](docs/usage.zh.md)
- [`docs/practices.zh.md`](docs/practices.zh.md)

## License

MIT. See [`LICENSE`](LICENSE).
