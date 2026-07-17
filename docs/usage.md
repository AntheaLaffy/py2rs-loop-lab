# Usage

[中文版本](usage.zh.md)

This repository is not meant to be dropped into an arbitrary codebase and run as-is. Use AI to study it, borrow the architecture, and create project-specific rewrite skills.

## Install Or Reference Skills

Keep this repository as a reference when designing project-specific skills. Copying the skills directly can be useful for study or bootstrapping, but a real rewrite should encode its own project facts before the loop starts.

If you want to install them into Codex first, see the [`Installation`](installation.md) guide. The recommended path is to give the guide's prompt to AI; for manual installs, the destination is `$CODEX_HOME/skills`, defaulting to `~/.codex/skills`.

Start with:

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`

Add R1-R6 review skills according to risk.

## Required Order

1. Establish the project repository and read its facts.
2. Ask AI to extract the relevant py2rs ideas for that project.
3. Decide which ideas fit and which do not.
4. Create project-specific skills from those decisions.
5. Initialize the rewrite workspace.
6. Start the loop only after the manifest/control plane and review policy exist.

## Initialize A Rewrite Workspace

1. Read project truth: mission, architecture, resources, manifest, records and tests.
2. Identify the accepted seam: CLI, service facade, Tauri command facade, Python module, library API, pipeline stage or another project-specific boundary.
3. Write or adapt project-specific skills for coordination, dependency bootstrap, writer work and review gates.
4. Ask the user for the granularity profile.
5. Create or reuse a manifest/control plane.
6. Snapshot first-layer direct Python dependency sources when storage, license and policy allow it.
7. Define rollback routes before implementation.

The initialization should preserve the [`teach`](../skills/foundations/teach/SKILL.md)-style progression model: mission first, resources before memory, records for non-obvious lessons, notes for preferences and small units with feedback.

## Work One Unit

1. Select one migration unit from the manifest.
2. Run dependency alignment if the unit touches third-party behavior, native code, broad package APIs, fixtures or unclear rollback.
3. Add or identify behavior fixtures.
4. Implement behind the accepted seam.
5. Mark the unit `reimplemented`, not `verified`.
6. Run R0 behavior review.
7. Run additional review roles required by the manifest.
8. Promote only after review evidence exists.

## Build Project-Specific Skills First

py2rs should usually lead to project-specific skills once stable project patterns are visible.

Good project skills encode:

- accepted architecture seam
- source-of-truth docs
- manifest location and state model
- dependency expansion policy
- writer workflow
- review roles
- promotion rules
- non-negotiable project constraints

The practice skills in this repository show two different outcomes: a Tauri backend facade rewrite and a Python dependency-heavy rewrite.
