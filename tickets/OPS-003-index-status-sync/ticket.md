---
id: OPS-003
title: "Sync REQ-010 INDEX status and acceptance with the shipped v0.4.0 tag"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-003/
branch: ticket/OPS-003-index-status-sync
---

# Sync REQ-010 INDEX status and acceptance with the shipped v0.4.0 tag

## Work

`REQ-010-tpr-invocation-record` is `done` and `v0.4.0` is tagged, but
`tickets/INDEX.md` still said `in-progress` and the acceptance boxes were never
ticked.

- Tick the acceptance items after re-running the evidence.
- Record the `v0.4.0` tag in the INDEX line.
- Adjust the OpenSpec item: the change is archived, so the original
  `openspec validate --strict tpr-invocation-record` command no longer names an
  active change; `openspec validate --all` is the applicable evidence.

## Done-when

`REQ-010` frontmatter, acceptance, and INDEX all agree that the record shipped
in `v0.4.0`.

## Evidence

- `make test` → 109 passed.
- `make check-symmetry` → drift green.
- `uv build` → `cli_invocation_contract-0.4.0` sdist + wheel.
- `openspec validate --all` → 10 passed.
- `git tag` → `v0.4.0`.
