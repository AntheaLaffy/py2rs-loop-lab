# 安装教程

[English version](installation.md)

这份教程面向只想先把 skills 用起来的人。最省事的方式是让 AI 安装；手动安装也很简单，但要知道要复制哪些目录。

先说明：`py2rs-loop-lab` 不是可以直接套到任意项目的通用重写包。直接安装这些 skills 适合学习、参考和启动项目专属设计。真正开始重写前，仍然应该让 AI 读取你的真实项目，再创建项目专属 rewrite skills。

## 推荐安装哪些

最小起步集合：

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`

需要更严格审核时，再安装：

- `skills/py2rs-review-r1-rust-style`
- `skills/py2rs-review-r2-error-tracing`
- `skills/py2rs-review-r3-io-concurrency`
- `skills/py2rs-review-r4-algo-complexity`
- `skills/py2rs-review-r5-architecture`
- `skills/py2rs-review-r6-ergonomics`

`skills/practices/*` 是具体项目实践示例，只有在研究这些案例时才需要安装。

## 方式 A：让 AI 安装

把下面这段话发给 Codex 或支持 Skills 的 AI：

```text
请从 GitHub 仓库 https://github.com/AntheaLaffy/py2rs-loop-lab 安装这些 Codex skills 到 $CODEX_HOME/skills；如果没有设置 $CODEX_HOME，就安装到默认的 ~/.codex/skills：

- skills/py2rs
- skills/py2rs-runtime
- skills/py2rs-dep-align
- skills/py2rs-env-bootstrap
- skills/py2rs-review-r0-behavior

如果你有 skill-installer，请使用它；否则请下载仓库并复制这些目录。安装完成后告诉我哪些 skills 已安装，以及下一轮如何触发。
```

如果你想一次安装完整审核门，把 R1-R6 也加到这段话里。

## 方式 B：手动安装

先下载仓库：

```bash
git clone https://github.com/AntheaLaffy/py2rs-loop-lab.git
cd py2rs-loop-lab
```

如果你不会用 Git，可以在 GitHub 页面点击 `Code` -> `Download ZIP`，解压后进入解压出来的 `py2rs-loop-lab` 文件夹。

### macOS / Linux

在仓库根目录运行：

```bash
dest="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$dest"

cp -R skills/py2rs "$dest/"
cp -R skills/py2rs-runtime "$dest/"
cp -R skills/py2rs-dep-align "$dest/"
cp -R skills/py2rs-env-bootstrap "$dest/"
cp -R skills/py2rs-review-r0-behavior "$dest/"
```

可选：继续安装完整 R1-R6 审核门：

```bash
cp -R skills/py2rs-review-r1-rust-style "$dest/"
cp -R skills/py2rs-review-r2-error-tracing "$dest/"
cp -R skills/py2rs-review-r3-io-concurrency "$dest/"
cp -R skills/py2rs-review-r4-algo-complexity "$dest/"
cp -R skills/py2rs-review-r5-architecture "$dest/"
cp -R skills/py2rs-review-r6-ergonomics "$dest/"
```

验证：

```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills/py2rs/SKILL.md"
```

### Windows PowerShell

在仓库根目录运行：

```powershell
$dest = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $HOME ".codex\skills" }
New-Item -ItemType Directory -Force $dest | Out-Null

Copy-Item -Recurse -Force .\skills\py2rs $dest
Copy-Item -Recurse -Force .\skills\py2rs-runtime $dest
Copy-Item -Recurse -Force .\skills\py2rs-dep-align $dest
Copy-Item -Recurse -Force .\skills\py2rs-env-bootstrap $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r0-behavior $dest
```

可选：继续安装完整 R1-R6 审核门：

```powershell
Copy-Item -Recurse -Force .\skills\py2rs-review-r1-rust-style $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r2-error-tracing $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r3-io-concurrency $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r4-algo-complexity $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r5-architecture $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r6-ergonomics $dest
```

验证：

```powershell
Test-Path (Join-Path $dest "py2rs\SKILL.md")
```

如果输出 `True`，说明至少 `py2rs` 已放到正确位置。

## 安装后怎么用

重新打开 Codex，或开启新对话，让系统重新加载 skills。然后在你的真实项目仓库里说：

```text
请使用 py2rs-loop-lab 的思路研究当前项目，并为这个项目设计项目专属 rewrite skills。先不要改代码，先给我迁移边界、manifest/control plane 和 review gates 的建议。
```

不要一上来就说“直接把 Python 改成 Rust”。更稳的起步方式是先让 AI 建立项目事实、选择 seam、定义回滚路径和审核门。
