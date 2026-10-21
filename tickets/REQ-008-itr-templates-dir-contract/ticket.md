---
id: REQ-008
title: "Record the itr templates-dir env key in the invocation contract"
kind: requirement
status: in-progress
lane: 2
links:
  openspec: itr-templates-dir-contract
  bmad: none
worktree: .worktrees/req-008/
branch: ticket/req-008-itr-templates-dir-contract
---

# Record the itr templates-dir env key in the invocation contract

## Requirement

The runtime hashes the `itr` templates directory but never tells `itr` which directory it
hashed; `itr` therefore resolves templates from its own settings chain. The invocation contract
SHALL close that gap by recording, on the `itr` record only, the env key `itr` already binds to
`templates.dir`:

- `invocation-contract.json`:
  - `clis.itr.env.required` SHALL list `ICON_RENDERER__TEMPLATES__DIR` alongside
    `ICON_RENDERER__OUTPUT__OUTPUT_DIR` and `ICON_RENDERER__COLOR_SCHEME__PATH`.
  - `clis.itr.env.injected` SHALL map `ICON_RENDERER__TEMPLATES__DIR` → `{templates_dir}`, the
    same placeholder-not-literal shape the other two path overrides use.
  - `contract_version` SHALL become `2` (the data shape changed). `argv`, `placeholders`,
    `artifacts`, `exit_codes`, and `timeout` SHALL NOT change for any CLI.
- `cli-invocation-contract` SHALL ship `0.2.0`: `CONTRACT_VERSION = "0.2.0"` (equal to the new
  `v0.2.0` tag without its `v`), `DATA_VERSION = 2`, distribution version `0.2.0`.
- `CONTRACT.md` SHALL document the new key and the versioning rule it exercises: adding a
  **required** env key is a **minor** bump that still moves `DATA_VERSION`, because `load()` is
  version-strict and a 0.1.x loader must refuse a v2 document rather than silently omit the key.
- The testkit API SHALL stay exactly two assertions; its positive `itr` path SHALL carry the new
  key.

The runtime side (setting the key from the already-resolved `templates_dir`) and the three CLI
re-pins are **consumer** slices; this ticket records the contract and the release they consume.

Evidence: the runtime builds the `itr` child env with only two keys while it hashes
`templates_hash` for the entry hash — `sed -n '402,407p;233p;317p'
src/runtime/src/runtime/adapters/itr_adapter.py` (dotfiles-v3 `8df35a9`) →
`env = build_env({`, `"ICON_RENDERER__OUTPUT__OUTPUT_DIR": str(output_dir),`,
`"ICON_RENDERER__COLOR_SCHEME__PATH": str(colors_yaml_path),`; `templates_hash =
canonical_hash_dir(effective_templates)`; `ih = icons_entry_hash(palette_hash, templates_hash,
mappings_hash)`. No `ICON_RENDERER__TEMPLATES__DIR` literal is present in that file
(`grep -n TEMPLATES src/runtime/src/runtime/adapters/itr_adapter.py` → no `ICON_RENDERER__`
hit).

Evidence: `itr` binds that exact key to `templates.dir`, and env outranks settings/discovery —
`grep -n "ICON_RENDERER__TEMPLATES__DIR" -r src tests docs`
(icon-templates-renderer `2543c00`) → `src/icon_templates_renderer/cli/main.py:37` (help:
`Env overrides: … ICON_RENDERER__TEMPLATES__DIR …`), `src/icon_templates_renderer/cli/_helpers.py:70`,
`src/icon_templates_renderer/adapters/icon_renderer.py:292`, `:317`,
`tests/integration/test_template_dir_override.py:80`, `docs/ARCHITECTURE_PLAN.md:149`
(ADR-011). The binding is declared once at
`src/icon_templates_renderer/adapters/assembled_config_resolver.py:66` (`ResolutionPolicy(
env_prefix="ICON_RENDERER")`) and `:70` (`OverrideRule("templates.dir", {OverrideSource.CLI,
OverrideSource.ENV})`), consumed at `:95` (`TemplatesSettings(dir=result.config.templates.dir)`).

Evidence: the contract's current `itr` env record has exactly two keys —
`uv run python -c "import json;d=json.load(open('invocation-contract.json'));print(d['contract_version'], d['clis']['itr']['env'])"`.
Verify: `git show v0.1.0:invocation-contract.json | rg -n "ICON_RENDERER__"` → the two keys only.

## Acceptance

Contract side (verifiable in this worktree):

- [x] `invocation-contract.json` declares `contract_version: 2` and the `itr` record's
  `env.required`/`env.injected` carry `ICON_RENDERER__TEMPLATES__DIR` → `{templates_dir}`; the
  `csg`/`weg` records do not carry the key, and no record's `argv`/`artifacts` changed.
  Verify: `uv run pytest -q tests/test_record.py` → exit 0.
- [x] `CONTRACT_VERSION` is `"0.2.0"`, `DATA_VERSION` is `2`, and the distribution version is
  `0.2.0`; a v1 document is refused by `load()`.
  Verify: `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"`
  → `0.2.0 2`; `uv run pytest -q tests/test_loader.py` → exit 0.
- [x] `CONTRACT.md` documents the new key plus the versioning rule (required env key → minor
  bump, `DATA_VERSION` 2), `CHANGELOG.md` carries a `0.2.0` entry citing this ticket, and the
  README status names `v0.2.0`.
  Verify: `rg -n "ICON_RENDERER__TEMPLATES__DIR|DATA_VERSION.?2|REQ-008" CONTRACT.md CHANGELOG.md README.md`
  → hits in all three.
- [x] `uv run pytest -q`, `uv build`, `make test`, `make check-symmetry`, and
  `openspec validate --strict itr-templates-dir-contract` all exit 0.
  Verify: each command's exit code (recorded in the closeout table below).
- [x] Annotated tag `v0.2.0` exists on the remote with a GitHub Release carrying the wheel +
  sdist built from the tag, and the tag is anonymously reachable.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/RandomGenericUsername/contracts 'refs/tags/v0.2.0'`
  → one line, exit 0; `gh release view v0.2.0 --json assets --jq '.assets[].name'` → two names.

Consumer side (must land before this ticket can close):

- [ ] The runtime sets `ICON_RENDERER__TEMPLATES__DIR` from the resolved `templates_dir` and
  re-pins `contracts` to `v0.2.0`; its `ItrAdapter` test runs the kit with the new key.
- [ ] `csg`, `weg`, and `itr` re-pin `v0.2.0` and their kit runs stay green (the key is additive
  for CLI binaries; `itr` already honours it).

## Out of scope

- Editing the runtime or any CLI repo (separate repos, separate slices).
- Changing `argv` for `itr` (for example adding `--template-dir`); the decided fix is the env
  key, matching the two existing path overrides.
- Changing `artifacts`, `exit_codes`, or `timeout` for any CLI.
- Closing this ticket, archiving the OpenSpec change, or moving the INDEX line to Done.

## Status

**In progress — not closed.** The contract side and the `v0.2.0` release are done; the two
consumer-side acceptance boxes cannot be ticked until the runtime and the three CLIs re-pin
`v0.2.0` in their own repos. Closing now would leave a released contract with no consumer pinned
to it.

## Evidence

Commands run from the worktree root unless a path is named. Base `5e03075`; worktree
`.worktrees/req-008/`, branch `ticket/req-008-itr-templates-dir-contract`.

| Claim | Command | Result |
| --- | --- | --- |
| `itr` JSON diff is exactly the new key + version | `git diff 5e03075 c6c3ab5 -- invocation-contract.json` | `contract_version` `1`→`2`; `required` gains `"ICON_RENDERER__TEMPLATES__DIR"`; `injected` gains `"ICON_RENDERER__TEMPLATES__DIR": "{templates_dir}"`; nothing else, exit 0 |
| `csg`/`weg` env unchanged | `uv run python -c "from cli_invocation_contract import get; print(get('csg')['env'], get('weg')['env'])"` | the two pre-existing env mappings, exit 0 |
| Package version/constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.2.0 2`, exit 0 |
| Wheel carries the v2 data and the 0.2.0 metadata | `unzip -p dist/cli_invocation_contract-0.2.0-py3-none-any.whl cli_invocation_contract/invocation-contract.json \| python3 -c "import json,sys; d=json.load(sys.stdin); print(d['contract_version'], d['clis']['itr']['env']['injected']['ICON_RENDERER__TEMPLATES__DIR'])"` | `2 {templates_dir}`, exit 0; `…/METADATA` → `Version: 0.2.0` |
| Tests | `uv run pytest -q` | `55 passed in 0.18s`, exit 0 (was 49 at `5e03075`) |
| Event-contract tests + package tests | `make test` | `Ran 10 tests … OK` then `55 passed`, exit 0 |
| Symmetric drift gate | `make check-symmetry` | `[drift] symmetric: contract and generated/ agree`, exit 0 |
| OpenSpec change valid (strict) | `openspec validate --strict itr-templates-dir-contract` | `Change 'itr-templates-dir-contract' is valid`, exit 0 |
| OpenSpec tree valid | `openspec validate --all` | `Totals: 11 passed, 0 failed (11 items)`, exit 0 |
| Build | `uv build` | `Successfully built dist/cli_invocation_contract-0.2.0.tar.gz` + `…-py3-none-any.whl`, exit 0 |
| Tag is annotated and peels to the implementation commit | `git cat-file -t v0.2.0`; `git rev-parse v0.2.0^{}` | `tag`; `c6c3ab5d523d06210f8e87535c464d3190d005c0`; tag object `442fb9abdc73fa109115ba804911a10af9f4cad1` |
| Assets built from the tag, not the tree | `git worktree add /tmp/opencode/contracts-v020 v0.2.0 && (cd /tmp/opencode/contracts-v020 && uv build)` | `HEAD is now at c6c3ab5`; both `0.2.0` artifacts, exit 0 (worktree removed afterwards) |
| Release assets | `gh release view v0.2.0 --json tagName,assets --jq …` | `{"assets":["cli_invocation_contract-0.2.0-py3-none-any.whl","cli_invocation_contract-0.2.0.tar.gz"],"tag":"v0.2.0"}` |
| Birth-gate: anonymous tag reachability | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/RandomGenericUsername/contracts 'refs/tags/v0.2.0'` | one line `442fb9abdc73fa109115ba804911a10af9f4cad1 refs/tags/v0.2.0`, exit 0 |
| CI | `gh run list --limit 5 --json headSha,conclusion,workflowName` | `5338d1d` → `success` (run `39654249183`), `c6c3ab5` → `success` (run `39654081676`), `da27780` → `success` (run `39654069916`) |
| Main pushed and clean | `git rev-parse origin/main main`; `git status --porcelain` | local `main` equals `origin/main` after every push in this ticket (release commit `c6c3ab5` onward, including the docs tips); porcelain empty |

Commits (oldest first, on `main`):

| Commit | Subject |
| --- | --- |
| `c144071` | `plan(REQ-008): open the itr templates-dir contract ticket + OpenSpec change` |
| `c6c3ab5` | `feat(REQ-008): record ICON_RENDERER__TEMPLATES__DIR for itr (contract 0.2.0, data v2)` — the tagged commit |
| `da27780` | `plan(REQ-008): record task and acceptance evidence for the contract change` |
| `5338d1d` | `docs(REQ-008): record the v0.2.0 tag, release assets and CI evidence; ticket stays open` |

Remaining before close: the runtime slice sets `ICON_RENDERER__TEMPLATES__DIR` from its resolved
`templates_dir` and re-pins `v0.2.0`; `csg`, `weg`, and `itr` re-pin the same tag. Then archive
`itr-templates-dir-contract`, tick the two consumer boxes, and move this INDEX line to Done.
