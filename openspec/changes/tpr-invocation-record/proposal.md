# tpr-invocation-record

## Why

The theme producer (`tpr`) is the successor to `csg` and is now tagged `v0.1.0` with both engines,
the projections and the container images built. The runtime cannot adopt it through the conformance
kit because `invocation-contract.json` has no `tpr` record. Adding the record now keeps the
adoption slice limited to the runtime adapter and the producer fingerprint.

Evidence: `theme-producer` `src/theme_producer/cli/generate_cmd.py` (argv + `--format`),
`src/theme_producer/adapters/projections/registry.py` (eight format names),
`src/theme_producer/adapters/settings/config_resolver.py` (`THEME` prefix and the two output
overrides), `tests/integration/test_cli_local.py` (`theme.json` + eight projections).
Verify: `cd theme-producer && uv run tpr generate --dry-run <wallpaper>` shows the argv; the
integration test asserts nine files.

## What Changes

- `invocation-contract.json`: add `clis.tpr` with the eight consumer artifacts, the two
  `THEME__OUTPUT__*` env keys and a 60 s timeout. The other records are unchanged;
  `contract_version` stays `2`.
- `cli-invocation-contract` `0.4.0`: bump `CONTRACT_VERSION`, `pyproject.toml`, `CHANGELOG.md`,
  `README.md`; `DATA_VERSION` stays `2`.
- `CONTRACT.md`: add the `tpr` section and the fourth-record wording.
- Tests: extend `test_record.py`, `test_loader.py`, `test_testkit_positive.py`,
  `test_testkit_negative.py` for `tpr`.
- OpenSpec: modify the "contract data pins all three CLIs" requirement to four, add the `tpr`
  requirements and scenarios.

## Capabilities

- **Modified:** `cli-invocation-contract` — one new record, same data shape.

## Non-goals

- No runtime/provisioning/CLI edits; those are the adoption slice in the dotfiles repos.
- No `theme.json` in the record: it is canonical but not a palette-entry artifact.
- No new testkit assertion.

## Impact

- Consumers re-pin `contracts` in the adoption slice; `csg`/`weg`/`itr` are unaffected.
- The runtime can call `tpr` through the same kit and reject argv/env/artifact drift.
