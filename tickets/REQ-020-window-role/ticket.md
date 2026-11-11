---
id: REQ-020
title: "surface.window role: required outer toplevel surface + host geometry"
kind: requirement
status: done
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

- [x] `surface.window` is required with exactly the eight tokens above; a
      missing group or token is rejected.
- [x] `surface.window.opacity` is a number in `[0, 1]`; strings, negatives and
      values above `1` are rejected.
- [x] `surface.panel` remains a distinct required role with unchanged tokens.
- [x] The `[host].inherit` enum is exactly the seven paths; window padding and
      window opacity are rejected; pill radius is rejected; the old panel-only
      policy and the five-path rectangle policy stay valid.
- [x] `host.defaults` accepts the four rectangle radii, panel border width and
      the two window geometry paths.
- [x] Docs map rofi/wlogout/GTK outer slots to window, AGS bar/overlays to
      panel, notifications to card and kitty to window opacity/padding + type;
      docs state the migration and no-alias rule.
- [x] `make test`, `make skin-test`, `make appearance-test`,
      `make generations-test`, `make schema-test`, `make contracts-drift` and
      `uv lock --check` exit 0.
- [x] Version metadata and `tests/test_record.py` agree on `0.12.0`; annotated
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
- Frozen result: manifest `surfaceGroup.required` is
  `["window", "panel", "card", "cell", "control", "pill"]`;
  `windowRole.required` is `["bg", "border", "border-width", "radius",
  "padding", "shadow", "blur", "opacity"]`; `host.inherit` is exactly
  `surface.window.radius`, `surface.window.border-width`,
  `surface.panel.radius`, `surface.panel.border-width`, `surface.card.radius`,
  `surface.control.radius`, `surface.cell.radius`. Generation `host.defaults`
  accepts the same seven paths with window radii `0..64` and window border
  width `0..16`.
- Versions stay token model `2` (manifest, resolved tokens, `appearance.json`)
  and generation `3`; contract release is `0.12.0`.
- Positive fixtures: migrated `glass`/`flat`/`paper` manifests and resolved
  documents (paper has a complete light `surface.window` override);
  `host-window.valid.json`; generation `host-window.valid.json`.
- Negative fixtures: `missing-window-group.invalid.json`,
  `missing-window-token.invalid.json`, `window-extra-key.invalid.json`,
  `opacity-string/negative/too-large.invalid.json`,
  `host-window-padding.invalid.json`, `host-window-opacity.invalid.json`, plus
  resolved `missing-window.invalid.json` and generation
  `host-window-padding/opacity.invalid.json`. The unchanged
  `host-old-two-path.valid.json`, five rectangle host fixtures and legacy
  generation snapshots still validate.

## Verification

Commands run from the worktree root (`.worktrees/REQ-020/`, branch
`ticket/REQ-020-window-role`, base `ca0a1f0`).

| Claim | Command | Result |
| --- | --- | --- |
| Full repo gate | `make test` | `Ran 10 tests ... OK`; `485 passed in 3.84s`, exit 0 |
| Frozen v1 skin gates | `make skin-test` | `110 passed in 0.69s`, exit 0 |
| Appearance contract | `make appearance-test` | `155 passed in 2.34s`, exit 0 |
| Generation contract | `make generations-test` | `111 passed in 0.39s`, exit 0 |
| AGS app contract | `make schema-test` | `40 passed in 0.09s`, exit 0 |
| Symmetric drift gate | `make contracts-drift` | `[ok]` symmetric; regenerate-and-diff clean, exit 0 |
| Lockfile check | `uv lock --check` | `Resolved 13 packages in 0.78ms`, exit 0 |
| Package version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.12.0 2` |

### Commits

| Commit | Subject |
| --- | --- |
| `ca0a1f0` | `docs(REQ-020): plan the required surface.window role` |
| `dcfa228` | `chore(REQ-020): start — record worktree/branch, move to in-progress` |
| `363cfe5` | `feat(REQ-020): add the required surface.window role` |
| release commit (the `v0.12.0` tag target) | `chore(REQ-020): release v0.12.0` |

### Status

**Done on `ticket/REQ-020-window-role`.** The required window role, the
unitless opacity type, the seven-path host allowlist and the generation window
geometry keys are frozen. Merge to `main` fast-forward, then create the
annotated `v0.12.0` tag on the merged release commit and push `main` plus the
tag; no existing tag moves. No runtime, assets, provisioning, composition or
app code is in this slice, and no live apply was run.

## Downstream pins (not part of this slice)

- `contracts v0.12.0` (this release).
- `dotfiles-runtime v1.5.0` — accept/emit the required window group, resolve and
  record the window host paths, render unitless opacity.
- `dotfiles-assets v0.19.0` — author window groups in every skin and the paper
  light override, remap rofi/wlogout/GTK outer slots, add the kitty `conf`
  template.
- `ags-platform v1.1.0` — window surface schema and opacity token kind (parse
  the unchanged `schemaVersion: 2` document with the new required role).
- `dotfiles-provision v0.1.63` and `dotfiles-v3` composition `v0.1.68` — later
  slices, after assets and runtime.
