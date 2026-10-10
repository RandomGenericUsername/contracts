# Tasks

## 1. Generator (≤2h)

- [ ] 1.1 Write `gen/generate.py` (stdlib only): parse `event-contract.xml` for methods/signals and `event-contract.json` for topics/delivery/versioning. Verify: `python3 gen/generate.py` → exit 0, one summary line per emitted file.
- [ ] 1.2 Emit `generated/contract.py` (constants + TypedDicts + wire method/signal tables + per-topic payload types). Verify: `grep -c 'class .*Payload(TypedDict)' generated/contract.py` → 6.
- [ ] 1.3 Emit `generated/contract.ts` (constants + types + per-topic payload interfaces). Verify: `grep -c 'export interface .*Payload' generated/contract.ts` → 6.
- [ ] 1.4 Ensure no private source is referenced. Verify: `grep -r contract.json gen/` → no output.

## 2. Determinism (≤1h)

- [ ] 2.1 Sort every emitted collection and terminate each file with a newline. Verify: `python3 gen/generate.py && python3 gen/generate.py; git diff --exit-code generated/` → exit 0.

## 3. Coverage test (≤1h)

- [ ] 3.1 Add `gen/test_generate.py` asserting 6 topics, 9 hub methods, 5 signals, the job interface, and byte-identical reruns. Verify: `python3 -m unittest discover -s gen -p 'test_*.py'` → `OK`.
- [ ] 3.2 Wire `make generate`. Verify: `make generate` → exit 0 and `git diff --exit-code generated/` → exit 0.
