# Changelog

Notable changes to the `contracts` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Release versions follow the git tags
(AD-9/AD-11): for every release the tag, the `cli-invocation-contract` distribution version, and
`CONTRACT_VERSION` are the same value (`v0.4.0` ↔ `0.4.0` ↔ `CONTRACT_VERSION = "0.4.0"`).

## [Unreleased]

(nothing yet)

## [0.11.0] - 2026-11-11

Minor release: host-delegated rectangle radii (ticket
[`REQ-019`](./tickets/REQ-019-host-rectangle-radii/ticket.md)). The skin
`[host]` allowlist expands from the outer panel to the inner rectangle roles.
This is additive: the old two-path policy, every existing manifest and every
generation fixture remain valid, and no token type or `required` list changes.

### Added

- `schemas/appearance-manifest.schema.json` — the `host.inherit` enum now
  accepts `surface.panel.radius`, `surface.panel.border-width`,
  `surface.card.radius`, `surface.control.radius` and `surface.cell.radius`.
  `surface.pill.radius` is deliberately absent: a pill is a capsule and its
  radius stays explicit. No padding, gap, type, paint, colour, state or
  `layout.<app>` path is delegable.
- `schemas/generation-manifest.schema.json` — `host.defaults` records the same
  five logical paths (radii `0..64`, panel border width `0..16`) when they
  participated. A two-key panel-only snapshot remains valid.
- `appearance.md`, `skins.md`, `generations.md` — the outer/inner
  rectangle-radius rule, the intentional pill exclusion, the unchanged
  `mode override > host > skin fallback` precedence and the panel-only
  border-width rule.
- Positive fixtures for all five paths, each inner radius individually and the
  old two-path policy; negative fixtures for the pill and an unknown path.
  Generation fixtures cover all five participating defaults.

### Changed

- `cli-invocation-contract` and `CONTRACT_VERSION` move to `0.11.0`;
  `DATA_VERSION` stays `2` and the invocation records are byte-identical.

### Release

- Annotated tag `v0.11.0` on the merged release commit. No runtime, platform,
  assets, provisioning, composition or app code was changed in this repo.

## [0.10.0] - 2026-11-10

Minor release: format-aware non-CSS appearance consumers (ticket
[`REQ-018`](./tickets/REQ-018-format-aware-consumers/ticket.md)). This is
additive: the generation manifest stays `version: 3`, every CSS-only generation
and `v0.9.0` fixture remains valid, and `appearance.targets` is unchanged.

### Added

- `schemas/generation-manifest.schema.json` — optional `appearance.artifacts`
  family: a non-empty array of closed `{consumer, path, format}` objects.
  `consumer` uses the existing safe lowercase config-dir segment (no dots),
  `format` is exactly `rasi|conf|theme` (CSS is excluded), and `path` matches
  `appearance/<consumer>.<ext>` with an allowed non-CSS extension. The draft-07
  schema enforces shape and allowed extensions; runtime validation, verify and
  the contract fixture gate enforce `path == appearance/<consumer>.<format>`
  and consumer/path uniqueness across `artifacts` and `targets`.
- `generations.md` — the second target family, its cross-property and
  uniqueness rules, AGS unknown-key tolerance, the re-pin requirement for
  strict validators, the no-fake-CSS rule and the reserved `conf`/`theme`
  formats.
- `appearance.md` — the frozen CSS family vs the optional non-CSS family, the
  format/extension/consumer equality rule, the AGS compatibility note and the
  rofi-first, kitty/btop-palette-only policy.
- Positive fixtures for a CSS-only manifest, `rasi`, `conf`, `theme` and all
  formats together; negative fixtures for a duplicate consumer/path, an
  extension/format mismatch, an unknown format, an extra key, a missing field,
  a dotted consumer and an empty array.

### Changed

- `cli-invocation-contract` and `CONTRACT_VERSION` move to `0.10.0`;
  `DATA_VERSION` stays `2` and the invocation records are byte-identical.

### Release

- Annotated tag `v0.10.0` on the merged release commit. No runtime, platform,
  assets, provisioning, composition or app code was changed in this repo.

## [0.9.0] - 2026-11-09

Minor release: optional host defaults (ticket
[`REQ-017`](./tickets/REQ-017-host-defaults/ticket.md)). A skin may delegate
only an explicit allowlist of logical token paths to the live compositor.
This is additive: existing manifests and generations without `[host]` remain
valid, no token type or `required` list changes, and the v2 appearance token
vocabulary is unchanged.

### Added

- `schemas/appearance-manifest.schema.json` — optional root `host` policy:
  closed object, required non-empty unique `inherit` enum exactly
  `surface.panel.radius` and `surface.panel.border-width`, optional `fallback`
  enum `skin|error` defaulting to `skin`. The policy is not a token group and
  cannot name layout, padding, gap, type, paint or colour paths.
- `schemas/generation-manifest.schema.json` — optional `host` block
  (`source: hyprland`, mapping `version: 1`, `fingerprint`, non-empty
  `defaults` with only the participating delegated values) and optional
  `intent.host`; `intent.host` is required when `host` is present and forbidden
  when it is absent. Equality with `host.fingerprint` is documented as a
  runtime validation rule because draft-07 cannot compare two properties.
- `appearance.md` — host policy, precedence (mode override > host > skin
  fallback), headless/invalid fallback, `fallback="error"` fail-closed and the
  `appearance.v3` identity with a participating-only `hostHash` (`-` when no
  delegated value participated; one-time identity churn accepted).
- `generations.md` — host snapshot shape, identity rules and the host-free
  daemon queue key (the host is read once inside `converge.lock`).
- Positive/negative fixtures for the host policy and generation host shape,
  plus a semantic fixture proving an `intent.host` / `host.fingerprint`
  mismatch is rejected by runtime validation.

### Changed

- The appearance identity formula is now `appearance.v3`; existing v2
  generations remain readable by their committed manifests and require no
  cache migration beyond normal GC.
- `cli-invocation-contract` and `CONTRACT_VERSION` move to `0.9.0`;
  `DATA_VERSION` stays `2` and the invocation records are byte-identical.

## [0.8.0] - 2026-11-06

Major release: Generations v3 (ticket
[`REQ-016`](./tickets/REQ-016-generations-v3/ticket.md)). One committed
generation, one convergence pipeline and a generation-bound apply/ack replace
the v2 multi-pointer and two-pipeline mechanics. This is a new major; the v2
appearance token vocabulary, composed-sheet rules and built-in skins are
unchanged.

### Added

- `generations.md` — the normative Generations v3 interface: the immutable
  `state/generations/<genHash>/` layout (`manifest.json`, `palette/`,
  `appearance/<configDir>.css` + `tokens.json`, `icons/`, `effects/`,
  wallpaper and in-generation compatibility aliases), the one atomic
  `state/current` commit transaction and crash matrix, consumer read/watch
  rules, artifact locality/immutability, the explicit `refresh`/`supervision`/
  `launch` lane policy, mode identity, the GC/pin contract, event-driven
  no-polling rules and the refresh protocol.
- `schemas/generation-manifest.schema.json` — draft-07, `version: 3`,
  `generationHash` (64 lowercase hex), created/committed metadata, required
  `wallpaper`/`palette` layers plus optional `effects`/`icons`, each with an
  entry hash and a generation-local relative path; `skin {name, entryHash,
  mode}`, `appearance {tokensPath, targets[]}`, `mode`, `intent` and `source`
  metadata. `additionalProperties: false` at every level; structure/variant
  keys, literal hex and paths that escape the generation are rejected.
- Positive `glass-dark`/`paper-light` generation manifests and negative
  fixtures for a stale layer path, an unknown layer, a wrong hash, a missing
  mode, extra keys, structure/variant and literal hex.
- `appearance-refresh.md` — the generation-bound
  `["appearance-refresh", "<genHash>"]` request, the
  applied/deferred/failed response union, the response-hash-equals-request rule,
  the resolve-the-requested-generation rule, state preservation and the ledger
  policy. A v3 app never acks "whatever `current` is", and the v2
  `{"ok":true}` ack is invalid.
- `schemas/appearance-refresh-result.schema.json` — draft-07 response union:
  `{applied: genHash}` | `{deferred: reason, genHash}` |
  `{failed: reason, retryable, genHash}` with a required 64-hex generation and
  no extra keys.
- Positive/negative refresh-result fixtures, including the rejected v2 boolean
  ack.
- `tests/test_generations_contract.py` and `make generations-test`: manifest and
  response schema gates, identity consistency checks, response/ack mismatch
  rejection for every variant, and documentation/protocol pins.

### Changed

- `ags-app-refresh.md` is retained for provenance and marked **superseded** by
  `appearance-refresh.md`; its `palette-refresh` request and `{"ok":true}` ack
  are not valid v3 acks.
- `appearance.md` keeps the v2 token vocabulary, mode resolution, template
  flattening, one-provider composition and built-in skins; a v3 note points its
  pointer/refresh mechanics at `generations.md` and `appearance-refresh.md`.
- `README.md` lists the v3 generation interface, schema and refresh protocol,
  and the `make generations-test` gate.
- `cli-invocation-contract` bumped `0.7.0` → `0.8.0`: `CONTRACT_VERSION =
  "0.8.0"`, `DATA_VERSION = 2` unchanged. `invocation-contract.json` and the
  `csg`/`weg`/`itr`/`tpr` records are byte-identical.

### Removed

- Nothing at the artifact level in this repo. The v3 contract retires the v2
  multi-pointer read path and the boolean ack for v3 consumers; the runtime,
  platform, provisioning and app implementations adopt the tag in their own
  waves.

### Release

- Annotated tag `v0.8.0` on the merged release commit; the wheel + sdist are
  built from that commit, not from a working tree. No runtime, platform, assets,
  provisioning or app code was changed in this repo.

## [0.7.0] - 2026-11-06

Major release: the Appearance plane v2 (ticket
[`REQ-015`](./tickets/REQ-015-appearance-plane-v2/ticket.md)). One generated appearance, one
atomically repointed hop, and the nested role/state/type/mode token model. This is a new major,
not a v1.1 hotfix; the v1 skin-plane artifacts are retired.

### Added

- `appearance.md` — the normative Appearance plane v2 contract: the
  `cache/appearance/<hash>/` generation (`colors.yaml`, `tokens.json`, `appearance.json`, one
  composed `<configDir>.css` per target), the single `current/appearance` pointer, the stable
  `config/<configDir>/appearance.css` convenience link, the inotify rationale for watching the
  repointed hop, one provider at USER priority 800 installed last, one monitor and one apply,
  the whole-appearance `palette-refresh` handler, systemd user units with `KillMode=control-group`,
  the v1 workarounds retired, fail-closed/drift rules and the built-in skins.
- `schemas/appearance-manifest.schema.json` — the v2 authored manifest (`schemaVersion: 2`,
  nested `surface`/`state`/`type`/`ink`/`layout` groups, optional same-shape
  `mode.dark`/`mode.light` overrides, `additionalProperties: false` at every level).
- `schemas/appearance-json.schema.json` — the resolved, mode-resolved `tokens.json` token map
  (`version: 2` plus the five groups).
- `schemas/appearance-artifact.schema.json` — `appearance.json` metadata (`version: 2`, `skin`,
  `mode`, `paletteHash`, `skinHash`, `appearanceHash`, `generationHash`, `tokenRef`).
- v2 `glass`/`flat`/`paper` manifest fixtures and resolved token fixtures, including
  `paper-light.valid.json`; the v1 values are converted faithfully and `paper` uses explicit
  `mode.light` overrides instead of palette guessing.
- `tests/test_appearance_contract.py` and `make appearance-test`: positive/negative fixtures for
  literal hex, transition, structure/variant, an unknown surface role, an incomplete mode override,
  unit-bearing numeric strings, a layout token in a template and template conditionals, plus a
  pure flattening/resolution check (`surface.panel.bg` → `{{SKIN_SURFACE_PANEL_BG}}`).

### Changed

- The appearance token model replaces the flat v1 vocabulary with nested per-role surface tokens
  (`panel`/`card`/`cell`/`control`/`pill`), explicit interaction states
  (`hover`/`selected`/`focus`/`disabled` with `fill`/`ink`/`ring`), shared type sizes and
  letter-spacing, an `accent-muted` ink, namespaced `layout.<app>` metrics, and optional
  `mode.dark`/`mode.light` group overrides selected at generation.
- `appearance.md` records the investigation evidence: the v1 first-hop/second-hop watch mismatch,
  the palette-only `theme.apply()` handlers, and the orphaned gjs child that held
  `org.freedesktop.Notifications` until `ags quit -i notifications`.
- `README.md` and `CONTRACT.md` describe the v2 plane and the `0.7.0` release; `appearance.md` and
  the three v2 schemas are listed as the current appearance sources, with the v1 skin files marked
  superseded.
- `cli-invocation-contract` bumped `0.6.0` → `0.7.0`: `CONTRACT_VERSION = "0.7.0"`,
  `DATA_VERSION = 2` unchanged. `invocation-contract.json` and the `csg`/`weg`/`itr`/`tpr`
  records are byte-identical.

### Removed

- The v1 skin-plane artifacts (`skin.css`, `skin.json`, `current/skins/`, `current/skin.json`)
  are retired by the contract. There is no v1.1 hotfix and no dual-publish window; consumers
  re-pin `v0.7.0` and adopt the single `current/appearance` hop.

### Release

- Annotated tag `v0.7.0` on the merged release commit; the wheel + sdist are built from that
  commit, not from a working tree. No runtime, platform, assets or app code was changed in this
  repo.

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
