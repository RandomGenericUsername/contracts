# Changelog

Notable changes to the `contracts` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release versions follow the git tags
(AD-9/AD-11): for `v0.1.0`, the tag, the `cli-invocation-contract` distribution version, and
`CONTRACT_VERSION` are the same value.

## [Unreleased]

### Changed

- Moved the two boundary specs `interface-contract-test` and `container-adapter-env-contract`
  here from `dotfiles-v3/openspec/specs/` (`openspec/specs/<name>/spec.md`), content preserved
  verbatim with a provenance header (cli-tools-repos split, slice S0b).

## [0.1.0] - 2026-10-19

First release: the `cli-invocation-contract` distribution, tagged `v0.1.0` on merge commit
[`48cf3cf`](https://github.com/RandomGenericUsername/contracts/commit/48cf3cf)
(`feat(REQ-006): cli-invocation-contract package + conformance kit`).

### Added

- `invocation-contract.json` — the runtime ↔ CLI invocation contract (spine AD-4), one record
  per CLI (`csg`, `weg`, `itr`) under `clis`, each carrying `binary`, `argv`, `env`
  (required keys plus adapter-injected overrides), `artifacts`, `exit_codes`, and `timeout`.
  `CONTRACT.md` cites the evidence report (`S1`) section for every value.
- `cli-invocation-contract` 0.1.0 — the import package `cli_invocation_contract`
  (`src/cli_invocation_contract/`), standard library only, no runtime dependencies:
  - `CONTRACT_VERSION = "0.1.0"` — the release version, equal to the tag without its leading
    `v` and to the distribution version.
  - `DATA_VERSION = 1` — the version of the `invocation-contract.json` data shape; a document
    declaring a different shape fails loudly instead of being misread.
  - `load(path=None)` returns `{cli: record}` for the three CLIs; `get(cli)` returns one
    record and raises `UnknownCliError` for an unknown CLI.
  - `cli_invocation_contract.testkit` — exactly two conformance assertions,
    `assert_consumer_invocation(record, cli, argv, env)` and
    `assert_cli_writes_artifacts(record, cli, run, cwd)`; no pytest import, so it runs in a
    consumer's own runner.
- Wheel package data `cli_invocation_contract/invocation-contract.json`, so `load()` resolves
  the same records from an installed distribution.

### Release

- Annotated tag `v0.1.0` points at `48cf3cf` (`git rev-parse v0.1.0^{}` →
  `48cf3cfed4b192b241505789409c4f282921c896`).
- GitHub Release assets (sdist + wheel) are built from the tag commit, not from a working tree.
- The Python runtime and the three CLIs (`csg`, `weg`, `itr`) pin this exact tag and run the
  kit instead of duplicating argv/env/artifact literals in their own tests.
