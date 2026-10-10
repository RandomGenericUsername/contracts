---
id: REQ-004
title: "Repoint consumers to generated bindings; delete embedded duplicates"
kind: requirement
status: done
lane: 3
links:
  openspec: repoint-runtime-to-generated-contract
  bmad: none
worktree: none
branch: none
---

# Repoint consumers to generated bindings; delete embedded duplicates

## Requirement

The Python runtime's hand-embedded wire tables/validation schemas import the generated bindings; embedded duplicates are deleted. **Narrowed scope (user decision):** the Python runtime is repointed now; the app-local TS readers are **not** repointed here — they are replaced by the platform's one event client (spine **AD-5**), which will consume the generated TS bindings. The generated TS bindings are vendored into dotfiles-v3 for that client.

Source: spine **AD-5**, **AD-6**; execution: dotfiles-v3 change `repoint-runtime-to-generated-contract` (merged at `7c0c029c`, contracts pin `dbdc5b8`).

## Acceptance

- [x] No hand-embedded `org.dotfiles.Events1` table or per-topic schema remains in the Python runtime outside the generated bindings (`git grep` in dotfiles-v3 → none). ✅
- [x] `make contracts-check` (40 passed) + the runtime test suite (2120 passed) pass; the AGS gates are unaffected. ✅
- [x] The pinned cross-repo version is recorded (`CONTRACT_PIN` = `dbdc5b8`; enforced by `make contract-pin-check`). ✅
- [~] App-local TS readers repointed → **deferred** to the platform migration (AD-5): they are deleted, not repointed; the generated TS bindings are vendored at `dotfiles/config/ags/lib/generated/contract.ts` for the platform client.
