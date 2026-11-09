---
id: REQ-017
title: "Host defaults: optional skin host policy and generation host identity"
kind: requirement
status: proposed
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-017/
branch: ticket/REQ-017-host-defaults
---

# Host defaults: optional skin host policy and generation host identity

## Requirement

Freeze the Phase 1 host-default contract in this repo. The design is fixed by
`dotfiles-v3/docs/109-hyprland-host-defaults.md` and the `SKIN-CONSUMERS`
epic; this slice is the contract only.

- **Opt-in per skin and per token.** The appearance manifest gains an optional
  root `[host]` policy with an explicit `inherit` allowlist and an optional
  `fallback` (`skin` or `error`, default `skin`). Existing manifests without
  `[host]` remain valid; no token type or `required` list changes.
- **Only two Phase 1 mappings.** `surface.panel.radius` follows Hyprland
  `decoration:rounding`; `surface.panel.border-width` follows
  `general:border_size`. Gaps, padding, type, colours, structure and literal
  hex are never host-injectable.
- **Precedence.** A value supplied by the selected `mode.<mode>` group wins
  over the host. Otherwise an inherited token uses the live host value. A
  token not in `inherit` always uses the skin’s concrete value. Headless or
  invalid host values fall back to the skin value; `fallback = "error"` fails
  the generation closed.
- **Identity.** `hostHash` is canonical JSON of the host mapping version and
  only the values that actually participated. It enters `appearance.v3`, the
  generation intent and the generation hash. No-host generations still use
  the v3 formula with a `-` placeholder (one-time identity churn is
  accepted). The daemon queue key stays host-free; the host is read inside
  `converge.lock`.
- **Generation manifest.** An optional `host` block records `source`,
  `version`, `fingerprint` and only the participating `defaults`.
  `intent.host` is required when `host` is present and must equal
  `host.fingerprint`; the JSON Schema expresses presence, while runtime
  validation enforces equality.
- **Compatibility.** A generation without a host block is unchanged in shape
  and remains valid. The v2 appearance token vocabulary and resolved
  `tokens.json` remain concrete; no token becomes `number | "host"`.

## Deliverables

1. `schemas/appearance-manifest.schema.json` — optional root `host` policy:
   closed object, required non-empty unique `inherit` enum exactly
   `surface.panel.radius` and `surface.panel.border-width`, optional
   `fallback` enum `skin|error` defaulting to `skin`.
2. `schemas/generation-manifest.schema.json` — optional `host` block
   (`source`, `version`, `fingerprint`, `defaults`) and optional `intent.host`;
   `intent.host` is required when `host` is present. The block records only
   participating values.
3. `appearance.md` — host policy, precedence, fallback and the
   `appearance.v3` identity (`hostHash` participation; no-host `-`).
4. `generations.md` — host block shape, identity rules, queue-key rule and
   equality/documentation rule.
5. Positive/negative fixtures and tests for the host policy and generation
   host shape, including a semantic mismatch fixture for `intent.host`.
6. Version bump to `v0.9.0`: `CHANGELOG.md`, `README.md`, `CONTRACT.md`,
   `pyproject.toml`, `src/cli_invocation_contract/__init__.py`, `uv.lock`,
   `tests/test_record.py`, ticket/INDEX; annotated tag `v0.9.0` on the merged
   release commit; push `main` and the tag.

## Acceptance

- [ ] The appearance schema accepts optional `[host]` with a closed object,
  non-empty unique `inherit`, exactly the two Phase 1 token paths and
  `fallback` `skin|error` (default `skin`); manifests without host still
  validate.
- [ ] The generation schema accepts an optional host block with `source`,
  `version`, `fingerprint` and non-empty `defaults`; `intent.host` is required
  when host is present; a no-host manifest remains valid.
- [ ] Fixtures prove valid host manifests and reject empty/duplicate/unknown
  inherit, bad fallback, host without `intent.host`, empty defaults, unknown
  defaults and invalid host source/hash.
- [ ] A semantic fixture proves `intent.host != host.fingerprint` is rejected
  by the documented runtime rule; the documentation states the schema cannot
  express equality.
- [ ] `appearance.md` documents mode-override > host > skin fallback,
  headless/invalid fallback, `fallback="error"` fail-closed, the two-token
  allowlist and the no-gaps/padding/type/colours/no-literal-hex rule.
- [ ] `appearance.v3` is documented with `hostHash` only for participating
  values and a `-` placeholder when none participate; queue keys stay
  host-free.
- [ ] `make test`, `make skin-test`, `make appearance-test`,
  `make generations-test`, `make schema-test` and `make contracts-drift` exit 0.
- [ ] Version metadata and `tests/test_record.py` agree on `0.9.0`; annotated
  tag `v0.9.0` points at the merged release commit; no existing tag moved.

## Evidence

- Design and criteria: `dotfiles-v3/docs/109-hyprland-host-defaults.md`
  §Decision, §Phase 1 scope, §Contract criteria H-1.1–H-1.5,
  §Runtime criteria H-2.5–H-2.7, §Verification matrix.
- Epic sequencing: `dotfiles-v3/docs/epics/SKIN-CONSUMERS.md` §Sequencing
  and collision rules (contract release, then runtime/assets, then
  composition).
- Live evidence: Hyprland 0.56.2 effective values come from
  `hyprctl -j getoption`, not config text; the live host reads rounding 0 /
  border 1 while the config text names 8 / 3. The current terminal skin
  publishes 0 / 1 by coincidence.
- Frozen schemas before this slice: `schemas/appearance-manifest.schema.json`
  is `schemaVersion: 2` with `additionalProperties: false` at the root and no
  `host`; `schemas/generation-manifest.schema.json` is `version: 3` with no
  host block.

## Verification

Commands run from the worktree root (`.worktrees/REQ-017/`, branch
`ticket/REQ-017-host-defaults`, base `8906f1a`). Filled after implementation.

| Claim | Command | Result |
| --- | --- | --- |
| Full repo gate | `make test` | pending |
| Frozen v1 skin gates | `make skin-test` | pending |
| Appearance contract | `make appearance-test` | pending |
| Generation contract | `make generations-test` | pending |
| AGS app contract | `make schema-test` | pending |
| Symmetric drift gate | `make contracts-drift` | pending |
| Package version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | pending |

### Commits

| Commit | Subject |
| --- | --- |
| pending | `docs(tickets): plan the host-defaults contract (REQ-017)` |
| pending | `chore(REQ-017): start — record worktree/branch, move to in-progress` |
| pending | `feat(REQ-017): freeze the host-defaults contract` |
| pending | `chore(REQ-017): release v0.9.0` |

### Status

**Proposed.** No runtime, assets, composition, provisioning or app code is in
this slice. Do not run a live apply.

## Downstream pins (not part of this slice)

- `contracts v0.9.0` (this release).
- `dotfiles-assets v0.15.0` — `[host]` on glass/paper; terminal/flat explicit;
  re-vendor `v0.9.0`.
- `dotfiles-runtime v1.1.0` — port/adapter/resolver/`appearance.v3`/manifest/
  GC/doctor.
- `dotfiles-v3 v0.1.56` — composition cutover.

## Non-goals

- No runtime adapter, resolver, hashing implementation, doctor change or GC
  change in this repo.
- No assets manifests/templates, composition pins, provisioning, apps or live
  state.
- No gaps/padding/type/colour mapping, no literal hex, no `"host"` sentinel
  token, no structural leakage.
- No Phase 2/3 mappings or socket2 watcher.
