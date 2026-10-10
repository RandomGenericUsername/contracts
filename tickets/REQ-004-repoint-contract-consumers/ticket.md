---
id: REQ-004
title: "Repoint consumers to generated bindings; delete embedded duplicates"
kind: requirement
status: proposed
lane: 3
links:
  openspec: repoint-contract-consumers
  bmad: none
worktree: none
branch: none
---

# Repoint consumers to generated bindings; delete embedded duplicates

## Requirement

The Python runtime's hand-embedded wire tables/validation schemas and the TS consumers import the generated bindings; embedded duplicates are deleted. This is a **cross-cutting repoint**: the runtime (`dbus_event_bus`, `emit_validation`, `hub`, `bus_name_owner`, `bar_subscriber`), 4 full TS clients (bar, hypr-pano, icme, wallpaper-selector), and 2 bespoke notification readers.

Source: spine **AD-5**, **AD-6**; sweep evidence (`bar_subscriber` repo-walk; `conftest.repo_root`; 4 node drift tests; provisioning file-layout pins).

## Acceptance

- [ ] No hand-embedded `org.dotfiles.Events1` table or per-topic schema remains outside the generated bindings (grep → none).
- [ ] `make contracts-check` + the runtime test suite + the AGS gates pass.
- [ ] The pinned cross-repo version is recorded (which `contracts` commit each consumer pins).
