# Changelog

Notable changes to the `contracts` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release versions follow the git tags
(AD-9/AD-11): for every release the tag, the `cli-invocation-contract` distribution version, and
`CONTRACT_VERSION` are the same value (`v0.4.0` ↔ `0.4.0` ↔ `CONTRACT_VERSION = "0.4.0"`).

## [Unreleased]

(nothing yet)

## [0.6.0] - 2026-11-05

Minor release: split the panel border from the hairlines and make the layout metrics
TSX-owned (ticket [`REQ-014`](./tickets/REQ-014-skin-hairline-layout-ownership/ticket.md)).
The vocabulary grows from 23 to 24 tokens; the six manifest groups are unchanged.

### Added

- `shape.hairline-w` in `schemas/skin-token.schema.json`,
  `schemas/skin-manifest.schema.json` and `schemas/skin-json.schema.json` — a unitless
  numeric token rendered as `<n>px` in a CSS length position. `border-w` now owns only the
  outer panel/frame border; `hairline-w` owns the card tile, row action and badge hairlines.
  The row/cell has no border (the template uses `none`).
- Positive `skin-json` fixtures for `flat` and `paper`, alongside `glass`, so all three
  built-in token maps are validated directly.

### Changed

- `skins.md` documents the border ownership split in a new normative **"Border ownership and
  row geometry"** section and records the rendering consequence: the source `.settings-net` row
  has `border: none`, and the transparent-border workaround changed its measured height from
  `50px` to `54px`.
- `skins.md` strengthens the layout rule: `panel-width`, `bt-list-spacing`, `bar-row-height`
  and `chip-min` are consumed ONLY by widgets through `skinValue()`; templates MUST NOT expand
  them into CSS (`min-width`, `margin`, `min-height`). Layout metrics are TSX-owned; the tokens
  may still appear in `skin.json` for consumers.
- Built-in border values are documented and mirrored in the fixtures: `glass` `border-w 1.5` /
  `hairline-w 1`; `flat` `border-w 0` / `hairline-w 0`; `paper` `border-w 1` / `hairline-w 1`.
- `tests/test_skin_contract.py` covers `hairline-w` in all three schemas, rejects a numeric
  string for it, validates the `flat`/`paper` resolved maps and pins the new doc statements.
- `README.md` lists 24 tokens and the `0.6.0` release; `CONTRACT.md` records the new token and
  release.
- `cli-invocation-contract` bumped `0.5.2` → `0.6.0`: `CONTRACT_VERSION = "0.6.0"`,
  `DATA_VERSION = 2` unchanged. `invocation-contract.json` and the `csg`/`weg`/`itr`/`tpr`
  records are byte-identical.

### Release

- Annotated tag `v0.6.0` on the merged release commit, with the wheel + sdist built from that
  commit, not from a working tree.
- Consumers re-pin this exact tag; the assets/runtime/platform repos add `hairline-w`, stop
  expanding layout tokens in templates, and keep the row borderless.

## [0.5.2] - 2026-11-05

Patch release: freeze the skin artifact interface (ticket
[`REQ-013`](./tickets/REQ-013-skin-artifact-interface/ticket.md)). No vocabulary change; the 23
tokens and the six manifest groups are unchanged.

### Added

- `skins.md` normative **"Template set and consumer artifacts"** section: the template set lives
  with the skin data (`dotfiles-assets/skins/templates/`), is independent of the selected
  manifest, and has one `<configDir>.gtk.css.j2` per target config dir rendering
  `<configDir>.css`. `{{SKIN_<TOKEN>}}` normalizes a token name to uppercase with
  non-alphanumerics → `_` (`radius-panel` → `SKIN_RADIUS_PANEL`); unknown or unresolved
  placeholders fail closed. Outputs are `current/skins/<configDir>.css` per target plus one
  shared `current/skin.json`; pointers are `config/<configDir>/skin.css` →
  `current/skins/<configDir>.css` and `config/<configDir>/skin.json` → `current/skin.json`
  (bar `configDir = ags`).
- `schemas/skin-json.schema.json` — draft-07 schema for the resolved grouped token map:
  `version` `const 1`, the six groups required, each group requiring exactly its v1 tokens with
  the same value types as `skin-token.schema.json`, and `additionalProperties: false` at the
  root and in every group. It validates a runtime `skin.json` without the manifest wrapper.
- Positive/negative fixtures under `tests/fixtures/skin-contract/skin-json/`: a valid grouped
  map plus rejected flat tokens, string numerics, `structure`/`variant` groups and an unknown
  group. `tests/test_skin_contract.py` checks the schema, fixtures, version and the cross-check
  against the existing vocabulary.

### Changed

- `skins.md` now names the palette-independent cache key
  `sha256(templates_hash ‖ manifest_hash)` consistently (the existing runtime fact used
  `template_set_hash`).
- `README.md` lists the new schema and the expanded `skins.md` scope; `CONTRACT.md` records the
  `0.5.2` release.
- `cli-invocation-contract` bumped `0.5.1` → `0.5.2`: `CONTRACT_VERSION = "0.5.2"`,
  `DATA_VERSION = 2` unchanged. `invocation-contract.json` and the `csg`/`weg`/`itr`/`tpr`
  records are byte-identical.

### Release

- Annotated tag `v0.5.2` on the merged release commit, with the wheel + sdist built from that
  commit, not from a working tree.
- Consumers re-pin this exact tag and consume the skin schemas + `skins.md` from its repo root.

## [0.5.1] - 2026-11-05

Patch release: freeze the skin value/unit convention (ticket
[`REQ-012`](./tickets/REQ-012-skin-units/ticket.md)). No vocabulary change; the 23 tokens and
the six manifest groups are unchanged.

### Added

- `skins.md` normative **"Value types and units"** section: the twelve numeric tokens
  (`radius-panel`, `radius-card`, `radius-cell`, `radius-pill`, `border-w`, `gap`, `title-size`,
  `text-size`, `panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min`) are unitless JSON
  numbers in the manifest and in the resolved `skin.json`; CSS expansion renders them as
  `<number>px` and the expander must not store units. `cell-pad` is the only literal
  `"Npx Npx"` length-pair token; layout tokens are read by `skinValue()` as numbers and may also
  appear in CSS placeholders; the default skin's `font-family` may be `"inherit"`.
- A consumer rule in `skins.md`: vendor and validate against this repo's canonical schemas, not
  a local lookalike such as a repo-local `skins/schema.json` that accepts `"12px"`.

### Changed

- Both skin schemas now document the convention in their descriptions/examples (unitless
  numbers, `cell-pad` as `"Npx Npx"`, `font-family: "inherit"`). The vocabulary, groups, palette
  enum and forbidden-construct rules are untouched.
- `tests/test_skin_contract.py` rejects `"12px"` for every numeric token (flat and manifest
  documents) while accepting `12`, requires `cell-pad` to be exactly `"Npx Npx"`, pins the schema
  descriptions, and proves the documented expander example renders `12` → `12px`. New negative
  fixtures: `numeric-string.invalid.json` and `cell-pad-single.invalid.json` in both schema
  fixture dirs.
- `cli-invocation-contract` bumped `0.5.0` → `0.5.1`: `CONTRACT_VERSION = "0.5.1"`,
  `DATA_VERSION = 2` unchanged. `invocation-contract.json` and the `csg`/`weg`/`itr`/`tpr`
  records are byte-identical.

### Release

- Annotated tag `v0.5.1` on the merged release commit, with the wheel + sdist built from that
  commit, not from a working tree.
- Consumers re-pin this exact tag and consume the skin schemas + `skins.md` from its repo root.

## [0.5.0] - 2026-11-05

Minor release: the frozen skin-plane v1 contract (ticket
[`REQ-011`](./tickets/REQ-011-skin-plane-contract/ticket.md)).

### Added

- `schemas/skin-token.schema.json` — the frozen 23-token skin vocabulary in six groups
  (`shape`, `rhythm`, `surface`, `ink`, `type`, `layout`) with the palette-role paint grammar:
  `transparent`, `@<role>`, `alpha(@<role>, 0..1)`, `color-mix(in srgb, @<role> <pct>%,
  transparent|@<role>)`, and gradients/shadows composed from those. No literal hex.
- `schemas/skin-manifest.schema.json` — `schemaVersion`, `name`, and the six groups with
  `additionalProperties: false` at every level; structure/variant/order/presence keys and
  `*variant*` tokens are rejected. The palette enum is exactly the 51-role `palette.v1`
  vocabulary (50 Material roles + `on_backdrop`).
- `skins.md` — the skin contract: selection in runtime `desired.json`, the palette-independent
  cache key `sha256(template_set_hash ‖ manifest_hash)`, the appearance hash including the skin
  hash, the palette-refresh/restart lanes (bar = restart), the single `Gtk.CssProvider` at USER
  priority (800) re-installed last, the module-scoped monitor GC rule, the near-black
  missing-palette failure, drift-gate expectations, and the `glass`/`flat`/`paper` built-ins.
- Positive/negative fixtures and `tests/test_skin_contract.py`, plus `make skin-test` and a CI
  step. Negatives cover literal hex, `transition`, structure/variant, unknown token, `blur(` as
  a value, an unknown palette role and `%` inside `calc()`.

### Changed

- `cli-invocation-contract` bumped `0.4.0` → `0.5.0`: `CONTRACT_VERSION = "0.5.0"` (equal to the
  `v0.5.0` tag without its `v`), `DATA_VERSION = 2` (the invocation data shape is unchanged).
  The `csg`, `weg`, `itr` and `tpr` records are byte-identical.
- `README.md` and `CONTRACT.md` name `v0.5.0`; the skin schemas are repo-root sources and are
  deliberately not wheel package data.

### Release

- Annotated tag `v0.5.0` on the merged release commit, with the wheel + sdist built from that
  commit, not from a working tree.
- Consumers re-pin this exact tag; the skin contract is consumed from the tag's repo root.

## [0.4.0] - 2026-10-28

Minor release: the `tpr` (theme producer) record joins the invocation contract (ticket
[`REQ-010`](./tickets/REQ-010-tpr-invocation-record/ticket.md), OpenSpec change
`tpr-invocation-record`).

### Added

- `clis.tpr` in `invocation-contract.json`: `binary: "tpr"`, the `generate {wallpaper}` argv with
  the eight `--format` values (`yaml`, `conf`, `gtk.css`, `adw.css`, `sequences`, `rasi`, `kitty`,
  `btop.theme`), `THEME__OUTPUT__DIRECTORY` / `THEME__OUTPUT__OVERWRITE` as required and injected
  env keys, the eight exact consumer artifacts (`colors.*`, `min_count: 8`, not recursive), the
  standard exit-code semantics and a 60 s timeout. `CONTRACT.md` documents the fourth record and
  the `theme.json` exclusion.

### Changed

- `cli-invocation-contract` bumped `0.3.0` → `0.4.0`: `CONTRACT_VERSION = "0.4.0"` (equal to the
  `v0.4.0` tag without its `v`), `DATA_VERSION = 2` (the record shape is unchanged and
  `invocation-contract.json` still declares `contract_version: 2`).
- `csg`, `weg` and `itr` are byte-identical; the testkit is unchanged (its two assertions already
  enforce the new record).

### Release

- Annotated tag `v0.4.0` on the merged release commit, with the wheel + sdist built from that
  commit, not from a working tree.
- Consumers re-pin this exact tag in the adoption slice; `tpr` is invoked through the same
  conformance kit as `csg`/`weg`/`itr`.

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
