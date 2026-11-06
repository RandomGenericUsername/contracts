---
id: REQ-011
title: "Frozen skin-plane contract v1 (token vocabulary, manifest, docs, fixtures)"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-011/
branch: ticket/REQ-011-skin-plane-contract
---

# Frozen skin-plane contract v1 (token vocabulary, manifest, docs, fixtures)

## Requirement

Add the canonical, language-neutral skin contract for the AGS platform. A skin is a
**palette/ink mapping + paint + rhythm/density**; it never carries structure. The frozen v1
vocabulary comes from executed GTK 4.24 probes and must be implemented exactly.

Deliver:

- `schemas/skin-token.schema.json` (draft-07): the flat token vocabulary with per-token value
  grammar — shape (`radius-panel`, `radius-card`, `radius-cell`, `radius-pill`, `border-w`),
  rhythm (`gap`, `cell-pad`), surface (`bg-panel`, `bg-card`, `border`, `shadow`, `blur`), ink
  (`ink`, `ink-dim`, `accent`, `ink-over: auto`), type (`font-family`, `title-size`,
  `text-size`), layout (`panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min`).
- `schemas/skin-manifest.schema.json` (draft-07): `schemaVersion`, `name`, `groups` with exactly
  `shape`, `surface`, `ink`, `type`, `rhythm`, `layout`; `additionalProperties: false` at every
  level; `$id` + frozen `status`.
- `skins.md`: selection via runtime `desired.json` `skin: "<name>"`, the palette-independent
  cache key `sha256(template_set_hash ‖ manifest_hash)`, the appearance hash including the skin
  hash, refresh lanes, the single-provider composition rule, forbidden categories, drift-gate
  expectations, and the `glass`/`flat`/`paper` built-ins.
- Positive and negative fixtures in the existing schema-test style, including negatives for a
  literal hex, `transition`, `structure`/`variant`, an unknown token, and `blur(` used as a
  non-blur value.
- `CHANGELOG.md` + `tickets/INDEX.md` updates per `LIFECYCLE.md`, then an annotated next-minor
  tag (`v0.5.0`) without moving an existing tag.

Frozen constraints:

- Surface values are CSS expressions over `palette.v1` role names only (`transparent`,
  `@<role>`, `alpha(@<role>, 0..1)`, `color-mix(in srgb, @<role> <pct>%, transparent|@<role>)`,
  and gradients/shadows composed from those). No literal hex.
- `blur` is `none` or `"blur(<n>px) [saturate(<n>)]"`.
- Ink values are palette role names or role expressions; `ink-over` is derived and is exactly
  `auto`.
- `layout` tokens are numbers consumed by `skinValue()`, never emitted as CSS.
- Reject structure: no keys named `structure`/`variant`/`order`/`presence` and no `*variant*`
  token.
- Explicitly reject `#` literals, `transition` keys/values, `blur(` outside the `blur` token,
  `%` inside `calc()`, and structure/variant tokens.
- The palette role enum is the existing `palette.v1` vocabulary (50 Material roles +
  `on_backdrop`); no new roles are invented.

No runtime, app or host code lives here; this is schema and protocol source only.

## Acceptance

- [ ] `schemas/skin-token.schema.json` is draft-07 valid, `$id`-self-named, frozen-status, and
  names exactly the 23 v1 tokens with the grammar above.
- [ ] `schemas/skin-manifest.schema.json` is draft-07 valid, requires `schemaVersion`, `name` and
  the six groups, and rejects extra keys at every level.
- [ ] The palette role enum is exactly the 51-role `palette.v1` vocabulary, including
  `on_backdrop`.
- [ ] Positive fixtures for `glass`, `flat` and `paper` are accepted; negatives for literal
  hex, transition, structure/variant, unknown token, `blur(` as a value, unknown palette role
  and `%` inside `calc()` are rejected.
- [ ] `skins.md` records selection, cache key, appearance hash, refresh lanes, provider
  composition, forbidden categories, drift-gate expectations, `ink-over: auto`, and the
  glass/flat/paper built-ins.
- [ ] `make test` (which includes the skin schema fixtures) exits 0; `make skin-test` exits 0.
- [ ] `CHANGELOG.md`, `tickets/INDEX.md`, `README.md`, `CONTRACT.md`, the package version and
  `CONTRACT_VERSION` agree on `0.5.0`; annotated tag `v0.5.0` points at the merged release
  commit and no existing tag moved.

## Evidence

- Frozen skin spec v1 in this ticket (GTK 4.24 probe results; selection/cache/hash/lane/provider
  facts supplied with the request).
- `palette.v1` vocabulary source: `dotfiles-runtime` `7f68574`,
  `src/runtime/domain/palette_vocabulary.py:42-94` (50 `MaterialRole` values + `on_backdrop`
  at line 93); producer side: `theme-producer` `c3970cf`,
  `src/theme_producer/domain/enums.py::MaterialRole` and `docs/VOCABULARY.md`.
- Existing schema/test style: `schemas/ags-app-manifest.schema.json`,
  `tests/test_ags_app_contract.py`.

## Non-goals

- No runtime renderer, `skinValue()` implementation or AGS app code in this repo.
- No palette role additions or renames.
- No structure/variant axis: that is deliberately outside the skin plane.
