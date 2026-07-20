# Rewrite Preferences

Use this reference only when initializing a py2rs workspace or revising the user's
rewrite/dependency preferences. `NOTES.md` is their single source of truth. The
manifest owns migration state and granularity; per-unit records own applied decisions.

## Contents

- [Stage 1: Rewrite Strategy](#stage-1-rewrite-strategy)
- [Stage 2: Relevant Framework Choices](#stage-2-relevant-framework-choices)
- [Crate Reconnaissance And Network](#crate-reconnaissance-and-network)
- [NOTES.md Schema](#notesmd-schema)
- [Handoff To Dependency Alignment](#handoff-to-dependency-alignment)

## Stage 1: Rewrite Strategy

Explain the tradeoff briefly, then ask whether the user wants the standard
policy or wants to customize the rewrite depth.

- `standard`: default. Compare capability coverage and prefer a maintained crate
  or crate plus semantic-delta adapter; use a fixture-backed hand-written path
  when it is smaller, safer, or easier to roll back.
- `ecosystem_first`: maximize maintained crate reuse. Hand-write only project
  semantics and observed semantic gaps that existing crates cannot own.
- `handwritten_first`: prefer hand-written project and domain behavior when it
  can be bounded by fixtures. General infrastructure crates remain allowed.
- `domain_from_scratch`: do not reuse crates that own the project's domain
  algorithms, domain data structures, or Python-visible domain semantics.
  Implement that domain stack bottom-up, while still allowing Rust `std` and
  general infrastructure such as async runtimes, serialization, diagnostics,
  tracing, transport, and build tooling.
- `custom`: record capability-specific rules that do not fit another profile.

If the user does not know or declines customization, select `standard` with
`strategy.source: default`. Never treat `domain_from_scratch` as a ban on all
third-party crates unless the user adds that separate hard constraint.

## Stage 2: Relevant Framework Choices

Inspect the repository before asking. Ask only about categories that are already
present or are required by the accepted target architecture:

- async runtime and scheduling
- serialization, configuration, and wire formats
- error types, diagnostics, logging, and tracing
- numeric arrays, linear algebra, dataframes, and tensor representation
- model inference, deep-learning runtime, and hardware acceleration
- Web server/client and transport protocols
- desktop, native UI, or Web frontend integration
- database, persistence, and migration tooling
- CLI parsing, progress, and operator ergonomics

Names such as Tokio, Serde, thiserror, anyhow, miette, tracing, ndarray, Polars,
Arrow, and established Web/UI/ML frameworks are non-exhaustive prompts, not a
fixed recommendation matrix. Before offering candidates, inspect existing
project dependencies and verify current, maintained choices from official
sources. Existing runtime/framework choices are project facts; do not propose a
second async runtime or competing UI stack without a concrete reason.

For every relevant category, let the user choose a framework, mark one as
`auto`, require no dependency with `none`, or identify a dependency to avoid.
Do not ask about irrelevant categories. Group related questions so repository
initialization remains short.

When one broad category needs multiple constraints, use clear sub-capability
keys rather than overwriting a choice, for example `public_library_errors` and
`application_error_context`.

## Crate Reconnaissance And Network

Record how the project wants to pay for Rust ecosystem research:

- `agent`: default. Run `py2rs-crate-recon` in a fresh context and give only its
  summary to dependency alignment.
- `manual`: save agent tokens; the user supplies candidate, feature, dependency
  path, and rejection evidence before dependency alignment.
- `disabled`: skip ecosystem evidence. Before accepting this, warn: "Disabling
  crate reconnaissance removes py2rs' evidence that a maintained crate or
  transitive backend exists. Choose this only if you understand the Rust
  ecosystem or will manually search crates.io/docs.rs and dependency features."

For `disabled`, require a non-empty acknowledgement in `NOTES.md`. Do not infer
that no crate exists, and do not label the skip as completed research.

Registry connectivity is also a project usage preference. Record a non-secret
proxy URL or an `env:VARIABLE_NAME` reference. Never store credentials, tokens,
or a proxy URL containing user information in `NOTES.md`.

## NOTES.md Schema

Create or update one fenced YAML block under `## Py2rs Rewrite Preferences`:

```yaml
rewrite_preferences:
  version: 1
  strategy:
    profile: standard # standard | ecosystem_first | handwritten_first | domain_from_scratch | custom
    source: default # user | default
    common_infrastructure: allowed
  crate_reconnaissance:
    mode: agent # agent | manual | disabled
    source: default # user | default
    disabled_acknowledgement: null
  network:
    crates_io:
      proxy: none # none | env:VARIABLE_NAME | non-secret URL
      source: default # user | default
  project_skills:
    default_mode: prompt # prompt | scaffold
    archive_root: .py2rs/skill-archive
    roles:
      dependency_bootstrap:
        mode: scaffold
        active: .claude/skills/project-dependency-bootstrap
        archived: .py2rs/skill-archive/dependency-bootstrap/prompt
  frameworks:
    async_runtime:
      selection: auto # auto | none | crate/framework name
      strength: prefer # prefer | require | avoid
      reason: "No project-specific preference."
```

Omit capability categories that are not relevant. Use these semantics:

- `prefer`: use the selection when project evidence does not favor another path.
- `require`: treat the selection as a hard constraint; do not silently deviate.
- `avoid`: exclude the named selection. With `selection: none`, exclude the
  whole dependency category.
- `auto`: let dependency alignment choose later from project facts and current
  official sources.
- `crate_reconnaissance.mode: manual` requires user-supplied ecosystem evidence;
  `disabled` requires the warning acknowledgement but no report.
- A proxy is a runtime preference. Pass it to discovery commands without writing
  project `.cargo/config.toml` files.
- Only one mode of each project skill role may live in agent discovery roots.
  Archive the counterpart outside those roots, require role/mode markers on both
  variants, update this block from the switcher's output, and then start a fresh session.

Update this block in place when preferences change. Do not duplicate it in the
manifest and do not add dependencies during this interview.

## Handoff To Dependency Alignment

Initialization is complete when:

- the overall profile is explicit, including whether it came from the user or
  the default;
- every detected architecture-significant category is selected or marked
  `auto`;
- hard requirements and exclusions are unambiguous;
- crate reconnaissance mode, risk acknowledgement, and registry proxy are explicit;
- every project skill role has one active prompt/scaffold mode and an external archive path;
- `Cargo.toml` and lockfiles are unchanged by preference capture alone.

`py2rs-dep-align` later applies this profile to one seam or migration unit. A
per-unit dependency record must name the profile it applied and explain every
deviation.
