# AGENTS.md — contracts operating contract

Canonical agent instructions for this repo. Claude (`CLAUDE.md` symlinks here), OpenCode, and all BMAD/OpenSpec skills must follow this.

## 1. Evidence rule (hard requirement)

No suggestion "in the air". Every technical claim, recommendation, or design decision must carry testable evidence — at least one of:

- **Doc evidence:** file path + line range, or commit SHA, or URL + quoted section.
- **Prototype evidence:** a script/command in-repo that runs and prints the validating output. State the exact command and observed result.
- **Test evidence:** `command run → result` (exit code + key output). Failing-as-expected counts if it validates the claim.

Format: any non-trivial claim gets an `Evidence:` line and a `Verify:` line (how to reproduce in one command). If evidence doesn't exist yet, say `Evidence: MISSING — run <X> to produce it` and do not present the claim as fact.

## 2. How we work here

- This repo owns the **event contract** for the AGS platform: `org.dotfiles.Events` (`event-contract.json` + `event-contract.xml`) and the **bindings generated from it**. It is the single source of truth consumed by the **Python runtime** and by **ags-platform**.
- The contract is **versioned**: a breaking change is a new interface (`Events2`); non-breaking changes stay on `Events1`; both may coexist during migration.
- Bindings are **generated, never hand-edited**. Regenerate and commit.
- Prefer executed output over recalled text. Read files, run commands, paste results.

## 3. OpenSpec + BMAD routing (via tickets)

- All work starts as a ticket in `tickets/` (`_template/`, vocab + rollup in `INDEX.md`, flow in `LIFECYCLE.md`). Triage with `/triage` (lanes in `tickets/_fixtures/router-lanes.md`).
- Broad scope (contract evolution, versioning strategy) → BMAD. Only installed skills: `bmad`, `bmad-build`, `bmad-architecture`, `bmad-product-brief`, `bmad-spec` — say so when a step needs a missing skill instead of improvising.
- Bounded slices (one proposal + spec + design + tasks) → OpenSpec (`/opsx-propose`, `/opsx-apply`, `/opsx-archive`). Artifact rules in `openspec/config.yaml` restate this evidence rule per artifact.
- Never work on main: `scripts/worktree-guard.sh create <id> <slug>` scaffolds `ticket/<id>-<slug>` + worktree, aborts when dirty. Record worktree/branch in the ticket.
- Keep changes small, verifiable, committable. Never mix planning edits with implementation in one turn.
