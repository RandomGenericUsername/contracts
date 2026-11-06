---
id: REQ-016
title: "Generations v3: one committed generation, one convergence pipeline, generation-bound apply/ack"
kind: requirement
status: proposed
lane: 2
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# Generations v3: one committed generation, one convergence pipeline, generation-bound apply/ack

## Requirement

Freeze the **Generations v3** contract in this repo. The design is fixed by
`dotfiles-v3/docs/107-generations-v3.md` and is not open to workarounds:

- **Generation is the unit.** A generation is
  `state/generations/<genHash>/` with `manifest.json`, `palette/`,
  `appearance/<configDir>.css` + `appearance/tokens.json`, `icons/`, `effects/`
  and wallpaper. `state/current -> generations/<genHash>` is the only commit
  pointer and moves with one atomic `rename`. Consumers read through
  `current/`.
- **One convergence pipeline.** `converge(intent)` is the only mutation path;
  it runs through the daemon job queue over the existing event bus, or the CLI
  runs the same function under the same exclusive kernel `flock` with no retry
  loop. There is no second pipeline and no publish-then-fail path.
- **Generation-bound apply/ack.** The request carries the `genHash`; the app
  applies that exact generation (verifying `current/manifest.json` or reading
  the generation directory) and answers with that same `genHash`. A mismatch
  is deferred/retryable, and the ledger records `applied` only on an exact
  match.
- **Artifact locality.** Runtime writes only under `state/`, never under
  `<install>/` or an app tag. The platform reads
  `$XDG_STATE_HOME/dotfiles/current/appearance/<configDir>.css` and watches
  `current` (one hop).
- **No polling as correctness.** inotify for `desired.json`/`current`, D-Bus
  `NameOwnerChanged` for AGS registration, and systemd `JobRemoved`/`--wait`
  for restarts. A timeout is an abort/report bound, never a readiness signal.
- **Lane policy.** Each app declares `live` or `restart`; exactly one is
  enforced. Unit management changes *how* a restart happens, not *whether*.
- **Mode is a generation input and part of generation identity.**

This is a new major contract (`v0.8.0`). It documents the v3 interface and
freezes the machine-readable manifest + refresh result schemas; it changes no
runtime, platform, assets, provisioning or app code.

## Deliverables

1. **`generations.md`** — normative v3 interface: generation layout, manifest
   fields, the single-pointer commit transaction and crash matrix, consumer
   read/watch rules, artifact locality/immutability, lane policy, mode
   identity, GC/pin contract, no-polling rules and the refresh protocol.
2. **`schemas/generation-manifest.schema.json`** — draft-07, `version: 3`,
   `generationHash` (64 lowercase hex), created/committed metadata, `layers`
   (`wallpaper`, `palette`, optional `effects`/`icons` with entry hashes and
   relative paths), `skin {name, entryHash, mode}`, `appearance {tokensPath,
   targets[]}`, `mode`, `intent`/`source` metadata; required fields,
   `additionalProperties: false`, structure/variant and literal-hex rejection.
   Positive and negative fixtures cover a stale/unknown layer, a wrong hash, a
   missing mode and extra keys.
3. **`appearance-refresh.md` + `schemas/appearance-refresh-result.schema.json`**
   — request `["appearance-refresh", "<genHash>"]`; response union
   `{applied: genHash}` | `{deferred: "reason", genHash}` |
   `{failed: "reason", retryable: bool, genHash}`; the response hash MUST equal
   the request; the app resolves the requested generation and never acks
   "whatever current is". The v2 `palette-refresh` docs stay in the repo,
   marked superseded for provenance.
4. **Program-tuple/manifest schema notes** — update only if required. The v2
   appearance token vocabulary and built-in skins are unchanged.
5. **Tests and release** — schema fixtures, response/ack mismatch rejection,
   protocol/doc pins, version bump to `v0.8.0`, `CHANGELOG.md`/`README.md`,
   annotated tag `v0.8.0`, fast-forward merge and push of `main` + tag.

## Acceptance

- [ ] `generations.md` freezes the generation layout, manifest fields, single
  pointer commit and crash matrix, consumer read/watch rules, artifact
  locality/immutability, lane policy, mode identity, GC/pin contract,
  no-polling rules and refresh protocol.
- [ ] `schemas/generation-manifest.schema.json` is draft-07, self-named,
  frozen, `version: 3`, requires every manifest field and rejects stale/unknown
  layers, wrong hashes, missing mode, extra keys, structure/variant and
  literal hex.
- [ ] Positive/negative generation-manifest fixtures exist and pass/fail as
  named by the tests.
- [ ] `appearance-refresh.md` freezes the `["appearance-refresh", "<genHash>"]`
  request and the three response variants, requires the response hash to equal
  the request, and pins the "resolve the requested generation" rule.
- [ ] `schemas/appearance-refresh-result.schema.json` is draft-07, self-named,
  frozen, accepts exactly the three v3 variants and rejects the old boolean
  `{"ok":true}` ack.
- [ ] Tests reject a response/ack whose hash differs from the request and pin
  the protocol and documentation statements.
- [ ] `ags-app-refresh.md` remains for provenance and is marked superseded by
  the v3 protocol; the v2 appearance token vocabulary and skins are unchanged.
- [ ] `make test`, `make skin-test`, `make appearance-test` and
  `make schema-test` exit 0.
- [ ] `CHANGELOG.md`, `README.md`, `CONTRACT.md`, `tickets/INDEX.md`,
  `pyproject.toml`, `src/cli_invocation_contract/__init__.py`, `uv.lock` and
  the version test agree on `0.8.0`; annotated tag `v0.8.0` points at the merged
  release commit and no existing tag moved.

## Evidence

- Frozen design: `dotfiles-v3/docs/107-generations-v3.md` §0 (decisions),
  §2.1 (layout), §2.2 (manifest), §2.3 (commit transaction), §2.4 (crash
  matrix), §2.5 (one convergence function), §2.6 (generation-bound refresh),
  §2.7 (artifact locality), §2.8 (lane policy), §2.9 (event-driven rules) and
  §2.10 (GC/pin).
- Multi-pointer skew and two-pipeline evidence: the same RFC §1.1–§1.6 cites
  `dotfiles-runtime/src/runtime/adapters/seeder.py:660-807`,
  `.../application/reconcile.py:308-326`,
  `.../adapters/invalidation.py:140-173`, `.../cli/main.py:2096-2240` and the
  live `state/current` listing.
- Boolean ack without a generation: `contracts/ags-app-refresh.md:64-78`
  (frozen v2 table) and the RFC §1.3 evidence.

## Non-goals

- No runtime, platform, assets, provisioning or app code in this repo.
- No second pointer, second pipeline, "apply whatever current is" ack, or
  retry loop that hides a missing event.
- No change to the v2 appearance token vocabulary, built-in skins or program
  tuple fields.
