---
name: py2rs-crate-recon
description: Research Rust crate candidates and their feature/dependency paths before py2rs dependency alignment. Use when a migration unit may introduce or hand-write Rust behavior, when a named crate appears too high-level, when crate reuse is being rejected, or when py2rs needs registry evidence before allowing implementation.
---

# py2rs Crate Reconnaissance

Run this skill in a fresh context before `py2rs-dep-align`. Produce ecosystem
evidence only: do not write production code or change the target project's
Cargo manifests and lockfiles.

## Preconditions

Read the selected unit, public behavior, fixtures, accepted seam, dependency
source records, and `NOTES.md` rewrite preferences. The coordinator invokes
this skill only when `rewrite_preferences.crate_reconnaissance.mode` is `agent`.
For `manual` or `disabled`, follow the rules in `py2rs-dep-align` instead.

Name the observable capabilities before searching. Search for capabilities such
as "WAV decode to PCM samples", not only Python package names.

## Step 1: Search The Registry

For every capability, run:

```bash
python scripts/crate_recon.py search \
  --capability "WAV decode to PCM samples" \
  --query "wav" \
  --query "wav decoder" \
  --query "audio pcm decoder" \
  --candidate rodio \
  --limit 3 \
  --output <evidence-dir>
```

Pass `--proxy` from `NOTES.md` when configured. Use one to three short registry
queries per capability, then shortlist the three most relevant candidates from
their combined results. User-named candidates are mandatory and do not consume
the three-candidate limit. The collector records each named candidate as
`required_inspection`; its later `cargo info` result supplies registry evidence
even when free-text search ranking omits it.

If fresh registry access fails, the collector tries the configured proxy and
then the local Cargo cache. Also inspect project lockfiles and project-controlled
source snapshots. If this evidence cannot support a candidate decision, mark
the report `blocked`; do not infer that no crate exists.

Completion criterion: each public capability has registry or explicitly local
search evidence, and every user-named candidate is queued for mandatory inspect.

## Step 2: Read Candidate Documentation

Use Context7 first. Resolve each shortlisted or user-named crate, then query
only for the required capability, relevant Cargo features, lower-level APIs,
and official examples. Context7 is documentation evidence; it does not replace
registry discovery or Cargo's resolved graph.

If Context7 is not installed or configured in the current environment, bootstrap
it using the available `find-docs` setup instructions and the current agent's
tool convention. Request user/network approval when required. Missing tooling by
itself is not a reason to skip candidate documentation.

Fall back to docs.rs and downloaded crate source only when Context7 setup or the
service fails, or when Context7 does not index the candidate. Record the
provider, library/version, focused queries, source references, and exact fallback
reason. Never treat unavailable documentation tooling as evidence that the
capability or crate does not exist.

Completion criterion: every inspected candidate has focused API/feature
documentation evidence or an explicit, evidence-preserving fallback.

## Step 3: Inspect Capability Ownership

Inspect each shortlisted or user-named candidate with only the relevant
features enabled:

```bash
python scripts/crate_recon.py inspect \
  --crate rodio@0.22.2 \
  --features wav \
  --no-default-features \
  --output <evidence-dir>
```

Read `cargo-info.txt`, `inspect.json`, `cargo-metadata.json`, and
`cargo-tree.txt`. For an umbrella crate, follow feature/dependency paths until
the crate that owns the required decoder, parser, codec, data structure, or
runtime capability is identified. A high-level public API is not a valid reason
to reject its lower-layer dependencies.

Stop at the capability owner. Do not expand unrelated transitive dependencies
or reconstruct the entire Rust ecosystem.

Completion criterion: every candidate records the selected features, actual
dependency paths, covered capability, semantic gaps, and fit decision.

## Step 4: Decide The Gate

Use these fit decisions based on the API the target implementation will call,
not whether a crate is marketed as high-level:

- `direct`: the target implementation can call the candidate's public API to
  cover the capability, even if that crate delegates internally.
- `backend`: the target implementation should call a feature-selected lower
  dependency instead of the umbrella candidate API.
- `adapter`: candidate/backend plus a narrow adapter covers it.
- `reference_only`: useful source or semantic reference under a hand-written profile.
- `reject`: evidence-backed technical, license, security, build, portability,
  maintenance, or explicit user-policy rejection.

Under `standard` or `ecosystem_first`, permit a hand-written implementation only
after every plausible candidate and relevant backend has an evidence-backed
rejection. Under `handwritten_first` or `domain_from_scratch`, record discovered
crates but allow `reference_only` or policy rejection without pretending that
the crate is technically incapable.

## Durable Report

Use the project convention or write:

```text
rewrite-records/dependencies/<unit>-crate-recon.yaml
```

Record:

```yaml
unit: example_unit
profile: standard
status: complete # complete | policy_rejected | blocked
capabilities:
  - id: wav_decode
    queries: ["WAV decode to PCM samples"]
    candidates:
      - crate: example
        version: "1.2.3"
        features: [wav]
        documentation:
          provider: context7 # context7 | docs_rs | crate_source
          library_id: /example/example
          queries: ["WAV decoding feature and lower-level sample API"]
          fallback_reason: null
        dependency_paths:
          - [example, container_backend]
          - [example, sample_decoder]
        coverage: "WAV container and PCM sample decoding"
        gaps: ["legacy error projection"]
        decision: adapter
raw_evidence: rewrite-evidence/crates/example_unit/
handwritten_gate:
  allowed: false
  reason: "A maintained backend covers decoding."
```

Keep raw collector output in the project's evidence directory; if none exists,
use `rewrite-evidence/crates/<unit>/`. The dependency aligner consumes the YAML
summary and loads raw files only when challenging a conclusion.

## Exit Criteria

- Every capability and user-named candidate is accounted for.
- Context7 was bootstrapped and used for focused documentation lookup when
  available; otherwise the provider and fallback reason are explicit.
- Feature-selected dependency paths reach the actual capability owner.
- Rejections cite evidence; API-level impressions are not evidence.
- The report status and hand-written gate match the project's rewrite profile.
- Target project manifests, lockfiles, and production code are unchanged.
