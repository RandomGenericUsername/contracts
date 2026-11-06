# Skin-plane contract v1 (frozen)

> **Status: frozen v1.** The vocabulary below comes from executed GTK 4.24 probes and is the
> only skin surface the platform accepts. The machine-readable forms are
> [`schemas/skin-token.schema.json`](./schemas/skin-token.schema.json),
> [`schemas/skin-manifest.schema.json`](./schemas/skin-manifest.schema.json) and
> [`schemas/skin-json.schema.json`](./schemas/skin-json.schema.json). This repo owns the
> contract only; the runtime renderer, `skinValue()`, and the AGS apps live elsewhere.

A skin is **palette/ink mapping + paint + rhythm/density**. Structure is deliberately outside the
skin plane: a skin may not describe layout trees, variants, ordering, or presence. Appearance is a
function of the selected palette and the selected skin; structure belongs to the app.

## Manifest shape

```json
{
  "schemaVersion": 1,
  "name": "glass",
  "groups": {
    "shape":   { "radius-panel": 18, "radius-card": 14, "radius-cell": 10, "radius-pill": 999, "border-w": 1 },
    "rhythm":  { "gap": 10, "cell-pad": "6px 10px" },
    "surface": {
      "bg-panel": "linear-gradient(180deg, alpha(@surface, 0.72), alpha(@surface_container, 0.82))",
      "bg-card":  "alpha(@surface_container_high, 0.55)",
      "border":   "1px solid color-mix(in srgb, @outline 60%, transparent)",
      "shadow":   "0 8px 24px alpha(@shadow, 0.35)",
      "blur":     "blur(18px) saturate(1.2)"
    },
    "ink": {
      "ink": "@on_surface",
      "ink-dim": "alpha(@on_surface_variant, 0.8)",
      "accent": "@primary",
      "ink-over": "auto"
    },
    "type":   { "font-family": "Inter, sans-serif", "title-size": 15, "text-size": 12 },
    "layout": { "panel-width": 380, "bt-list-spacing": 8, "bar-row-height": 32, "chip-min": 72 }
  }
}
```

`schemaVersion` is `1`. `name` is a lowercase hyphenated skin name. `groups` has exactly the six
groups and every group has exactly the tokens below; `additionalProperties: false` applies at the
manifest, group and token levels.

## Token groups and value grammar

| Group | Token | Value |
| --- | --- | --- |
| shape | `radius-panel`, `radius-card`, `radius-cell`, `radius-pill` | non-negative **unitless number** (`12`), rendered as `12px` in CSS |
| shape | `border-w` | **unitless number** (`1.5`), rendered as `1.5px` in CSS |
| rhythm | `gap` | **unitless number** (`8`), rendered as `8px` in CSS |
| rhythm | `cell-pad` | string `"Npx Npx"` — the only literal length-pair token (e.g. `"8px 9px"`) |
| surface | `bg-panel`, `bg-card`, `border`, `shadow` | CSS paint composed only from palette role expressions (below) |
| surface | `blur` | `none` or `"blur(<n>px) [saturate(<n>)]"` |
| ink | `ink`, `ink-dim`, `accent` | a `palette.v1` role name, or a role expression |
| ink | `ink-over` | exactly `auto` (derived; see below) |
| type | `font-family` | string; the default skin may use `"inherit"` |
| type | `title-size`, `text-size` | **unitless number**, rendered as px in CSS |
| layout | `panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min` | **unitless number** consumed by `skinValue()`; may also appear in CSS placeholders, rendered with px |

### Surface paint grammar

A surface value is a CSS expression over palette role names only. The permitted color atoms are:

```text
transparent
@<role>
alpha(@<role>, <number 0..1>)
color-mix(in srgb, @<role> <pct>%, transparent|@<role>)
```

Gradients and shadows are strings composed from those atoms, for example
`linear-gradient(180deg, alpha(@surface, 0.72), alpha(@surface_container, 0.82))` or
`0 8px 24px alpha(@shadow, 0.35)`. There is **no literal hex anywhere** (`#...` is rejected), and
`@<role>` must name an existing palette role.

### Palette vocabulary

Roles are exactly the existing `palette.v1` vocabulary: the 50 Material roles emitted by the theme
producer plus the produced `on_backdrop` role (51 total). The enum is copied into both schemas from
`dotfiles-runtime` `src/runtime/domain/palette_vocabulary.py` (`PALETTE_VOCABULARY_V1`, 50
`MaterialRole` values + `on_backdrop`) and theme-producer's `MaterialRole`. A skin never invents a
role; a missing role is a vocabulary violation in the palette producer, not something a skin may
alias.

### `ink-over: auto`

`ink-over` is the ink painted over the wallpaper band. It is **derived**, never authored: the only
legal value is `auto`, which tells the runtime to use the palette's documented
`on_backdrop` role for the band. A skin cannot pin a fixed role there, because the correct ink
depends on the wallpaper and the palette.

## Value types and units (normative)

The contract separates the **stored value** from its **CSS rendering**. The twelve numeric
tokens are **unitless JSON numbers** in the authored manifest and in the resolved `skin.json`:

`radius-panel`, `radius-card`, `radius-cell`, `radius-pill`, `border-w`, `gap`, `title-size`,
`text-size`, `panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min`.

- Store `12`, `1.5`, `312` — **never** `"12px"`, `"1.5px"` or `"312px"`. A string in any of
  these positions is invalid against both canonical schemas and is rejected by the runtime
  parser (`numeric tokens must be finite`).
- When a numeric token placeholder is used in a **CSS length position**, the expander renders it
  as `<number>px`. The manifest and the resolved `skin.json` stay unitless: the expander MUST
  NOT store units in either document.
- `cell-pad` is the **only** token whose value is a literal CSS length-pair string, exactly
  `"Npx Npx"` (for example `"8px 9px"`). The expander passes it through unchanged.
- The paint (`bg-panel`, `bg-card`, `border`, `shadow`), `blur`, ink (`ink`, `ink-dim`,
  `accent`) and `font-family` tokens are CSS/role-expression strings, not numeric tokens.
- The layout tokens (`panel-width`, `bt-list-spacing`, `bar-row-height`, `chip-min`) are consumed
  by `skinValue()` as numbers **and** may appear in CSS placeholders, where they render with
  `px` exactly like the other numeric tokens.
- `font-family` for the default skin may be `"inherit"`.

The rendering rule, as a single example:

```text
manifest:  "radius-card": 12
           "panel-width": 312
template:  border-radius: <radius-card>; width: <panel-width>;
expanded:  border-radius: 12px; width: 312px;
```

### Consumers

Consumer repos MUST vendor this repo's canonical schemas
([`schemas/skin-token.schema.json`](./schemas/skin-token.schema.json),
[`schemas/skin-manifest.schema.json`](./schemas/skin-manifest.schema.json),
[`schemas/skin-json.schema.json`](./schemas/skin-json.schema.json)) and validate manifests and
the resolved `skin.json` against them. A local lookalike schema — for example a repo-local
`skins/schema.json` that accepts `"12px"` strings — is **not** this contract; validating
against it produces values the runtime parser rejects at app start.

## Template set and consumer artifacts (normative)

This section freezes how a selected skin becomes files on disk. The resolved-token document is
[`schemas/skin-json.schema.json`](./schemas/skin-json.schema.json); consumers validate a
runtime `skin.json` directly against it, without the manifest wrapper.

### Template set

- The template set lives with the skin data, in `dotfiles-assets/skins/templates/`, and is
  **independent of the selected manifest**: the same templates render every built-in skin.
- There is exactly **one template per target config directory**, named
  `<configDir>.gtk.css.j2`; the expander renders `<configDir>.css`. `configDir` is the
  consumer's config directory name (for the bar, `ags` — see the pointers below).
- A placeholder is `{{SKIN_<TOKEN>}}`. The token name is uppercased and every run of
  non-alphanumeric characters becomes `_` (leading/trailing `_` trimmed): `radius-panel` →
  `SKIN_RADIUS_PANEL`, `font-family` → `SKIN_FONT_FAMILY`.
- An unknown placeholder (a `SKIN_*` name that no token normalizes to), and any `{{SKIN_`
  left unresolved after substitution, is an **error**. Expansion fails closed; it never passes
  a placeholder through.

### Expansion inputs and outputs

- **Inputs.** The manifest is the selected skin: grouped tokens with the value types and units
  of v0.5.1. The templates are the shared set above. The manifest does not choose a template
  and does not carry a per-app map.
- **Outputs.** Exactly `current/skins/<configDir>.css` per target config directory, plus
  **one shared** `current/skin.json` for all consumers. There is no per-app `skin.json`.

### Pointers (consumer contract)

For every target config directory:

```text
{install}/config/<configDir>/skin.css   -> current/skins/<configDir>.css
{install}/config/<configDir>/skin.json  -> current/skin.json
```

For the bar today `configDir = ags` (dotfiles-v3 `apps.yaml`, bar `configDir: ags`); every
other app uses its own `configDir`. Apps resolve the CSS through
`$XDG_CONFIG_HOME/<configDir>/skin.css`, which is spine-linked to the pointer above.

### `skin.json` shape

The document is exactly:

```text
{"version": 1, "<group>": {"<token>": <unitless number|string>, ...}, ...}
```

- `version` is the integer `1`.
- The six groups are `shape`, `surface`, `ink`, `type`, `rhythm`, `layout`; all six are
  required, each group has exactly the tokens in the table above, and
  `additionalProperties: false` applies at the root and inside every group.
- Numeric tokens are raw JSON numbers (`12`, `1.5`, `312`), never strings. String tokens are
  emitted as-is (`"6px 10px"`, `"@on_surface"`, `"inherit"`).
- There are no extra keys, no flat token map, and no `structure`/`variant` group.

### Read order and refresh

- **Selection.** The runtime reads the selected skin from `desired.json` `skin`; the default is
  `glass`.
- **Cache key.** A compiled skin is cached under
  `sha256(templates_hash ‖ manifest_hash)` and is palette-independent.
- **Appearance hash.** The appearance hash includes the skin hash, so a skin change is an
  appearance change.
- **Refresh.** Live apps refresh through the existing `palette-refresh` request; the bar stays
  restart-only. No new refresh protocol is introduced.
- **Fail closed.** Missing or invalid artifacts (template, manifest, expanded CSS, or
  `skin.json`) abort expansion/publication or consumer load; no partial artifact is published
  and a consumer keeps its previous skin instead of painting an invalid one.

## Explicitly rejected constructs

The schemas reject these **by construction** (positive/negative fixtures in
`tests/test_skin_contract.py`):

- literal hex — any `#` in a value;
- `transition` — as a key and inside any value;
- structure/variant — keys named `structure`, `variant`, `order` or `presence`, and any
  `*variant*` token name (for example `bg-panel-variant`);
- unknown tokens — any key outside the frozen vocabulary;
- `blur(` as a value — only the `blur` token may contain `blur(...)`;
- `%` inside `calc()` — `calc(1px + 10%)` is invalid;
- unknown palette roles — every `@reference` must be a `palette.v1` role;
- unit-bearing numeric tokens — `"12px"` where a unitless number is required; `cell-pad` is the
  only `"Npx Npx"` string token;
- out-of-range `alpha()` and malformed `color-mix()` color atoms.

## Runtime facts

These are contract facts, not implementation in this repo.

- **Selection.** The selected skin lives in the runtime `desired.json` as
  `skin: "<name>"`. There is no per-app skin choice in v1.
- **Cache key.** Skins are palette-independent. A compiled skin is cached under
  `sha256(templates_hash ‖ manifest_hash)`; changing the palette does not change this key.
- **Appearance hash.** The appearance hash includes the skin hash. A skin change is therefore an
  appearance change and flows through the same comparison/ledger as a palette change.
- **Refresh lanes.** Skin refresh rides the existing palette-refresh/restart lanes. Live apps
  answer `palette-refresh`; the bar is a **restart** lane app (bar = restart). No new refresh
  protocol is introduced.
- **One provider.** Exactly **one** `Gtk.CssProvider` consumes the skin. It composes the runtime
  palette role block + the expanded skin CSS, is added at **USER priority (800)**, and is
  **re-installed LAST** so it wins over app/theme providers. Do not add a second provider for
  skins.
- **Monitors are module-scoped.** Any style/monitor object must be module-scoped, not local to a
  factory callback; a local reference is collected and the skin stops tracking (GC hazard).
- **Missing palette provider paints near-black.** A skin is not self-contained: without the
  runtime palette role block, role references resolve to nothing and the UI paints near-black.
  This is why the drift gates below assert a known ink instead of merely checking that the app
  loaded.
- **Drift-gate expectations.** A skin drift gate must assert a known ink (for example the resolved
  `on_surface`/`on_backdrop` color of a rendered probe) so a missing palette provider (near-black)
  or a stale skin fails the gate. Schema gates also assert the exact six groups, the 23-token
  vocabulary, the 51-role palette enum, and the forbidden constructs above.

## Built-in skins (v1)

- **`glass`** — the default skin, and the app fallback parity target. Translucent panels/cards,
  rounded corners, blur and a soft shadow.
- **`flat`** — zero radii, no blur, no shadow, solid role paint; minimal elevation.
- **`paper`** — the role-based ink/palette axis: clean rules and light-weight borders with ink
  taken from the palette roles. `paper` does **not** force a light look by itself; a light look
  depends on the selected palette (a light palette + `paper` reads as light, a dark palette +
  `paper` stays dark).

The runtime falls back to `glass` when no valid skin is selected, matching the app fallback.

## Verification

Evidence: the frozen vocabulary and runtime facts are recorded in
`tickets/REQ-011-skin-plane-contract/ticket.md`; the machine-readable constraints are
`schemas/skin-token.schema.json` and `schemas/skin-manifest.schema.json`; the palette enum source
is `dotfiles-runtime` `7f68574` `src/runtime/domain/palette_vocabulary.py:42-94`.

Verify:

```bash
uv run pytest -q tests/test_skin_contract.py
```

This validates both schemas as draft-07, accepts the `glass`/`flat`/`paper` fixtures, rejects every
named negative fixture, checks the token/group vocabulary and the exact 51-role palette enum, pins
the runtime-fact strings in this document, and enforces the value/unit convention: every numeric
token rejects `"12px"` and accepts `12`, `cell-pad` requires `"Npx Npx"`, and the expander example
above renders `12` → `12px`.
