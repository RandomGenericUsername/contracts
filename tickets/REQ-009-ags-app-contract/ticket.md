---
id: REQ-009
title: "AGS app manifest, install-list, program-tuple and palette-refresh contracts"
kind: requirement
status: proposed
lane: 2
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# AGS app manifest, install-list, program-tuple and palette-refresh contracts

## Requirement

Add the canonical, language-neutral contracts for the standalone AGS app
program defined by `ags-apps` EPIC-002 and its architecture spine.

Deliver:

- `schemas/ags-app-manifest.schema.json`: `schemaVersion`, `app`, `instance`,
  `configDir`, `mode: live|restart`, `holdsUnsavedState`; identity fields are one
  lowercase path segment.
- `schemas/ags-apps-install-list.schema.json`: the single `dotfiles-v3` app list
  with `app`, `installDir`, `owner: legacy|standalone`, repo/tag (standalone),
  instance, configDir, spine/XDG/config links, optional bin link, launcher,
  autostart, launch policy, bar palette pointer and cutover id.
- `schemas/program-tuple.schema.json`: the one `ags-platform` / `contracts` /
  `dotfiles-assets` tag tuple per install.
- `schemas/ags-app-refresh-result.schema.json`: runtime per-app result/log record
  (`applied|deferred|failed|skipped`, reason, retryable, timing/identity fields).
- `ags-app-refresh.md`: the fixed `palette-refresh` command protocol —
  appearance hash argument, one JSON-encoded string response on stdout, exactly
  once, applied vs deferred vs failed, 5 s caller timeout, idempotency and
  state-preservation requirements.
- Update the `wallpaper.state` contract description: it is the progress/UI event,
  not the palette-refresh trigger.

No runtime/app code lives here; this is the schema and protocol source.

## Acceptance

- [ ] All four JSON Schemas are present, draft-07 valid and exercised by a
      positive + negative fixture test.
- [ ] The manifest schema rejects a restart mode with `holdsUnsavedState: true`.
- [ ] The install-list schema rejects duplicate `app`/`instance`/config link and
      an invalid `owner`/`installDir` combination.
- [ ] The program-tuple schema pins exactly the three program tags.
- [ ] The refresh-result schema covers `applied|deferred|failed|skipped` and a
      retryable error.
- [ ] The `palette-refresh` protocol doc matches AGS 3.1.0's string transport and
      the runtime's 5 s timeout.
- [ ] The `wallpaper.state` contract note is corrected and no consumer drift gate
      breaks.
- [ ] `make gates` (or the repo's equivalent) is green; CI runs the schema tests.

## Dependencies

- `ags-apps` EPIC-002 / REQ-008 architecture spine.
- `ags-platform` manifest helper and `dotfiles-runtime` consumer implementation.
- `dotfiles-v3` app-list/program-tuple owner.

## Evidence

- `ags-apps/_bmad-output/initiative-ags-standalone-apps/architecture-standalone-app-contract/architecture-standalone-app-contract.md`
  (AD-26, AD-27, AD-31, AD-34).
- `ags-apps/tickets/SPIKE-001-ags-refresh-patterns/ticket.md`.
- Current AGS string transport: `/usr/share/ags/js/lib/gtk4/app.ts:272-296`.
