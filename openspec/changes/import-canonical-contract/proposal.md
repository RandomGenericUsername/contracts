# import-canonical-contract

## Why

The event contract currently lives in `dotfiles-v3/contracts/` and is read by the Python runtime and pinned by tests across components. The architecture spine (**AD-6**) makes this repo the single source of truth; nothing downstream can be regenerated or repointed until the contract is here.

Evidence: `dotfiles-v3/contracts/event-contract.{xml,json,md}` + `dotfiles-v3/contracts/schemas/*.schema.json`; spine `ARCHITECTURE-SPINE.md` AD-6.
Verify: `ls /home/inumaki/Development/dotfiles-v3/contracts` → 3 files + `schemas/` (4 schemas).

## What Changes

- Import `event-contract.{xml,json,md}` and `schemas/*.schema.json` **byte-identical** to the cut commit.
- Record the cut commit so the repointing step (REQ-004) can diff against a known baseline.

## Non-goals

- **Not** the generator — that is `build-contract-generator` (REQ-002).
- **Not** repointing consumers — that is `repoint-contract-consumers` (REQ-004).
- The `dotfiles-v3` copy stays in place until the repoint; this change does not delete it.

## Impact

- This repo: `event-contract.{xml,json,md}`, `schemas/`.
- No consumer is touched yet.
