---
id: REQ-005
title: "Close the known contract drift"
kind: requirement
status: proposed
lane: 2
links:
  openspec: close-known-contract-drift
  bmad: none
worktree: none
branch: none
---

# Close the known contract drift

## Requirement

Fix the drift the sweep found: `wallpaper.state` (the embedded validator schema carries `stage` + `reload_failures` that the contract JSON omits — add them so both agree), and remove the dead `speedtest.finished` literal still exported by hypr-pano. Add a **reverse** drift check (schema → contract) so this class cannot recur.

Source: spine **AD-6**; sweep evidence (`emit_validation.py`, `hypr-pano/lib/event-bus-core.ts`).

## Acceptance

- [ ] `wallpaper.state` contract JSON includes `stage` + `reload_failures`; the symmetric gate passes.
- [ ] `speedtest.finished` appears nowhere in code (grep → none).
- [ ] A reverse drift check fails when schema and contract disagree (negative test).
