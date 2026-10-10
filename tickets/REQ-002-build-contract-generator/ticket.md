---
id: REQ-002
title: "Build the contract generator"
kind: requirement
status: proposed
lane: 2
links:
  openspec: build-contract-generator
  bmad: none
worktree: none
branch: none
---

# Build the contract generator

## Requirement

Repoint the `spikes/codegen` prototype at the canonical `contracts/event-contract.{xml,json}`, parse **both** encodings (XML = wire, JSON = topics/delivery), and emit deterministically: Python (`contract.py` — constants + TypedDicts + wire tables + validation schemas) and TypeScript (`contract.ts` — types + constants + per-topic payload interfaces), plus the JSON schemas. No private `contract.json` copy survives.

Source: spine **AD-6**; codegen feasibility assessment (memlog).

## Acceptance

- [ ] Two consecutive generator runs produce byte-identical output (command: run twice, `git diff --exit-code` → exit 0).
- [ ] The generator reads `contracts/event-contract.xml` for methods/signals and `.json` for topics/delivery (grep: no `spikes/codegen/contract.json`).
- [ ] Output covers all 6 topics, 9 hub methods, 5 signals, and the job interface (assert in a test).
