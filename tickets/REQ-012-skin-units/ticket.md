---
id: REQ-012
title: "Freeze skin value types and units (numeric tokens are unitless numbers)"
kind: requirement
status: done
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-012/
branch: ticket/REQ-012-skin-units
---

# Freeze skin value types and units (numeric tokens are unitless numbers)

## Requirement

Close two integration bugs between the canonical skin contract and its consumers by freezing
the value/unit convention in the contract (patch release `v0.5.1`, no vocabulary change):

1. `schemas/skin-token.schema.json` declares twelve tokens as JSON numbers
   (`radius-panel`, `radius-card`, `radius-cell`, `radius-pill`, `border-w`, `gap`,
   `title-size`, `text-size`, `panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min`),
   but the assets repo wrote them as `"12px"` strings and validated against a local
   non-canonical schema. The two disagree.
2. `ags-platform/ports/skin.ts` `parseSkinJson` rejects those strings
   (`numeric tokens must be finite`), so a runtime `skin.json` built from such manifests fails
   at app start; `readSkinToken("panel-width", 312)` silently falls back on `"312px"`.

The fix is normative documentation plus schema descriptions/examples and tests — not a
vocabulary change and not a change to the numeric typing:

- `skins.md` gains a normative **"Value types and units"** section:
  - the twelve numeric tokens are **unitless JSON numbers** in manifests and in the resolved
    `skin.json` (`12`, `1.5`, `312` — never `"12px"`);
  - CSS expansion renders a numeric token in a CSS length position as `<number>px`
    (`border-radius: 12px`); the expander MUST NOT put units back into the manifest or
    `skin.json`;
  - `cell-pad` is the ONLY module whose value is a literal CSS length-pair string
    (`"8px 9px"`); paint/shadow/blur/ink/accent/font-family are CSS/role-expression strings;
  - `panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min` are consumed by `skinValue()`
    as numbers AND may appear in CSS placeholders (rendered with px);
  - the default skin's `font-family` may be `"inherit"`.
- `schemas/skin-token.schema.json` and `schemas/skin-manifest.schema.json` descriptions/examples
  state the convention; no token is added, renamed or removed (23 tokens stay).
- Tests assert that numeric tokens reject `"12px"` and accept `12`, `cell-pad` requires
  `"Npx Npx"`, and the documented expander example renders `12` → `12px`.
- `skins.md` notes that consumer repos MUST vendor/validate against this canonical schema, not a
  local lookalike.

## Acceptance

- [x] `skins.md` has a normative "Value types and units" section covering all twelve numeric
  tokens as unitless numbers, the expander's `<number>px` rendering rule, `cell-pad` as the only
  length-pair string token, the layout-token dual use, and `font-family: "inherit"`.
- [x] Both skin schemas carry descriptions/examples for the convention with the 23-token
  vocabulary and the six groups unchanged.
- [x] `tests/test_skin_contract.py` rejects `"12px"` (token and manifest), accepts `12`, rejects
  `"8px"`/`"8 9"`/`"8px 9px 10px"` for `cell-pad`, and proves the documented expander example
  renders `12` → `12px`.
- [x] `skins.md` states the consumer vendoring/validation rule (canonical schema, not a local
  lookalike).
- [x] `make test`, `make skin-test` and `make schema-test` exit 0.
- [x] `CHANGELOG.md`, `tickets/INDEX.md`, the package version and `CONTRACT_VERSION` agree on
  `0.5.1`; annotated tag `v0.5.1` points at the merged release commit and no existing tag moved.

## Evidence

- Mismatch: `dotfiles-assets/skins/manifests/glass.toml:12-16,19-20,32-33,36-39` writes the
  numeric tokens as `"12px"`, `"1.5px"`, `"8px"`, `"12.5px"`, `"312px"`, while
  `schemas/skin-token.schema.json` types them `number` (`#/definitions/number`).
- Local non-canonical schema: `dotfiles-assets/skins/schema.json` has `$id: "skins/schema.json"`
  and `$defs/dimension` requiring `"Npx"` strings; it is not this repo's schema.
- Runtime reject: `ags-platform/ports/skin.ts:194-201` throws
  `numeric tokens must be finite and non-negative` for non-number values; `skin.ts:410-430`
  `readSkinToken` only coerces a bare numeric string, so `"312px"` falls back.
- Contract source of truth: `skins.md` (token table), `schemas/skin-token.schema.json`,
  `schemas/skin-manifest.schema.json`, `tests/test_skin_contract.py`.

## Verification

Commands run from the worktree root (`.worktrees/REQ-012/`, branch
`ticket/REQ-012-skin-units`, base `0625b56`).

| Claim | Command | Result |
| --- | --- | --- |
| Numeric tokens reject `"12px"`/accept `12`; `cell-pad` is `"Npx Npx"`; expander `12` → `12px` | `make skin-test` | `70 passed in 0.25s`, exit 0 |
| Full repo gate (event tests + all pytest suites) | `make test` | `Ran 10 tests ... OK`; `179 passed in 0.33s`, exit 0 |
| AGS app schema gate unchanged | `make schema-test` | `40 passed in 0.06s`, exit 0 |
| No generated drift | `make contracts-drift` | regenerate-and-diff clean, exit 0 |
| Package build + version constants | `make build`; `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | wheel + sdist `0.5.1`; `0.5.1 2` |
| Wheel metadata | `unzip -p dist/cli_invocation_contract-0.5.1-py3-none-any.whl cli_invocation_contract-0.5.1.dist-info/METADATA \| grep -m1 '^Version:'` | `Version: 0.5.1` |

### Commits

| Commit | Subject |
| --- | --- |
| `c8ceff4` | `docs(tickets): plan the skin value/unit freeze (REQ-012)` |
| `84bfa7d` | `chore(REQ-012): start — record worktree/branch, move to in-progress` |
| `bc54358` | `fix(REQ-012): freeze skin value types and units in the contract` |
| release commit (the `v0.5.1` tag target) | `chore(REQ-012): release v0.5.1` |

### Status

**Done on `ticket/REQ-012-skin-units`.** The convention is frozen in `skins.md`, both canonical
schemas and the skin tests. No token was added, renamed or removed (23 tokens, six groups). No
runtime, assets or app code was changed in this repo. Merge to `main` fast-forward, then create
the annotated `v0.5.1` tag on the merged release commit.

## Non-goals

- No token vocabulary change, no new groups, no new palette roles.
- No runtime, assets, app or host code in this repo — the assets manifests and the TypeScript
  port are fixed in their own repos against this contract.
- No change to `invocation-contract.json` or `DATA_VERSION` (`2`).
