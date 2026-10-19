# build-contract-generator

## Why

The event contract is the single source of truth (REQ-001; spine AD-6), but this repo emits nothing from it yet: every consumer hand-embeds constants, and the only generator that exists is a stale prototype that reads its own private copy. AD-6 reverses the prior no-codegen decision (AD-44) precisely because hand-embedded constants already drifted.

Evidence: the canonical files are present at the repo root — `event-contract.xml` (wire) and `event-contract.json` (semantics) — imported byte-identical in REQ-001 (branch `ticket/REQ-001-import-canonical-contract`, commit `cb8337f`).
Verify: `ls event-contract.xml event-contract.json` → both exist.

Evidence: the prototype reads its own private source, not the canonical contract. `spikes/codegen/gen.py` line 31 is `SOURCE = HERE / "contract.json"`, and its source `spikes/codegen/contract.json` lists the dead topic `speedtest.finished`, which the canonical contract supersedes with `speedtest.state`.
Verify: `grep -n 'contract.json' dotfiles-v3/spikes/codegen/gen.py` → line 31; `grep -c speedtest.finished event-contract.json` → 0.

Evidence: spine `ARCHITECTURE-SPINE.md` AD-6 (lines 92–96): "`contracts/event-contract.xml` … and `contracts/event-contract.json` … are the **only** source. A generator emits Python + TS bindings … This supersedes AD-44".
Verify: `sed -n '92,96p' <planning-repo>/architecture/architecture-ags-platform-2026-10-09/ARCHITECTURE-SPINE.md`.

## What Changes

- Add `gen/generate.py` (Python, stdlib only) that reads the canonical `event-contract.xml` (methods/signals) and `event-contract.json` (topics/delivery/versioning) and emits, deterministically (sorted keys, trailing newline):
  - `generated/contract.py` — constants + TypedDicts + wire method/signal tables + per-topic payload types.
  - `generated/contract.ts` — constants + types + per-topic payload interfaces.
  - `generated/events.schema.json` — JSON Schema (draft 2020-12) with per-topic required/optional/enum/type definitions and the signal/method/topic envelopes.
- Add `gen/test_generate.py` asserting output coverage (6 topics, 9 hub methods, 5 signals, the job interface, the schema's required keys + enums) and byte-identical reruns.
- Wire the `Makefile` `generate` target to the generator.
- No private `contract.json` copy survives in `gen/`.

## Capabilities

- **New Capabilities:** `event-contract` — the generated bindings are a new observable behaviour of the contract capability.
- **Modified Capabilities:** none.

## Non-goals

- **Not** the structural `schemas/*.schema.json` (state artifacts) — `schemas/` stays exactly as imported in REQ-001. The event wire schema `generated/events.schema.json` **is** in scope.
- **Not** the CI regenerate-and-diff gate — that is REQ-003 (`symmetric-drift-gate`).
- **Not** repointing consumers or deleting their embedded duplicates — that is REQ-004.
- **Not** changing the contract itself — REQ-005 owns the known drift (`wallpaper.state`).
- **Not** a TypeScript toolchain: no `node_modules`, no compile step in this change.

## Impact

- New: `gen/generate.py`, `gen/test_generate.py`, `generated/contract.py`, `generated/contract.ts`, `generated/events.schema.json`.
- Modified: `Makefile` (`generate` target only).
- No consumer is touched; no contract file is modified; `schemas/` is untouched.
