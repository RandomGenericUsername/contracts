---
id: REQ-006
title: "Ship the cli-invocation-contract package"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: cli-invocation-contract
  bmad: none
worktree: .worktrees/req-006/
branch: ticket/REQ-006-cli-invocation-contract
---

# Ship the cli-invocation-contract package

## Requirement

The `contracts` repo SHALL own the runtime ↔ CLI invocation contract as versioned data plus a
stdlib-only conformance kit (spine **AD-4**, slice **S0a**):

- `invocation-contract.json` at the repo root pins, per CLI (`csg`, `weg`, `itr`): binary name,
  argv template, required env keys + the adapter-injected overrides, required artifacts,
  exit-code semantics, and default timeout. Every literal comes from `S1` §1.3–1.5 and §2.2 —
  none is re-derived here.
- `src/cli_invocation_contract/` is a distribution `cli-invocation-contract` (import package
  `cli_invocation_contract`) exposing `CONTRACT_VERSION`, `load(path=None)`, `get(cli)`, and
  exactly two conformance assertions in `cli_invocation_contract.testkit`:
  `assert_consumer_invocation(...)` and `assert_cli_writes_artifacts(...)`.
- The package is stdlib-only at runtime; `pytest` is the only dev dependency; the existing event
  contract toolchain (`gen/`, `schemas/`, `Makefile`) is untouched.

Source: spine **AD-4** (`ARCHITECTURE-SPINE.md` lines 132–136); slice **S0a**
(`SLICES.md` lines 37–101); evidence report `S1-runtime-cli-addressing.md` §1.3–1.5, §2.2.

## Acceptance

- [ ] `invocation-contract.json` carries `contract_version: 1` and one record per CLI with the
  five contract fields (`argv`, `env`, `artifacts`, `exit_codes`, `timeout`) plus `binary`;
  values match S1 §1.3–1.5, §2.2 (verified by `tests/test_record.py`).
  Verify: `uv run pytest tests/test_record.py -q` → exit 0.
- [ ] `CONTRACT_VERSION` is the release version (`0.1.0`, equal to the `v0.1.0` tag per AD-11),
  `DATA_VERSION` is the JSON shape version (`1`), and `load()` exposes the data:
  `sorted(load()) == ['csg', 'itr', 'weg']` with the five contract fields per record.
  Verify: `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION, load; c=load(); assert sorted(c)==['csg','itr','weg']; assert all({'argv','env','artifacts','exit_codes','timeout'} <= set(v) for v in c.values()); print(CONTRACT_VERSION, DATA_VERSION)"` → `0.1.0 1`.
- [ ] `cli_invocation_contract.testkit` exposes exactly two public assertions and imports no
  pytest (nor any third-party module).
  Verify: `uv run python -c "import cli_invocation_contract.testkit as t; print(t.__all__)"` → `['assert_cli_writes_artifacts', 'assert_consumer_invocation']`.
- [ ] Tests cover record completeness for all three CLIs, loader/get behavior (unknown CLI raises),
  a positive fake-CLI artifact run, and a negative missing-artifact rejection.
  Verify: `uv run pytest -q` → exit 0.
- [ ] `uv build` produces `dist/cli_invocation_contract-0.1.0-*.whl` and `.tar.gz`; the wheel
  carries `cli_invocation_contract/invocation-contract.json` as package data.
  Verify: `uv build && unzip -l dist/cli_invocation_contract-0.1.0-*.whl | grep invocation-contract.json`.
- [ ] `openspec validate cli-invocation-contract --strict` exits 0.
- [ ] `README.md` and `AGENTS.md` §2 name **both** seams (AGS event contract + runtime ↔ CLI
  invocation contract), and state that the contract is versioned and pinned at the same tag by
  the Python runtime and all three CLIs.
  Verify: `rg -n "invocation" README.md AGENTS.md` → both files name the seam.

## Out of scope

- Tagging `contracts v0.1.0` and publishing release artifacts (AD-9 release ritual; orchestrator
  decision after review — this ticket stops at a green branch).
- Moving the two boundary specs (`interface-contract-test`, `container-adapter-env-contract`)
  into this repo (S0a step 6, second half): they live in `dotfiles-v3` and moving them would
  touch a second repo; handled in S0b.
- Any `dotfiles-v3` edit, any consumer pin bump, any real-CLI invocation in tests.
