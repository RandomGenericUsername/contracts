---
id: REQ-020
title: "surface.window role: required outer toplevel surface + host geometry"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: none
  bmad: none
  design: dotfiles-v3/docs/113-window-role-kitty-projection.md
worktree: .worktrees/REQ-020/
branch: ticket/REQ-020-window-role
---

# surface.window role: required outer toplevel surface + host geometry

## Requirement

Add the approved **`surface.window`** role from
`dotfiles-v3/docs/113-window-role-kitty-projection.md` (D4-B) to the appearance
contract. `surface.window` is a real, required outer/toplevel surface role, not
an alias for `surface.panel`.

- **Eight tokens, all required:** `bg`, `border`, `border-width`, `radius`,
  `padding`, `shadow`, `blur`, `opacity`.
- **`opacity` is a new value type:** a unitless number in `[0, 1]`, never a
  length and never derived from an `alpha()` paint.
- **No silent alias:** the group is required in every manifest and resolved
  token document. A manifest without `[groups.surface.window]` fails schema
  validation naming the group; it is never populated from `surface.panel`.
- **`surface.panel` stays:** it remains the AGS bar/settings and layer-shell
  overlay outer role with its existing tokens and consumers.
- **Host allowlist expands to exactly seven paths:** add
  `surface.window.radius` (`0..64`) and `surface.window.border-width`
  (`0..16`) while keeping the five existing panel/card/control/cell paths. No
  window padding/opacity delegation; `surface.pill.radius` stays invalid.
- **Generation `host.defaults`** accepts the two window geometry paths.
- **Version:** the token-model version stays the skin schema `2` (manifest
  `schemaVersion: 2`, resolved `version: 2`, `appearance.json` `version: 2`)
  and the generation manifest stays `version: 3`; the contract release is
  `v0.12.0`.
- **Migration:** existing skins must add an explicit window group in the
  manifest. No runtime fallback or alias exists.

## Deliverables

1. `schemas/appearance-manifest.schema.json` — `surfaceGroup.window`
   (`windowRole`), required; `opacityValue`; expanded `host.inherit` enum;
   updated descriptions and schemaVersion description.
2. `schemas/appearance-json.schema.json` — the same `windowRole` /
   `opacityValue` and required window role.
3. `schemas/generation-manifest.schema.json` — `host.defaults` gains
   `surface.window.radius` and `surface.window.border-width`.
4. `appearance.md`, `skins.md`, `generations.md`, `README.md`, `CHANGELOG.md`
   — role semantics and consumer mapping, opacity type, seven-path host
   allowlist, migration/no-alias rule, unchanged versions.
5. Fixtures/tests: all eight window tokens; missing group/token, opacity
   bounds/type and extra key negatives; host window geometry valid, window
   padding/opacity host invalid, panel paths still valid; generation window
   defaults; migrated built-in fixtures plus a legacy no-window negative.
6. Version metadata `0.12.0`, all gates green, annotated tag `v0.12.0`.

## Acceptance

- [ ] `surface.window` is required with exactly the eight tokens above; a
      missing group or token is rejected.
- [ ] `surface.window.opacity` is a number in `[0, 1]`; strings, negatives and
      values above `1` are rejected.
- [ ] `surface.panel` remains a distinct required role with unchanged tokens.
- [ ] The `[host].inherit` enum is exactly the seven paths; window padding and
      window opacity are rejected; pill radius is rejected; the old panel-only
      policy and the five-path rectangle policy stay valid.
- [ ] `host.defaults` accepts the four rectangle radii, panel border width and
      the two window geometry paths.
- [ ] Docs map rofi/wlogout/GTK outer slots to window, AGS bar/overlays to
      panel, notifications to card and kitty to window opacity/padding + type;
      docs state the migration and no-alias rule.
- [ ] `make test`, `make skin-test`, `make appearance-test`,
      `make generations-test`, `make schema-test`, `make contracts-drift` and
      `uv lock --check` exit 0.
- [ ] Version metadata and `tests/test_record.py` agree on `0.12.0`; annotated
      tag `v0.12.0` points at the merged release commit; no existing tag moves.

## Non-goals

- No runtime resolver/renderer, assets skins/templates, provisioning,
  composition, apps or live apply.
- No kitty `conf` artifact implementation; this repo only freezes the window
  role and its host geometry.
- No window padding/opacity host delegation and no panel deprecation.

## Evidence

- Design: `dotfiles-v3/docs/113-window-role-kitty-projection.md` §1–§6, §9.
- Baseline: `schemas/appearance-manifest.schema.json` at `v0.11.0` (commit
  `6a3ed99`): five surface roles, `host.inherit` five paths.
- Baseline generation: `schemas/generation-manifest.schema.json`
  `host.defaults` five paths at `v0.11.0`.
