# Usage

## Use The Core Skills

Install or reference:

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`
- optional R1-R6 review skills

## Initialize A Rewrite

1. Read project truth: mission, architecture, resources, manifest, records and tests.
2. Identify the accepted seam: CLI, service facade, Tauri command facade, Python module, library API, pipeline stage or another project-specific boundary.
3. Ask the user for the granularity profile.
4. Create or reuse a manifest/control-plane.
5. Snapshot first-layer direct Python dependency sources if storage, license and policy allow it.
6. Define rollback routes before implementation.

## Work One Unit

1. Select one migration unit from the manifest.
2. Run dependency alignment if the unit touches third-party behavior, native code, broad package APIs, fixtures or unclear rollback.
3. Add or identify behavior fixtures.
4. Implement behind the accepted seam.
5. Mark the unit `reimplemented`, not `verified`.
6. Run R0 behavior review.
7. Run additional review roles required by the manifest.
8. Promote only after review evidence exists.

## Build Project-Specific Skills

py2rs should usually produce project-specific skills once the project shows stable patterns.

Good project skills encode:

- accepted architecture seam
- source-of-truth docs
- manifest location and status model
- dependency expansion policy
- writer workflow
- review roles
- promotion rules
- non-negotiable project constraints

See the practice skills for examples.
