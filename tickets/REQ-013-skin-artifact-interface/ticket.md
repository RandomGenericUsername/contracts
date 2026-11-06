---
id: REQ-013
title: "Freeze the skin artifact interface (template set, pointers, skin.json)"
kind: requirement
status: proposed
lane: 2
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# Freeze the skin artifact interface (template set, pointers, skin.json)

## Requirement

The runtime, assets and platform implementations diverged on how a selected skin
becomes consumer artifacts. Freeze the interface in this repo (patch release `v0.5.2`, no
vocabulary change) so every consumer aligns on one template set, one output set, one pointer
layout and one resolved-token document:

1. `skins.md` gains a normative **"Template set and consumer artifacts"** section:
   - the template set lives with the skin data (`dotfiles-assets/skins/templates`), is
     independent of the selected manifest, and has one template per target config dir named
     `<configDir>.gtk.css.j2`; the expander renders `<configDir>.css`;
   - `{{SKIN_<TOKEN>}}` normalizes the token name to uppercase with non-alphanumerics → `_`
     (`radius-panel` → `SKIN_RADIUS_PANEL`); unknown or unresolved placeholders are errors;
   - inputs are the selected manifest (grouped tokens, units per `v0.5.1`) plus the shared
     template set; outputs are `current/skins/<configDir>.css` per target plus one shared
     `current/skin.json`;
   - consumer pointers are `{install}/config/<configDir>/skin.css` →
     `current/skins/<configDir>.css` and `{install}/config/<configDir>/skin.json` →
     `current/skin.json`; for the bar `configDir = ags` (dotfiles-v3 `apps.yaml`), other apps
     use their own `configDir`, and apps resolve through
     `$XDG_CONFIG_HOME/<configDir>/skin.css` (spine-linked);
   - the resolved `skin.json` is exactly
     `{"version": 1, "<group>": {"<token>": <unitless number|string>, ...}, ...}` for the six
     groups, numeric tokens as raw numbers and strings as-is, with no extra keys, no flat
     tokens and no structure/variant;
   - selection comes from runtime `desired.json` `skin` (default `glass`); the cache key is
     `sha256(templates_hash ‖ manifest_hash)` and is palette-independent; the appearance hash
     includes the skin hash; live apps refresh through `palette-refresh`, the bar stays
     restart-only; missing or invalid artifacts fail closed.
2. `schemas/skin-json.schema.json` (draft-07) validates the resolved grouped token map on its
   own (no manifest wrapper): `version` is `const 1`, the six groups are required, each group
   requires exactly its tokens with the same value types as `skin-token.schema.json`, and
   `additionalProperties: false` applies at every level.
3. Positive/negative fixtures cover a valid grouped map and reject flat tokens, string
   numerics, structure/variant groups and unknown groups.
4. `tests/test_skin_contract.py` exercises the new schema and fixtures; `README.md`,
   `CHANGELOG.md` and `CONTRACT.md` carry the `v0.5.2` pointers.
5. Release plumbing: `pyproject.toml`, `CONTRACT_VERSION`, `uv.lock`, the INDEX and the
   changelog agree on `0.5.2`; annotated tag `v0.5.2` on the merged release commit.

## Acceptance

- [ ] `skins.md` contains the normative "Template set and consumer artifacts" section with
  the template naming/placeholder rule, inputs/outputs, pointers (`configDir = ags` for the
  bar), the exact `skin.json` shape, and the read-order/refresh/fail-closed rules.
- [ ] `schemas/skin-json.schema.json` is valid draft-07 with `$id`
  `https://dotfiles.local/schemas/skin-json.schema.json`, `version` `const 1`, the six groups
  required, the 23 tokens typed identically to `skin-token.schema.json`, and
  `additionalProperties: false` at the root and in every group.
- [ ] Positive fixture `skin-json/glass.valid.json` validates; negative fixtures reject flat
  tokens, `"12px"`/`"12"` string numerics, `structure`/`variant` groups and an unknown group.
- [ ] `tests/test_skin_contract.py` covers the new schema and its fixtures, including the
  cross-check against the existing 23-token vocabulary and six groups.
- [ ] `make test`, `make skin-test` and `make schema-test` exit 0.
- [ ] `CHANGELOG.md`, `README.md`, `CONTRACT.md`, `tickets/INDEX.md`, the package version,
  `uv.lock` and `CONTRACT_VERSION` agree on `0.5.2`; annotated tag `v0.5.2` points at the
  merged release commit and no existing tag moved.

## Evidence

- Runtime invented its own manifest shape: `dotfiles-runtime/src/runtime/adapters/skin_expander.py:12-21`
  documents `[tokens]` + `[apps]` (app → template path) and emits `<app>.css` plus a **flat**
  `skin.json` (`:224-229`), not the grouped manifest of this contract.
- Assets use grouped manifests and a bar-specific template name:
  `dotfiles-assets/skins/manifests/glass.toml:11,22` (`[shape]`, `[surface]`) and
  `dotfiles-assets/skins/templates/ags-bar.gtk.css.j2` (see `skins/README.md:28`).
- Platform reads the bar pointer and a grouped token map:
  `ags-platform/adapters/skin.ts:53-61` (`config/ags/skin.css`,
  `state/dotfiles/current/skin.json`), `ags-platform/ports/skin.ts:18-20` (top-level `shape`,
  `surface`, `ink`, `type`, `rhythm`, `layout` groups) and `parseSkinJson` (`:223-290`).
- The bar config dir is `ags`: `dotfiles-v3/dotfiles/provisioning/apps.yaml:32-42`
  (`configDir: ags`, `spineLink: ags`).
- Contract source of truth today: `skins.md`, `schemas/skin-token.schema.json`,
  `schemas/skin-manifest.schema.json`, `tests/test_skin_contract.py`.

## Non-goals

- No change to the 23-token vocabulary, the six groups, the palette enum or the existing
  token/manifest schema meanings.
- No runtime, assets, platform or app code in this repo; those repos adopt this interface
  against the tag.
- No change to `invocation-contract.json` or `DATA_VERSION` (`2`).
