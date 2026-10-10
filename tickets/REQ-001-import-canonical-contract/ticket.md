---
id: REQ-001
title: "Import the canonical event contract into contracts/"
kind: requirement
status: done
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

- [x] `contracts/event-contract.{xml,json,md}` + `schemas/` exist here and match the `dotfiles-v3` originals at the cut commit (command: `diff -r schemas /home/inumaki/Development/dotfiles-v3/contracts/schemas` → no output).
- [x] `openspec validate import-canonical-contract --type change` exits 0.
- [x] The cut commit is recorded: `ce3fd4a473eacbf3841a3d0b45566b2594f83f2d` (dotfiles-v3) for the repointing step (REQ-004).
