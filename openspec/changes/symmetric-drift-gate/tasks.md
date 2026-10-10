# Tasks

## 1. Symmetric content checker (≤2h)

- [x] 1.1 Add `gen/check_symmetry.py` (stdlib only) that loads `event-contract.{json,xml}` and the committed `generated/{contract.py,contract.ts,events.schema.json}` and returns a list of mismatches. Verify: `python3 gen/check_symmetry.py` → exit 0 and one `[ok]` line per leg on a clean tree. ✅
- [x] 1.2 Schema ↔ contract, **both directions**: per-topic key sets equal, `required` equals payload keys minus `optional`, each property type fragment equals the contract's D-Bus→JSON mapping, and every enum equals the contract enum. Verify: `python3 gen/check_symmetry.py` → `[ok] schema <-> contract`; adding a schema-only key `ghost` → `[schema] wallpaper.state: schema key 'ghost' not in contract`. ✅
- [x] 1.3 Python bindings ↔ contract: identity/versioning/delivery/validation/job-lease constants, `EVENTS_METHODS`/`EVENTS_SIGNALS`/`JOB_METHODS` vs the XML, `EVENTS_TOPICS`, and each `*Payload` TypedDict (fields, optionality, `Literal` enums) equal the contract. Verify: `python3 gen/check_symmetry.py` → `[ok] python <-> contract`. ✅
- [x] 1.4 TypeScript bindings ↔ contract: scalar constants, `EVENTS_TOPICS`, the wire method/signal tables vs the XML, and each `*Payload` interface equal the contract. Verify: `python3 gen/check_symmetry.py` → `[ok] typescript <-> contract`. ✅
- [x] 1.5 Leave a clearly named hook for the cross-repo runtime-tables leg (REQ-004) — a `TODO(REQ-004)` marker and an explicit `[skip]` report line; do not fake it. Verify: `grep -n 'REQ-004' gen/check_symmetry.py` → 1 line. ✅

## 2. The gate target (≤1h)

- [x] 2.1 Add `make check-symmetry`, `make contracts-drift` (symmetric check, pre-regeneration drift guard, regenerate, `git diff --exit-code generated/`, untracked guard) and `make drift` (alias). Update `make help`. Verify: `make contracts-drift` → exit 0 on a clean tree. ✅
- [x] 2.2 Confirm the gate fails on drift: hand-edit a generated file (constant → content check; appended blank line → pre-regeneration diff), run the gate, observe non-zero. Verify: `git status --porcelain` → clean after reverting. ✅

## 3. Negative tests (≤2h)

- [x] 3.1 Add `gen/test_symmetry.py` (stdlib `unittest`) with a clean-tree pass plus failure cases on temp copies: (a) a hand-edited generated artifact; (b) a topic/key added to the contract without regeneration; (c) an extra schema key absent from the contract (reverse check); (d) a hand-edited TS table. Verify: `python3 -m unittest discover -s gen -p 'test_*.py'` → `OK` (10 tests). ✅
- [x] 3.2 Demonstrate (a), (b), (c) against `make contracts-drift` in the worktree and revert each. Verify: `git status --porcelain` → clean. ✅

## 4. CI (≤1h)

- [x] 4.1 Add `.github/workflows/drift.yml` running `make contracts-drift` and `make test` on push and pull request. Verify: `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/drift.yml'))"` → `yaml OK`. ✅

## 5. Defect found by the gate (folded in to keep the tree green, AD-19)

- [x] 5.1 Fix `gen/generate.py`: single-argument `Method` `in_args`/`out_args` were emitted as a bare `Member` (iterating raised `TypeError`); `_py_args` now emits the trailing comma. Regenerate `generated/contract.py`. Verify: `python3 -c "import importlib.util as u,sys;s=u.spec_from_file_location('c','generated/contract.py');m=u.module_from_spec(s);sys.modules['c']=m;s.loader.exec_module(m);print(type(next(x for x in m.EVENTS_METHODS if x.name=='BeginJob').out_args).__name__)"` → `tuple`. ✅
