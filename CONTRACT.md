# The CLI invocation contract

`invocation-contract.json` is the single source for how the Python runtime invokes `csg`, `weg`,
and `itr`. It is versioned data (`contract_version`) shipped by the `cli-invocation-contract`
distribution; the conformance kit is `cli_invocation_contract.testkit`.

**Source of truth.** Every literal below is transcribed from the investigation report
`S1-runtime-cli-addressing.md` (in the `dotfiles-v3` `clirsplit` worktree, under
`docs/investigation/`). The report records the adapters' code, a recording probe of the exact
argv/env/cwd/stdin of all three calls, and the artifact checks. This file does not re-derive
anything; it cites the S1 section for each field.

Evidence: `S1` §0 (condensed facts table), §1.3–1.6, §2.2. Verify (from that worktree):
`sed -n '20,34p;118,271p;314,329p' docs/investigation/S1-runtime-cli-addressing.md`.

## Top level

Two versions are exported and kept distinct:

- `CONTRACT_VERSION = "0.2.0"` — the **release** version, equal to the `contracts` tag without its
  leading `v` (AD-11: each CLI reports this version and it must equal the pinned tag).
- `DATA_VERSION = 2` — the **data shape** version declared by `contract_version` in the JSON.

| Field | Meaning |
|---|---|
| `contract_version` | Integer version of the data shape. `cli_invocation_contract.DATA_VERSION` must equal it, or `load()` raises `ValueError`. Bumped with every data change, in a new `contracts` tag. |
| `timeout_unit` | Unit for every record's `timeout`: seconds. |
| `clis` | Mapping `cli name` → record. Exactly `csg`, `weg`, `itr` today. |

### Versioning rule

- **Adding a required env key is a minor bump** (`0.1.0` → `0.2.0`): no argv, artifact, or
  exit-code semantics change, so the record stays usable by every consumer — but `load()` is
  version-strict, so a **0.1.x loader refuses a v2 document** instead of reading it and silently
  ignoring a key it does not know. That loud failure is why `DATA_VERSION` also moves (`1` → `2`)
  on an additive change; the shape identifier follows the tag.
- Removing or renaming a required key, or changing argv/artifact/exit-code semantics, is a
  breaking change: a new major (or, on 0.x, the next minor) that every consumer re-pins.
- Consumers pin one tag, never a range (AD-9/AD-11), so a v2 document never reaches a 0.1.x
  loader in a correct install.

Evidence: `invocation-contract.json` `contract_version` and
`src/cli_invocation_contract/__init__.py` `CONTRACT_VERSION` / `DATA_VERSION`; the strict
comparison is `load()`'s `if version != DATA_VERSION` branch. Verify:
`uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"`
→ `0.2.0 2`.

## Per-CLI record

| Field | Meaning | S1 |
|---|---|---|
| `binary` | The console name the runtime resolves on `PATH` (`argv[0]`) when no explicit `*_bin` override is given. | §1.2 |
| `argv` | Ordered tokens after the executable. `{name}` is a placeholder; `{name}?` is an optional trailing placeholder. Literal tokens must match exactly. | §1.3 |
| `placeholders` | Human-readable map `{name}` → who supplies it and when. Placeholders are **not** contract values; a consumer fills them from its own run. | §1.3, §3.2 |
| `env.required` | Keys that must be present in the child environment. | §1.5 |
| `env.injected` | Values the adapter writes. A literal (no braces) is compared exactly; a `{placeholder}` must resolve to a non-empty path/value. | §1.5 |
| `artifacts.match` | `exact_filename` (named files directly in the output dir) or `suffix` (any file with a listed extension). | §2.2 |
| `artifacts.recursive` | Whether the suffix scan descends into subdirectories. `false` for `csg`; `true` for `weg`/`itr`. | §2.2 |
| `artifacts.filenames` | Required exact names (empty for a suffix match). | §2.2 |
| `artifacts.suffixes` | Required extension set (empty for an exact match), compared case-insensitively. | §2.2 |
| `artifacts.min_count` | Minimum number of matching files. Equal to `len(filenames)` for `exact_filename`. | §2.2 |
| `exit_codes.success` | `0`. | §2.2 |
| `exit_codes.nonzero_is_failure` | `true`: any non-zero exit is a failed invocation; the runtime raises with the exit code and truncated stderr/stdout. A negative code is a signal. | §2.4 |
| `exit_codes.success_requires_artifacts` | `true`: exit 0 alone is not success — the artifacts must exist, or the invocation is fatal. | §2.2 |
| `timeout` | Default wall-clock budget in seconds. `csg` 60, `weg` 600, `itr` 60. | §1.6 |

## The three records

### `csg` — color scheme generation

```
csg generate <wallpaper> --format yaml --format conf --format gtk.css --format adw.css \
    --format sequences --format rasi --format kitty --format btop.theme
```

- No `-o`/`--output`: output redirection is exclusively
  `COLORSCHEME__OUTPUT__DIRECTORY=<output_dir>`, with `COLORSCHEME__OUTPUT__OVERWRITE="true"`.
- Required artifacts, exact names: `colors.yaml`, `colors.conf`, `colors.gtk.css`,
  `colors.adw.css`, `colors.sequences`, `colors.rasi`, `colors.kitty`, `colors.btop.theme`.
- Timeout 60 s.

Evidence: `S1` §1.3 (`csg_adapter.py:278-300` and the observed argv), §1.5 (`:269-276`),
§2.2 (`:352-380`), §1.6 (`:127`). Verify:
`sed -n '118,150p;226,240p;314,329p;259,270p' docs/investigation/S1-runtime-cli-addressing.md`.

### `weg` — wallpaper effects

```
weg batch all -- <wallpaper>
```

- The `--` separator is part of the contract; the wallpaper is the final token.
- Only env override: `WALLPAPER__OUTPUT__DIRECTORY=<output_dir>`.
- Required artifacts: at least one file, recursively under the output dir, with suffix
  `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff`, or `.gif`.
- Timeout 600 s.

Evidence: `S1` §1.3 (`weg_adapter.py:351-360`), §1.5 (`:344-349`), §2.2 (`:429-444`),
§1.6 (`:188`, `DEFAULT_TIMEOUT = 600`). Verify:
`sed -n '144,154p;226,240p;314,329p;259,270p' docs/investigation/S1-runtime-cli-addressing.md`.

### `itr` — icon template rendering

```
itr render [<mappings-file>]
```

- `render` is always present. The mappings file is appended **only** when the resolved mappings
  input is a regular file; when it is a directory the adapter passes no positional, and a real
  `itr render` then exits 2 (`Missing argument 'yaml_file'`). The provisioned spine supplies
  `<install>/icon-mappings/icons.yaml`, so the file branch is the production path.
- Env overrides: `ICON_RENDERER__OUTPUT__OUTPUT_DIR=<output_dir>`,
  `ICON_RENDERER__COLOR_SCHEME__PATH=<palette colors.yaml>`, and
  `ICON_RENDERER__TEMPLATES__DIR=<templates dir>`.
- `ICON_RENDERER__TEMPLATES__DIR` is the directory the runtime hashes into the icons entry key;
  `itr` binds it to `templates.dir` and ranks env above `settings.toml` and discovery, so without
  the key the process could render from a directory the runtime never hashed. The record
  therefore requires it and injects the `{templates_dir}` placeholder (REQ-008).
- Required artifacts: at least one `.svg`, recursively under the output dir.
- Timeout 60 s.

Evidence: `S1` §1.3 (`itr_adapter.py:410-419`; real `itr render` exit 2), §1.5 (`:402-408`),
§2.2 (`:487-497`), §1.6 (`:102`); REQ-008 for the templates key — `itr` binds it at
`assembled_config_resolver.py:66,70` (`ResolutionPolicy(env_prefix="ICON_RENDERER")`,
`OverrideRule("templates.dir", …)`) and names it in `cli/main.py:37` and
`icon_renderer.py:292`; the runtime hashes it at `itr_adapter.py:233` but its `build_env` call
(`:402-407`) omits it. Verify:
`sed -n '154,193p;226,240p;314,329p;259,270p' docs/investigation/S1-runtime-cli-addressing.md`
and, in `dotfiles-v3`, `grep -n "ICON_RENDERER__TEMPLATES__DIR"
src/runtime/src/runtime/adapters/itr_adapter.py` → no output (the gap this key closes).

## The child environment

The recorded `env` is added to an **allowlisted copy** of the host environment, not
`dict(os.environ)`: `PATH`, `HOME`, `XDG_*`, `TERM`, `LANG`, `LC_*`, TLS/proxy variables, plus
keys starting `COLORSCHEME__`, `WALLPAPER__`, `ICON_RENDERER__`, `XDG_`. Keys containing
`TOKEN`, `SECRET`, `PASSWORD`, `AWS_`, `GITHUB_` are blocked. `build_env` lives in the runtime
(`adapters/env.py`), not in this contract; the record names only the keys an invocation depends on,
and the kit tolerates extra env keys.

Evidence: `S1` §1.5 (allowlist paragraph) and §3.3 (probe shows a secret and single-underscore
config vars absent, XDG forwarded). Verify:
`sed -n '240,257p;498,551p' docs/investigation/S1-runtime-cli-addressing.md`.

## The kit

`cli_invocation_contract.testkit` exposes exactly two assertions:

```python
assert_consumer_invocation(record, cli, argv, env)   # recorded invocation vs record
assert_cli_writes_artifacts(record, cli, run, cwd)   # run the CLI, check artifacts
```

`assert_consumer_invocation` accepts `argv[0]` as the bare binary or a path whose basename is it,
checks the template walk (optional tail included), requires every `env.required` key, and compares
literal overrides exactly.

`assert_cli_writes_artifacts` runs a zero-argument callable (returning `None`, an exit code, or an
object with `returncode`) or a complete argv, requires exit 0, then checks the record's artifacts
under `cwd` and returns the matched paths.

Both are stdlib-only; neither imports pytest. Usage from a consumer:

```python
from cli_invocation_contract import get
from cli_invocation_contract.testkit import assert_cli_writes_artifacts

record = get("csg")
assert_cli_writes_artifacts(record, "csg", ["csg", *argv_tail], output_dir)
```

Verify: `uv run python -c "import cli_invocation_contract.testkit as t; print(t.__all__)"`
→ `['assert_cli_writes_artifacts', 'assert_consumer_invocation']`.
