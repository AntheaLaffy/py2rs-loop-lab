# Usage

[中文版本](usage.zh.md)

This repository is not meant to be dropped into an arbitrary codebase and run as-is. Use AI to study it, borrow the architecture, and create project-specific rewrite skills.

## Install Or Reference Skills

Keep this repository as a reference when designing project-specific skills. Copying the skills directly can be useful for study or bootstrapping, but a real rewrite should encode its own project facts before the loop starts.

If you want to install them into Codex or Claude first, see the [`Installation`](installation.md) guide. The recommended path is to give the guide's prompt to AI. Codex uses `$CODEX_HOME/skills`, defaulting to `~/.codex/skills`; Claude Code uses `~/.claude/skills`.

Start with:

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-crate-recon`
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
4. Ask for the overall rewrite strategy, relevant framework categories, crate reconnaissance mode and crates.io proxy. Store them in `NOTES.md`; default to `standard` plus agent reconnaissance.
5. Ask for granularity and identify one independently comparable legacy public
   seam per unit. Record exact comparison by default and any public-contract
   model or numeric tolerances before writer work.
6. Ask how many reimplemented units share one review: `per_unit`, every N units,
   or `end_of_scope`. Default to a three-unit batch.
7. Create or reuse the control plane and record manifest partitioning separately
   from execution policy. Large projects may be sharded; execution defaults serial.
8. Create a canonical shared dependency registry when units share capabilities;
   `/tmp` cannot be a durable path.
9. Snapshot first-layer direct Python dependency sources when policy allows it.
10. Define rollback routes before implementation.

Preference capture does not add crates or change a lockfile. Reconnaissance may be `agent`, `manual` or `disabled`; disabling saves tokens but requires the user to understand or manually research the Rust ecosystem. Dependencies are added and locked only after reconnaissance policy and dependency alignment are satisfied.

`agent` mode requires working Context7 access. If it is missing, bootstrap it through the [Installation](installation.md#configure-context7) guide; missing tooling is not evidence that no suitable crate exists. `disabled` skips independent comparative ecosystem research, not minimum official-source due diligence for a dependency the unit actually selects, and it cannot support a claim of complete ecosystem coverage.

The initialization should preserve the [`teach`](../skills/foundations/teach/SKILL.md)-style progression model: mission first, resources before memory, records for non-obvious lessons, notes for preferences and small units with feedback.

Once the seam and state model are stable, scaffold fixed project workflows as
script-backed skills. Keep architectural judgment in reasoning skills; move
repeatable registry queries, state transitions, review-batch flushing, fixture
orchestration and per-unit report validation into tested code so later sessions consume schemas instead of prompt
mechanics. Select `prompt` or `scaffold` per role, keep only the selected variant
in skill discovery roots, and archive the other outside them. Start a fresh
agent session after a mode switch.

## Switch Project Skill Modes

A new role starts in `prompt` mode. Before switching, both variants use the same
skill name, contain a correct `.py2rs-skill-variant.json`, and point
`validation_evidence` to a real validation file inside each variant. This
example uses Claude project paths; Codex users set `PY2RS_RUNTIME` and the
active/discovery paths to their `.codex` equivalents.

Dry-run from the project root and list every discovery root actually used by
the project:

```bash
PY2RS_RUNTIME="${PY2RS_RUNTIME:-$HOME/.claude/skills/py2rs-runtime}"
switcher="$PY2RS_RUNTIME/scripts/switch_skill_mode.py"

python "$switcher" \
  --role dependency-bootstrap \
  --current-mode prompt \
  --target-mode scaffold \
  --active .claude/skills/project-dependency-bootstrap \
  --archive-root .py2rs/skill-archive \
  --discovery-root .claude/skills \
  --discovery-root .codex/skills
```

After the output reports `ready`, rerun the same arguments with `--apply`. The
script moves the variants and leaves a `switched_pending_notes` journal. Apply
the returned `notes_update` to `NOTES.md` immediately, then acknowledge the
durable state:

```bash
python "$switcher" \
  --role dependency-bootstrap \
  --archive-root .py2rs/skill-archive \
  --ack-notes
```

Start a fresh session only after `notes_acknowledged`. If the script reports
`manual_recovery_required`, preserve the journal and recover from its recorded
paths and phase; do not overwrite the active path with another copy. See
[Architecture](architecture.md#mode-lifecycle) for the full invariants.

## Work One Write/Review Batch

1. Select one migration unit from the manifest.
2. Satisfy the `NOTES.md` crate reconnaissance mode: fresh agent report, manual evidence, or an acknowledged disabled warning.
3. Apply reconnaissance/preferences and check canonical shared dependencies.
4. Confirm `behavior_verification` names the legacy public seam and comparison policy.
5. Add Python/Rust behavior fixtures for that seam.
6. Implement behind the accepted seam.
7. Run writer verification; when it passes, mark the unit `reimplemented` and
   add it to the open review batch, not `verified`.
8. If cadence is not reached and no early flush applies, select the next unit.
9. Flush at N units, scope completion or before promotion; apply `risk_override`
   at high-risk boundaries.
10. Run R0 behavior for every unit first, then additional roles; every report
   gives per-unit verdicts.
11. Promote a unit only after all of its own review evidence exists.

## Manifest Partitioning And Execution

Sharding is a control-plane tool for large projects, not a parallel switch.
Prefer stable shards traversed serially by one writer so project context and
Cargo artifacts are reused without competing builds or dependency drift.

Start multiple writers only under explicit `coordinated_parallel`. The
coordinator exclusively owns the root manifest, shared dependency registry,
shared Cargo files and build queue. Workers edit assigned shard paths and wait
for coordinator decisions on shared dependency changes.

## Build Project-Specific Skills First

py2rs should usually lead to project-specific skills once stable project patterns are visible.

Good project skills encode:

- accepted architecture seam
- source-of-truth docs
- manifest location and state model
- rewrite-depth and framework preference profile
- crate reconnaissance and registry proxy policy
- per-role `prompt`/`scaffold` selection and off-discovery archive location
- dependency expansion policy
- behavior verification seam, comparison policy and fixture evidence
- manifest partitioning, serial-first execution, canonical dependency registry and Cargo build policy
- writer workflow
- review roles, review cadence and batch flush rules
- promotion rules
- non-negotiable project constraints

The practice skills in this repository show two different outcomes: a Tauri backend facade rewrite and a Python dependency-heavy rewrite.
