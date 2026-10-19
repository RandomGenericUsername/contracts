# symmetric-drift-gate

## Why

AD-6 makes the canonical contract the single source and requires a **regenerate-and-diff gate** that fails CI on drift — and it must be **symmetric**: the contract is checked against **both** the generated bindings and the runtime tables, not one direction. This repo has the contract (REQ-001) and the generator (REQ-002) but **no drift gate at all**: nothing fails when a source change lands without a regenerated commit, and nothing catches a generated artifact that gained a key the contract does not have.

Evidence: the `Makefile` has `generate` but no drift/diff target. `grep -n drift Makefile` → no output.
Verify: `grep -n drift Makefile` → (no output).

Evidence: no CI exists. `ls .github` → no such directory.
Verify: `ls .github` → `ls: cannot access '.github': No such file or directory`.

Evidence: the current generator cross-checks the XML and JSON **names** only, so a schema property that the contract does not declare is never rejected. `gen/generate.py` lines 137–142 compare `set(events_iface["methods"]) != set(doc["methods"])` etc.; the emitted schema's per-topic `properties` are copied from the contract, so an **extra** property hand-added to `generated/events.schema.json` would survive a plain regenerate-and-diff only if it were not committed — but a committed extra property passes every existing check because there is no reverse check.
Verify: `sed -n '137,142p' gen/generate.py`.

Evidence: the only existing coverage test asserts contract → schema (one direction): `gen/test_generate.py` `test_json_schema_covers_the_contract` checks required keys and enums of expected topics but never asserts that the schema has **no** key absent from the contract.
Verify: `sed -n '106,135p' gen/test_generate.py`.

Evidence: spine `ARCHITECTURE-SPINE.md` AD-6 (lines 92–96): "A **regenerate-and-diff gate** fails CI on drift, and it is **symmetric**: the contract is checked against **both** the TS and the runtime tables, not one direction."
Verify: `sed -n '92,96p' <planning-repo>/architecture/architecture-ags-platform-2026-10-09/ARCHITECTURE-SPINE.md`.

Evidence: spine AD-19 (lines 170–174) requires the per-repo gate to run in CI; AD-23 (lines 194–202) names `contracts` as running "the codegen regenerate-and-diff + schema validation" on GitHub Actions.
Verify: `sed -n '170,174p;194,202p' <planning-repo>/architecture/architecture-ags-platform-2026-10-09/ARCHITECTURE-SPINE.md`.

## What Changes

- Add `gen/check_symmetry.py` — a stdlib-only checker that compares the **committed** generated artifacts against the canonical contract in **both** directions:
  - `event-contract.json` ↔ `generated/events.schema.json`: per-topic key sets, required/optional split, scalar types, and enums must be equal (every contract key present in the schema **and** every schema key present in the contract; every enum equal, in order).
  - `event-contract.xml` ↔ `generated/contract.py` and `generated/contract.ts`: the wire method/signal tables must equal the XML argument lists.
  - `event-contract.json` ↔ `generated/contract.py` and `generated/contract.ts`: identity/versioning/delivery/validation/job-lease constants, topic→producer tables, and per-topic payload fields (names, optionality, types, enums) must equal the contract.
  - A clearly named **hook** for the cross-repo runtime-tables leg, owned by REQ-004; it is not faked here.
- Add `make contracts-drift` (alias `make drift`): run the symmetric content check, regenerate with `gen/generate.py`, then `git diff --exit-code generated/` (plus an untracked-file guard) so a source change without a regenerated commit fails.
- Add negative tests (`gen/test_symmetry.py`) proving the gate can fail: a hand-edited generated file, a contract key added without regeneration, and an extra schema key absent from the contract are each rejected.
- Add `.github/workflows/drift.yml` running the gate on push and pull request.

## Capabilities

- **New Capabilities:** `event-contract` — the symmetric drift gate is a new observable behaviour of the contract capability (additive to REQ-002's generation).
- **Modified Capabilities:** none.

## Non-goals

- **Not** the cross-repo **runtime tables** leg (the runtime's hand-embedded wire tables/validation schemas in `dotfiles-v3`). That check is only meaningful after REQ-004 repoints the runtime; this change leaves a named `TODO(REQ-004)` hook and does not fake it.
- **Not** repointing consumers or deleting embedded duplicates — REQ-004.
- **Not** changing the contract — REQ-005 owns the known `wallpaper.state` drift.
- **Not** the structural `schemas/*.schema.json` state artifacts (REQ-001) — only the event wire schema `generated/events.schema.json` is in scope.
- **Not** a TypeScript toolchain: `gen/check_symmetry.py` parses the generated `.ts` as text; no `node_modules`, no compile step.

## Impact

- New: `gen/check_symmetry.py`, `gen/test_symmetry.py`, `.github/workflows/drift.yml`, `openspec/changes/symmetric-drift-gate/**`.
- Modified: `Makefile` (add `check-symmetry`, `contracts-drift`, `drift`; update `help`).
- No contract file, no generator, and no generated artifact changes; `schemas/` is untouched.
