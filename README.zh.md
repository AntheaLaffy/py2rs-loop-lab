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
4. 初始化重写工作区：mission、resources、notes、records、manifest、重写/框架偏好、依赖源码策略和 granularity profile。
5. 再进入 loop：侦察 crate 能力路径、依赖对齐、实现一个单元、运行 R0，再按需要增加 R1-R6。

核心产物不是 Rust 代码。核心产物是一个能持续产出已审核 Rust 代码的项目专属 loop。

## 当前架构简介

这次架构把两个容易混在一起的问题拆成了独立控制轴：

- **依赖与重写策略**：初始化时在 `NOTES.md` 记录重写力度、相关框架偏好、crate 侦察模式和项目自己的 crates.io 代理。真正需要某项能力时，再通过 Context7、registry 搜索和 Cargo 依赖图判断应该复用 crate、使用下层 backend、增加 adapter，还是手写差异组件。
- **项目 Skill 执行形态**：每个 coordinator、dependency bootstrap、writer 或 review role 独立选择 `prompt` 或 `scaffold`。仍需创意调整时使用 `prompt`；输入、输出和失败路径稳定并经过验证后切换到 `scaffold`，把固定操作交给脚本。

两种 skill 形态可以随项目成熟度切换，但同一角色只能有一种留在 agent 的 discovery roots。另一种必须归档到目录外，切换状态写回 `NOTES.md`，然后开启新会话。这样既保留架构判断的自由度，也避免每轮用 prompt 重新执行已经固化的机械流程。

## 有状态的渐进式仓库架构

py2rs 不是靠一次长提示词完成迁移，而是把迁移过程变成一个有状态、可继续、可审查、可回滚的仓库工作流。AI 每一轮都应该读取这些持久状态，而不是依赖聊天记忆。

- `mission`：记录为什么要重写、成功标准是什么、哪些行为和约束绝不能丢。
- `resources`：保存 source-of-truth docs、现有测试、依赖源码 snapshot、协议说明和可信参考，避免 AI 凭印象重写。
- `notes`：记录用户偏好，包括重写力度和框架画像，以及项目约束和临时观察。
- `records`：记录非显然决策、踩坑、行为差异、依赖取舍和审核结论，让后续会话能继承经验。
- `manifest` / 清单：记录每个迁移单元的状态、owner、目标 owner、验证命令、回滚路径和必需审核门。它是重写进度的控制面。
- crate 侦察：按能力搜索，用 Context7 定向核对 API/features，再沿 Cargo dependencies 找到实际能力 owner，避免因高层 API 不匹配就直接造轮子。
- 依赖对齐：先应用已记录的重写/框架偏好，再按能力判断 Python 依赖、Rust crate、compatibility adapter 或手写实现如何覆盖同一行为。
- bootstrap：在迁移业务逻辑前，先证明选定 seam 能跑通参数、返回值、错误、日志、测试和回滚路径。
- review evidence：每个单元通过 R0 行为一致性和必要的 R1-R6 审核后，才从“已实现”推进到“已验证”或“可提升”。

这套架构的意义是让迁移在任何时刻都保持可运行、可测试、可回滚。即使换一个 AI 会话，也能通过仓库里的 mission、records、manifest 和 reviews 接着做，而不是重新猜项目状态。

### 初始化偏好与依赖引入时机

这次的初始化架构把用户意图和迁移状态分开管理：先记录总体重写策略和相关框架偏好，同时记录 crate 侦察采用 agent、manual 还是 disabled，以及 crates.io 代理。长期偏好写入 `NOTES.md`；单元 owner、验证命令和回滚路径继续由 manifest 管理。

初始化阶段不预装尚未证明需要的 crate。agent 侦察在独立上下文中产出精简证据，manual 模式允许熟悉 Rust 生态的用户自行提供。为了节省 token 也可以关闭侦察，但 py2rs 会明确提示用户需要自行检索 crates.io、docs.rs 和 feature/dependency 路径。依赖对齐完成后才加入并锁定真正需要的 crate。

详细的模式生命周期和操作步骤分别见 [`架构`](docs/architecture.zh.md#项目-skill-脚手架) 与 [`用法`](docs/usage.zh.md#切换项目-skill-模式)。

## 最终代码会是什么样

使用这套 skills 迁移 Python 到 Rust 后，第一阶段的 Rust 代码目标不是逐行翻译 Python，也不是立刻写出最优雅、最 idiomatic 的 Rust 风格。它的目标更窄，也更重要：得到一个严格行为一致的 Rust 版本，并配套覆盖面极广的完整测试。

也就是说，迁移后的 Rust 代码首先应该证明：

- 对外行为和原 Python 版本一致。
- 边界情况、错误路径、fixture 和回归用例被测试覆盖。
- 每个迁移单元都有 review evidence，而不是只靠“看起来对”。

完成 py 到 rs 的行为迁移后，建议再给 AI 一个独立 goal：

```text
按照rust社区的标准建立完整的文档
```

如果之后还有精力，再让 AI 按 Rust 社区惯例做风格与结构优化。这个阶段应该建立在行为测试已经稳定的基础上，并且优化后重新运行行为一致性审核和完整测试。

如果你只是想先把 skills 装进 Codex 或 Claude，见 [`docs/installation.zh.md`](docs/installation.zh.md)。教程包含“让 AI 安装”的提示词、两种 discovery 目录、Context7 配置，以及 macOS/Linux 和 Windows 手动安装命令。

## 核心 Skills

- [`py2rs`](skills/py2rs/SKILL.md)：总重写纪律和路由。
- [`py2rs-runtime`](skills/py2rs-runtime/SKILL.md)：重写偏好、控制面、manifest、状态机、shards 和粒度。
- [`py2rs-crate-recon`](skills/py2rs-crate-recon/SKILL.md)：fresh-context 能力搜索、Context7 文档核对和 Cargo feature/dependency 证据。
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
