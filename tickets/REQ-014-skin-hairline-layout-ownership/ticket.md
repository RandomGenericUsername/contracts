---
id: REQ-014
title: "Split the panel border from the hairlines and make layout metrics TSX-owned"
kind: requirement
status: done
lane: 2
links:
  openspec: none
  bmad: none
worktree: .worktrees/REQ-014/
branch: ticket/REQ-014-skin-hairline-layout-ownership
---

# Split the panel border from the hairlines and make layout metrics TSX-owned

## Requirement

Rendering the real assets against real GTK exposed two contract defects after `v0.5.2`:

1. **One `border-w` cannot reproduce today's stylesheet.** The panel/frame border is `1.5px`,
   while the card tile, row action and badge hairlines are `1px`, and the row/cell itself has
   no border (`none`). Forcing the row to carry a transparent border to consume `border-w`
   changed its measured height (`54px` vs `50px`).
2. **Layout tokens have dual ownership.** The template expands `panel-width` into `min-width`,
   `bt-list-spacing` into `margin`, `bar-row-height` into `min-height` and `chip-min` into
   `min-width`, while the widgets already own the same metrics through `skinValue()`. A size
   declared in both places breaks when either side changes.

Close both defects in the skin contract (minor release `v0.6.0`: one new token, no change to the
other 23):

1. Add exactly one numeric token to the `shape` group: `hairline-w`. It follows the `v0.5.1`
   unit rule — a unitless JSON number in the manifest and in `skin.json`, rendered as `<n>px`
   when a template places it in a CSS length position. The vocabulary becomes **24 tokens**;
   `skin-token.schema.json`, `skin-manifest.schema.json` and `skin-json.schema.json` all type it
   identically and require it.
2. Amend `skins.md`:
   - add `hairline-w` to the numeric-token list (thirteen numeric tokens) and to the shape table:
     `border-w` is the outer panel/frame border; `hairline-w` is the card tile, row action and
     badge hairlines; the row/cell itself has no border (the template uses `none`);
   - strengthen the layout rule: `panel-width`, `bt-list-spacing`, `bar-row-height` and
     `chip-min` are consumed ONLY by widgets through `skinValue()`; templates MUST NOT expand
     layout tokens into CSS (no `min-width`, `margin` or `min-height` from layout tokens) to
     avoid dual ownership. They may still appear in `skin.json` for consumers;
   - record the rendering consequence that motivated `hairline-w`: the source `.settings-net`
     row has `border: none`, so the row height must not change (the transparent-border attempt
     rendered `54px` instead of `50px`).
3. Document the built-in skin values: `glass` `border-w 1.5` / `hairline-w 1`; `flat`
   `border-w 0` / `hairline-w 0`; `paper` `border-w 1` / `hairline-w 1`. Update the canonical
   fixtures to those values.
4. Tests: `hairline-w` rejects a numeric string and accepts a number in the token, manifest and
   `skin.json` documents; `skin.json` validation includes the token; doc pins cover the shape
   ownership split, the layout-only-through-`skinValue()` rule and the built-in values.
5. Release plumbing: `pyproject.toml`, `CONTRACT_VERSION`, `uv.lock`, `conftest`/version pins,
   the INDEX and the changelog agree on `0.6.0`; annotated tag `v0.6.0` on the merged release
   commit.

## Acceptance

- [x] `hairline-w` is a required numeric `shape` token in all three frozen schemas, typed
  identically to `border-w` (`#/definitions/number`), taking the vocabulary to 24 tokens.
- [x] `skins.md` names `border-w` as the outer panel/frame border and `hairline-w` as the card
  tile, row action and badge hairlines; it states the row/cell has no border and records the
  `54px` vs `50px` row-height consequence.
- [x] `skins.md` states the layout tokens are consumed only by widgets through `skinValue()` and
  that templates MUST NOT expand them into CSS (`min-width`/`margin`/`min-height`), while they
  may still appear in `skin.json`; the old "may appear in CSS placeholders" allowance is gone.
- [x] `skins.md` documents `glass` `border-w 1.5` / `hairline-w 1`, `flat` `border-w 0` /
  `hairline-w 0`, `paper` `border-w 1` / `hairline-w 1`; the three valid fixtures carry those
  values.
- [x] `tests/test_skin_contract.py` covers `hairline-w` numeric-string rejection in the token,
  manifest and `skin.json` documents, includes it in the `skin.json`/manifest cross-check, and
  pins the new doc statements.
- [x] `make test`, `make skin-test` and `make schema-test` exit 0.
- [x] `CHANGELOG.md`, `README.md`, `CONTRACT.md`, `tickets/INDEX.md`, `pyproject.toml`,
  `src/cli_invocation_contract/__init__.py`, `uv.lock` and the version test agree on `0.6.0`;
  annotated tag `v0.6.0` points at the merged release commit and no existing tag moved.

## Evidence

- One-token deviation, panel vs hairlines:
  `dotfiles-assets/skins/tests/fixtures/parity/deviations.json:2,9-12,16-19,23-26` records that
  the single frozen `border-w` makes `.settings-card`, `.settings-rowact` and `.settings-badge`
  render `1.5px` instead of the source `1px`; the glass manifest comment
  `dotfiles-assets/skins/manifests/glass.toml:1-6` names the same limitation.
- Panel is `1.5px` and cell/control hairlines are `1px` in the source:
  `ags-apps/bar/style.css:283` (`border: 1.5px solid` on the panel),
  `:303`, `:316`, `:385` (card/footer `1px` shadows), `:428`/`:442` (badge/row-action `1px`).
- The row has no border and row height must not change:
  `ags-apps/bar/style.css:498-508` `.settings-net` includes `border: none`; the template comment
  `dotfiles-assets/skins/templates/ags.gtk.css.j2:16-24` explains that the transparent-border
  workaround changed geometry.
- Dual ownership: `dotfiles-assets/skins/templates/ags.gtk.css.j2:63` expands
  `{{SKIN_PANEL_WIDTH}}` into `min-width`, `:150` expands `{{SKIN_BAR_ROW_HEIGHT}}` into
  `min-height`, `:152` expands `{{SKIN_BT_LIST_SPACING}}` into `margin-bottom`, and `:212`
  expands `{{SKIN_CHIP_MIN}}` into `min-width`; the template itself says the widgets own those
  values (`:21-24`).
- Built-in values already in the asset manifests:
  `dotfiles-assets/skins/manifests/glass.toml:16` (`border-w = 1.5`),
  `flat.toml:11` (`border-w = 0`), `paper.toml:13` (`border-w = 1`).
- Contract source of truth today: `skins.md`, `schemas/skin-token.schema.json`,
  `schemas/skin-manifest.schema.json`, `schemas/skin-json.schema.json`,
  `tests/test_skin_contract.py`.

## Verification

Commands run from the worktree root (`.worktrees/REQ-014/`, branch
`ticket/REQ-014-skin-hairline-layout-ownership`, base `efb8348`).

| Claim | Command | Result |
| --- | --- | --- |
| `hairline-w` schema/doc/fixture gates | `make skin-test` | `110 passed in 0.47s`, exit 0 |
| Full repo gate (event tests + all pytest suites) | `make test` | `Ran 10 tests in 0.049s ... OK`; `219 passed in 0.61s`, exit 0 |
| AGS app schema gate unchanged | `make schema-test` | `40 passed in 0.08s`, exit 0 |
| No generated drift | `make contracts-drift` | symmetric contract/generated agree; regenerate-and-diff clean, exit 0 |
| Package version constants | `uv run python -c "from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION; print(CONTRACT_VERSION, DATA_VERSION)"` | `0.6.0 2` |

### Commits

| Commit | Subject |
| --- | --- |
| `efb8348` | `docs(tickets): plan the hairline/layout-ownership correction (REQ-014)` |
| `ef6e981` | `chore(REQ-014): start — record worktree/branch, move to in-progress` |
| `fe8c7aa` | `feat(REQ-014): split panel border from hairlines and make layout TSX-owned` |
| release commit (the `v0.6.0` tag target) | `chore(REQ-014): release v0.6.0` |

### Status

**Done on `ticket/REQ-014-skin-hairline-layout-ownership`.** The contract now has 24 tokens:
`border-w` owns the outer panel/frame border and the new `shape.hairline-w` owns the card tile,
row action and badge hairlines, with the row/cell borderless. The layout tokens are consumed only
by widgets through `skinValue()`; templates must not expand them. No runtime, assets or app code
was changed in this repo. Merge to `main` fast-forward, then create the annotated `v0.6.0` tag on
the merged release commit.

## Non-goals

- No change to any of the other 23 tokens, the six groups or the 51-role palette enum.
- No change to the template set, pointers, `skin.json` wrapper or `DATA_VERSION` (`2`).
- No runtime, assets, platform or app code in this repo; those repos adopt `hairline-w` and drop
  the template layout expansions against this tag.
