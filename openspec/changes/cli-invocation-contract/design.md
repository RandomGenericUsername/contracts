# Design — cli-invocation-contract

Scope: the data record, the loader, the two-assertion kit, and the packaging that lets a consumer
install the same tag and run the same records. No consumer changes.

## D1 — The record is data at the repo root, one entry per CLI

`invocation-contract.json` is the single source:

```json
{ "contract_version": 1, "timeout_unit": "seconds",
  "clis": { "csg": { ... }, "weg": { ... }, "itr": { ... } } }
```

Each CLI record carries exactly the fields AD-4 names, plus `binary` so a consumer can derive
`argv[0]` without a second lookup:

| Field | Shape | Source |
|---|---|---|
| `binary` | string (`"csg"`, `"weg"`, `"itr"`) | S1 §1.2 (literal name unless a constructor override is given) |
| `argv` | ordered list of tokens; `{name}` = placeholder, `{name}?` = optional tail | S1 §1.3 |
| `placeholders` | map `"{name}"` → description (which layer supplies it) | S1 §1.3, §3.2 |
| `env.required` | keys that must be present in the child env | S1 §1.5 |
| `env.injected` | adapter-written values; a literal is compared exactly, a `{placeholder}` must be non-empty | S1 §1.5 |
| `artifacts.match` | `exact_filename` or `suffix` | S1 §2.2 |
| `artifacts.recursive` | whether the scan descends into subdirectories | S1 §2.2 |
| `artifacts.filenames` / `suffixes` | the names, or the suffix set | S1 §2.2 |
| `artifacts.min_count` | minimum files; equal to `len(filenames)` for `exact_filename` | S1 §2.2 (all eight names are required) |
| `exit_codes` | `success: 0`, `nonzero_is_failure: true`, `success_requires_artifacts: true` | S1 §2.2, §2.4 |
| `timeout` | seconds (`60` csg, `600` weg, `60` itr) | S1 §1.6 |

Why `timeout` and not `timeout_seconds`: the slice's acceptance gate reads the record keys
directly (`{'argv','env','artifacts','exit_codes','timeout'} <= set(v)`), so the key name is part
of the contract; `timeout_unit` at the top level disambiguates it.
Evidence: `SLICES.md` lines 85–92.
Verify: `sed -n '85,92p' <planning-repo>/architecture/architecture-cli-repos-2026-10-19/SLICES.md`.

`min_count` for `exact_filename` is redundant with the list but makes the two artifact modes
uniform, so the kit has one branch for "how many are required".

## D2 — Loader: stdlib `json`, plain mappings, strict version

`load(path=None)` returns `{cli: record}` — the mapping the acceptance gate iterates. It:

1. resolves the default path to the packaged `invocation-contract.json` (wheel) and falls back to
   the repo-root file (source checkout), so the same call works pre- and post-install;
2. parses with `json` and requires `contract_version == DATA_VERSION`, raising `ValueError`
   otherwise (a consumer on incompatible data fails loudly instead of silently reading a
   different shape);
3. requires a non-empty `clis` mapping.

`get(cli, path=None)` is `load(path)[cli]` with a dedicated `UnknownCliError(KeyError)`, so
`except KeyError` and `except UnknownCliError` both work while the message names the known CLIs.

Plain dicts, not dataclasses: the consumers read a handful of keys and the record is validated by
tests (`tests/test_record.py`), so a model layer would add code without removing a failure mode.
Evidence for "no model needed": the only observed consumer reads are key lookups in the adapters
(S1 §2.2, §6.1). `SLICES.md` line 55 says "json + dataclasses" as an implementation hint; this
design keeps `json` and drops dataclasses, which does not change any exported name.

## D3 — `assert_consumer_invocation(record, cli, argv, env)`

Checks a consumer's **recorded** invocation against the record, without running anything:

- `record["binary"] == cli`, else `AssertionError` (a record paired with the wrong CLI is a test
  bug, not a contract violation);
- `argv` is non-empty and `argv[0]` is the binary name or a path whose basename is it — S1 §1.2
  shows the adapter uses the literal name unless an explicit `*_bin` path is supplied, so both are
  conforming;
- the remaining tokens walk the template in order: a literal token must match exactly; a
  `{placeholder}` token must be a non-empty string; a trailing `{placeholder}?` may be absent,
  and any token after it is an error. This encodes `itr render [<mappings-file>]` (S1 §1.3) and
  the fixed CSG/WEG argv without hard-coding those literals outside the JSON;
- every `env.required` key is present; an `env.injected` literal (e.g.
  `COLORSCHEME__OUTPUT__OVERWRITE = "true"`) must match exactly and a placeholder value must be
  non-empty. Extra keys are allowed because the child env is an allowlisted copy of the host env
  (S1 §1.5), not the override map alone.

It returns `None`; failures are `AssertionError` with the offending token/key in the message.

## D4 — `assert_cli_writes_artifacts(record, cli, run, cwd)`

Runs the CLI (or a stand-in) and asserts the record's artifacts exist under `cwd`:

- `run` callable → called with no arguments; `None` means success, an `int` is an exit code, and
  an object with `returncode` is inspected (covers `subprocess.CompletedProcess`).
- `run` sequence of strings → executed as a complete argv via `subprocess.run(argv, cwd=cwd)`;
  a non-zero return code is an `AssertionError`. The list is the **full** argv (executable first)
  because placeholder values are the caller's data, not the record's.
- artifacts: `exact_filename` requires each listed name to be a regular file directly in `cwd`;
  `suffix` walks `cwd` recursively when `recursive` is true and matches case-insensitively, then
  requires at least `min_count` files.

Returns the sorted matched paths. It raises `AssertionError` for missing artifacts and `TypeError`
for an unusable `run`, and never imports pytest (the kit must run inside a consumer's own runner,
including a plain script). Evidence for the runner-injection requirement: `SLICES.md` lines 61–65.
Verify: `sed -n '61,67p' <planning-repo>/architecture/architecture-cli-repos-2026-10-19/SLICES.md`.

## D5 — Packaging: one JSON, included in the wheel and the sdist

The root file stays the only source. Hatchling force-includes it into the wheel as
`cli_invocation_contract/invocation-contract.json`; the sdist lists the root file plus `src/` and
`tests/`. No second copy is committed, so a stale duplicate cannot exist.

`requires-python = ">=3.11"` (ticket instruction): the module uses only `json`, `pathlib`,
`os`, `re`, and `subprocess`, all available on 3.11, and a lower floor cannot exclude a consumer
that requires 3.14 (the runtime and CSG today). No runtime dependencies; `pytest` is in the dev
dependency group only.

## D6 — No real binary, no ambient state

Tests build a fake CLI as a temp file (or a Python callable) that writes the expected artifacts
into `tmp_path`. They never invoke `csg`/`weg`/`itr`, never read `HOME`/XDG paths, and never touch
the network. This is the AD-8 hermetic shape applied to a package that has no discovery logic:
every assertion's inputs are explicit arguments.

## Verification plan

| Decision | Check | Expected |
|---|---|---|
| D1 | `uv run pytest tests/test_record.py -q` | exit 0; three CLI records, exact CSG names, suffix sets, timeouts |
| D1 | `uv run python -c "from cli_invocation_contract import load; c=load(); print(sorted(c), sorted(c['csg']))"` | `['csg','itr','weg']` and the five contract fields + `binary`/`placeholders` |
| D2 | `uv run pytest tests/test_loader.py -q` | exit 0; data-version mismatch `ValueError`; unknown CLI raises `UnknownCliError` |
| D3/D4 | `uv run pytest tests/test_testkit_positive.py tests/test_testkit_negative.py -q` | exit 0; fake CLI accepted, missing artifact rejected |
| D3 | `uv run python -c "import cli_invocation_contract.testkit as t; print(t.__all__)"` | `['assert_cli_writes_artifacts', 'assert_consumer_invocation']` |
| D5 | `uv build` then `unzip -l dist/cli_invocation_contract-0.1.0-*.whl \| grep invocation-contract.json` | wheel contains the data file; `dist/` has wheel + sdist |
| D5 | `uv run python -c "import sys, cli_invocation_contract; print(cli_invocation_contract.__file__)"` | installed from the wheel/synced tree; stdlib only |
| D6 | `rg -n "subprocess.run|pytest" src/cli_invocation_contract/` | only the kit's own `subprocess.run`; no pytest import |

## Risks / open items

- **`>=3.11` vs `>=3.12`.** `SLICES.md` line 54 says `>=3.12`; the ticket says `>=3.11`. This
  change follows the ticket. A 3.11 floor is strictly more permissive for the 3.14 consumers;
  raising it later is non-breaking for them.
- **`assert_cli_conformance` naming.** `SLICES.md` line 64 names the second assertion
  `assert_cli_conformance(...)`; the ticket fixes `assert_cli_writes_artifacts(record, cli, run,
  cwd)`. This change ships the ticket name and records the rename here so S0b pins the same name.
- **Tag/release** is deliberately out of scope. Two versions are exported and kept distinct:
  `CONTRACT_VERSION = "0.1.0"` is the release version (equal to the `v0.1.0` tag without `v`, as
  AD-11 requires a CLI to report) and `DATA_VERSION = 1` is the JSON shape version. Only a release
  moves `CONTRACT_VERSION`; only an incompatible record shape moves `DATA_VERSION`.
