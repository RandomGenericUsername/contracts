---
id: REQ-011
title: "Frozen skin-plane contract v1 (token vocabulary, manifest, docs, fixtures)"
kind: requirement
status: done
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

- [x] `schemas/skin-token.schema.json` is draft-07 valid, `$id`-self-named, frozen-status, and
  names exactly the 23 v1 tokens with the grammar above.
- [x] `schemas/skin-manifest.schema.json` is draft-07 valid, requires `schemaVersion`, `name` and
  the six groups, and rejects extra keys at every level.
- [x] The palette role enum is exactly the 51-role `palette.v1` vocabulary, including
  `on_backdrop`.
- [x] Positive fixtures for `glass`, `flat` and `paper` are accepted; negatives for literal
  hex, transition, structure/variant, unknown token, `blur(` as a value, unknown palette role
  and `%` inside `calc()` are rejected.
- [x] `skins.md` records selection, cache key, appearance hash, refresh lanes, provider
  composition, forbidden categories, drift-gate expectations, `ink-over: auto`, and the
  glass/flat/paper built-ins.
- [x] `make test` (which includes the skin schema fixtures) exits 0; `make skin-test` exits 0.
- [x] `CHANGELOG.md`, `tickets/INDEX.md`, `README.md`, `CONTRACT.md`, the package version and
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

### Verification

Commands run from the worktree root (`.worktrees/REQ-011/`, branch
`ticket/REQ-011-skin-plane-contract`, base `16555cd`).

| Claim | Command | Result |
| --- | --- | --- |
| Schemas draft-07 valid, frozen, self-named | `make skin-test` | `39 passed in 0.11s`, exit 0; `test_every_schema_is_draft_07_self_valid_and_frozen` checks `$schema`/`$id`/`status` and `Draft7Validator.check_schema` |
| Positive + negative fixtures | `make skin-test` | `glass`/`flat`/`paper` accepted; literal hex, transition key/value, structure, variant token, unknown token, `blur(` value, `%` in `calc()`, unknown role and extra top-level key rejected |
| Token vocabulary == manifest groups | `make skin-test` | `23` flat tokens equal the union of the six group property sets, exit 0 |
| Palette enum is exactly palette.v1 | `make skin-test` | `51` roles, set equality with `palette.v1`, `on_backdrop` present |
| Runtime facts pinned in the doc | `make skin-test` | `test_skins_doc_pins_the_runtime_contract` asserts `desired.json`, `skin: "<name>"`, cache key, appearance hash, `Gtk.CssProvider`, priority `800`, re-installed last, module scope, near-black, `ink-over`, glass/flat/paper, restart |
| Full repo gate | `make test` | `Ran 10 tests in 0.035s` → `OK`; `148 passed in 0.25s`, exit 0 |
| AGS app schema gate unchanged | `make schema-test` | `40 passed in 0.06s`, exit 0 |
| Symmetric regenerate-and-diff | `make contracts-drift` | `[drift] symmetric: contract and generated/ agree`; `git diff --exit-code generated/` clean, exit 0 |
| Package build | `make build` | `Successfully built dist/cli_invocation_contract-0.5.0.tar.gz` and `...-0.5.0-py3-none-any.whl`, exit 0 |
| Version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.5.0 2`, exit 0 |
| Wheel metadata | `unzip -p dist/cli_invocation_contract-0.5.0-py3-none-any.whl cli_invocation_contract-0.5.0.dist-info/METADATA \| grep -m1 '^Version:'` | `Version: 0.5.0`, exit 0 |

### Commits

| Commit | Subject |
| --- | --- |
| `16555cd` | `docs(tickets): plan the frozen skin-plane contract (REQ-011)` |
| `aff160b` | `chore(REQ-011): start — record worktree/branch, move to in-progress` |
| `e4f4f59` | `feat(REQ-011): add the frozen skin-plane token and manifest contracts` |
| release commit (the `v0.5.0` tag target) | `chore(REQ-011): release v0.5.0 for the skin-plane contract` |

### Status

**Done on `ticket/REQ-011-skin-plane-contract`.** The frozen token/manifest schemas,
`skins.md`, fixtures and gates are in the implementation commit. No runtime, app or host code was
changed. Merge to `main`, then create the annotated `v0.5.0` tag on the merged release commit.

## Non-goals

- No runtime renderer, `skinValue()` implementation or AGS app code in this repo.
- No palette role additions or renames.
- No structure/variant axis: that is deliberately outside the skin plane.
