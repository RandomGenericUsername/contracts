# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.
> Entry format: link — title | `status` | execution links. Epics add `done/total children done`, done-when, and one nested line per child. Bugs add severity. Spikes add timebox state.

## Active epics

- [EPIC-001-stand-up-contracts/ticket.md](./EPIC-001-stand-up-contracts/ticket.md) — Stand up the contracts repo: canonical event contract + codegen | `in-progress` | links: none | 3/5 children done
  - done-when: The event contract lives only in contracts/; the generator emits Python + TS bindings + JSON schemas; the symmetric regenerate-and-diff gate runs in CI; the runtime and TS consumers import generated bindings with no embedded duplicates.
  - [REQ-001-import-canonical-contract/ticket.md](./REQ-001-import-canonical-contract/ticket.md) — Import the canonical event contract into contracts/ | `done` | openspec: import-canonical-contract
  - [REQ-002-build-contract-generator/ticket.md](./REQ-002-build-contract-generator/ticket.md) — Build the contract generator | `done` | openspec: build-contract-generator
  - [REQ-003-symmetric-drift-gate/ticket.md](./REQ-003-symmetric-drift-gate/ticket.md) — Add the symmetric regenerate-and-diff CI gate | `done` | openspec: symmetric-drift-gate
  - [REQ-004-repoint-contract-consumers/ticket.md](./REQ-004-repoint-contract-consumers/ticket.md) — Repoint consumers to generated bindings; delete embedded duplicates | `proposed` | openspec: repoint-contract-consumers
  - [REQ-005-close-known-contract-drift/ticket.md](./REQ-005-close-known-contract-drift/ticket.md) — Close the known contract drift | `in-progress` | openspec: close-known-contract-drift

## Requirements

(none)

## Bugs

(none)

## Ops tasks

(none)

## Spikes

(none)

## Tasks

(none)

## Done (links only, newest last)

(none)
