# contracts

Two versioned contracts, one repo.

1. **AGS event contract** (`org.dotfiles.Events`) — `event-contract.json` + `event-contract.xml`
   and the bindings generated from them.
2. **Runtime ↔ CLI invocation contract** — `invocation-contract.json` and the
   `cli-invocation-contract` package (`cli_invocation_contract`).

The event contract is the single source of truth for the runtime ↔ AGS event seam. It is
consumed by:

- the Python runtime (`dotfiles-v3` / `src/runtime`), and
- `ags-platform` (the event-contract client).

The invocation contract is the single source of truth for how the runtime invokes the three
installed consoles (`csg`, `weg`, `itr`): argv template, required env keys and injected
overrides, required artifacts, exit-code semantics, default timeout. It is **versioned**, and the
Python runtime plus **all three CLIs** pin the **same `contracts` tag** — not merely a compatible
range — so one record and one conformance kit serve four consumers. A contract change is a new
tag that every consumer re-pins; literals are not duplicated in consumer tests.

## Contract files

- `event-contract.json` — the machine-readable event contract.
- `event-contract.xml` — the D-Bus interface definition.
- `invocation-contract.json` — the runtime ↔ CLI invocation contract, one record per CLI.
- `CONTRACT.md` — field-by-field reference for the invocation contract, citing the evidence
  report (`S1`) section for every value.

## The `cli-invocation-contract` package

- `src/cli_invocation_contract/__init__.py` — `CONTRACT_VERSION`, `load(path=None)`, `get(cli)`;
  stdlib only, no runtime dependencies.
- `src/cli_invocation_contract/testkit.py` — exactly two assertions:
  `assert_consumer_invocation(record, cli, argv, env)` and
  `assert_cli_writes_artifacts(record, cli, run, cwd)`.
- `tests/` — record completeness, loader behaviour, and positive/negative kit paths against a
  fake CLI (never a real binary).
- `Makefile` — `make sync` (uv), `make test` (event-contract unittest + pytest), `make build`
  (sdist + wheel). The wheel carries `invocation-contract.json` as package data, so `load()`
  works from an installed tag.

## Tooling here

- **BMAD-METHOD:** `.agents/skills/` (`bmad`, `bmad-build`, `bmad-architecture`, `bmad-product-brief`, `bmad-spec`).
- **OpenSpec:** `openspec/` (spec-driven). Start: `/opsx-propose "your idea"`.
- **Tickets:** `tickets/` (see `INDEX.md`, `LIFECYCLE.md`); route with `/triage`.

## Status

Both seams live. The AGS event contract and generated bindings landed in REQ-001–REQ-005; the
invocation contract is REQ-006. The repo is not tagged yet: `v0.1.0` (AD-9) is the first release
and ships `cli-invocation-contract` 0.1.0.
