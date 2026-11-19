---
id: REQ-021
title: "Add the Neovim projection to the tpr invocation contract"
kind: requirement
status: done
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-021/
branch: ticket/REQ-021-nvim-invocation-contract
---

# Add the Neovim projection to the tpr invocation contract

## Requirement

1. The `tpr` record requests `--format nvim.lua` and requires `colors.nvim.lua`.
2. `min_count` rises from 8 to 9.
3. Release `v0.13.0`; the runtime pins it before requesting the artifact.
4. Update `CONTRACT.md`, tests and the changelog.

## Acceptance

- [x] Contract record updated.
- [x] `make test` and `make check-symmetry` pass.
- [x] `v0.13.0` tagged/pushed/released.


- Release: https://github.com/RandomGenericUsername/contracts/releases/tag/v0.13.0
