# Tasks

## 1. Pin the data (≤1.5h)

- [x] 1.1 Add `invocation-contract.json` at the repo root with `contract_version: 1`,
  `timeout_unit: "seconds"`, and the `csg` / `weg` / `itr` records transcribed from S1 §1.3–1.6,
  §2.2 (argv, placeholders, env required + injected, artifacts, exit codes, timeout).
  Verify: `python3 -c "import json;c=json.load(open('invocation-contract.json'));print(c['contract_version'], sorted(c['clis']), c['clis']['weg']['timeout'])"`
  → `1 ['csg', 'itr', 'weg'] 600`.
- [x] 1.2 Add `CONTRACT.md` explaining every field and citing the S1 section for each.
  Verify: `rg -n "S1 §" CONTRACT.md` → one citation per field group.

## 2. Package + loader (≤1.5h)

- [x] 2.1 Add `pyproject.toml` (hatchling; distribution `cli-invocation-contract`, version
  `0.1.0`, `requires-python >=3.11`, zero runtime dependencies, dev group `pytest`; wheel
  force-includes the root JSON; `testpaths = ["tests"]`).
  Verify: `uv sync` → exit 0 and `.venv/` created.
- [x] 2.2 Add `src/cli_invocation_contract/__init__.py` with `CONTRACT_VERSION` (`"0.1.0"`,
  the release version), `DATA_VERSION` (`1`, the JSON shape), `load(path=None)` (packaged copy
  first, repo-root fallback, strict data-version check), `get(cli)` raising
  `UnknownCliError(KeyError)`, and `__all__`.
  Verify: `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION, load; print(CONTRACT_VERSION, DATA_VERSION, sorted(load()))"`
  → `0.1.0 1 ['csg', 'itr', 'weg']`.

## 3. Conformance kit (≤2h)

- [x] 3.1 Add `src/cli_invocation_contract/testkit.py` with exactly two public assertions:
  `assert_consumer_invocation(record, cli, argv, env)` (executable basename, template walk with
  optional tail, required env keys, literal-vs-placeholder overrides) and
  `assert_cli_writes_artifacts(record, cli, run, cwd)` (callable or argv, exit 0, exact filenames
  or recursive suffix count, returns matched paths). Stdlib only; no pytest import.
  Verify: `uv run python -c "import cli_invocation_contract.testkit as t; print(t.__all__)"`
  → `['assert_cli_writes_artifacts', 'assert_consumer_invocation']`.

## 4. Tests (≤2h)

- [x] 4.1 Add `tests/test_record.py`: three records, five contract fields, exact CSG argv/names,
  WEG separator + suffix set, ITR optional mappings + `.svg`, env keys/overrides, exit codes,
  timeouts.
  Verify: `uv run pytest tests/test_record.py -q` → exit 0.
- [x] 4.2 Add `tests/test_loader.py`: default `load()`, explicit-path load, `get()` for each CLI,
  unknown CLI raises `UnknownCliError`/`KeyError`, version mismatch raises `ValueError`.
  Verify: `uv run pytest tests/test_loader.py -q` → exit 0.
- [x] 4.3 Add `tests/test_testkit_positive.py` (fake callable/argv that writes artifacts; exact,
  recursive `.svg`, and accepted invocations for all three CLIs) and
  `tests/test_testkit_negative.py` (missing CSG artifact, extra argv token, missing/wrong env,
  no `.svg` match, non-zero exit).
  Verify: `uv run pytest tests/test_testkit_positive.py tests/test_testkit_negative.py -q` → exit 0.

## 5. Wiring + docs (≤1h)

- [x] 5.1 Add `sync`, `test`, and `build` Makefile verbs; `test` keeps the event-contract unittest
  leg and appends `uv run pytest -q` (errors visible, no suppression). Update
  `.github/workflows/drift.yml` to install `uv` before `make test`.
  Verify: `make test` → both legs pass, exit 0; `make build` → `dist/*.whl` + `*.tar.gz`.
- [x] 5.2 Update `README.md` and `AGENTS.md` §2 to name both seams and the versioned same-tag pin
  (runtime + all three CLIs at one `contracts` tag).
  Verify: `rg -n "invocation" README.md AGENTS.md` → each file names the invocation contract.

## 6. Gates (≤1h)

- [x] 6.1 `uv sync && uv run pytest -q && uv build` → exit 0; `dist/` holds wheel + sdist and the
  wheel contains `cli_invocation_contract/invocation-contract.json`.
  Verify: `unzip -l dist/cli_invocation_contract-0.1.0-*.whl | grep invocation-contract.json`.
- [x] 6.2 `make contracts-drift` → exit 0 (event machinery unchanged).
- [x] 6.3 `openspec validate cli-invocation-contract --strict` → exit 0.
