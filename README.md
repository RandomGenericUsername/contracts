# contracts

Canonical contract sources for the AGS platform, one repo.

1. **AGS event contract** (`org.dotfiles.Events`) — `event-contract.json` + `event-contract.xml`
   and the bindings generated from them.
2. **Runtime ↔ CLI invocation contract** — `invocation-contract.json` and the
   `cli-invocation-contract` package (`cli_invocation_contract`).
3. **Standalone AGS app contract** — `schemas/ags-app-manifest.schema.json`,
   `schemas/ags-apps-install-list.schema.json`, `schemas/program-tuple.schema.json`,
   `schemas/ags-app-refresh-result.schema.json`, and the fixed `palette-refresh`
   protocol in `ags-app-refresh.md`. Draft-07 schemas with positive/negative
   fixtures (`tests/test_ags_app_contract.py`), consumed by `dotfiles-v3`,
   `dotfiles-provision`, `dotfiles-runtime`, `ags-platform`, and every app repo.
4. **Appearance plane v2** — `appearance.md` plus
   `schemas/appearance-manifest.schema.json`, `schemas/appearance-json.schema.json`
   and `schemas/appearance-artifact.schema.json`. The nested
   surface/state/type/ink/layout/mode token model and the composed-sheet rules.
   v2 supersedes the frozen v1 skin-plane artifacts; there is no v1.1 hotfix.
5. **Generations v3** — `generations.md` plus
   `schemas/generation-manifest.schema.json`,
   `appearance-refresh.md` and
   `schemas/appearance-refresh-result.schema.json`. One immutable
   `state/generations/<genHash>/` unit, one atomic `state/current` pointer, one
   `converge(intent)` pipeline (daemon queue or CLI `flock` fallback), and a
   generation-bound `appearance-refresh` apply/ack. The v2 appearance token
   vocabulary and skins are unchanged.

The event contract is the single source of truth for the runtime ↔ AGS event seam. It is
consumed by:

- the Python runtime (`dotfiles-v3` / `src/runtime`), and
- `ags-platform` (the event-contract client).

The invocation contract is the single source of truth for how the runtime invokes the four
installed consoles (`csg`, `weg`, `itr`, `tpr`): argv template, required env keys and injected
overrides, required artifacts, exit-code semantics, default timeout. It is **versioned**, and the
Python runtime plus **all four CLIs** pin the **same `contracts` tag** — not merely a compatible
range — so one record and one conformance kit serve five consumers. A contract change is a new
tag that every consumer re-pins; literals are not duplicated in consumer tests.

## Contract files

- `event-contract.json` — the machine-readable event contract.
- `event-contract.xml` — the D-Bus interface definition.
- `invocation-contract.json` — the runtime ↔ CLI invocation contract, one record per CLI.
- `CONTRACT.md` — field-by-field reference for the invocation contract, citing the evidence
  report (`S1`) section for every value.
- `schemas/ags-app-manifest.schema.json` — the per-app identity, mode and
  unsaved-state manifest (`app.manifest.json`).
- `schemas/ags-apps-install-list.schema.json` — the single dotfiles-v3 app list
  and ownership source (`apps.yaml`).
- `schemas/program-tuple.schema.json` — the one `ags-platform` / `contracts` /
  `dotfiles-assets` tag tuple per install.
- `schemas/ags-app-refresh-result.schema.json` — the runtime-owned per-app
  refresh result/log record (v2 provenance; the v3 ack is
  `schemas/appearance-refresh-result.schema.json`).
- `generations.md` — the frozen Generations v3 interface: the
  `state/generations/<genHash>/` layout, the manifest, the single atomic
  `state/current` commit and crash matrix, consumer read/watch rules, artifact
  locality/immutability, lane policy, mode identity, GC/pins, no-polling rules
  and the refresh protocol.
- `schemas/generation-manifest.schema.json` — the v3 generation manifest
  (`version: 3`, generation hash, created/committed metadata, layer entry
  hashes + relative paths, skin, appearance targets, mode and intent/source).
- `appearance-refresh.md` — the generation-bound
  `["appearance-refresh", "<genHash>"]` request and the
  applied/deferred/failed response union; a response hash must equal the
  request.
- `schemas/appearance-refresh-result.schema.json` — the v3 refresh response
  union (`applied`, `deferred`, `failed`) with a required generation hash.
- `appearance.md` — the Appearance plane v2 token/composition contract (nested
  v2 token model, mode resolution, template flattening, one-provider
  composition, systemd user units, drift gates, built-in skins). Its pointer
  and `palette-refresh` mechanics are superseded by `generations.md` and
  `appearance-refresh.md`; the token vocabulary and skins are unchanged.
- `schemas/appearance-manifest.schema.json` — the v2 authored manifest
  (`schemaVersion: 2`, nested surface/state/type/ink/layout groups, optional
  same-shape `mode.dark`/`mode.light` overrides, structure/variant forbidden).
- `schemas/appearance-json.schema.json` — the resolved, mode-resolved
  `tokens.json` token map (`version: 2` plus the five groups), validated without
  the manifest wrapper.
- `schemas/appearance-artifact.schema.json` — `appearance.json` metadata
  (`version: 2`, skin, mode, palette/skin/appearance/generation hashes and the
  `tokens.json` ref).
- `schemas/skin-token.schema.json`, `schemas/skin-manifest.schema.json`,
  `schemas/skin-json.schema.json`, `skins.md` — the frozen v1 skin-plane
  contract. Superseded by the Appearance plane v2; retained as the historical
  source for the existing v1 fixtures and gates.
- `ags-app-refresh.md` — the v2 `palette-refresh` request/response protocol,
  retained for provenance and superseded by `appearance-refresh.md`.

## The `cli-invocation-contract` package

- `src/cli_invocation_contract/__init__.py` — `CONTRACT_VERSION`, `load(path=None)`, `get(cli)`;
  stdlib only, no runtime dependencies.
- `src/cli_invocation_contract/testkit.py` — exactly two assertions:
  `assert_consumer_invocation(record, cli, argv, env)` and
  `assert_cli_writes_artifacts(record, cli, run, cwd)`.
- `tests/` — record completeness, loader behaviour, and positive/negative kit paths against a
  fake CLI (never a real binary).
- `Makefile` — `make sync` (uv), `make test` (event-contract unittest + schema fixtures +
  pytest), `make schema-test` (AGS app contract fixtures), `make skin-test` (skin-plane
  fixtures), `make appearance-test` (appearance-plane v2 fixtures),
  `make generations-test` (Generations v3 manifest + refresh-result fixtures),
  `make build` (sdist + wheel).
  The wheel carries `invocation-contract.json` as package data, so `load()` works from an
  installed tag.

## Tooling here

- **BMAD-METHOD:** `.agents/skills/` (`bmad`, `bmad-build`, `bmad-architecture`, `bmad-product-brief`, `bmad-spec`).
- **OpenSpec:** `openspec/` (spec-driven). Start: `/opsx-propose "your idea"`.
- **Tickets:** `tickets/` (see `INDEX.md`, `LIFECYCLE.md`); route with `/triage`.

## Status

The event, invocation and AGS app seams are live. The AGS event contract and generated bindings
landed in REQ-001–REQ-005; the invocation contract is REQ-006, released as `v0.1.0` (AD-9) on
`48cf3cf`, then `v0.2.0` with `cli-invocation-contract` 0.2.0 (`DATA_VERSION` `2`) and the
`itr` record's `ICON_RENDERER__TEMPLATES__DIR` env key (REQ-008).

`v0.3.0` ships the standalone AGS app contract (REQ-009): the manifest, install-list,
program-tuple and refresh-result schemas plus the fixed `palette-refresh` protocol, and bumps
`cli-invocation-contract` to 0.3.0 (`CONTRACT_VERSION` `0.3.0`, `DATA_VERSION` `2`, invocation
data unchanged). It is schema/protocol source only, with no runtime or app code in this repo —
see `CHANGELOG.md` and the releases.

`v0.4.0` (`cli-invocation-contract` 0.4.0) adds the `tpr` theme-producer record (REQ-010):
`tpr generate {wallpaper}` with the eight `--format` values, the `THEME__OUTPUT__*` env overrides,
the eight exact consumer artifacts and a 60 s timeout. `DATA_VERSION` stays `2` and the `csg`,
`weg` and `itr` records are unchanged. `theme.json` is deliberately not part of the record — see
`CONTRACT.md` and `CHANGELOG.md`.

`v0.5.0` (`cli-invocation-contract` 0.5.0) adds the frozen skin-plane contract (REQ-011): the
23-token vocabulary and the six-group manifest schemas, plus `skins.md` for selection, cache key,
appearance hash, refresh lanes and the one-provider composition rule. `DATA_VERSION` stays `2`
and the invocation records are byte-identical; the skin schemas are repo-root sources, not wheel
package data.

`v0.5.1` (`cli-invocation-contract` 0.5.1) is a patch that freezes the skin value/unit convention
(REQ-012): the twelve numeric tokens are unitless JSON numbers, CSS expansion renders them as
`<number>px`, and `cell-pad` is the only `"Npx Npx"` string token. The vocabulary is unchanged;
`DATA_VERSION` stays `2` and the invocation records are byte-identical.

`v0.5.2` (`cli-invocation-contract` 0.5.2) is a patch that freezes the skin artifact interface
(REQ-013): the shared `<configDir>.gtk.css.j2` template set, the `current/skins/<configDir>.css`
+ shared `current/skin.json` outputs, the consumer pointers, and the grouped
`schemas/skin-json.schema.json`. The 23-token vocabulary is unchanged; `DATA_VERSION` stays `2`
and the invocation records are byte-identical.

`v0.6.0` (`cli-invocation-contract` 0.6.0) adds the `shape.hairline-w` token (REQ-014): `border-w`
now owns only the outer panel/frame border while `hairline-w` owns the card tile, row action and
badge hairlines, and the row/cell stays borderless. The vocabulary becomes 24 tokens; the layout
tokens are consumed only by widgets through `skinValue()` and must not be expanded by templates.
`DATA_VERSION` stays `2` and the invocation records are byte-identical.

`v0.7.0` (`cli-invocation-contract` 0.7.0) is the Appearance plane v2 major (REQ-015): one
generated `cache/appearance/<hash>/` entry, one atomically repointed `current/appearance` hop, the
nested surface/state/type/ink/layout token model, optional same-shape `mode.dark`/`mode.light`
overrides, and three new schemas plus `appearance.md`. The existing `palette-refresh` transport
must now re-apply the whole appearance, and AGS apps run as systemd user units. v1 skin artifacts
are retired; there is no v1.1 hotfix. `DATA_VERSION` stays `2` and the invocation records are
byte-identical.

`v0.8.0` (`cli-invocation-contract` 0.8.0) is the Generations v3 major (REQ-016): one immutable
`state/generations/<genHash>/` unit with a last-written `manifest.json`, one atomic
`state/current -> generations/<genHash>` pointer, one `converge(intent)` pipeline serialized by the
daemon job queue or the CLI `flock` fallback, and the generation-bound
`["appearance-refresh", "<genHash>"]` protocol with applied/deferred/failed responses. Runtime
writes stay under `state/`; consumers read through `current/` and pass events, not sleeps. The v2
appearance token vocabulary and built-in skins are unchanged. `DATA_VERSION` stays `2` and the
invocation records are byte-identical.
