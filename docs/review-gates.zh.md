# R0-R6 审核门

[English version](review-gates.md)

py2rs 把写代码和审核分开。writer 可以准备代码和 fixtures，但 review evidence 必须来自独立角色。每个单元先在 manifest 记录用于 R0 behavior 的 legacy public seam。

独立审核不必在每个 writer 环节后立即启动。manifest 的 `review_policy` 可以选择每单元审核、每 N 个单元总审核，或等小项目的当前 scope 全部写完再总审。用户未选择时默认每 3 个单元一批。

## R0 Behavior

Skill: [`py2rs-review-r0-behavior`](../skills/py2rs-review-r0-behavior/SKILL.md)

目标：证明重写实现保留了选定的公共行为。

R0 behavior 通过项目接受的 seam 检查 public inputs、outputs、errors、side effects、persistence 和 user-visible payloads。批量审核还要检查单元间集成行为。深层推理只要穿透该 seam，就必须覆盖 tensor handoff、codec、model artifact 和模型加载。默认精确比较；模型或数值容差必须来自已有公共契约或实现前明确批准。

## R1 Rust Style

Skill: [`py2rs-review-r1-rust-style`](../skills/py2rs-review-r1-rust-style/SKILL.md)

目标：检查 Rust 模块形态和可维护性。

R1 关注 ownership、visibility、warnings、clippy 风格问题、测试结构，以及未来维护者是否能理解这段 Rust 代码。

## R2 Error Tracing

Skill: [`py2rs-review-r2-error-tracing`](../skills/py2rs-review-r2-error-tracing/SKILL.md)

目标：让故障可诊断，同时不泄露敏感信息。

R2 检查 structured errors、context propagation、logs、trace IDs、redaction，以及 source errors 是否保留了足够调试信息。

## R3 IO Concurrency

Skill: [`py2rs-review-r3-io-concurrency`](../skills/py2rs-review-r3-io-concurrency/SKILL.md)

目标：检查 IO 周围的 runtime 和 operational behavior。

R3 覆盖 blocking IO、async boundaries、cancellation、retries、concurrency limits、repeated calls 和 runtime nesting 风险。

## R4 Algorithm Complexity

Skill: [`py2rs-review-r4-algo-complexity`](../skills/py2rs-review-r4-algo-complexity/SKILL.md)

目标：让算法修改有证据。

R4 只在有复杂度分析、理论依据或 benchmark 证据时支持算法改变。它不是在行为证明前提前优化的许可。

## R5 Architecture

Skill: [`py2rs-review-r5-architecture`](../skills/py2rs-review-r5-architecture/SKILL.md)

目标：检查数据 ownership 和 API 边界。

R5 审查 ownership、canonical storage、data structures、module depth，以及选定 seam 是否仍然干净。

## R6 Ergonomics

Skill: [`py2rs-review-r6-ergonomics`](../skills/py2rs-review-r6-ergonomics/SKILL.md)

目标：从用户和运维视角检查迁移。

R6 检查 CLI/help text、recovery、batching、cache behavior、error readability、configuration、accessibility 和 operational workflow。

## Gate Selection

R0 behavior 是 promotion 前的必选门。R1-R6 根据风险、manifest policy 和 granularity profile 选择。如果当前 seam 无法证明 parity，就重切单元、外移 seam 或保留 legacy owner。

## Batch Rules

- 每个单元进入 open batch 前必须通过 writer verification，并保持 `reimplemented`。
- 达到配置数量、scope 完成或准备 promotion 时必须收批；高风险边界是否提前收批由 `risk_override` 决定，默认提前。
- 一个审核周期先为每个单元跑 R0 behavior，再跑其它角色的并集。
- 每个角色可以为整批写一份报告，但必须列出 unit ids 和逐单元 verdict；只有 manifest 没要求该角色的单元可以使用 `not_required`。
- 一个单元失败不会抹掉其它单元的有效证据；只提升所需 verdict 全部通过的单元。
- 修复失败单元后，按影响范围重跑 R0 和被修复影响的其它门禁。
