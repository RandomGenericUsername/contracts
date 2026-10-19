# cli-invocation-contract

## Why

The runtime ↔ CLI seam is real but unpinned: the runtime invokes three installed consoles and
asserts argv/env/artifact literals that today live only in per-adapter tests. Spine **AD-4**
moves those literals into this repo as versioned data plus a conformance kit, so the runtime and
all three CLIs test one record instead of each other's copies.

Evidence: the runtime invokes the installed consoles by literal binary name and never imports the
CLI packages. `S1-runtime-cli-addressing.md` §0 row 1 and §1.1 (`rg` over `src/runtime` → exit 1,
no matches; subprocess entry points `csg_adapter.py:304`, `weg_adapter.py:364`,
`itr_adapter.py:423`).
Verify: from the `dotfiles-v3` `clirsplit` worktree,
`rg -n '^(from|import) (color_scheme_generator|wallpaper_effects_generator|icon_templates_renderer)' src/runtime --glob '*.py'` → exit 1.

Evidence: the literals are duplicated in consumer tests. `S1` §6.1 quotes the per-adapter
assertions for env keys, absent `-o/--output` flags, and the `--format` pair count
(`tests/unit/test_csg_adapter.py:128-135`, `tests/unit/test_weg_adapter.py:114-119`,
`tests/unit/test_itr_adapter.py:126-132`).
Verify: `sed -n '775,818p' docs/investigation/S1-runtime-cli-addressing.md`.

Evidence: the exact argv/env/artifact/timeout values are established by execution, not recalled.
`S1` §1.3 (argv), §1.5 (env allowlist + per-adapter overrides), §1.6 (timeouts), §2.2 (required
artifacts and the "exit 0 + artifacts" success rule), with the recording-probe log as the
observed side.
Verify: `sed -n '118,271p' docs/investigation/S1-runtime-cli-addressing.md`.

Evidence: AD-4 fixes the package names and the two-assertion kit, and requires this repo to gain
a `pyproject.toml` (it has none today).
Verify: `sed -n '132,136p' <planning-repo>/architecture/architecture-cli-repos-2026-10-19/ARCHITECTURE-SPINE.md`;
`ls pyproject.toml` → exit 2 before this change.

## What Changes

- Add `invocation-contract.json` at the repo root: `contract_version` plus one record per CLI
  (`csg`, `weg`, `itr`). Each record carries `binary`, an argv template with documented
  placeholders, the required env keys and the adapter-injected overrides, the required artifacts
  (exact filenames for `csg`; recursive suffixes for `weg`/`itr`), the exit-code semantics, and the
  default timeout. Values are transcribed from `S1` §1.3–1.6 and §2.2.
- Add the `cli-invocation-contract` distribution (`src/cli_invocation_contract/`, hatchling,
  version `0.1.0`, zero runtime dependencies): `CONTRACT_VERSION`, `load(path=None)`, `get(cli)`,
  and `cli_invocation_contract.testkit` with exactly two public assertions —
  `assert_consumer_invocation(record, cli, argv, env)` and
  `assert_cli_writes_artifacts(record, cli, run, cwd)`.
- Add `tests/` covering record completeness, loader/get (including the unknown-CLI error), and
  the kit's positive and negative paths against a fake CLI, with no real binary invocation.
- Add `CONTRACT.md` documenting every field with its S1 citation.
- Add `sync` / `test` / `build` Makefile verbs (existing targets unchanged; `test` runs the event
  contract unittest suite and then pytest).
- Update `README.md` and `AGENTS.md` §2 so the charter names both seams and the same-tag pin rule.

## Capabilities

- **New Capabilities:** `cli-invocation-contract` — versioned invocation data plus a conformance
  kit that consumers execute instead of duplicating literals.
- **Modified Capabilities:** none. The AGS event contract (`org.dotfiles.Events`) is untouched.

## Non-goals (out of scope)

- **Not** tagging `contracts v0.1.0`, publishing a GitHub Release, or bumping any consumer pin.
  S0a's release step (AD-9) runs after review; S0b consumes the tag.
- **Not** moving the two boundary specs (`openspec/specs/interface-contract-test`,
  `openspec/specs/container-adapter-env-contract`) into this repo. They still live in
  `dotfiles-v3`; moving them is a cross-repo edit (S0b).
- **Not** a runtime or CLI change: no `dotfiles-v3` file is touched, and no test shells out to a
  real `csg`/`weg`/`itr`.
- **Not** a schema validator, dataclass model, or generated binding. The record is the source; the
  loader returns plain mappings and refuses an unknown `contract_version`.
- **Not** lifecycle semantics beyond the observed ones: no version handshake, no capability probe,
  no new argv flags. `S1` §4 records that none exists today.

## Impact

- New: `invocation-contract.json`, `CONTRACT.md`, `pyproject.toml`, `src/cli_invocation_contract/`
  (`__init__.py`, `testkit.py`), `tests/`, `uv.lock`.
- Modified: `Makefile` (adds `sync`, `test` gains the pytest leg, `build`), `README.md`,
  `AGENTS.md` §2, `.github/workflows/drift.yml` (installs `uv` so the new `make test` leg runs).
- Unchanged: `event-contract.{json,xml,md}`, `gen/`, `schemas/`, `generated/`, `tickets/REQ-001…005`.
