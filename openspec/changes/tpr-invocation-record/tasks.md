# Tasks — tpr-invocation-record

## 1. Record (≤1h)

- [x] 1.1 Add `clis.tpr` to `invocation-contract.json` with the eight artifacts, the two
  `THEME__OUTPUT__*` env keys and `timeout: 60`. Leave the other records byte-identical.
  Verify: `uv run python -c "import json;d=json.load(open('invocation-contract.json'));print(d['clis']['tpr'])"`
  → the record; `git diff -- invocation-contract.json` only adds `tpr`.
- [x] 1.2 Keep `contract_version: 2` and `DATA_VERSION = 2`.
  Verify: `uv run python -c "from cli_invocation_contract import DATA_VERSION;print(DATA_VERSION)"`
  → `2`.

## 2. Package (≤1h)

- [x] 2.1 `CONTRACT_VERSION = "0.4.0"`, `pyproject.toml` version `0.4.0`.
  Verify: `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION;print(CONTRACT_VERSION)"`
  → `0.4.0`.
- [x] 2.2 Do not edit `src/cli_invocation_contract/testkit.py` (the two assertions already enforce
  the record).
  Verify: `git diff --stat -- src/cli_invocation_contract/testkit.py` → no output.

## 3. Tests (≤1h)

- [x] 3.1 `tests/test_record.py`: four records, `CONTRACT_VERSION == "0.4.0"`, tpr argv/env/
  artifacts/timeout, and the other records unchanged.
- [x] 3.2 `tests/test_loader.py`: four records; `get("tpr")`; unknown-error text lists `tpr`.
- [x] 3.3 `tests/test_testkit_positive.py`: a tpr invocation is accepted; a fake tpr writes the
  eight artifacts.
- [x] 3.4 `tests/test_testkit_negative.py`: missing `THEME__OUTPUT__DIRECTORY` and a seven-file
  tpr run are rejected.
  Verify: `uv run pytest -q tests/test_record.py tests/test_loader.py tests/test_testkit_positive.py tests/test_testkit_negative.py`
  → exit 0.

## 4. Docs (≤1h)

- [x] 4.1 `CONTRACT.md`: add the `tpr` section, update "Exactly csg, weg, itr" to four, and the
  timeout table.
- [x] 4.2 `CHANGELOG.md` `0.4.0` entry citing REQ-010; `README.md` status `v0.4.0`.
  Verify: `rg -n "tpr|0.4.0|REQ-010" CONTRACT.md CHANGELOG.md README.md` → hits.

## 5. Gates and release (≤1h)

- [x] 5.1 `make test`, `make check-symmetry`, `uv build` → exit 0.
- [x] 5.2 `openspec validate --strict tpr-invocation-record` → exit 0.
- [x] 5.3 Orchestrator: merge and tag `v0.4.0` (annotated), no push without a remote. (orchestrator)
