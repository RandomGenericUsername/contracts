---
id: REQ-007
title: "Publish the v0.1.0 release and land the two boundary specs"
kind: requirement
status: in-progress
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

- [ ] `tickets/REQ-007-v010-release-and-specs/ticket.md` exists with this worktree/branch
  recorded and a matching line in `tickets/INDEX.md`.
  Verify: `rg -n "REQ-007" tickets/INDEX.md tickets/REQ-007-v010-release-and-specs/ticket.md` → both hit.
- [ ] `CHANGELOG.md` has a `0.1.0`/`v0.1.0` entry citing `48cf3cf` and the tag, and stating the
  package surface (`load()`/`get()`, two kit assertions, `CONTRACT_VERSION` `0.1.0`,
  `DATA_VERSION` `1`).
  Verify: `rg -n "48cf3cf|CONTRACT_VERSION|DATA_VERSION" CHANGELOG.md` → expected lines.
- [ ] The release assets are built from the tag, not the working tree.
  Verify: `git worktree add /tmp/opencode/contracts-v010 v0.1.0 && (cd /tmp/opencode/contracts-v010 && uv build)` →
  wheel + sdist for `0.1.0`, exit 0.
- [ ] `gh release view v0.1.0 --json assets --jq '.assets[].name'` lists the sdist and the wheel.
- [ ] `openspec/specs/interface-contract-test/spec.md` and
  `openspec/specs/container-adapter-env-contract/spec.md` exist here, carry the provenance
  header, and preserve the original requirements verbatim.
  Verify: `diff <(git -C /home/inumaki/Development/dotfiles-v3 show HEAD:openspec/specs/interface-contract-test/spec.md) <(tail -n +N openspec/specs/interface-contract-test/spec.md)` → empty.
- [ ] `openspec validate --all` exits 0 with the two new specs listed as passing.
- [ ] `git status --porcelain` is empty after the merge back to `main`.

## Out of scope

- Deleting the source specs from `dotfiles-v3` (orchestrator-owned, after this push).
- Changing `invocation-contract.json`, `src/cli_invocation_contract/`, `CONTRACT.md`, or any
  consumer pin.
- Re-tagging or moving `v0.1.0`; the tag stays on `48cf3cf`.
