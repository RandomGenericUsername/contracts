---
id: REQ-019
title: "Host-delegated rectangle radii: expand the skin allowlist"
kind: requirement
status: done
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-019/
branch: ticket/REQ-019-host-rectangle-radii
---

# Host-delegated rectangle radii: expand the skin allowlist

## Requirement

Expand the frozen Phase 1 host-default allowlist from the outer panel only to
the skin's **rectangle radii**. The allowlist is exactly:

- `surface.panel.radius`
- `surface.panel.border-width`
- `surface.card.radius`
- `surface.control.radius`
- `surface.cell.radius`

`surface.pill.radius` stays **explicit and invalid** in `[host].inherit`: the
pill's capsule identity is the skin's own decision and must not be flattened by
the host rounding value. No other path is delegable -- no card/cell/control
border width, padding, gap, type, paint, colour, state or `layout.<app>` path.

- **Outer and inner rectangle roles.** The host rounding value may feed the
  outer panel and the inner card/control/cell rectangles when a skin names
  them. Border width expands only for `surface.panel.border-width`; there is no
  card/control/cell border-width delegation.
- **Precedence unchanged.** Mode override > host > skin fallback. A token not
  named in `inherit` stays the skin's explicit value.
- **Generation snapshot unchanged in shape.** The host `defaults` object gains
  the same four additional rectangle-radius keys so a participating inner
  radius can be recorded; all values remain finite non-negative numbers and
  the existing two-key snapshot remains valid.
- **Compatibility.** Existing `[host]` policies with only the two panel paths
  remain valid, every existing manifest/generation fixture stays valid, and no
  token type or required list changes. Additive contracts release `v0.11.0`.

## Deliverables

1. `schemas/appearance-manifest.schema.json` -- the `host.inherit` enum lists
   exactly the five paths above and the descriptions state the rectangle-radius
   rule and the pill exclusion.
2. `schemas/generation-manifest.schema.json` -- `host.defaults` accepts the
   five logical paths (radii `0..64`, panel border width `0..16`).
3. `appearance.md`, `skins.md`, `generations.md` -- the expanded allowlist,
   outer/inner rectangle roles, the intentional pill exclusion, the unchanged
   precedence and the panel-only border-width rule.
4. Positive/negative fixtures: all five paths, each inner radius individually,
   the old two-path policy, pill rejected, unknown path rejected; existing
   fixtures stay valid. Generation fixtures cover the expanded defaults.
5. Version bump to `v0.11.0` in `CHANGELOG.md`, `README.md`, `CONTRACT.md`,
   `pyproject.toml`, `src/cli_invocation_contract/__init__.py`, `uv.lock`,
   `tests/test_record.py`, ticket/INDEX; annotated tag `v0.11.0` on the merged
   release commit; push `main` and the tag.

## Acceptance

- [x] The appearance host enum is exactly the five rectangle paths.
- [x] `surface.pill.radius` is rejected; every unknown/padding/colour/layout
      path is rejected.
- [x] Old two-path host policies and every existing manifest fixture validate.
- [x] The generation host `defaults` object accepts the five paths and still
      accepts the two-path snapshot.
- [x] Docs state rectangle-radii delegation, the pill exclusion, unchanged
      precedence and no border-width expansion beyond the panel.
- [x] `make test`, `make skin-test`, `make appearance-test`,
      `make generations-test`, `make schema-test` and `make contracts-drift`
      exit 0.
- [x] Version metadata and `tests/test_record.py` agree on `0.11.0`; annotated
      tag `v0.11.0` points at the merged release commit; no existing tag moves.

## Evidence

- Frozen baseline: `schemas/appearance-manifest.schema.json` host
  `inherit.items.enum` is exactly `surface.panel.radius` and
  `surface.panel.border-width` at `v0.10.0` (commit `8af8aca`).
- Frozen generation baseline: `schemas/generation-manifest.schema.json`
  `host.defaults.properties` names the same two paths at `v0.10.0`.
- Positive fixtures: `host.valid.json` (all five), `host-old-two-path.valid.json`,
  `host-card-radius.valid.json`, `host-control-radius.valid.json` and
  `host-cell-radius.valid.json` under
  `tests/fixtures/appearance-contract/appearance-manifest/`.
- Negative fixtures: `host-pill-inherit.invalid.json` and
  `host-unknown-inherit.invalid.json` (`surface.card.border-width`).
- Generation fixtures: `host-rectangles.valid.json`,
  `host-pill-default.invalid.json` and the updated
  `host-unknown-default.invalid.json` under
  `tests/fixtures/generations-contract/generation-manifest/`; the legacy
  `host.valid.json` two-key snapshot still validates.

## Verification

Commands run from the worktree root (`.worktrees/REQ-019/`, branch
`ticket/REQ-019-host-rectangle-radii`, base `e5dabc1`).

| Claim | Command | Result |
| --- | --- | --- |
| Full repo gate | `make test` | `Ran 10 tests ... OK`; `448 passed in 2.72s`, exit 0 |
| Frozen v1 skin gates | `make skin-test` | `110 passed in 0.61s`, exit 0 |
| Appearance contract | `make appearance-test` | `124 passed in 1.70s`, exit 0 |
| Generation contract | `make generations-test` | `105 passed in 0.39s`, exit 0 |
| AGS app contract | `make schema-test` | `40 passed in 0.10s`, exit 0 |
| Symmetric drift gate | `make contracts-drift` | `[ok]` symmetric; regenerate-and-diff clean, exit 0 |
| Lockfile check | `uv lock --check` | `Resolved 13 packages in 0.76ms`, exit 0 |
| Package version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.11.0 2` |

### Commits

| Commit | Subject |
| --- | --- |
| `e5dabc1` | `docs(REQ-019): plan the rectangle-radii host allowlist` |
| `acc6a7b` | `chore(REQ-019): start — record worktree/branch, move to in-progress` |
| `c49c116` | `feat(REQ-019): delegate rectangle radii to the host` |
| release commit (the `v0.11.0` tag target) | `chore(REQ-019): release v0.11.0` |

### Status

**Done on `ticket/REQ-019-host-rectangle-radii`.** The five-path host allowlist,
the panel-only border width, the pill exclusion and the expanded generation
host snapshot are frozen. Merge to `main` fast-forward, then create the
annotated `v0.11.0` tag on the merged release commit and push `main` plus the
tag; no existing tag moves. No runtime, assets, provisioning, composition or
app code is in this slice, and no live apply was run.

## Downstream pins (not part of this slice)

- `contracts v0.11.0` (this release).
- `dotfiles-assets v0.18.0` -- delegate the rectangle radii in the shipped
  skin manifests and re-vendor `v0.11.0`.
- `dotfiles-runtime v1.4.0` -- resolve and record the additional delegated
  rectangle radii, then re-pin `v0.11.0`.
- Engine/composition -- later slice, after assets and runtime.

## Non-goals

- No runtime resolver/identity/manifest implementation.
- No assets skins/templates, provisioning, composition, apps or live apply.
- No pill, border-width (beyond the panel), padding, gap, type, paint, colour,
  state or layout delegation.
