# contracts

The AGS event contract (`org.dotfiles.Events`) and the bindings generated from it.

Single source of truth for the runtime ↔ AGS event seam. Consumed by:

- the Python runtime (`dotfiles-v3` / `src/runtime`), and
- `ags-platform` (the event-contract client).

## Contract files

- `event-contract.json` — the machine-readable contract.
- `event-contract.xml` — the D-Bus interface definition.

## Tooling here

- **BMAD-METHOD:** `.agents/skills/` (`bmad`, `bmad-build`, `bmad-architecture`, `bmad-product-brief`, `bmad-spec`).
- **OpenSpec:** `openspec/` (spec-driven). Start: `/opsx-propose "your idea"`.
- **Tickets:** `tickets/` (see `INDEX.md`, `LIFECYCLE.md`); route with `/triage`.

## Status

Scaffold. Next: import the contract from `dotfiles-v3:contracts/`, add generation + validation, then repoint consumers.
