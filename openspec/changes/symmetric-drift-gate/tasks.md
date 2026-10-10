# Tasks

## 1. Symmetric content checker (≤2h)

- [ ] 1.1 Add `gen/check_symmetry.py` (stdlib only) that loads `event-contract.{json,xml}` and the committed `generated/{contract.py,contract.ts,events.schema.json}` and returns a list of mismatches. Verify: `python3 gen/check_symmetry.py` → exit 0 and one `[ok]` line per leg on a clean tree.
- [ ] 1.2 Schema ↔ contract, **both directions**: per-topic key sets equal, `required` equals payload keys minus `optional`, each property type fragment equals the contract's D-Bus→JSON mapping, and every enum equals the contract enum. Verify: `python3 -c "import json;d=json.load(open('generated/events.schema.json'))['$defs']['Topic_capture_state'];print(set(d['properties']),set(d['required']))"` matches `event-contract.json` `capture.state`.
- [ ] 1.3 Python bindings ↔ contract: identity/versioning/delivery/validation/job-lease constants, `EVENTS_METHODS`/`EVENTS_SIGNALS`/`JOB_METHODS` vs the XML, `EVENTS_TOPICS`, and each `*Payload` TypedDict (fields, optionality, `Literal` enums) equal the contract. Verify: `python3 gen/check_symmetry.py` → `[ok] contract.py <-> contract`.
- [ ] 1.4 TypeScript bindings ↔ contract: scalar constants, `EVENTS_TOPICS`, the wire method/signal tables vs the XML, and each `*Payload` interface equal the contract. Verify: `python3 gen/check_symmetry.py` → `[ok] contract.ts <-> contract`.
- [ ] 1.5 Leave a clearly named hook for the cross-repo runtime-tables leg (REQ-004) — a `TODO(REQ-004)` marker and an explicit `[skip]` report line; do not fake it. Verify: `grep -n 'REQ-004' gen/check_symmetry.py` → at least one line.

## 2. The gate target (≤1h)

- [ ] 2.1 Add `make check-symmetry`, `make contracts-drift` (run the checker, regenerate, `git diff --exit-code generated/` + untracked guard) and `make drift` (alias). Update `make help`. Verify: `make contracts-drift` → exit 0 on a clean tree.
- [ ] 2.2 Confirm the gate fails on drift: hand-edit a generated file, run `make contracts-drift`, observe non-zero. Verify: `git status --porcelain` → clean after reverting.

## 3. Negative tests (≤2h)

- [ ] 3.1 Add `gen/test_symmetry.py` (stdlib `unittest`) with a clean-tree pass plus three failure cases on temp copies: (a) a hand-edited generated artifact; (b) a topic/key added to the contract without regeneration; (c) an extra schema key absent from the contract (reverse check). Verify: `python3 -m unittest discover -s gen -p 'test_*.py'` → `OK`.
- [ ] 3.2 Demonstrate (a), (b), (c) against `make contracts-drift` in the worktree and revert each. Verify: `git status --porcelain` → clean.

## 4. CI (≤1h)

- [ ] 4.1 Add `.github/workflows/drift.yml` running `make contracts-drift` and `make test` on push and pull request. Verify: `python3 -c "import yaml,sys;yaml.safe_load(open('.github/workflows/drift.yml'))"` → exit 0 (or inspect the file).
