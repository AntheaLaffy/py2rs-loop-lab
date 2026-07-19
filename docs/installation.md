# Installation

[中文版本](installation.zh.md)

This guide is for people who want to start using the skills quickly. The easiest route is to ask AI to install them. Manual installation is also straightforward after choosing the Codex or Claude discovery directory.

First, a boundary: `py2rs-loop-lab` is not a drop-in rewrite pack for any project. Installing these skills directly is useful for study, reference and bootstrapping project-specific design. Before a real rewrite starts, ask AI to read your actual project and create project-specific rewrite skills.

## What To Install

Recommended starter set:

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-crate-recon`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`
- `skills/py2rs-review-r0-compatibility`

For stricter review coverage, also install:

- `skills/py2rs-review-r1-rust-style`
- `skills/py2rs-review-r2-error-tracing`
- `skills/py2rs-review-r3-io-concurrency`
- `skills/py2rs-review-r4-algo-complexity`
- `skills/py2rs-review-r5-architecture`
- `skills/py2rs-review-r6-ergonomics`

The `skills/practices/*` directories are concrete project examples. Install them only when studying those examples.

## Option A: Ask AI To Install

Send this to Codex, Claude or another AI environment that supports Skills:

```text
Please install these skills from https://github.com/AntheaLaffy/py2rs-loop-lab. For Codex, use $CODEX_HOME/skills, defaulting to ~/.codex/skills. For Claude Code, use ~/.claude/skills:

- skills/py2rs
- skills/py2rs-runtime
- skills/py2rs-crate-recon
- skills/py2rs-dep-align
- skills/py2rs-env-bootstrap
- skills/py2rs-review-r0-behavior
- skills/py2rs-review-r0-compatibility

If skill-installer is available, use it. Otherwise, download the repository and copy these directories. Do not leave different versions under multiple discovery roots. Verify each installed directory, then tell me how to trigger the skills on the next turn.
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
# Codex:
dest="${CODEX_HOME:-$HOME/.codex}/skills"
# For Claude Code instead:
# dest="$HOME/.claude/skills"
mkdir -p "$dest"

cp -R skills/py2rs "$dest/"
cp -R skills/py2rs-runtime "$dest/"
cp -R skills/py2rs-crate-recon "$dest/"
cp -R skills/py2rs-dep-align "$dest/"
cp -R skills/py2rs-env-bootstrap "$dest/"
cp -R skills/py2rs-review-r0-behavior "$dest/"
cp -R skills/py2rs-review-r0-compatibility "$dest/"
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
ls "$dest/py2rs/SKILL.md"
ls "$dest/py2rs-crate-recon/SKILL.md"
```

### Windows PowerShell

Run this from the repository root:

```powershell
# Codex:
$dest = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $HOME ".codex\skills" }
# For Claude Code instead:
# $dest = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force $dest | Out-Null

Copy-Item -Recurse -Force .\skills\py2rs $dest
Copy-Item -Recurse -Force .\skills\py2rs-runtime $dest
Copy-Item -Recurse -Force .\skills\py2rs-crate-recon $dest
Copy-Item -Recurse -Force .\skills\py2rs-dep-align $dest
Copy-Item -Recurse -Force .\skills\py2rs-env-bootstrap $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r0-behavior $dest
Copy-Item -Recurse -Force .\skills\py2rs-review-r0-compatibility $dest
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

## Configure Context7

`py2rs-crate-recon` uses Context7 by default for focused candidate API,
feature and official-example lookup. If Context7 is unavailable, bootstrap it
instead of falling back to model memory or claiming that no suitable crate
exists.

With Node.js and npm available, run:

```bash
npx ctx7 setup
```

Choose `CLI + Skills`, then select every agent that will use Context7. Complete
device authorization if requested. Do not store Context7 credentials or proxy
credentials in project `NOTES.md`.

Verify library resolution:

```bash
npx ctx7 library rodio "WAV decoding feature and PCM sample API" --json
```

The command should return a Context7 library ID. If the project needs a proxy
for registry or Context7 access, record a non-secret URL or environment-variable
reference as a project preference in `NOTES.md`. A local port such as `7890` is
a project instance, not a py2rs global default.

## After Installation

Restart Codex/Claude or start a new conversation so the skills and Context7 rules are loaded. Then, inside your real project repository, say:

```text
Use the py2rs-loop-lab approach to study this project and design project-specific rewrite skills for it. Do not change code yet. First recommend migration boundaries, behavior-parity or verified-Rust compatibility oracles, manifest partitioning, serial-first execution policy, control plane, review roles and cadence.
```

Do not start with "convert Python to Rust directly." Establish project facts, choose the seam/oracle, define rollback and canonical dependencies, and let the user decide review cadence. Execution remains serial by default even when the manifest is sharded.
