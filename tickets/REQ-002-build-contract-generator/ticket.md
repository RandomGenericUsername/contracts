---
id: REQ-002
title: "Build the contract generator"
kind: requirement
status: done
lane: 2
links:
  openspec: build-contract-generator
  bmad: none
worktree: .worktrees/REQ-002/
branch: ticket/REQ-002-build-contract-generator
---

# Build the contract generator

## Requirement

Repoint the `spikes/codegen` prototype at the canonical `contracts/event-contract.{xml,json}`, parse **both** encodings (XML = wire, JSON = topics/delivery), and emit deterministically: Python (`contract.py` — constants + TypedDicts + wire tables + validation schemas) and TypeScript (`contract.ts` — types + constants + per-topic payload interfaces), plus the JSON schemas. No private `contract.json` copy survives.

Source: spine **AD-6**; codegen feasibility assessment (memlog).

## Acceptance

- [x] Two consecutive generator runs produce byte-identical output (`python3 gen/generate.py && git diff --exit-code generated/` → exit 0). ✅
- [x] The generator reads `event-contract.xml` (methods/signals) + `.json` (topics/delivery); `grep -r contract.json gen/` → no matches. ✅
- [x] Output covers all 6 topics, 9 hub methods, 5 signals, the job interface, and the JSON validation schema (`python3 -m unittest discover -s gen -p 'test_*.py'` → 4 tests OK). ✅
