# Installation

[中文版本](installation.zh.md)

This guide is for people who want to start using the skills quickly. The easiest route is to ask AI to install them. Manual installation is also straightforward once you know which directories to copy.

First, a boundary: `py2rs-loop-lab` is not a drop-in rewrite pack for any project. Installing these skills directly is useful for study, reference and bootstrapping project-specific design. Before a real rewrite starts, ask AI to read your actual project and create project-specific rewrite skills.

## What To Install

Recommended starter set:

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`

For stricter review coverage, also install:

- `skills/py2rs-review-r1-rust-style`
- `skills/py2rs-review-r2-error-tracing`
- `skills/py2rs-review-r3-io-concurrency`
- `skills/py2rs-review-r4-algo-complexity`
- `skills/py2rs-review-r5-architecture`
- `skills/py2rs-review-r6-ergonomics`

The `skills/practices/*` directories are concrete project examples. Install them only when studying those examples.

## Option A: Ask AI To Install

Send this to Codex or another AI environment that supports Skills:

```text
Please install these Codex skills from https://github.com/AntheaLaffy/py2rs-loop-lab into $CODEX_HOME/skills. If $CODEX_HOME is not set, use the default ~/.codex/skills:

- skills/py2rs
- skills/py2rs-runtime
- skills/py2rs-dep-align
- skills/py2rs-env-bootstrap
- skills/py2rs-review-r0-behavior

If skill-installer is available, use it. Otherwise, download the repository and copy these directories. After installation, tell me which skills were installed and how to trigger them on the next turn.
```

To install all review gates at once, add R1-R6 to that prompt.

## Option B: Manual Install

Download the repository first:

```bash
git clone https://github.com/AntheaLaffy/py2rs-loop-lab.git
cd py2rs-loop-lab
```

If you do not use Git, open the GitHub page, click `Code` -> `Download ZIP`, unzip it, then open the extracted `py2rs-loop-lab` folder.

### macOS / Linux

Run this from the repository root:

```bash
dest="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$dest"

cp -R skills/py2rs "$dest/"
cp -R skills/py2rs-runtime "$dest/"
cp -R skills/py2rs-dep-align "$dest/"
cp -R skills/py2rs-env-bootstrap "$dest/"
cp -R skills/py2rs-review-r0-behavior "$dest/"
```

Optional: install the full R1-R6 review gates too:

```bash
cp -R skills/py2rs-review-r1-rust-style "$dest/"
cp -R skills/py2rs-review-r2-error-tracing "$dest/"
cp -R skills/py2rs-review-r3-io-concurrency "$dest/"
cp -R skills/py2rs-review-r4-algo-complexity "$dest/"
cp -R skills/py2rs-review-r5-architecture "$dest/"
cp -R skills/py2rs-review-r6-ergonomics "$dest/"
```

Verify:

```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills/py2rs/SKILL.md"
```

### Windows PowerShell

Run this from the repository root:

```powershell
$dest = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $HOME ".codex\skills" }
New-Item -ItemType Directory -Force $dest | Out-Null

Copy-Item -Recurse -Force .\skills\py2rs $dest
Copy-Item -Recurse -Force .\skills\py2rs-runtime $dest
Copy-Item -Recurse -Force .\skills\py2rs-dep-align $dest
Copy-Item -Recurse -Force .\skills\py2rs-env-bootstrap $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r0-behavior $dest
```

Optional: install the full R1-R6 review gates too:

```powershell
Copy-Item -Recurse -Force .\skills\py2rs-review-r1-rust-style $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r2-error-tracing $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r3-io-concurrency $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r4-algo-complexity $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r5-architecture $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r6-ergonomics $dest
```

Verify:

```powershell
Test-Path (Join-Path $dest "py2rs\SKILL.md")
```

If it prints `True`, at least the `py2rs` skill is in the right place.

## After Installation

Restart Codex or start a new conversation so the skills are loaded. Then, inside your real project repository, say:

```text
Use the py2rs-loop-lab approach to study this project and design project-specific rewrite skills for it. Do not change code yet. First give me recommendations for migration boundaries, the manifest/control plane and review gates.
```

Do not start with "convert Python to Rust directly." A safer start is to establish project facts, choose an accepted seam, define rollback routes and decide the review gates.
