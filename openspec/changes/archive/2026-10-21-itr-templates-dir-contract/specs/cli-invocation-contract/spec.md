# cli-invocation-contract (delta)

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: the contract data pins all three CLIs

`invocation-contract.json` SHALL declare `contract_version: 2` and one record per CLI (`csg`,
`weg`, `itr`) under `clis`, each carrying `binary`, `argv`, `env`, `artifacts`, `exit_codes`, and
`timeout`.

Source: spine **AD-4** lines 132–136; slice **S0a** lines 58–60, 85–92; `S1` §1.3–1.6, §2.2;
`contract_version` 2 from REQ-008 (data shape gained a required `itr` env key).

#### Scenario: load() exposes the three records

- **WHEN** `load()` is called with no path
- **THEN** `sorted(load())` is `['csg', 'itr', 'weg']`

#### Scenario: every record carries the contract fields

- **WHEN** each record in `load()` is inspected
- **THEN** it contains `binary`, `argv`, `env`, `artifacts`, `exit_codes`, and `timeout`, and
  `argv` is a non-empty list of strings

#### Scenario: the document declares the v2 data shape

- **WHEN** the packaged `invocation-contract.json` is parsed
- **THEN** its top-level `contract_version` is `2`

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

### Requirement: the loader is stdlib-only and version-strict

`cli_invocation_contract` SHALL export `CONTRACT_VERSION = "0.2.0"` (release version, equal to
the tag without `v`), `DATA_VERSION = 2` (JSON shape version), `load(path=None)`, and `get(cli)`.
`load()` returns `{cli: record}`; `get()` raises `UnknownCliError` (a `KeyError`) for an unknown
CLI; an explicit path is honoured; a mismatched `contract_version` — whether older (`1`) or
newer than `DATA_VERSION` — raises `ValueError`.

Source: **AD-4** line 136; **AD-11**; `SLICES.md` lines 61–62, 85–92; REQ-008 (0.2.0 / data
shape 2).

#### Scenario: release and data versions are distinct

- **WHEN** `CONTRACT_VERSION` and `DATA_VERSION` are read
- **THEN** `CONTRACT_VERSION` is `"0.2.0"`, `DATA_VERSION` is `2`, and the packaged
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
