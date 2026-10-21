# itr-templates-dir-contract

## Why

The runtime hashes the `itr` templates directory as an input to the icons cache key, but it never
passes that directory to the `itr` process. `itr` resolves `templates.dir` from its own chain
(`--template-dir` > `ICON_RENDERER__TEMPLATES__DIR` > `settings.toml` > discovery), so today the
process can render from a different directory than the one the runtime hashed — the cache key and
the rendered bytes are silently decoupled. The fix is one contract fact: `itr` invocations depend
on `ICON_RENDERER__TEMPLATES__DIR`, a key the CLI already binds.

Evidence: the runtime's `itr` env has no templates key, though `templates_hash` is computed and
used in the entry hash — `sed -n '402,407p;233p;317p' src/runtime/src/runtime/adapters/itr_adapter.py`
(dotfiles-v3 `8df35a9`) →
`env = build_env({` / `"ICON_RENDERER__OUTPUT__OUTPUT_DIR": str(output_dir),` /
`"ICON_RENDERER__COLOR_SCHEME__PATH": str(colors_yaml_path),`; `templates_hash =
canonical_hash_dir(effective_templates)`; `ih = icons_entry_hash(palette_hash, templates_hash,
mappings_hash)`.
Verify: `grep -n "ICON_RENDERER__\|templates_hash" src/runtime/src/runtime/adapters/itr_adapter.py`
in `dotfiles-v3` → lines 405, 406, 233, 317, and no `TEMPLATES` key.

Evidence: `itr` binds `ICON_RENDERER__TEMPLATES__DIR` to `templates.dir` and ranks env above
settings and discovery — `grep -rn "ICON_RENDERER__TEMPLATES__DIR" src tests docs`
(icon-templates-renderer `2543c00`) → `src/icon_templates_renderer/cli/main.py:37`,
`src/icon_templates_renderer/cli/_helpers.py:70`, `src/icon_templates_renderer/adapters/icon_renderer.py:292` and `:317`,
`tests/integration/test_template_dir_override.py:80`, `docs/ARCHITECTURE_PLAN.md:149`.
The single binding site is
`src/icon_templates_renderer/adapters/assembled_config_resolver.py:66` (`ResolutionPolicy(env_prefix="ICON_RENDERER")`),
`:70` (`OverrideRule("templates.dir", {OverrideSource.CLI, OverrideSource.ENV})`), `:95`
(`TemplatesSettings(dir=result.config.templates.dir)`); `itr`'s own help text names the key
(`src/icon_templates_renderer/cli/main.py:37`: `Env overrides: … ICON_RENDERER__OUTPUT__OUTPUT_DIR,
… ICON_RENDERER__TEMPLATES__DIR, ICON_RENDERER__COLOR_SCHEME__PATH, …`).
Verify: `uv run itr --help` in `icon-templates-renderer` → the env-override line lists
`ICON_RENDERER__TEMPLATES__DIR`.

Evidence: the contract's current `itr` env record names exactly the two keys the runtime sets —
`git show v0.1.0:invocation-contract.json | rg -n "ICON_RENDERER__"` → `ICON_RENDERER__OUTPUT__OUTPUT_DIR`
and `ICON_RENDERER__COLOR_SCHEME__PATH` only.
Verify: `git show v0.1.0:invocation-contract.json | rg -c "ICON_RENDERER__TEMPLATES__DIR"` → exit 1 (no match).

## What Changes

- `invocation-contract.json`: bump `contract_version` to `2`; add
  `ICON_RENDERER__TEMPLATES__DIR` to `clis.itr.env.required` and map it to `{templates_dir}` in
  `clis.itr.env.injected`. Nothing else in the document changes: `argv`, `placeholders`,
  `artifacts`, `exit_codes`, `timeout` stay byte-identical for `csg`, `weg`, and `itr`.
- `cli-invocation-contract` 0.2.0: `CONTRACT_VERSION = "0.2.0"`, `DATA_VERSION = 2`,
  `pyproject.toml` version `0.2.0`.
- `CONTRACT.md`: document the new `itr` key and the versioning rule it exercises (adding a
  required env key is a minor bump that still moves `DATA_VERSION`, because `load()` is
  version-strict).
- `CHANGELOG.md`: a `0.2.0` entry citing REQ-008. `README.md`: status names `v0.2.0`.
- Tests: `tests/test_record.py` asserts the key for `itr` and its absence for `csg`/`weg`;
  `tests/test_loader.py` asserts `DATA_VERSION = 2` and the refusal of a v1 document;
  `tests/test_testkit_positive.py` carries the key in the `itr` invocation and
  `tests/test_testkit_negative.py` proves its absence is rejected. The testkit API is unchanged
  (still exactly two assertions).
- The testkit itself (`src/cli_invocation_contract/testkit.py`) is **not** edited: it already
  enforces every key in `env.required` and every placeholder in `env.injected`.

## Capabilities

- **New Capabilities:** none.
- **Modified Capabilities:** `cli-invocation-contract` — the `itr` record gains a required env
  key, the data version moves to 2, and the release version moves to 0.2.0.

## Non-goals

- **Not** changing any CLI's argv. Adding `--template-dir` to the `itr` argv was considered and
  rejected (see `design.md`); the env key matches the two path overrides already recorded.
- **Not** changing artifacts, exit codes, or timeouts for any CLI.
- **Not** touching `event-contract.json`, `event-contract.xml`, `gen/`, `generated/`, or
  `schemas/`.
- **Not** editing the runtime or CLI repos, or re-pinning them — those are consumer slices that
  land after this tag.
- **Not** archiving this change or closing REQ-008: the ticket's consumer-side acceptance cannot
  hold until the runtime and the three CLIs re-pin.

## Impact

- Modified: `invocation-contract.json`, `src/cli_invocation_contract/__init__.py`,
  `pyproject.toml`, `CONTRACT.md`, `CHANGELOG.md`, `README.md`, `tests/test_record.py`,
  `tests/test_loader.py`, `tests/test_testkit_positive.py`, `tests/test_testkit_negative.py`.
- New: `openspec/changes/itr-templates-dir-contract/**`,
  `tickets/REQ-008-itr-templates-dir-contract/ticket.md`, `tickets/INDEX.md` line.
- Release: annotated tag `v0.2.0` + GitHub Release (wheel + sdist built from the tag). Every
  consumer pins this exact tag; 0.1.x loaders refuse the v2 document by design.
