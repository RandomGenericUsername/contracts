# contracts

Canonical contract sources for the AGS platform, one repo.

1. **AGS event contract** (`org.dotfiles.Events`) — `event-contract.json` + `event-contract.xml`
   and the bindings generated from them.
2. **Runtime ↔ CLI invocation contract** — `invocation-contract.json` and the
   `cli-invocation-contract` package (`cli_invocation_contract`).
3. **Standalone AGS app contract** — `schemas/ags-app-manifest.schema.json`,
   `schemas/ags-apps-install-list.schema.json`, `schemas/program-tuple.schema.json`,
   `schemas/ags-app-refresh-result.schema.json`, and the fixed `palette-refresh`
   protocol in `ags-app-refresh.md`. Draft-07 schemas with positive/negative
   fixtures (`tests/test_ags_app_contract.py`), consumed by `dotfiles-v3`,
   `dotfiles-provision`, `dotfiles-runtime`, `ags-platform`, and every app repo.

The event contract is the single source of truth for the runtime ↔ AGS event seam. It is
consumed by:

- the Python runtime (`dotfiles-v3` / `src/runtime`), and
- `ags-platform` (the event-contract client).

The invocation contract is the single source of truth for how the runtime invokes the three
installed consoles (`csg`, `weg`, `itr`): argv template, required env keys and injected
overrides, required artifacts, exit-code semantics, default timeout. It is **versioned**, and the
Python runtime plus **all three CLIs** pin the **same `contracts` tag** — not merely a compatible
range — so one record and one conformance kit serve four consumers. A contract change is a new
tag that every consumer re-pins; literals are not duplicated in consumer tests.

## Contract files

- `event-contract.json` — the machine-readable event contract.
- `event-contract.xml` — the D-Bus interface definition.
- `invocation-contract.json` — the runtime ↔ CLI invocation contract, one record per CLI.
- `CONTRACT.md` — field-by-field reference for the invocation contract, citing the evidence
  report (`S1`) section for every value.
- `schemas/ags-app-manifest.schema.json` — the per-app identity, mode and
  unsaved-state manifest (`app.manifest.json`).
- `schemas/ags-apps-install-list.schema.json` — the single dotfiles-v3 app list
  and ownership source (`apps.yaml`).
- `schemas/program-tuple.schema.json` — the one `ags-platform` / `contracts` /
  `dotfiles-assets` tag tuple per install.
- `schemas/ags-app-refresh-result.schema.json` — the runtime-owned per-app
  refresh result/log record.
- `ags-app-refresh.md` — the fixed `palette-refresh` request/response protocol.

## The `cli-invocation-contract` package

- `src/cli_invocation_contract/__init__.py` — `CONTRACT_VERSION`, `load(path=None)`, `get(cli)`;
  stdlib only, no runtime dependencies.
- `src/cli_invocation_contract/testkit.py` — exactly two assertions:
  `assert_consumer_invocation(record, cli, argv, env)` and
  `assert_cli_writes_artifacts(record, cli, run, cwd)`.
- `tests/` — record completeness, loader behaviour, and positive/negative kit paths against a
  fake CLI (never a real binary).
- `Makefile` — `make sync` (uv), `make test` (event-contract unittest + schema fixtures +
  pytest), `make schema-test` (AGS app contract fixtures only), `make build` (sdist + wheel).
  The wheel carries `invocation-contract.json` as package data, so `load()` works from an
  installed tag.

## Tooling here

- **BMAD-METHOD:** `.agents/skills/` (`bmad`, `bmad-build`, `bmad-architecture`, `bmad-product-brief`, `bmad-spec`).
- **OpenSpec:** `openspec/` (spec-driven). Start: `/opsx-propose "your idea"`.
- **Tickets:** `tickets/` (see `INDEX.md`, `LIFECYCLE.md`); route with `/triage`.

## Status

The event and invocation seams are live. The AGS event contract and generated bindings landed in REQ-001–REQ-005; the
invocation contract is REQ-006, released as `v0.1.0` (AD-9) on `48cf3cf`. `v0.2.0` ships
`cli-invocation-contract` 0.2.0 (`CONTRACT_VERSION` `0.2.0`, `DATA_VERSION` `2`), adding the
`itr` record's `ICON_RENDERER__TEMPLATES__DIR` env key (REQ-008) — see `CHANGELOG.md` and the
GitHub Releases. The standalone AGS app contract (manifest, install list, program tuple,
refresh result and `palette-refresh` protocol) is REQ-009; it is schema/protocol source only,
with no runtime or app code in this repo.
