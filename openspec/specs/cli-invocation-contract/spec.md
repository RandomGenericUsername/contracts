# cli-invocation-contract Specification

## Purpose

This capability is the runtime ↔ CLI seam: `invocation-contract.json` records, per CLI (`csg`,
`weg`, `itr`), the binary, argv template, required and injected env, expected artifacts, exit
codes and timeout, and the stdlib-only `cli_invocation_contract` package loads it (`load()` /
`get()`) with exactly two testkit assertions for consumers. It exists so the Python runtime and
all three CLIs agree on one invocation shape, pin the same `contracts` tag, and never re-type
argv/env/artifact literals in their own tests.

## Requirements

### Requirement: CSG argv and artifacts match the observed invocation

The `csg` record SHALL carry the generated-file argv from S1 §1.3 (eight `--format` pairs, no
`-o`/`--output`) and the eight exact artifact filenames from S1 §2.2.

Source: `S1` §1.3 (`csg_adapter.py:278-300` and the recording-probe argv) and §2.2
(`csg_adapter.py:352-367` presence check, `:369-380` hashes).

#### Scenario: the format pairs are exact

- **WHEN** the `csg` record's `argv` is read from `load()`
- **THEN** it is `["generate", "{wallpaper}", "--format", "yaml", "--format", "conf",
  "--format", "gtk.css", "--format", "adw.css", "--format", "sequences", "--format", "rasi",
  "--format", "kitty", "--format", "btop.theme"]`, so it contains exactly eight `--format`
  tokens and no `-o`/`--output`

#### Scenario: the artifacts are exact filenames, not a suffix scan

- **WHEN** the `csg` record's `artifacts` is read
- **THEN** `match` is `exact_filename`, `recursive` is `false`, `filenames` lists the eight names,
  and `min_count` is `8`

### Requirement: WEG argv and artifacts match the observed invocation

The `weg` record SHALL carry the argv template `["batch", "all", "--", "{wallpaper}"]` and a
recursive suffix artifact set of `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff`, `.gif` with a
minimum of one file.

Source: `S1` §1.3 (`weg_adapter.py:351-360`: `args = [bin_name, "batch", "all", "--",
str(wallpaper_path)]`) and §2.2 (`weg_adapter.py:429-444` recursive image scan).

#### Scenario: the separator before the wallpaper is retained

- **WHEN** the `weg` record's `argv` is read
- **THEN** the last three tokens are `all`, `--`, `{wallpaper}`

#### Scenario: artifacts are a recursive image scan

- **WHEN** the `weg` record's `artifacts` is read
- **THEN** `match` is `suffix`, `recursive` is `true`, `min_count` is `1`, and `suffixes` is
  exactly `['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif']`

### Requirement: ITR argv and artifacts match the observed invocation

The `itr` record SHALL carry the argv template `["render", "{mappings_file}?"]` — the mappings
file is optional because the adapter appends it only when the resolved mappings input is a regular
file — and a recursive `.svg` artifact set with a minimum of one file.

Source: `S1` §1.3 (`itr_adapter.py:410-419`, including the real-CLI `Missing argument
'yaml_file'` exit 2 for the directory branch) and §2.2 (`itr_adapter.py:487-497` recursive SVG
scan).

#### Scenario: render is always present, mappings is optional

- **WHEN** the `itr` record's `argv` is read
- **THEN** it is `["render", "{mappings_file}?"]` and `placeholders["{mappings_file}"]` documents
  that it is supplied only for a regular file

#### Scenario: artifacts are a recursive SVG scan

- **WHEN** the `itr` record's `artifacts` is read
- **THEN** `match` is `suffix`, `recursive` is `true`, `min_count` is `1`, and `suffixes` is
  `['.svg']`

### Requirement: env records name the required keys and the injected overrides

Each record's `env` SHALL carry `required` (keys present in the child env) and `injected` (the
values the adapter writes). Literal values appear verbatim; directory/path values are
placeholders. Every key in `required` SHALL also appear in `injected`.

Source: `S1` §1.5 (the per-adapter override table and the allowlist paragraph); REQ-008 for the
`itr` templates key.

#### Scenario: CSG env

- **WHEN** the `csg` record's `env` is read
- **THEN** `required` is `COLORSCHEME__OUTPUT__DIRECTORY` and `COLORSCHEME__OUTPUT__OVERWRITE`,
  the first `injected` value is `{output_dir}`, and the second is the literal `"true"`

#### Scenario: WEG env

- **WHEN** the `weg` record's `env` is read
- **THEN** `required` is `WALLPAPER__OUTPUT__DIRECTORY` and its `injected` value is
  `{output_dir}`

#### Scenario: ITR env

- **WHEN** the `itr` record's `env` is read
- **THEN** `required` is `ICON_RENDERER__OUTPUT__OUTPUT_DIR`,
  `ICON_RENDERER__COLOR_SCHEME__PATH`, and `ICON_RENDERER__TEMPLATES__DIR`, with injected values
  `{output_dir}`, `{palette_colors_yaml}`, and `{templates_dir}`

### Requirement: exit-code semantics are success = 0 plus artifacts

Each record SHALL declare `exit_codes.success = 0`, `exit_codes.nonzero_is_failure = true`, and
`exit_codes.success_requires_artifacts = true`.

Source: `S1` §2.2 ("Success is exit status + artifact presence, not stdout"; "A zero exit with
missing artifacts is also fatal") and §2.4 (non-zero exit raises with the exit code).

#### Scenario: zero without artifacts is not success

- **WHEN** the `exit_codes` of any record is read
- **THEN** `success` is `0`, `nonzero_is_failure` is `true`, and `success_requires_artifacts` is
  `true`

### Requirement: default timeouts match the adapters

The records SHALL declare `timeout` 60 for `csg`, 600 for `weg`, and 60 for `itr`, in seconds.

Source: `S1` §1.6 (`csg_adapter.py:127`, `itr_adapter.py:102`, `weg_adapter.py:188`).

#### Scenario: WEG's longer budget is preserved

- **WHEN** `load()` returns the three records
- **THEN** `load()['csg']['timeout'] == 60`, `load()['weg']['timeout'] == 600`, and
  `load()['itr']['timeout'] == 60`, with the top-level `timeout_unit` equal to `"seconds"`

### Requirement: the loader is stdlib-only and version-strict

`cli_invocation_contract` SHALL export `CONTRACT_VERSION = "0.3.0"` (release = tag without `v`),
`DATA_VERSION = 2`, `load(path=None)`, and `get(cli)`. `load()` returns `{cli: record}`; `get()`
raises `UnknownCliError` (a `KeyError`) for an unknown CLI; a document whose `contract_version`
differs from `DATA_VERSION` raises `ValueError`; an explicit path is honoured.

Source: **AD-4** line 136; **AD-11**; `SLICES.md` lines 61–62, 85–92; REQ-008 (data v2);
v0.3.0 release (REQ-009).

#### Scenario: release and data versions are distinct

- **WHEN** `CONTRACT_VERSION` and `DATA_VERSION` are read
- **THEN** `CONTRACT_VERSION` is `"0.3.0"`, `DATA_VERSION` is `2`, and the packaged
  `invocation-contract.json` declares `contract_version: 2`

#### Scenario: unknown CLI is an error

- **WHEN** `get("nope")` is called
- **THEN** it raises `UnknownCliError`, which is a subclass of `KeyError`

#### Scenario: a v1 document is refused

- **WHEN** `load(path)` reads a document with `contract_version: 1`
- **THEN** it raises `ValueError` naming the expected (`2`) and observed (`1`) versions

#### Scenario: version mismatch is refused

- **WHEN** `load(path)` reads a document with `contract_version: 3`
- **THEN** it raises `ValueError` naming the expected and observed versions

#### Scenario: explicit path is honoured

- **WHEN** `load(path)` reads a document with all three records at `contract_version: 2`
- **THEN** the returned mapping has the same keys as the packaged contract

### Requirement: the testkit exposes exactly two assertions

`cli_invocation_contract.testkit` SHALL expose exactly two public names —
`assert_consumer_invocation(record, cli, argv, env)` and
`assert_cli_writes_artifacts(record, cli, run, cwd)` — and SHALL import no third-party module
(no pytest).

Source: spine **AD-4** ("The kit exposes exactly two assertions: (1) a consumer's recorded
invocation matches the record; (2) the CLI accepts the recorded invocation and writes the required
artifacts"); ticket REQ-006.

#### Scenario: only two public names

- **WHEN** the module's `__all__` is read
- **THEN** it is `['assert_cli_writes_artifacts', 'assert_consumer_invocation']`

#### Scenario: no pytest dependency

- **WHEN** the module's imports are inspected
- **THEN** every import is from the standard library or the package itself

### Requirement: the invocation assertion accepts the recorded invocation

`assert_consumer_invocation` SHALL accept an invocation whose executable basename equals the
record's `binary`, whose tail tokens match the template with non-empty placeholder values (and an
omitted optional tail), and whose env contains every required key with literal overrides matching
exactly.

Source: `S1` §1.2 (literal binary name or explicit `*_bin` path), §1.3 (argv), §1.5 (env
overrides).

#### Scenario: exact CSG invocation passes

- **WHEN** a consumer records `argv = ["csg", "generate", "/w/wallpaper.png", "--format",
  "yaml", …, "--format", "btop.theme"]` and env with
  `COLORSCHEME__OUTPUT__DIRECTORY` and `COLORSCHEME__OUTPUT__OVERWRITE="true"`
- **THEN** `assert_consumer_invocation` returns without raising

#### Scenario: a path-qualified executable passes

- **WHEN** `argv[0]` is `/usr/local/bin/weg`
- **THEN** it matches the `weg` record's `binary` `"weg"`

### Requirement: the invocation assertion rejects drift

`assert_consumer_invocation` SHALL raise `AssertionError` for a wrong executable, an unexpected
or missing token, a missing required env key, or a literal override with the wrong value.

Source: spine **AD-4** (the assertion exists to catch "each side testing its own literals …
argv shape, env key, exit code, artifact filenames and hashes drift silently"); `S1` §6.1.

#### Scenario: extra argv token

- **WHEN** a CSG invocation appends `--output /tmp/x`
- **THEN** `assert_consumer_invocation` raises `AssertionError`

#### Scenario: missing env key

- **WHEN** the env omits `WALLPAPER__OUTPUT__DIRECTORY` for `weg`
- **THEN** `assert_consumer_invocation` raises `AssertionError`

#### Scenario: wrong literal override

- **WHEN** `COLORSCHEME__OUTPUT__OVERWRITE` is `"false"`
- **THEN** `assert_consumer_invocation` raises `AssertionError`

### Requirement: the artifact assertion runs the CLI and checks the record

`assert_cli_writes_artifacts` SHALL run the supplied callable or full argv, require exit 0, then
require the record's artifacts under `cwd` (`exact_filename` names, or `min_count` recursive
suffix matches). It SHALL return the matched paths and raise `AssertionError` when one is
missing.

Source: `S1` §2.2; `SLICES.md` lines 63–65 ("runner injected").

#### Scenario: fake CLI that writes all eight CSG files passes

- **WHEN** the callable writes the eight CSG filenames into `cwd` and returns `0`
- **THEN** the assertion passes and returns the eight paths

#### Scenario: missing artifact fails

- **WHEN** the callable writes seven of the eight CSG filenames
- **THEN** the assertion raises `AssertionError` naming the missing file

#### Scenario: recursive suffix match

- **WHEN** the callable writes `battery/battery-0.svg` under `cwd` for `itr`
- **THEN** the assertion passes for the `itr` record

#### Scenario: no suffix match fails

- **WHEN** the callable writes only `.png` files under `cwd` for `itr`
- **THEN** the assertion raises `AssertionError`

### Requirement: the itr record names the icon templates directory

The `itr` record SHALL require and inject the env key `ICON_RENDERER__TEMPLATES__DIR` so an
invocation renders from the directory whose hash the runtime folds into the icons entry key. The
key SHALL appear in both `env.required` and `env.injected` (value `{templates_dir}`); `csg` and
`weg` SHALL NOT carry it.

Source: REQ-008 (`assembled_config_resolver.py:66,70`; `itr_adapter.py:233,402-407`).

#### Scenario: the itr env carries the templates directory

- **WHEN** the `itr` record's `env` is read from `load()`
- **THEN** `required` contains `ICON_RENDERER__TEMPLATES__DIR` and
  `injected["ICON_RENDERER__TEMPLATES__DIR"]` is the placeholder `{templates_dir}`

#### Scenario: the key is scoped to itr

- **WHEN** the `csg` and `weg` records' `env.required` lists are read
- **THEN** neither contains `ICON_RENDERER__TEMPLATES__DIR`

#### Scenario: the kit requires the key for an itr invocation

- **WHEN** `assert_consumer_invocation` is called with an `itr` argv matching the template and an
  env that omits `ICON_RENDERER__TEMPLATES__DIR`
- **THEN** it raises `AssertionError` naming the missing key

### Requirement: the tpr record matches the observed invocation

The contract SHALL carry a `tpr` record with `binary: "tpr"`, the recorded `generate` argv, the
`THEME__OUTPUT__DIRECTORY` / `THEME__OUTPUT__OVERWRITE` env keys, the eight exact consumer
artifacts, the standard exit-code semantics and a 60 s timeout.

Source: `theme-producer` `src/theme_producer/cli/generate_cmd.py`,
`src/theme_producer/adapters/settings/config_resolver.py`,
`src/theme_producer/adapters/projections/registry.py`.

#### Scenario: the tpr record is exposed

- **WHEN** `load()` is called with no path
- **THEN** `sorted(load())` is `['csg', 'itr', 'tpr', 'weg']` and `get("tpr")["binary"]` is `tpr`

#### Scenario: the tpr env carries the output overrides

- **WHEN** the `tpr` record's `env` is read
- **THEN** `required` is `["THEME__OUTPUT__DIRECTORY", "THEME__OUTPUT__OVERWRITE"]` and
  `injected` maps them to `{output_dir}` and the literal `"true"`

#### Scenario: the tpr artifacts are the eight palette files

- **WHEN** the `tpr` record's `artifacts` are read
- **THEN** `match` is `exact_filename`, `recursive` is `false`, `min_count` is `8`, and the
  filenames are the eight consumer files (`colors.yaml`, `colors.conf`, `colors.gtk.css`,
  `colors.adw.css`, `colors.sequences`, `colors.rasi`, `colors.kitty`, `colors.btop.theme`)

#### Scenario: the kit rejects tpr drift

- **WHEN** a `tpr` invocation omits `THEME__OUTPUT__DIRECTORY` or writes only seven artifacts
- **THEN** `assert_consumer_invocation` / `assert_cli_writes_artifacts` raise `AssertionError`

### Requirement: the contract data pins all four CLIs

`invocation-contract.json` SHALL declare `contract_version: 2` and one record per CLI (`csg`,
`weg`, `itr`, `tpr`) under `clis`, each carrying `binary`, `argv`, `env`, `artifacts`, `exit_codes`,
and `timeout`.

Source: spine AD-4; this change adds `tpr` (REQ-010). The data shape is unchanged.

#### Scenario: load() exposes the four records

- **WHEN** `load()` is called with no path
- **THEN** `sorted(load())` is `['csg', 'itr', 'tpr', 'weg']`

#### Scenario: the document declares the v2 data shape

- **WHEN** the packaged `invocation-contract.json` is parsed
- **THEN** its top-level `contract_version` is `2`
