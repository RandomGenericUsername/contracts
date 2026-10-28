# cli-invocation-contract (delta)

## ADDED Requirements

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

## MODIFIED Requirements

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
