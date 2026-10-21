# Tasks — itr-templates-dir-contract

## 1. Record the key and bump the data version (≤1h)

- [x] 1.1 In `invocation-contract.json`, set `contract_version` to `2` and add
  `ICON_RENDERER__TEMPLATES__DIR` to `clis.itr.env.required` and
  `clis.itr.env.injected` → `{templates_dir}`. Change nothing else.
  Verify: `uv run python -c "import json;d=json.load(open('invocation-contract.json'));print(d['contract_version'], d['clis']['itr']['env'])"`
  → `2 {'required': [...3 keys...], 'injected': {...3 keys...}}`.
- [x] 1.2 Confirm the other records and every argv/artifact field are untouched.
  Verify: `git diff v0.1.0 -- invocation-contract.json` → only the `contract_version` line and
  the two `itr` env blocks.

## 2. Bump the package (≤1h)

- [x] 2.1 `pyproject.toml` version → `0.2.0`; `CONTRACT_VERSION = "0.2.0"`,
  `DATA_VERSION = 2` in `src/cli_invocation_contract/__init__.py`.
  Verify: `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"`
  → `0.2.0 2`.
- [x] 2.2 Leave `src/cli_invocation_contract/testkit.py` unchanged (it already enforces
  `env.required` / `env.injected`).
  Verify: `git diff v0.1.0 --stat -- src/cli_invocation_contract/testkit.py` → no output.

## 3. Extend the tests (≤1h)

- [x] 3.1 `tests/test_record.py`: assert `CONTRACT_VERSION == "0.2.0"`, `DATA_VERSION == 2`, the
  three-key `itr` env, the key present for `itr`, and absent for `csg`/`weg`.
  Verify: `uv run pytest -q tests/test_record.py` → exit 0.
- [x] 3.2 `tests/test_loader.py`: keep the newer-version refusal, add an explicit v1 refusal, and
  assert the packaged document declares `contract_version: 2`.
  Verify: `uv run pytest -q tests/test_loader.py` → exit 0.
- [x] 3.3 `tests/test_testkit_positive.py`: `itr` env carries `ICON_RENDERER__TEMPLATES__DIR`;
  `tests/test_testkit_negative.py`: omitting it raises `AssertionError` naming the key.
  Verify: `uv run pytest -q tests/test_testkit_positive.py tests/test_testkit_negative.py` →
  exit 0; `tests/test_testkit_api.py` still passes (two assertions).

## 4. Docs (≤1h)

- [x] 4.1 `CONTRACT.md`: add the key to the `itr` env list and document the versioning rule —
  adding a required env key is a minor bump, `DATA_VERSION` 2, 0.1.x loaders refuse the document.
  Verify: `rg -n "ICON_RENDERER__TEMPLATES__DIR|minor" CONTRACT.md` → hits in the `itr` section
  and the top-level version table.
- [x] 4.2 `CHANGELOG.md`: `0.2.0` entry citing REQ-008 and the key. `README.md`: status names
  `v0.2.0` / `cli-invocation-contract 0.2.0`.
  Verify: `rg -n "0.2.0|REQ-008" CHANGELOG.md README.md` → hits in both.

## 5. Gates (≤1h)

- [x] 5.1 `uv run pytest -q` → exit 0 with the new count.
- [x] 5.2 `uv build` → `dist/cli_invocation_contract-0.2.0.tar.gz` +
  `dist/cli_invocation_contract-0.2.0-py3-none-any.whl`, exit 0.
- [x] 5.3 `make test` and `make check-symmetry` → exit 0.
- [x] 5.4 `openspec validate --strict itr-templates-dir-contract` and `openspec validate --all`
  → exit 0.

## 6. Release (≤1h)

- [x] 6.1 Push `main`; create annotated tag `v0.2.0` on the implementation commit and push it.
  Verify: `git cat-file -t v0.2.0` → `tag`; `git rev-parse v0.2.0^{}` → the commit.
- [x] 6.2 Build the assets from the tag in a throwaway worktree and attach them to a GitHub
  Release. Verify: `gh release view v0.2.0 --json assets --jq '.assets[].name'` → wheel + sdist.
- [x] 6.3 Birth-gate proof: anonymous `ls-remote` returns exactly one line; the CI run for the
  pushed commit concludes `success`.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/RandomGenericUsername/contracts 'refs/tags/v0.2.0'`
  → one line; `gh run list --commit <sha> --json conclusion` → `success`.

## Observed (sections 1–6)

Run from the worktree root, base `5e03075`:

| Task | Command | Result |
| --- | --- | --- |
| 1.1 | `uv run python -c "…print(d['contract_version'], d['clis']['itr']['env'])"` | `2 {'required': ['ICON_RENDERER__OUTPUT__OUTPUT_DIR', 'ICON_RENDERER__COLOR_SCHEME__PATH', 'ICON_RENDERER__TEMPLATES__DIR'], 'injected': {... 'ICON_RENDERER__TEMPLATES__DIR': '{templates_dir}'}}`, exit 0 |
| 1.2 | `git diff -- invocation-contract.json` | only the `contract_version` line and the two `itr` env blocks, exit 0 |
| 2.1 | `uv run python -c "…print(CONTRACT_VERSION, DATA_VERSION)"` | `0.2.0 2`, exit 0 |
| 2.2 | `git diff --stat -- src/cli_invocation_contract/testkit.py` | no output, exit 0 |
| 3.1–3.3 | `uv run pytest -q` | `55 passed in 0.23s`, exit 0 |
| 4.1–4.2 | `rg -n "ICON_RENDERER__TEMPLATES__DIR|REQ-008|0.2.0" CONTRACT.md CHANGELOG.md README.md` | hits in all three |
| 5.2 | `uv build` | `Successfully built dist/cli_invocation_contract-0.2.0.tar.gz` + `…-py3-none-any.whl`, exit 0 |
| 5.3 | `make test` | `Ran 10 tests … OK` + `55 passed`, exit 0 |
| 5.3 | `make check-symmetry` | `[drift] symmetric: contract and generated/ agree`, exit 0 |
| 5.4 | `openspec validate --strict itr-templates-dir-contract` | `Change 'itr-templates-dir-contract' is valid`, exit 0 |
| 5.4 | `openspec validate --all` | `Totals: 11 passed, 0 failed (11 items)`, exit 0 |
| 6.1 | `git cat-file -t v0.2.0`; `git rev-parse v0.2.0^{}` | `tag`; `c6c3ab5d523d06210f8e87535c464d3190d005c0` (tag object `442fb9ab`), pushed |
| 6.2 | `gh release view v0.2.0 --json assets --jq '.assets[].name'` | `cli_invocation_contract-0.2.0-py3-none-any.whl`, `cli_invocation_contract-0.2.0.tar.gz` (built in a worktree at `v0.2.0`) |
| 6.3 | anonymous `ls-remote`; `gh run list` | one line, exit 0; runs `39654081676` (`c6c3ab5`) and `39654069916` (`da27780`) both `success` |
