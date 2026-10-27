---
id: REQ-009
title: "AGS app manifest, install-list, program-tuple and palette-refresh contracts"
kind: requirement
status: done
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-009/
branch: ticket/REQ-009-ags-app-contract
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

- [x] All four JSON Schemas are present, draft-07 valid and exercised by a
      positive + negative fixture test.
- [x] The manifest schema rejects a restart mode with `holdsUnsavedState: true`.
- [x] The install-list schema rejects duplicate `app`/`instance`/config link and
      an invalid `owner`/`installDir` combination.
- [x] The program-tuple schema pins exactly the three program tags.
- [x] The refresh-result schema covers `applied|deferred|failed|skipped` and a
      retryable error.
- [x] The `palette-refresh` protocol doc matches AGS 3.1.0's string transport and
      the runtime's 5 s timeout.
- [x] The `wallpaper.state` contract note is corrected and no consumer drift gate
      breaks.
- [x] `make gates` (or the repo's equivalent) is green; CI runs the schema tests.

## Dependencies

- `ags-apps` EPIC-002 / REQ-008 architecture spine.
- `ags-platform` manifest helper and `dotfiles-runtime` consumer implementation.
- `dotfiles-v3` app-list/program-tuple owner.

## Evidence

- `ags-apps/_bmad-output/initiative-ags-standalone-apps/architecture-standalone-app-contract/architecture-standalone-app-contract.md`
  (AD-26, AD-27, AD-31, AD-34).
- `ags-apps/tickets/SPIKE-001-ags-refresh-patterns/ticket.md`.
- Current AGS string transport: `/usr/share/ags/js/lib/gtk4/app.ts:272-296`.

### Verification

Commands run from the worktree root (`.worktrees/REQ-009/`, branch
`ticket/REQ-009-ags-app-contract`, base `4f05a90`).

| Claim | Command | Result |
| --- | --- | --- |
| All four schemas are draft-07 valid and self-validating | `make schema-test` | `40 passed in 0.09s`, exit 0; `test_every_schema_is_draft_07_and_self_valid` checks each `$schema`/`$id` and `Draft7Validator.check_schema` |
| Positive + negative fixtures | `make schema-test` | every `*.valid.json` accepted and every `*.invalid.json` rejected, exit 0 |
| Manifest rejects restart + unsaved state | `uv run pytest -q tests/test_ags_app_contract.py -k restart` | passes; `restart-unsaved.invalid.json` fails at `holdsUnsavedState` (`False was expected`) |
| Install list rejects duplicate `app`/`instance`/config link | `uv run pytest -q tests/test_ags_app_contract.py -k duplicate` | 3 duplicate fixtures rejected by the schema's `x-uniqueKeys` contract gate, exit 0 |
| `owner`/`installDir` combinations | `uv run pytest -q tests/test_ags_app_contract.py -k 'install_list or fixture'` | `invalid-owner`, `invalid-install-dir`, `legacy-with-repo` and `standalone-missing-repo` are rejected, exit 0 |
| Tuple pins exactly the three program tags | `uv run pytest -q tests/test_ags_app_contract.py -k program_tuple` | schema has only `schemaVersion` + the three tag properties, `additionalProperties: false`; missing/extra/invalid tags rejected |
| Refresh result covers all statuses + retryable error | `uv run pytest -q tests/test_ags_app_contract.py -k refresh_result` | applied, deferred, failed (retryable and terminal) and skipped fixtures accepted; unknown status and failed-without-retryable rejected |
| Protocol doc matches AGS 3.1.0 string transport / 5 s | `uv run pytest -q tests/test_ags_app_contract.py -k protocol` | doc contains `ags request palette-refresh <appearance-hash> -i <instance>`, `res(JSON.stringify(`, all four response shapes, `exactly once`, `5 s`; source `/usr/share/ags/js/lib/gtk4/app.ts:272-296` |
| `wallpaper.state` is progress/UI only | `uv run pytest -q tests/test_ags_app_contract.py -k wallpaper_state` | note contains `progress/UI` and `not the palette-refresh trigger`, old `LIVE refresh` claim gone; `.md` paragraph agrees |
| Full repo gate | `make test` | `Ran 10 tests … OK` then `95 passed in 0.25s`, exit 0 |
| Symmetric regenerate-and-diff gate | `make contracts-drift` | `[ok] schema`, `[ok] python`, `[ok] typescript`, `[drift] symmetric: contract and generated/ agree`; `git diff --exit-code generated/` clean, exit 0 |
| Red/green proof that the fixtures catch defects | temporary removal of the manifest `allOf` restart rule and the install-list `x-uniqueKeys` then `uv run pytest -q tests/test_ags_app_contract.py` | red: `9 failed, 31 passed` (restart-unsaved, all three duplicate fixtures, and the key-list assertions); restored: `40 passed`, exit 0 |
| Package build still works | `make build` | `Successfully built dist/cli_invocation_contract-0.2.0.tar.gz` + wheel, exit 0 |
| CI runs the schema tests | `.github/workflows/drift.yml` | adds `make schema-test` after `make test`; no remote run in this ticket because the branch is not pushed |
| Worktree clean at closeout | `git status --porcelain` | empty after the closeout commit |

### Commits

| Commit | Subject |
| --- | --- |
| `664b706` | `chore(REQ-009): start — record worktree/branch, move to in-progress` |
| `33c87b4` | `feat(REQ-009): add the AGS app manifest, install-list, program-tuple and refresh contracts` |
| closeout commit | `docs(REQ-009): record evidence, tick acceptance, close the ticket` |

### Status

**Closed — done on `ticket/REQ-009-ags-app-contract`.** All four schemas, the
`palette-refresh` protocol and the corrected `wallpaper.state` note are in the
implementation commit; the fixture gate is green and CI runs it. No runtime, app
or host code was changed. The work is merged to `main` and tagged `v0.3.0` by the
OPS-002 release; the ticket branch itself was not pushed separately.
