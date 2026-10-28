# Design — tpr-invocation-record

## D1 — Record `tpr` as a fourth CLI, not a variant of `csg`

`tpr` is a separate binary with its own settings prefix and artifact writer. The record names it
directly; `csg` stays untouched.

Evidence: `theme-producer/src/theme_producer/adapters/settings/config_resolver.py` uses
`ResolutionPolicy(env_prefix="THEME")`; `csg` uses `COLORSCHEME`. The two must not share env keys.

## D2 — Eight consumer artifacts, `theme.json` excluded

`tpr generate` always writes `theme.json` plus the selected projections. The runtime palette entry
accepts exactly the eight consumer files (`contracts/schemas/meta.schema.json:29-73`); an
unrecorded ninth file makes `verify_staging` reject the entry
(`dotfiles-runtime/.../cache.py:448-465`). The record therefore names the eight, and the adoption
adapter copies only those.

Evidence: `theme-producer/tests/integration/test_cli_local.py` asserts nine output files; the
runtime contract asserts eight. The `theme.json` exclusion is deliberate.

## D3 — 60 s timeout, local-first

The record's timeout is 60 s, matching `csg`/`itr`. Container runs use the adapter's own timeout
(the same split as `csg` contract 60 vs adapter 330). No new timeout semantics.

## D4 — Data shape stays 2, package 0.4.0

Adding a CLI record does not change the record shape, so `DATA_VERSION` stays 2 and
`contract_version` stays 2. The release version moves to 0.4.0 (minor: additive record).

## Verification

- `uv run python -c "from cli_invocation_contract import get; print(get('tpr'))"` → the record.
- `uv run pytest -q tests/test_record.py tests/test_loader.py tests/test_testkit_positive.py tests/test_testkit_negative.py` → green.
- `make test` + `make check-symmetry` + `uv build` → green.
- `openspec validate --strict tpr-invocation-record` → green.
- Consumer proof: `theme-producer` `tests/contract/test_invocation_contract.py` after the pin
  (adoption slice).
