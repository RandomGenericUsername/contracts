---
id: REQ-007
title: "Publish the v0.1.0 release and land the two boundary specs"
kind: requirement
status: done
lane: 3
links:
  openspec: none
  bmad: none
worktree: .worktrees/req-007/
branch: ticket/req-007-release-v010-and-specs
---

# Publish the v0.1.0 release and land the two boundary specs

## Requirement

Slice **S0b** on the contracts side SHALL close out the `cli-invocation-contract` release and
take ownership of the two boundary specs that were stranded in `dotfiles-v3`:

- **Release record.** `CHANGELOG.md` SHALL carry a `0.1.0` entry that describes what shipped in
  the `cli-invocation-contract` package (the `csg` / `weg` / `itr` records, the two-assertion
  conformance kit, `CONTRACT_VERSION` `0.1.0` / `DATA_VERSION` `1`) and names the merge commit
  `48cf3cf` and the `v0.1.0` tag.
- **GitHub Release.** A `v0.1.0` release SHALL exist on the remote with an sdist + wheel built
  from the tag commit (`48cf3cf`), never from a dirty working tree.
- **Spec relocation.** `interface-contract-test` and `container-adapter-env-contract` SHALL move
  from `dotfiles-v3/openspec/specs/` into this repo's `openspec/specs/`, content preserved, with
  a provenance header naming the move (`dotfiles-v3` → `contracts`, cli-tools-repos split, S0b).
  The source copies stay in place; the orchestrator removes them after the push.

The contract data (`invocation-contract.json`) and the package code
(`src/cli_invocation_contract/`) SHALL NOT change in this slice.

## Acceptance

- [x] `tickets/REQ-007-v010-release-and-specs/ticket.md` exists with this worktree/branch
  recorded and a matching line in `tickets/INDEX.md`.
  Verify: `rg -n "REQ-007" tickets/INDEX.md tickets/REQ-007-v010-release-and-specs/ticket.md` → both hit.
- [x] `CHANGELOG.md` has a `0.1.0`/`v0.1.0` entry citing `48cf3cf` and the tag, and stating the
  package surface (`load()`/`get()`, two kit assertions, `CONTRACT_VERSION` `0.1.0`,
  `DATA_VERSION` `1`).
  Verify: `rg -n "48cf3cf|CONTRACT_VERSION|DATA_VERSION" CHANGELOG.md` → expected lines.
- [x] The release assets are built from the tag, not the working tree.
  Verify: `git worktree add /tmp/opencode/contracts-v010 v0.1.0 && (cd /tmp/opencode/contracts-v010 && uv build)` →
  wheel + sdist for `0.1.0`, exit 0.
- [x] `gh release view v0.1.0 --json assets --jq '.assets[].name'` lists the sdist and the wheel.
- [x] `openspec/specs/interface-contract-test/spec.md` and
  `openspec/specs/container-adapter-env-contract/spec.md` exist here, carry the provenance
  header, and preserve the original requirements verbatim.
  Verify: `diff <(git -C /home/inumaki/Development/dotfiles-v3 show HEAD:openspec/specs/interface-contract-test/spec.md) <(tail -n +N openspec/specs/interface-contract-test/spec.md)` → empty.
- [x] `openspec validate --all` exits 0 with the two new specs listed as passing.
- [x] `git status --porcelain` is empty after the merge back to `main`.

## Out of scope

- Deleting the source specs from `dotfiles-v3` (orchestrator-owned, after this push).
- Changing `invocation-contract.json`, `src/cli_invocation_contract/`, `CONTRACT.md`, or any
  consumer pin.
- Re-tagging or moving `v0.1.0`; the tag stays on `48cf3cf`.

## Closeout

Closed 2026-10-19 on `ticket/req-007-close-close-ticket` (worktree `.worktrees/req-007-close/`),
fast-forwarded onto `main` at `55ad61b`. The slice worktree/branch recorded in the frontmatter
(`.worktrees/req-007/` / `ticket/req-007-release-v010-and-specs`) is the one that authored the
four slice commits; this closeout only ticks the record, writes this section, and moves
`tickets/INDEX.md` to Done. No contract data, package code, `CONTRACT.md`, or consumer pin was
touched — `invocation-contract.json` and `src/cli_invocation_contract/` are unchanged since
`48cf3cf`.

Slice commits (oldest first, all on `main`):

| Commit | Subject |
| --- | --- |
| `ff6dcba` | `plan(REQ-007): open v0.1.0 release + boundary-spec relocation ticket` |
| `a34ae37` | `plan(REQ-007): relocate interface-contract-test + container-adapter-env-contract specs` |
| `fcba526` | `docs(REQ-007): add 0.1.0 changelog entry and correct release status` |
| `55ad61b` | `plan(REQ-007): record the worktree-guard branch name` |

The `CHANGELOG.md` `0.1.0` entry landed in `fcba526` (the SHA to cite for the release record).

Evidence (commands run from the repo root unless a worktree path is named):

| Claim | Command | Result |
| --- | --- | --- |
| Release exists at the right tag/commit with both assets | `gh release view v0.1.0 --json assets,tagName,targetCommitish --jq '{tag:.tagName,target:.targetCommitish,assets:[.assets[].name]}'` | `{"assets":["cli_invocation_contract-0.1.0-py3-none-any.whl","cli_invocation_contract-0.1.0.tar.gz"],"tag":"v0.1.0","target":"48cf3cfed4b192b241505789409c4f282921c896"}`, exit 0 |
| Tag resolves to the merge commit | `git rev-parse v0.1.0^{commit}` | `48cf3cfed4b192b241505789409c4f282921c896`, exit 0 |
| Assets are reproducible from the tag, not a dirty tree | `git worktree add /tmp/opencode/contracts-v010 v0.1.0 && cd /tmp/opencode/contracts-v010 && uv build` | `HEAD is now at 48cf3cf`; `Successfully built dist/cli_invocation_contract-0.1.0.tar.gz` + `...-py3-none-any.whl`; exit 0 (worktree removed afterwards) |
| `CHANGELOG.md` release record | `rg -n "48cf3cf\|CONTRACT_VERSION\|DATA_VERSION" CHANGELOG.md` | lines 19 (`48cf3cf`), 30 (`CONTRACT_VERSION = "0.1.0"`), 32 (`DATA_VERSION = 1`), exit 0 |
| Specs relocated verbatim | `diff <(git -C ../dotfiles-v3 show HEAD:openspec/specs/<name>/spec.md \| tail -n +3) <(tail -n +10 openspec/specs/<name>/spec.md)` | empty output, exit 0 — for **both** `interface-contract-test` and `container-adapter-env-contract` (the `+10` skips the 9-line title + provenance block; the source body from `## Purpose` down is byte-identical) |
| OpenSpec validates, both new specs pass | `openspec validate --all` | `Totals: 10 passed, 0 failed (10 items)`, exit 0, with `✓ spec/interface-contract-test` and `✓ spec/container-adapter-env-contract` listed |
| Ticket + INDEX line agree | `rg -n "REQ-007" tickets/INDEX.md tickets/REQ-007-v010-release-and-specs/ticket.md` | hits in both files, exit 0 |
| `main` is pushed and clean | `git rev-parse origin/main main` | both `55ad61b008ceefec66c37fc2f37f3d3419f64d42`; `git status --porcelain` empty after the merge |

`openspec validate --all` exits 0 while reporting pre-existing warnings only (three placeholder
`Purpose` sections and one over-long requirement in `spec/cli-invocation-contract`); no warning
is on a file this slice authored.
