---
id: REQ-001
title: "Import the canonical event contract into contracts/"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: import-canonical-contract
  bmad: none
worktree: .worktrees/REQ-001/
branch: ticket/REQ-001-import-canonical-contract
---

# Import the canonical event contract into contracts/

## Requirement

`contracts/event-contract.{xml,json,md}` and `contracts/schemas/*.schema.json` move from `dotfiles-v3` into this repo as the single source of truth, and the repo is published. The XML is the D-Bus wire source; the JSON carries methods/signals/topics/delivery.

Source: spine **AD-6**; doc 101 §3.1, §10; handoff iteration 2.

## Acceptance

- [ ] `contracts/event-contract.{xml,json,md}` + `schemas/` exist here and match the `dotfiles-v3` originals at the cut commit (command: `diff -r contracts/ <dotfiles-v3>/contracts/` → no output).
- [ ] `openspec validate --change import-canonical-contract` exits 0.
- [ ] The cut commit is recorded on the ticket for the repointing step (REQ-004).
