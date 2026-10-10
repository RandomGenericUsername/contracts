---
id: EPIC-001
title: "Stand up the contracts repo: canonical event contract + codegen"
kind: epic
status: done
lane: bmad-advisory
links:
  openspec: none
  bmad: none
worktree: none
branch: none
children: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005]
done-when: "The event contract lives only in contracts/; the generator emits Python + TS bindings + JSON schemas from the canonical XML + JSON; the symmetric regenerate-and-diff gate runs in CI; the Python runtime imports the generated bindings with no embedded duplicates, and the generated TS bindings are vendored for the platform client."
---

# Stand up the contracts repo: canonical event contract + codegen

## Done-when

The event contract lives only in `contracts/`; the generator emits Python + TS bindings + JSON schemas from the canonical XML + JSON; the symmetric regenerate-and-diff gate runs in CI; the Python runtime imports the generated bindings with no embedded duplicates, and the generated TS bindings are vendored for the platform client (the app-local TS readers are replaced by that client, AD-5).

Governed by spine **AD-6** (the contract is the single source; bindings are generated; supersedes AD-44), **AD-1** (dependency direction), **AD-22** (one producer per topic).

## Children

- [x] `REQ-001` — Import the canonical event contract into `contracts/` (`done`)
- [x] `REQ-002` — Build the contract generator (`done`)
- [x] `REQ-003` — Add the symmetric regenerate-and-diff CI gate (`done`)
- [x] `REQ-004` — Repoint consumers to generated bindings; delete embedded duplicates (`done`)
- [x] `REQ-005` — Close the known contract drift (`done`)
