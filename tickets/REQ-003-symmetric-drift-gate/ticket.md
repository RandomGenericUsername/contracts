---
id: REQ-003
title: "Add the symmetric regenerate-and-diff CI gate"
kind: requirement
status: done
lane: 2
links:
  openspec: symmetric-drift-gate
  bmad: none
worktree: .worktrees/REQ-003/
branch: ticket/REQ-003-symmetric-drift-gate
---

# Add the symmetric regenerate-and-diff CI gate

## Requirement

One `make` target regenerates the artifacts and diffs them, and the gate is **symmetric**: the canonical contract is checked against BOTH the generated TS and the generated runtime tables — not one direction (today's gate only checks contract → schema, so extra schema properties pass).

Source: spine **AD-6** (symmetric gate), **AD-19**.

## Acceptance

- [x] `make contracts-drift` regenerates then `git diff --exit-code` over `generated/` (exit 0 when clean). ✅
- [x] A deliberately hand-edited generated file fails the gate (negative test → exit 2). ✅
- [x] The gate runs in CI (`.github/workflows/drift.yml`). ✅
- [x] The symmetric reverse check catches a schema-only key absent from the contract. ✅
