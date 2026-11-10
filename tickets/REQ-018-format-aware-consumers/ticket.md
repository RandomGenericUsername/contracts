---
id: REQ-018
title: "Format-aware skin consumers: non-CSS appearance artifacts"
kind: requirement
status: done
lane: 2
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
- **Scope of the first release.** The contract accepts all three non-CSS
  formats so the family is stable, but the first implementation ships only
  GTK3, GTK4 and rofi. btop stays palette-only (`.theme` needs literal hex,
  which the skin plane forbids) and kitty stays palette-only until a
  px→pt/colour rule is approved.
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

- [x] `appearance.artifacts` is optional; existing CSS-only generations and
      every `v0.9.0` fixture validate unchanged.
- [x] A manifest with `{consumer: "rofi", path: "appearance/rofi.rasi",
      format: "rasi"}` validates; a duplicate consumer, a path/extension
      mismatch, an unknown format and a dot in `consumer` fail.
- [x] `appearance.targets` semantics are byte-identical to `v0.9.0`.
- [x] The docs state that AGS consumers ignore the new key and that strict
      schema consumers must re-pin.
- [x] No runtime, assets, provisioning or composition pin is changed by this
      ticket.

## Evidence

- Design and criteria: `dotfiles-v3/docs/110-format-aware-skin-consumers.md`
  §2.1 (two target families), §2.3 (versioning), §8 Phase 3A-1 (`F-1.1`–`F-1.4`)
  and §11 (open questions).
- Frozen baseline: `schemas/generation-manifest.schema.json` at `v0.9.0` has
  `appearance.required = ["tokensPath", "targets"]` and no `artifacts`
  property; commit `5c9fd61` is the `v0.9.0` release.
- AGS unknown-key tolerance: `ags-platform/ports/appearance.ts:889-983`
  (`parseGenerationManifest` reads `version`, `generationHash`,
  `appearance.tokensPath`, `appearance.targets`, `mode`, `skin.mode` and
  `intent.mode`, then returns a fresh object; it never rejects an unknown
  `appearance` key).
- Contract fixture handoff: `tests/fixtures/generations-contract/
  generation-manifest/artifacts-rasi.valid.json` is the input for a downstream
  AGS parser test; this repo has no TypeScript parser harness.

## Verification

Commands run from the worktree root (`.worktrees/REQ-018/`, branch
`ticket/REQ-018-format-aware-consumers`, base `5c9fd61`).

| Claim | Command | Result |
| --- | --- | --- |
| Full repo gate | `make test` | `Ran 10 tests ... OK`; `432 passed in 5.67s`, exit 0 |
| Generation contract | `make generations-test` | `101 passed in 0.80s`, exit 0 |
| AGS app contract | `make schema-test` | `40 passed in 0.23s`, exit 0 |
| Appearance contract | `make appearance-test` | `112 passed in 3.25s`, exit 0 |
| Symmetric drift gate | `make contracts-drift` | `[ok]` symmetric; regenerate-and-diff clean, exit 0 |
| Lockfile check | `uv lock --check` | `Resolved 13 packages in 1ms`, exit 0 |
| Package version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.10.0 2` |

### Commits

| Commit | Subject |
| --- | --- |
| `679a52d` | `docs(REQ-018): open format-aware consumer ticket` |
| `c8a3fb9` | `chore(REQ-018): start — record worktree/branch, move to in-progress` |
| `0299e90` | `feat(REQ-018): freeze format-aware appearance artifacts` |
| release commit (the `v0.10.0` tag target) | `chore(REQ-018): release v0.10.0` |

### Status

**Done on `ticket/REQ-018-format-aware-consumers`.** The optional non-CSS
`appearance.artifacts` family, its cross-property runtime rules and the
CSS-family compatibility statement are frozen. Merge to `main` fast-forward,
then create the annotated `v0.10.0` tag on the merged release commit and push
`main` plus the tag; no existing tag moves. No runtime, assets, provisioning,
composition or app code is in this slice, and no live apply was run.

## Downstream handoff (not part of this slice)

- Next runtime slice: Phase 3A-3 `F-3.1`/`F-3.3`/`F-3.4` — suffix→(family,
  format, output) discovery with fail-closed unknown suffixes, a format value
  renderer, publication of `appearance.artifacts` in the manifest, and
  generation-store copy/verify of `appearance/<consumer>.<ext>`.
- Then assets Phase 3A-2 (`gtk3`, `gtk4`, `rofi` templates) and provisioning
  Phase 3A-4 links/imports before the composition cutover.
- All downstream repositories pin `contracts v0.10.0`; any strict validator
  still on `v0.9.0` must re-pin before an artifact-emitting runtime ships.

## Open questions (from docs/110 §11)

1. Final family name: `artifacts` vs `formats`/`nonCssTargets` (this release
   uses `artifacts`).
2. GTK selector allowlist frozen by assets (not expressible in this schema).
3. rofi typography deferred (px vs Pango pt); no type tokens ship.
4. kitty type/units deferred; `.conf` reserved.
5. `theme` enum kept but no template shipped (btop stays palette-only).
6. Manifest stays version 3; additive optional family.
