# Design — itr-templates-dir-contract

## Context

`ItrAdapter.render` hashes `templates_dir` and folds that hash into `icons_entry_hash`, then
spawns `itr render` with two env keys and an optional positional mappings file. `itr` resolves
`templates.dir` independently (`--template-dir` > `ICON_RENDERER__TEMPLATES__DIR` >
`settings.toml` > discovery). The contract is the only place the runtime and `itr` agree on what
an invocation consists of, so the missing dependency belongs there — not in either consumer's
tests.

Evidence: `sed -n '402,420p' src/runtime/src/runtime/adapters/itr_adapter.py` (dotfiles-v3
`8df35a9`) → `env = build_env({"ICON_RENDERER__OUTPUT__OUTPUT_DIR": …,
"ICON_RENDERER__COLOR_SCHEME__PATH": …})`, `args = [bin_name, "render"]`, mappings appended only
when it is a file. `sed -n '66,70p;95p'
src/icon_templates_renderer/adapters/assembled_config_resolver.py` (icon-templates-renderer
`2543c00`) → `ResolutionPolicy(env_prefix="ICON_RENDERER")` +
`OverrideRule("templates.dir", {OverrideSource.CLI, OverrideSource.ENV})` →
`TemplatesSettings(dir=result.config.templates.dir)`.

## Decisions

### D1 — Record the env key, not a new argv flag

Add `ICON_RENDERER__TEMPLATES__DIR` to the `itr` record; do not add `--template-dir` to `argv`.

- `itr` already binds the env key to `templates.dir` and ranks it above `settings.toml` and
  discovery, so no CLI change is needed: `grep -n "ICON_RENDERER__TEMPLATES__DIR"
  src/icon_templates_renderer/adapters/icon_renderer.py` → `292`, `317`.
- The other two `itr` path inputs are env-injected (`{output_dir}`, `{palette_colors_yaml}`); a
  flag for one input and env for the rest would split the record's addressing scheme.
- The runtime already resolves the directory (it hashes it); only the forwarding is missing, so
  the consumer change is two lines in `build_env`.
- An argv flag would change the argv template, which every consumer's kit run would then have to
  re-verify — a larger blast radius for the same behaviour.

Rejected alternative: leave the contract alone and let each side rely on `settings.toml`. That is
the current bug — the hashed directory and the resolved directory can differ, so the icons cache
key can name bytes it did not render.

### D2 — Keep `required` and `injected` in lockstep

The new key appears in both `env.required` and `env.injected` (`{templates_dir}`), exactly like
`ICON_RENDERER__OUTPUT__OUTPUT_DIR` and `ICON_RENDERER__COLOR_SCHEME__PATH`.

- `required` is what the kit checks for presence; `injected` is what the record says the adapter
  writes. Every existing `itr` key is in both, so the record stays uniform.
- A placeholder (not a literal) keeps the contract from fixing an install path; the kit only
  requires a non-empty value. Same rule as the other two path keys.

Evidence: `uv run python -c "import json;d=json.load(open('invocation-contract.json'));print(d['clis']['itr']['env'])"`
at `v0.1.0` → `{'required': ['ICON_RENDERER__OUTPUT__OUTPUT_DIR',
'ICON_RENDERER__COLOR_SCHEME__PATH'], 'injected': {'ICON_RENDERER__OUTPUT__OUTPUT_DIR':
'{output_dir}', 'ICON_RENDERER__COLOR_SCHEME__PATH': '{palette_colors_yaml}'}}` — keys in
lockstep, both values placeholders.

### D3 — `contract_version: 2` and package `0.2.0` (minor)

- The package bump is **minor** (`0.1.0` → `0.2.0`): the change adds a key, it does not rename or
  remove one, and it does not change argv/artifacts. The `contracts` tag is `v0.2.0` and
  `CONTRACT_VERSION` equals it (AD-11).
- The **data** version moves `1` → `2` even though the change is additive, because `load()` is
  version-strict on `contract_version`: a 0.1.x loader must refuse a v2 document instead of
  reading it and silently ignoring a key it does not know. That loud failure is the documented
  contract rule ("a document that declares a different shape fails loudly instead of being
  misread"), so the shape identifier moves with the tag.
- Consumers pin one tag, never a range (AD-9/AD-11), so a v2 document never reaches a 0.1.x
  loader in a correct install; the version check is the guard rail, not the migration path.

Evidence: `sed -n '34,38p;76,82p' src/cli_invocation_contract/__init__.py` at `v0.1.0` →
`CONTRACT_VERSION = "0.1.0"`, `DATA_VERSION = 1`, and the strict-equality check
`if version != DATA_VERSION: raise ValueError(... "contract data version mismatch" ...)`.
Verify: `uv run python -c "import cli_invocation_contract as c; print(c.CONTRACT_VERSION, c.DATA_VERSION)"`.

### D4 — No testkit source change

`assert_consumer_invocation` already (a) requires every key in `env.required` to be present and
(b) requires every `env.injected` placeholder to be non-empty. Adding the key to the record
therefore tightens every consumer's kit run with no code change, which keeps the public surface at
exactly two assertions.

Evidence: `sed -n '169,190p' src/cli_invocation_contract/testkit.py` → the `env_record["required"]`
presence loop and the `env_record["injected"]` placeholder/literal loop. The kit's `__all__` is
asserted unchanged by `tests/test_testkit_api.py::test_public_surface_is_exactly_two_assertions`.
Verify: `uv run pytest -q tests/test_testkit_api.py` → exit 0.

## Verification plan

| Decision | Check | Expected |
| --- | --- | --- |
| D1 | `uv run pytest -q tests/test_record.py` | exit 0; the `itr` env test asserts three keys, and no argv test changed |
| D1/D2 | `uv run python -c "from cli_invocation_contract import get; print(get('itr')['env'])"` | third key `ICON_RENDERER__TEMPLATES__DIR: {templates_dir}`; `csg`/`weg` unchanged |
| D2 | `uv run pytest -q tests/test_testkit_positive.py tests/test_testkit_negative.py` | exit 0; positive `itr` env carries the key, negative omission raises `AssertionError` |
| D3 | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.2.0 2` |
| D3 | `uv run pytest -q tests/test_loader.py` | exit 0; a v1 document is refused with `version mismatch` |
| D4 | `uv run pytest -q tests/test_testkit_api.py` | exit 0; `__all__` still the two assertions |
| Release | `git worktree add /tmp/opencode/contracts-v020 v0.2.0 && (cd /tmp/opencode/contracts-v020 && uv build)` | `cli_invocation_contract-0.2.0.tar.gz` + `-py3-none-any.whl`, exit 0 |
