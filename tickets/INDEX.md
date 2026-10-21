# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.
> Entry format: link — title | `status` | execution links. Epics add `done/total children done`, done-when, and one nested line per child. Bugs add severity. Spikes add timebox state.

## Active epics

(none)

## Requirements

- [REQ-008-itr-templates-dir-contract/ticket.md](./REQ-008-itr-templates-dir-contract/ticket.md) — Record the itr templates-dir env key in the invocation contract | `in-progress` | openspec: itr-templates-dir-contract

## Bugs

(none)

## Ops tasks

(none)

## Spikes

(none)

## Tasks

(none)

## Done (links only, newest last)

- [EPIC-001-stand-up-contracts/ticket.md](./EPIC-001-stand-up-contracts/ticket.md) — Stand up the contracts repo: canonical event contract + codegen | `done` | links: none | 5/5 children done
  - done-when: The event contract lives only in contracts/; the generator emits Python + TS bindings + JSON schemas from the canonical XML + JSON; the symmetric gate runs in CI; the Python runtime imports the generated bindings with no embedded duplicates, and the generated TS bindings are vendored for the platform client.
  - [REQ-001-import-canonical-contract/ticket.md](./REQ-001-import-canonical-contract/ticket.md) — Import the canonical event contract into contracts/ | `done` | openspec: import-canonical-contract
  - [REQ-002-build-contract-generator/ticket.md](./REQ-002-build-contract-generator/ticket.md) — Build the contract generator | `done` | openspec: build-contract-generator
  - [REQ-003-symmetric-drift-gate/ticket.md](./REQ-003-symmetric-drift-gate/ticket.md) — Add the symmetric regenerate-and-diff CI gate | `done` | openspec: symmetric-drift-gate
  - [REQ-004-repoint-contract-consumers/ticket.md](./REQ-004-repoint-contract-consumers/ticket.md) — Repoint consumers to generated bindings; delete embedded duplicates | `done` | openspec: repoint-runtime-to-generated-contract (dotfiles-v3)
  - [REQ-005-close-known-contract-drift/ticket.md](./REQ-005-close-known-contract-drift/ticket.md) — Close the known contract drift | `done` | openspec: close-known-contract-drift
- [REQ-006-cli-invocation-contract/ticket.md](./REQ-006-cli-invocation-contract/ticket.md) — Ship the cli-invocation-contract package | `done` | openspec: cli-invocation-contract (archived 2026-10-19)
- [REQ-007-v010-release-and-specs/ticket.md](./REQ-007-v010-release-and-specs/ticket.md) — Publish the v0.1.0 release and land the two boundary specs | `done` | openspec: none
