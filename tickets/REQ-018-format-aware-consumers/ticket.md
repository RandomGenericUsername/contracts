---
id: REQ-018
title: "Format-aware skin consumers: non-CSS appearance artifacts"
kind: requirement
status: proposed
lane: TBD
links:
  design: dotfiles-v3/docs/110-format-aware-skin-consumers.md
  epic: dotfiles-v3/docs/epics/SKIN-CONSUMERS.md
  openspec: none
  bmad: none
worktree: .worktrees/REQ-018/
branch: ticket/REQ-018-format-aware-consumers
---

# Format-aware skin consumers: non-CSS appearance artifacts

## Requirement

Freeze the Phase 3 contract extension that lets a skin emit honest non-CSS
appearance artifacts for rofi (`.rasi`), and reserves `.conf`/`.theme` for
kitty/btop without shipping a fake CSS target. The design is
`dotfiles-v3/docs/110-format-aware-skin-consumers.md`; the epic is
`SKIN-CONSUMERS` (`W-3.1`–`W-3.7`).

- **Keep `appearance.targets` frozen.** It remains the CSS family
  (`{configDir, path}` with `path = appearance/<configDir>.css`) because every
  AGS app hard-rejects any other target shape through
  `ags-platform/ports/appearance.ts:887-940`.
- **Add an optional `appearance.artifacts` family.** Each entry is
  `{consumer, path, format}`:
  - `consumer` matches the existing safe lowercase segment;
  - `format` is `rasi | conf | theme` (CSS stays exclusively in `targets`);
  - `path` is exactly `appearance/<consumer>.<ext>` with the canonical
    extension for `format` (cross-property rule enforced by runtime/verify).
- **GTK3/GTK4 are CSS consumers with aliases.** `gtk3` and `gtk4` are ordinary
  `configDir` values; provisioning maps `config/gtk-3.0/appearance.css ->
  current/appearance/gtk3.css` and the same for 4.0. The `configDir` pattern
  does not change and dots stay forbidden.
- **Scope of the first release.** The contract accepts all four formats so the
  family is stable, but the first implementation ships only GTK3, GTK4 and
  rofi. btop stays palette-only (`.theme` needs literal hex, which the skin
  plane forbids) and kitty stays palette-only until a px→pt/colour rule is
  approved.
- **Versioning.** Additive contracts `v0.10.0`; generation manifest `version`
  stays 3; existing manifests remain valid; no existing tag moves. All in-tree
  strict validators must re-pin before an artifact-emitting runtime ships.
- **Refresh lanes.** GTK3/GTK4/rofi are `launch`; kitty is `live` only via the
  existing `SIGUSR1` reloader; btop is `live` via `SIGUSR2` but palette-only.
  No false live lane.

## Deliverables (contract slice)

1. `schemas/generation-manifest.schema.json` — optional `appearance.artifacts`
   with `consumer`, `path`, `format`; closed object; no changes to `targets`.
2. `generations.md` — the second target family, extension/format consistency,
   uniqueness, versioning and compatibility rule.
3. Positive/negative fixtures: CSS-only manifest unchanged, rasi manifest,
   duplicate consumer, wrong extension, unknown format.
4. Version bump to `v0.10.0` in `CHANGELOG.md`, `README.md`, `CONTRACT.md`,
   `pyproject.toml`, `src/cli_invocation_contract/__init__.py`, `uv.lock`,
   `tests/test_record.py`, ticket/INDEX; annotated tag on the merged release
   commit.

## Acceptance

- [ ] `appearance.artifacts` is optional; existing CSS-only generations and
      every `v0.9.0` fixture validate unchanged.
- [ ] A manifest with `{consumer: "rofi", path: "appearance/rofi.rasi",
      format: "rasi"}` validates; a duplicate consumer, a path/extension
      mismatch, an unknown format and a dot in `consumer` fail.
- [ ] `appearance.targets` semantics are byte-identical to `v0.9.0`.
- [ ] The docs state that AGS consumers ignore the new key and that strict
      schema consumers must re-pin.
- [ ] No runtime, assets, provisioning or composition pin is changed by this
      ticket.

## Open questions (from docs/110 §11)

1. Final family name: `artifacts` vs `formats`/`nonCssTargets`.
2. GTK selector allowlist frozen by assets.
3. rofi typography deferred (px vs Pango pt).
4. kitty type/units deferred; `.conf` reserved.
5. `theme` enum kept but no template shipped.
6. Manifest stays version 3.
