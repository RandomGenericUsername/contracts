# Tasks

## 1. Generator (≤2h)

- [x] 1.1 Write `gen/generate.py` (stdlib only): parse `event-contract.xml` for methods/signals and `event-contract.json` for topics/delivery/versioning. Verify: `python3 gen/generate.py` → exit 0, one summary line per emitted file. ✅
- [x] 1.2 Emit `generated/contract.py` (constants + TypedDicts + wire method/signal tables + per-topic payload types). Verify: `grep -c 'class .*Payload(TypedDict)' generated/contract.py` → 6. ✅
- [x] 1.3 Emit `generated/contract.ts` (constants + types + per-topic payload interfaces). Verify: `grep -c 'export interface .*Payload' generated/contract.ts` → 6. ✅
- [x] 1.4 Emit `generated/events.schema.json` (draft 2020-12): per-topic required/optional/enum/type defs + the signal/method/topic envelopes. Verify: `Topic_speedtest_state` required == {state,trigger}. ✅
- [x] 1.5 Ensure no private source is referenced. Verify: `grep -r contract.json gen/` → no output. ✅

## 2. Determinism (≤1h)

- [x] 2.1 Sort every emitted collection and terminate each file with a newline. Verify: `python3 gen/generate.py && python3 gen/generate.py; git diff --exit-code generated/` → exit 0. ✅

## 3. Coverage test (≤1h)

- [x] 3.1 Add `gen/test_generate.py` asserting 6 topics, 9 hub methods, 5 signals, the job interface, the JSON schema's required keys + enums, and byte-identical reruns. Verify: `python3 -m unittest discover -s gen -p 'test_*.py'` → `OK` (4 tests). ✅
- [x] 3.2 Wire `make generate`. Verify: `make generate` → exit 0 and `git diff --exit-code generated/` → exit 0. ✅
