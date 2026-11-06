---
id: REQ-015
title: "Appearance plane v2: one generated appearance and one repointed hop"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-015/
branch: ticket/REQ-015-appearance-plane-v2
---

# Appearance plane v2: one generated appearance and one repointed hop

## Requirement

Replace the v1 skin plane with a single **Appearance plane v2** that composes palette, skin and
mode into one generated artifact set and one atomically repointed pointer. The decisions below
are frozen; this is a new major (`v0.7.0`), not a `v1.1` hotfix.

### Why v1 cannot be repaired in place (investigation context)

- The v1 consumer chain is `config/<app>/skin.css -> current/skins/<app>.css -> cache/skins/<hash>/<app>.css`.
  AGS adapters watch the stable first hop (`config/<app>/skin.css`), while the runtime repoints the
  second hop (`current/skins/<app>.css`). A live skin change therefore never reaches a running app.
  Palette changes do reach apps because `theme.ts` watches `current/colors.yaml`, which is the hop
  the runtime actually replaces.
- Every app's `palette-refresh` handler only calls `theme.apply()`; none re-applies the skin.
- AGS apps are raw processes today (no systemd units). Killing an `ags run` parent can leave the
  gjs child owning the D-Bus name; the live investigation observed `org.freedesktop.Notifications`
  kept by the old child until `ags quit -i notifications`.
- v1 workarounds that v2 retires: a global `border-w`/`hairline-w` cannot express per-role borders;
  hover/selected/disabled paints and small type/paddings live as template literals; clipboard
  contrast math re-derives roles; layout tokens are bar-only; `paper` depends on palette-mode
  guessing instead of explicit mode overrides.

### Deliverables

1. **`appearance.md`** — normative artifact and refresh contract:
   - runtime generation at `cache/appearance/<hash>/` containing `colors.yaml` (palette.v1 roles),
     `tokens.json` (the resolved, mode-resolved v2 token document), `appearance.json`
     (`version: 2`, skin, mode, palette hash, skin hash, generation hash, token ref) and one
     composed `<configDir>.css` per target (palette `@define-color` block + skin CSS);
   - a **single** atomically repointed hop `current/appearance -> cache/appearance/<hash>/`;
     consumer convenience links `config/<configDir>/appearance.css -> current/appearance/<configDir>.css`;
     consumers MUST watch `current/appearance` and read the config path;
   - one provider per app (composed CSS at `GTK_STYLE_PROVIDER_PRIORITY_USER` = 800, installed
     last), one monitor, one apply;
   - refresh: the existing `palette-refresh` request remains the transport, but the platform
     handler re-applies the whole appearance (palette + skin); the bar keeps the restart lane;
   - `appearanceHash = f(palette entry hash, skin entry hash, mode)`; palette and skin caches stay
     independent; appearance is their composition.
2. **Schemas** (`schemas/`): `appearance-manifest.schema.json` (v2 manifest),
   `appearance-json.schema.json` (resolved tokens, `version: 2`), and
   `appearance-artifact.schema.json` (`appearance.json` metadata). Value rules: unitless numbers
   for lengths, role/paint/shadow/blur strings, no literal hex, no transitions, no
   structure/variant.
3. **Token model v2** (nested):
   - `surface.panel|card|cell|control|pill` each with `bg`, `border`, `border-width`, `radius`,
     `padding` (plus `shadow` and `blur` on `panel`; `hover-bg` on `cell`; `font-size` and
     `font-weight` on `control`; `font-size` and `letter-spacing` on `pill`);
   - `state.hover|selected|focus|disabled` with `fill`, `ink`, `ring` role expressions and
     documented semantics;
   - `type`: `font-family`, `font-weight`, `letter-spacing`, `size-caption`, `size-meta`,
     `size-body`, `size-title`, `size-display`;
   - `ink`: `ink`, `ink-dim`, `accent`, `accent-muted`, `ink-over` (auto);
   - `layout.<app>`: namespaced numeric tokens (for example `layout.bar.panel-width`), TSX-owned
     and never emitted by templates;
   - `mode.dark` / `mode.light`: optional, same-shape group overrides selected from the palette
     mode at generation;
   - still no structure/variant tokens.
4. **Templates**: v2 placeholder flattening (`surface.panel.bg` ->
   `{{SKIN_SURFACE_PANEL_BG}}`), mode resolved before expansion, and templates have no
   conditionals.
5. **Fixtures and tests**: v2 `glass`/`flat`/`paper` manifests (v1 values converted faithfully,
   per-role/state values taken from the real app stylesheets where applicable, `paper` using
   explicit `mode.*` overrides), positive/negative schema fixtures, and tests for hex, transition,
   structure/variant, a layout token in a template, a missing mode override and an unknown surface
   role.
6. **Release**: bump to `v0.7.0`, update `CHANGELOG.md` and `README.md`, annotated tag, merge
   fast-forward to main. No changes to the runtime, platform or assets repos.

## Acceptance

- [ ] `appearance.md` defines the `cache/appearance/<hash>/` generation, its four artifact
  kinds, the single `current/appearance` hop, the stable consumer link, the inotify rationale,
  the one-provider/monitor/apply rule and the whole-appearance `palette-refresh` handling.
- [ ] `appearance.md` documents the nested v2 token model, mode resolution before template
  expansion, placeholder flattening, value/unit rules, and that templates have no conditionals.
- [ ] `schemas/appearance-manifest.schema.json` is draft-07, self-named, frozen, `schemaVersion: 2`,
  and enforces the surface roles, state roles, type/ink/layout groups and optional same-shape
  mode overrides with `additionalProperties: false` at every level.
- [ ] `schemas/appearance-json.schema.json` is draft-07, self-named, frozen, `version: 2`, and
  validates a fully resolved token document with the same group shapes as the manifest.
- [ ] `schemas/appearance-artifact.schema.json` is draft-07, self-named, frozen, `version: 2`, and
  requires `skin`, `mode`, `paletteHash`, `skinHash`, `appearanceHash`, `generationHash` and
  `tokenRef`.
- [ ] Positive `glass`/`flat`/`paper` manifests and resolved token documents validate; the v1
  values are converted faithfully and `paper` carries explicit `mode.light` overrides.
- [ ] Negatives for literal hex, transition, structure/variant, layout token in a template, a
  missing/incomplete mode override and an unknown surface role are rejected by the contract and
  tests.
- [ ] `make test`, `make skin-test` and `make schema-test` exit 0.
- [ ] `CHANGELOG.md`, `README.md`, `CONTRACT.md`, `tickets/INDEX.md`, `pyproject.toml`,
  `src/cli_invocation_contract/__init__.py`, `uv.lock` and the version test agree on `0.7.0`;
  annotated tag `v0.7.0` points at the merged release commit and no existing tag moved.

## Evidence

- v1 watch/repoint mismatch: `ags-platform/adapters/skin.ts` (`watchSkin`, `SKIN_CSS_POINTER`) and
  `ags-platform/ports/skin.ts` watch `skinCssPath` / `skinJsonPath`; the runtime repoints
  `current/skins/<app>.css` in `dotfiles-runtime/src/runtime/adapters/seeder.py`
  (`repoint_current_symlinks`, `repoint_consumer_symlinks`). The palette path works because
  `ags-platform/adapters/theme.ts` watches `current/colors.yaml`, the repointed hop.
- Palette-only handlers: `ags-apps/notifications/app.tsx:73-74`,
  `ags-apps/icme/app.tsx:32-38`, `ags-apps/wallpaper-selector/app.tsx:35-41`,
  `ags-apps/capture-tool/app.tsx:52-58`, `ags-apps/btop-theme-studio/app.tsx:31-40`,
  `ags-apps/hypr-pano/app.tsx:16-17`, `ags-apps/bar/app.tsx:141` all call `theme.apply()` and no
  skin apply.
- Raw-process failure mode: the live investigation observed a killed `ags run` parent leaving a
  gjs child owning `org.freedesktop.Notifications` until `ags quit -i notifications`.
- Real per-role/state values: `ags-apps/bar/style.css` (`.settings-surface` `border: 1.5px`,
  `.settings-card` `1px`, `.settings-net` borderless with `8px 9px` padding and hover/selected
  fills, `.settings-badge` `9.5px`/`0.05em`/`20px` radius, `.settings-rowact` `1px`/`11px`/`600`);
  `ags-apps/wallpaper-selector/style.css` and `ags-apps/capture-tool/style.css` selected/hover
  states; `ags-apps/notifications/style.css` small metadata type.
- Frozen v1 values to convert: `tests/fixtures/skin-contract/skin-manifest/{glass,flat,paper}.valid.json`.

## Non-goals

- No runtime, platform, assets or app code in this repo; those repos adopt v2 against the tag.
- No `v1.1` hotfix and no compatibility shim that keeps the v1 second-hop watch alive.
- No structure/variant tokens; no template conditionals; no new palette roles.
