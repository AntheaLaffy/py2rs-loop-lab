# 用法

[English version](usage.md)

## 安装或参考 Skills

把 `skills/` 下需要的目录复制到 agent 的 skill 目录，或把这个仓库作为设计项目专属 skills 的参考。

建议从这些开始：

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`

再根据风险加入 R1-R6 审核 skills。

## 初始化重写

1. 读取项目事实：mission、architecture、resources、manifest、records 和 tests。
2. 识别接受的 seam：CLI、service facade、Tauri command facade、Python module、library API、pipeline stage 或其它项目专属边界。
3. 询问用户 granularity profile。
4. 创建或复用 manifest/control plane。
5. 在存储、license 和项目政策允许时，snapshot 第一层直接 Python 依赖源码。
6. 在实现前定义回滚路径。

## 推进一个单元

1. 从 manifest 选择一个迁移单元。
2. 如果单元触及第三方行为、native code、宽泛 package API、fixtures 或不清楚的 rollback，先做依赖对齐。
3. 添加或识别 behavior fixtures。
4. 在接受的 seam 后实现。
5. 把单元标为 `reimplemented`，不是 `verified`。
6. 运行 R0 行为审核。
7. 运行 manifest 要求的其它 review roles。
8. 只有在 review evidence 存在后才能 promotion。

## 构建项目专属 Skills

当项目模式稳定后，py2rs 通常应该发展出项目专属 skills。

好的项目 skill 会编码：

- 接受的架构 seam。
- source-of-truth docs。
- manifest 位置和状态模型。
- 依赖展开策略。
- writer workflow。
- review roles。
- promotion rules。
- 不可违反的项目约束。

本仓库的实践 skills 展示了两个不同结果：Tauri backend facade 重写，以及依赖复杂的 Python 项目重写。
