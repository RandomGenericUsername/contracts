---
id: REQ-019
title: "Host-delegated rectangle radii: expand the skin allowlist"
kind: requirement
status: in-progress
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

- [ ] The appearance host enum is exactly the five rectangle paths.
- [ ] `surface.pill.radius` is rejected; every unknown/padding/colour/layout
      path is rejected.
- [ ] Old two-path host policies and every existing manifest fixture validate.
- [ ] The generation host `defaults` object accepts the five paths and still
      accepts the two-path snapshot.
- [ ] Docs state rectangle-radii delegation, the pill exclusion, unchanged
      precedence and no border-width expansion beyond the panel.
- [ ] `make test`, `make skin-test`, `make appearance-test`,
      `make generations-test`, `make schema-test` and `make contracts-drift`
      exit 0.
- [ ] Version metadata and `tests/test_record.py` agree on `0.11.0`; annotated
      tag `v0.11.0` points at the merged release commit; no existing tag moves.

## Evidence

- Frozen baseline: `schemas/appearance-manifest.schema.json` host
  `inherit.items.enum` is exactly `surface.panel.radius` and
  `surface.panel.border-width` at `v0.10.0`.
- Frozen generation baseline: `schemas/generation-manifest.schema.json`
  `host.defaults.properties` names the same two paths at `v0.10.0`.
- Existing fixtures: `tests/fixtures/appearance-contract/appearance-manifest/
  host.valid.json` and `tests/fixtures/generations-contract/generation-manifest/
  host.valid.json`.

## Verification

Commands run from the worktree root (`.worktrees/REQ-019/`, branch
`ticket/REQ-019-host-rectangle-radii`, base `8af8aca`). Filled after
implementation.

| Claim | Command | Result |
| --- | --- | --- |

### Commits

| Commit | Subject |
| --- | --- |

### Status

**Proposed.** Contract-only slice. No runtime, assets, provisioning,
composition, app or live-state change.

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
