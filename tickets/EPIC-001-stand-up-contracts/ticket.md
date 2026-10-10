---
id: EPIC-001
title: "Stand up the contracts repo: canonical event contract + codegen"
kind: epic
status: in-progress
lane: bmad-advisory
links:
  openspec: none
  bmad: none
worktree: .worktrees/EPIC-001/
branch: ticket/EPIC-001-event-contract-repo
children: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005]
done-when: "The event contract lives only in contracts/; the generator emits Python + TS bindings + JSON schemas from the canonical XML + JSON; the symmetric regenerate-and-diff gate runs in CI; the runtime and TS consumers import generated bindings with no embedded duplicates."
---

# Stand up the contracts repo: canonical event contract + codegen

## Done-when

The event contract lives only in `contracts/`; the generator emits Python + TS bindings + JSON schemas from the canonical XML + JSON; the symmetric regenerate-and-diff gate runs in CI; and the runtime + TS consumers import the generated bindings with no embedded duplicates left.

Governed by spine **AD-6** (the contract is the single source; bindings are generated; supersedes AD-44), **AD-1** (dependency direction), **AD-22** (one producer per topic).

## Children

- [ ] `REQ-001` — Import the canonical event contract into `contracts/` (`proposed`)
- [ ] `REQ-002` — Build the contract generator (`proposed`)
- [ ] `REQ-003` — Add the symmetric regenerate-and-diff CI gate (`proposed`)
- [ ] `REQ-004` — Repoint consumers to generated bindings; delete embedded duplicates (`proposed`)
- [ ] `REQ-005` — Close the known contract drift (`proposed`)
