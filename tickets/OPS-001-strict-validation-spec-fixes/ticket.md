---
id: OPS-001
title: "Clear the three pre-existing strict-validation failures"
kind: ops-task
status: in-progress
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-001/
branch: ticket/OPS-001-strict-validation-spec-fixes
---

# Clear the three pre-existing strict-validation failures

> `ops-task` MAY be read as `chore` (Shortcut mapping); the file MUST still declare `kind: ops-task`.
> An `ops-task` SHALL NOT declare a `parent:`. Trivial ops tasks may skip OpenSpec/BMAD ceremony but never skip git discipline (main-clean check + worktree + ticket branch).

## Work

`openspec validate --all --strict` fails on three items at base `a0f8f05`. None of them is a
new capability — each is spec hygiene the tree has carried since before this slice, so this
ticket is an `ops-task` with no OpenSpec change of its own.

1. `spec/container-adapter-env-contract` — `overview`: the `## Purpose` is still the sentence
   `openspec archive` writes for a created capability (`TBD - created by archiving change
   container-adapter-decoupling. Update Purpose after archive.`). Inherited from the
   `dotfiles-v3` → `contracts` relocation (REQ-007, slice S0b), which preserved the source
   spec verbatim and therefore preserved the placeholder.
2. `spec/interface-contract-test` — same `overview` placeholder, same provenance.
3. `spec/ticket-system` — `requirements[6]` (`### Requirement: Index entries carry link,
   title, status, rollup`) has a 512-character body against the strict 500-character cap. A
   trim would drop behavior, so the requirement is **split** into two coherent requirements,
   preserving both existing scenarios.

The fix for (1) and (2) is a Purpose paragraph written from the requirement bodies the spec
already asserts — no new scope, no new requirement, no scenario touched. The fix for (3) is a
requirement split (base entry fields vs. kind-specific detail) with both scenarios moved
unchanged.

Out of scope:

- Any change to `invocation-contract.json`, the package, the generated bindings, or the
  event contract — this ticket moves no data and no code, so it cuts **no tag**.
- Reworking the relocated scenarios to match the CLI repos' current code; the specs stay as
  relocated.
- The four OpenSpec changes under `openspec/changes/` (all already strict-valid).

## Done-when

`openspec validate --all --strict` reports `0 failed`, with `uv run pytest -q` and
`make check-symmetry` still green.

## Evidence

Base: `a0f8f05` (`main`, clean). Worktree `.worktrees/OPS-001/`, branch
`ticket/OPS-001-strict-validation-spec-fixes`.

| Claim | Command | Result |
| --- | --- | --- |
| Baseline reproduces | `openspec validate --all --strict` | `Totals: 7 passed, 3 failed (10 items)`, exit 1 |
| (1) is a placeholder, not content | `openspec validate container-adapter-env-contract --type spec --strict` | `⚠ [WARNING] overview: Purpose section is still a placeholder…`, exit 1; the line at `openspec/specs/container-adapter-env-contract/spec.md:11` is the archive-written `TBD` sentence |
| (2) is a placeholder, not content | `openspec validate interface-contract-test --type spec --strict` | same `overview` warning, exit 1; `openspec/specs/interface-contract-test/spec.md:11` |
| (3) is a length failure on the 7th requirement | `openspec validate ticket-system --type spec --strict` | `⚠ [WARNING] requirements[6]: Requirement text is very long (>500 characters)`, exit 1 |
| The body really is over the cap | `sed -n '65p' openspec/specs/ticket-system/spec.md \| wc -c` (base) | `513` (512 chars + newline) |
| No artifact references the two requirement titles being touched | `grep -rn "Index entries carry\|Global index mirrors" --include='*.md' --include='*.py' --include='*.json' . \| grep -v '^./openspec/specs/ticket-system'` | no matches — the split is internal to that spec |
| Each spec validates on its own (strict) | `for s in container-adapter-env-contract interface-contract-test ticket-system; do openspec validate "$s" --type spec --strict; done` | `Specification '<name>' is valid` for all three, exit 0 |
| Strict validator clean across the tree | `openspec validate --all --strict` | `Totals: 10 passed, 0 failed (10 items)`, exit 0 |
| Non-strict validator agrees | `openspec validate --all` | `Totals: 10 passed, 0 failed (10 items)`, exit 0 |
| Both split bodies are under the cap | python3 body-length scan over `openspec/specs/ticket-system/spec.md` (whitespace-normalised text between the heading and the first blank line) | `requirements[6]` `512` → `204`; `requirements[7]` (new) `307`; every other requirement byte-identical to base (`237/150/163/228/296/155`) |
| Nothing but prose moved in `ticket-system` | `git show a0f8f05:…/spec.md \| grep -c '^#### Scenario:'` vs. the same on the branch | `8` before, `8` after; requirements `7` → `8` (the split only) |
| Package tests unaffected | `uv run pytest -q` | `55 passed in 0.27s`, exit 0 |
| Both test legs | `make test` | `Ran 10 tests … OK` then `55 passed in 0.22s`, exit 0 |
| Generated bindings unaffected | `make check-symmetry` | `[drift] symmetric: contract and generated/ agree`, exit 0 |
| No tag is cut (no package/data change) | `git diff --stat a0f8f05 HEAD -- src invocation-contract.json event-contract.json generated/ dist/` | empty (exit 0) — only `openspec/` and `tickets/` changed |

Commits (oldest first):

| Commit | Subject |
| --- | --- |
| `09530b9` | `plan(OPS-001): open the strict-validation spec-hygiene ticket` |
| `1a8fee0` | `fix(OPS-001): clear the three strict-validation failures in the spec tree` |

## Status

**In progress — evidence recorded, closeout pending the merge.** The three failures are
cleared and every gate is green on the ticket branch; the merge to `main` and the INDEX move
to Done land in the closeout commit, as in REQ-008.
