# Changelog

Notable changes to the `contracts` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release versions follow the git tags
(AD-9/AD-11): for every release the tag, the `cli-invocation-contract` distribution version, and
`CONTRACT_VERSION` are the same value (`v0.3.0` ↔ `0.3.0` ↔ `CONTRACT_VERSION = "0.3.0"`).

## [Unreleased]

(nothing yet)

## [0.3.0] - 2026-10-26

Feature release: the standalone AGS app contract (ticket
[`REQ-009`](./tickets/REQ-009-ags-app-contract/ticket.md)) is now canonical source in this repo.
The invocation contract data is unchanged, so `DATA_VERSION` stays `2`; the distribution and
`CONTRACT_VERSION` move with the repo tag.

### Added

- Draft-07 schemas for the standalone AGS app program: the per-app identity/mode manifest
  (`schemas/ags-app-manifest.schema.json`, `app.manifest.json`), the dotfiles-v3 app list and
  ownership source (`schemas/ags-apps-install-list.schema.json`), the per-install program tag
  tuple (`schemas/program-tuple.schema.json`) and the runtime-owned per-app refresh result
  (`schemas/ags-app-refresh-result.schema.json`).
- The fixed `palette-refresh` request/response protocol in `ags-app-refresh.md`: the
  appearance-hash argument, one JSON-encoded string response on stdout exactly once,
  applied/deferred/failed semantics, the 5 s caller timeout, idempotency and
  state-preservation requirements.
- Positive/negative schema fixtures and `make schema-test`, wired into CI after `make test`.

### Changed

- `wallpaper.state` is documented as the progress/UI event only. It is not the
  palette-refresh trigger; the runtime invokes live apps through
  `palette-refresh` (AD-27).
- Added the `jsonschema` dev dependency for the schema fixture gate.

### Release

- Annotated tag `v0.3.0` on the merged release commit, with the wheel + sdist built from that
  commit, not from a working tree.
- `cli-invocation-contract` bumped `0.2.0` → `0.3.0`: `CONTRACT_VERSION = "0.3.0"` (equal to the
  `v0.3.0` tag without its `v`), `DATA_VERSION = 2` (invocation data shape unchanged). The AGS app
  schemas and protocol are repo-root sources at the tag; they are not part of the
  `cli-invocation-contract` distribution.

## [0.2.0] - 2026-10-21

Minor release: the `itr` record now pins the env key that selects the icon templates directory
(ticket [`REQ-008`](./tickets/REQ-008-itr-templates-dir-contract/ticket.md), OpenSpec change
`itr-templates-dir-contract`).

### Added

- `clis.itr.env` records `ICON_RENDERER__TEMPLATES__DIR`: listed in `required` and injected as
  the `{templates_dir}` placeholder, alongside the two existing path overrides. `itr` binds this
  key to `templates.dir` (env ranks above `settings.toml` and discovery), so the runtime can pass
  the directory it hashes into the icons entry key instead of letting the process resolve a
  different one. `csg` and `weg` are unchanged, and no CLI's `argv` or `artifacts` changed.

### Changed

- `invocation-contract.json` `contract_version` bumped `1` → `2`. The change is additive, but
  `load()` is version-strict, so a 0.1.x loader refuses a v2 document rather than silently
  ignoring the new key (see the versioning rule in `CONTRACT.md`).
- `cli-invocation-contract` bumped `0.1.0` → `0.2.0`: `CONTRACT_VERSION = "0.2.0"` (equal to the
  `v0.2.0` tag without its `v`), `DATA_VERSION = 2`.
- Moved the two boundary specs `interface-contract-test` and `container-adapter-env-contract`
  here from `dotfiles-v3/openspec/specs/` (`openspec/specs/<name>/spec.md`), content preserved
  verbatim with a provenance header (cli-tools-repos split, slice S0b; REQ-007).

### Release

- Annotated tag `v0.2.0` with the wheel + sdist built from the tag commit, not from a working
  tree.
- The Python runtime and the three CLIs (`csg`, `weg`, `itr`) re-pin this exact tag; the runtime
  additionally sets `ICON_RENDERER__TEMPLATES__DIR` from its resolved `templates_dir`.

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
