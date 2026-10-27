---
id: OPS-002
title: "Release v0.3.0 for the AGS app contract"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-002/
branch: ticket/OPS-002-v030-release
---

# Release v0.3.0 for the AGS app contract

> `ops-task` MAY be read as `chore` (Shortcut mapping); the file MUST still declare `kind: ops-task`.
> An `ops-task` SHALL NOT declare a `parent:`. Trivial ops tasks may skip OpenSpec/BMAD ceremony but never skip git discipline (main-clean check + worktree + ticket branch).

## Work

Publish the contracts repo release for the AGS app contract work (REQ-009):

- bump `cli-invocation-contract` `0.2.0` → `0.3.0` and `CONTRACT_VERSION` with it;
  `DATA_VERSION` stays `2` because the invocation data shape did not change;
- move the `CHANGELOG.md` Unreleased AGS entries under `0.3.0` and record the release,
  including the `wallpaper.state` progress/UI note;
- update the README status, `CONTRACT.md` version reference and the current
  `cli-invocation-contract` spec to `0.3.0`;
- run `make schema-test`, `make test`, `make contracts-drift` and `make build`;
- merge the release commit to `main` only when every gate is green, then create the
  annotated `v0.3.0` tag on that commit. Do not push and do not publish a GitHub release.

## Done-when

`v0.3.0` is an annotated local tag on the merged release commit on `main`, all four gates
are green, `main` is clean, and the tag is local-only.

## Evidence

Commands run from the release worktree `.worktrees/OPS-002/` (branch
`ticket/OPS-002-v030-release`, base `5eb01b8`).

| Claim | Command | Result |
| --- | --- | --- |
| AGS app schema fixtures | `make schema-test` | `40 passed in 0.11s`, exit 0 |
| Contract + package tests | `make test` | `Ran 10 tests … OK`; `95 passed in 0.23s`, exit 0 |
| Symmetric regenerate-and-diff | `make contracts-drift` | `[drift] symmetric: contract and generated/ agree`; `git diff --exit-code generated/` clean, exit 0 |
| Package build | `make build` | `cli_invocation_contract-0.3.0.tar.gz` + `cli_invocation_contract-0.3.0-py3-none-any.whl`, exit 0 |
| Version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.3.0 2`, exit 0 |
| Wheel metadata | `unzip -p dist/cli_invocation_contract-0.3.0-py3-none-any.whl cli_invocation_contract-0.3.0.dist-info/METADATA \| grep -m1 '^Version:'` | `Version: 0.3.0`, exit 0 |
| Specs validate | `openspec validate --all` | `Totals: 10 passed, 0 failed (10 items)`, exit 0 |

## Release

Annotated tag `v0.3.0` on the release commit merged to `main`; the tag and merge are local-only
(not pushed), and no GitHub release was published.
