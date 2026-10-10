---
id: REQ-005
title: "Close the known contract drift"
kind: requirement
status: done
lane: 2
links:
  openspec: close-known-contract-drift
  bmad: none
worktree: .worktrees/REQ-005/
branch: ticket/REQ-005-close-known-contract-drift
---

# Close the known contract drift

## Requirement

Fix the drift the sweep found: `wallpaper.state` (the embedded validator schema carries `stage` + `reload_failures` that the contract JSON omits — add them so both agree), and remove the dead `speedtest.finished` literal still exported by hypr-pano. Add a **reverse** drift check (schema → contract) so this class cannot recur.

Source: spine **AD-6**; sweep evidence (`emit_validation.py`, `hypr-pano/lib/event-bus-core.ts`).

## Acceptance

- [x] `wallpaper.state` contract JSON includes `stage` (7-value enum) + `reload_failures` (string array), both optional; the symmetric gate passes (`make contracts-drift` → exit 0). ✅
- [x] A reverse drift check fails when schema and contract disagree (delivered in REQ-003: `gen/test_symmetry.py::test_c_extra_schema_key_reverse_check_fails`). ✅
- [~] `speedtest.finished` appears nowhere in code — **re-scoped to REQ-004**: the dead literal lives in `dotfiles-v3/src/gui-tools/hypr-pano/lib/event-bus-core.ts` (cross-repo); REQ-004 removes it when it repoints/deletes the TS readers. This child is contracts-repo-only.
