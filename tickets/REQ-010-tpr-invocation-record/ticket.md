---
id: REQ-010
title: "Record the tpr invocation contract"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: tpr-invocation-record
  bmad: none
worktree: .worktrees/REQ-010/
branch: ticket/REQ-010-tpr-invocation-record
---

# Record the tpr invocation contract

## Requirement

Add the `tpr` record to `invocation-contract.json` so the runtime can invoke the new theme producer
through the same conformance kit as `csg`, `weg` and `itr`.

The record:

- `binary`: `tpr`
- `argv`: `generate {wallpaper}` + the eight `--format` values (`yaml`, `conf`, `gtk.css`,
  `adw.css`, `sequences`, `rasi`, `kitty`, `btop.theme`)
- `env.required` / `injected`: `THEME__OUTPUT__DIRECTORY` -> `{output_dir}`,
  `THEME__OUTPUT__OVERWRITE` -> `"true"`
- `artifacts`: exact filenames, the same eight consumer artifacts as `csg`, `min_count: 8`
- `exit_codes`: success 0, nonzero failure, success requires artifacts
- `timeout`: 60 seconds

`theme.json` is written by `tpr generate` but is **not** part of the palette-entry artifact set; the
record names only the eight files the runtime cache accepts. This is recorded in the ticket and the
contract doc.

## Acceptance

- [ ] `invocation-contract.json` has a `tpr` record matching the values above; the other records are
  byte-identical.
- [ ] `CONTRACT_VERSION = "0.4.0"`, `DATA_VERSION = 2`, `pyproject.toml` version `0.4.0`.
- [ ] `tests/test_record.py`, `test_loader.py`, `test_testkit_positive.py`,
  `test_testkit_negative.py` cover `tpr` (record fields, env, artifacts, argv, drift rejection).
- [ ] `CONTRACT.md` documents the fourth record and the 60 s timeout.
- [ ] `CHANGELOG.md` has a `0.4.0` entry citing this ticket; `README.md` status names `v0.4.0`.
- [ ] `make test`, `make check-symmetry`, `uv build` and
  `openspec validate --strict tpr-invocation-record` exit 0.
- [ ] Annotated tag `v0.4.0` after the merge (orchestrator).

## Evidence

- `theme-producer/src/theme_producer/cli/generate_cmd.py` — argv and `--format` surface.
- `theme-producer/src/theme_producer/adapters/projections/registry.py` — the eight format names.
- `theme-producer/src/theme_producer/adapters/settings/config_resolver.py` — `THEME` prefix and
  the `output.directory` / `output.overwrite` OverrideRules.
- `theme-producer/tests/integration/test_cli_local.py` — generate writes `theme.json` + eight
  projections.
- `theme-producer/docs/HANDOFF-v0.1.0.md` — the 9 artifacts and the adoption notes.

## Non-goals

- No runtime, provisioning or CLI edits; those are the adoption slice.
- No change to the `theme.json` artifact set or the runtime palette cache.
- No new testkit assertion; the two existing assertions already enforce the record.
