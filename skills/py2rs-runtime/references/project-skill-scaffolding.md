# Project Skill Scaffolding

Use this reference during repository initialization after project truth,
accepted seam, rewrite preferences, and state locations are stable.

Each project role has one active mode:

- `prompt`: keep the workflow adaptable while its architecture, branches, or
  ergonomics still need creative iteration.
- `scaffold`: use after the workflow has stabilized; scripts own deterministic
  mechanics and the skill body stays focused on schemas and decisions.

Modes are complementary over time, but never simultaneously active for the same
role. Keep the inactive counterpart outside every agent skill discovery root so
its description and instructions cannot leak into later contexts.

Put this machine-readable marker beside `SKILL.md` in both variants:

```json
{
  "schema_version": 1,
  "role": "dependency-bootstrap",
  "mode": "prompt",
  "validated": true,
  "validation_evidence": "tests/project_dependency_bootstrap"
}
```

The archived counterpart uses the same role and the other mode. Both variants
must use the same `name` in `SKILL.md` frontmatter. `validation_evidence` is a
relative path inside that variant and must exist; point it to the latest test or
forward-test artifact that qualifies the variant for activation.

## Classify Before Generating

Keep architecture and judgment in high-freedom skills. Examples include seam
selection, migration-unit boundaries, rollback design, domain ownership, and
deciding which py2rs ideas fit the project. A code scaffold cannot make these
decisions safely.

Turn stable operational loops into project-specific script-backed skills.
Examples include registry evidence collection, manifest state transitions,
review-batch accumulation and flush rules, fixture orchestration, per-unit
verdict validation, canonical dependency lookup, Cargo build-queue enforcement,
promotion checks, and repeatable bridge/bootstrap commands.

Do not generate a script merely because a command appeared once. Scaffold when
the inputs, outputs, failure modes, and completion criterion are stable enough
to test.

## Generate The Project Skills

Use the available skill creator and its initialization script. Create skills in
the project's existing agent-skill directory. If none exists, use the current
agent environment's project-local convention and record that location.

Generate only the roles the project needs, commonly:

- coordinator: project facts, manifest/shard order, unit selection, behavior
  verification seam, review cadence, canonical shared dependencies, Cargo build scheduling,
  and routing
- crate reconnaissance/dependency bootstrap: deterministic evidence collectors
- unit writer: seam-specific behavior fixture commands, state updates, implementation
  boundary, and adding writer-verified units to the open review batch
- review gates: R0 behavior parity, batch-scoped
  checks, per-unit verdicts, and report validation

For every generated skill:

- keep `SKILL.md` focused on ordered steps, data structures, invariants,
  completion criteria, and recovery branches;
- put repeatable parsing, querying, state mutation, and command orchestration in
  `scripts/`;
- use `references/` only for project schemas or conditional detail;
- make scripts accept explicit inputs and produce machine-readable output;
- make batch scripts reject invalid cadence values, promotion with open review
  requirements, and units whose writer verification has not passed;
- reject missing legacy public seams, Rust-only or circular evidence, and any
  attempt to replace failed parity with compile or Rust-to-Rust evidence;
- default generated writer workflows to serial execution even for sharded
  manifests;
- if coordinated parallel mode is enabled, make scripts enforce coordinator-only
  shared dependency/Cargo file changes, worker path ownership, and a serialized
  build queue;
- reject `/tmp` and agent-private paths as canonical dependency inputs;
- prevent scripts from silently advancing manifest state after failed checks.

## Switch Modes Safely

Record the selected mode, active path, and archive path in `NOTES.md`. Use the
bundled switcher in dry-run mode first. Run it from the project root so returned
`NOTES.md` paths stay project-relative. This example uses the Claude install;
set `PY2RS_RUNTIME` to the actual installed skill directory for another agent:

```bash
PY2RS_RUNTIME="${PY2RS_RUNTIME:-$HOME/.claude/skills/py2rs-runtime}"
python "$PY2RS_RUNTIME/scripts/switch_skill_mode.py" \
  --role dependency-bootstrap \
  --current-mode prompt \
  --target-mode scaffold \
  --active .claude/skills/project-dependency-bootstrap \
  --archive-root .py2rs/skill-archive \
  --discovery-root .claude/skills
```

Repeat `--discovery-root` for every skill root visible to any agent that will
work on the project, including both Claude and Codex roots when both are used.
The switcher scans all declared roots for the same skill name and refuses to
switch while another discoverable copy exists.

After validating the plan, add `--apply`. The switcher validates the role/mode
markers and validation evidence, requires the active and archived variants to
be on one filesystem, refuses overwrites, uses a lock, and validates rollback
postconditions if activation fails.

Successful file switching leaves `.switch-journal.json` in phase
`switched_pending_notes`. Apply the returned `notes_update` to `NOTES.md`, then
acknowledge that durable update:

```bash
python "$PY2RS_RUNTIME/scripts/switch_skill_mode.py" \
  --role dependency-bootstrap \
  --archive-root .py2rs/skill-archive \
  --ack-notes
```

The acknowledgement clears the journal. Do not start the fresh session while
`notes_update_required` remains unresolved.

If a command reports `manual_recovery_required`, do not delete the journal or
move another skill into the active path. Inspect its recorded paths and markers:

- `prepared`: verify whether the active variant ever moved.
- `current_archived`: restore the recorded current variant only when the active
  path is absent and the target archive is still intact.
- `manual_recovery_required`: resolve unexpected occupants or missing paths,
  then prove one active variant and one archived counterpart before clearing it.

Rerun dry-run after recovery. A pre-existing lock or journal always blocks a new
switch instead of being overwritten.

Always start a fresh agent session after switching. Moving a skill prevents
future discovery but cannot remove instructions already loaded in the current
context.

## Validate The Scaffold

Run every generated script on representative project fixtures. Validate the
skill structure, then forward-test each operational skill in a fresh context.
The scaffold is complete only when another session can execute the fixed loop
from project state without rebuilding its mechanics in prompt tokens.

If project architecture is still changing, defer the affected operational
skill and record why. Do not freeze a speculative workflow into code.
