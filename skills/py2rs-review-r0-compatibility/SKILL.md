---
name: py2rs-review-r0-compatibility
description: "R0 Rust compatibility gate for one py2rs migration unit or closed review batch. Use when the manifest deliberately selects rust_compatibility instead of Python/legacy behavior parity at a deep framework or runtime boundary, and the target is an already verified canonical Rust contract. Reviews application-level tensor, codec, model-loading, artifact, schema, and error compatibility without editing production code or claiming legacy parity."
---

# R0 Rust Compatibility Review

Use this gate only when the manifest changes the verification oracle before
implementation:

```text
new Rust unit is compatible with verified canonical Rust contracts
```

This is not a weaker behavior pass. It is a declared boundary where reproducing
legacy framework internals would require rewriting an out-of-scope ecosystem,
while application-level compatibility can be specified and tested.

## Eligibility

Require all of these:

- `verification_policy.mode: rust_compatibility` was recorded before writer work;
- the rationale explains why exact legacy parity would require reproducing
  external framework semantics outside the rewrite scope;
- `oracle.kind` is `verified_rust_contract` and names evidence for each upstream
  Rust unit or contract;
- required application contracts and explicitly excluded legacy internals are
  listed;
- the public protocol change, if any, was approved by the user.

If any item is missing, do not review or pass. Return to the coordinator. A
failed behavior-parity review cannot silently switch the unit into this mode.

## Required Context

- project mission, architecture, manifest, records and verification policy
- selected unit or closed review batch
- verified Rust oracle units, contract docs and report paths
- new implementation and accepted application seam
- model artifacts, codecs, fixtures and integration workflows
- rollback route

Do not rely on the writer's summary when durable code or evidence can answer.

## Review Focus

Check only declared application contracts, including when relevant:

- tensor shape, dtype, layout, rank, device and serialization expectations;
- codec encode/decode and persisted artifact formats;
- model checkpoint/config/tokenizer/weight loading;
- adapter inputs, outputs, ordering and error projection;
- cache keys, schema versions and cross-unit handoff;
- end-to-end application startup or inference-chain smoke behavior;
- numeric tolerances or output quality thresholds explicitly named by policy.

Do not compare Python framework internal tensor representations, kernels,
allocators, graph layout, or other excluded internals merely because they differ.

## Workflow

1. Confirm eligibility and the unit ids in scope.
2. Resolve every oracle to verified Rust evidence; reject circular or unverified
   targets.
3. Build a compatibility matrix from required contracts, exclusions, normal
   cases, boundaries, corrupt artifacts and recovery paths.
4. Run existing application-level fixtures or add non-production reviewer tests
   when repository convention permits.
5. Verify model loading, codec and tensor handoffs through the accepted Rust
   seam, including cross-unit integration for a batch.
6. Report findings first, ordered by severity and grounded in files, contracts,
   fixtures or commands.
7. Give each unit `pass`, `pass-with-followups` or `fail` and save the report.

## Boundaries

- Do not edit production code.
- Do not claim Python/legacy behavior parity.
- Do not use compilation alone as compatibility evidence.
- Do not accept the new unit as its own oracle.
- Do not weaken a user-visible application contract unless the manifest records
  the approved protocol change.
- Do not mark units `verified`; the coordinator updates state after all required
  reports pass.

## Report

Use the project convention or:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-rust-compatibility.md
```

Include:

- verification policy and switch rationale
- canonical Rust oracle ids and evidence
- included unit ids and per-unit verdicts
- required and excluded contracts
- compatibility matrix and results
- checks run and artifact identifiers
- findings ordered by severity
- residual risk and promotion decision

## Exit Criteria

- Every oracle is independently verified and non-circular.
- Application-level compatibility evidence is repeatable.
- Model loading, codec and tensor boundary failures are findings, not excluded
  as framework internals.
- The report clearly says compatibility passed or failed without implying legacy
  parity.
