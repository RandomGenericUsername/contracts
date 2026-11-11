# Appearance plane v2 (frozen)

> **Status: frozen v2.** The appearance plane is the **one** contract for palette, skin and
> mode. It supersedes the v1 skin-plane artifacts (`skin.css`, `skin.json`, `current/skins/`);
> there is **no v1.1 hotfix** and no compatibility shim that keeps the v1 second-hop watch alive.
> The machine-readable forms are
> [`schemas/appearance-manifest.schema.json`](./schemas/appearance-manifest.schema.json),
> [`schemas/appearance-json.schema.json`](./schemas/appearance-json.schema.json) and
> [`schemas/appearance-artifact.schema.json`](./schemas/appearance-artifact.schema.json).
> This repo owns the contract only; the runtime renderer, `skinValue()`, and the AGS apps live
> elsewhere.
>
> **v3 note.** The token vocabulary, mode resolution and composed-sheet rules
> below are unchanged. The v3 generation layout, single commit pointer,
> convergence pipeline and generation-bound refresh are frozen in
> [`generations.md`](./generations.md) and
> [`appearance-refresh.md`](./appearance-refresh.md); the v2
> `current/appearance` pointer family and `palette-refresh` ack are superseded
> for v3 consumers.
>
> **v0.9.0 host note.** The optional root `[host]` policy delegates only an
> explicit allowlist of logical token paths to the live compositor. It is not a
> token group and does not change any token type; the resolved `tokens.json`
> stays concrete. The host snapshot participates in `appearance.v3` identity
> and the generation manifest host block.
>
> **v0.10.0 artifact note.** The manifest's `appearance.targets` remains the
> frozen CSS family. An optional, separate `appearance.artifacts` family adds
> `{consumer, path, format}` entries for non-CSS consumers; this document's
> token vocabulary, composed-CSS rules and skins are unchanged.
>
> **v0.11.0 host-radius note.** The `[host]` allowlist now delegates the outer
> panel plus the inner `surface.card`, `surface.control` and `surface.cell`
> rectangle radii. `surface.pill.radius` stays explicit because a pill is a
> capsule; `surface.panel.border-width` remains the only delegable border
> width. Precedence and the resolved concrete token model are unchanged.

An appearance is **palette + skin + mode**, composed once and consumed through **one atomically
repointed hop**. Structure is outside the appearance plane: an appearance may not describe layout
trees, variants, ordering or presence.

## Why v2 (investigation context)

The live end-to-end investigation found four independent defects in v1. They are the reason v2 is
a new major rather than a patch.

1. **The watched hop and the repointed hop were different.** The v1 consumer chain is
   `config/<app>/skin.css -> current/skins/<app>.css -> cache/skins/<hash>/<app>.css`. The AGS
   adapters watch the stable first hop (`config/<app>/skin.css`), while the runtime repoints the
   second hop (`current/skins/<app>.css`). A live skin change therefore never reaches a running
   app. Palette changes do reach apps because the palette adapter watches `current/colors.yaml`,
   which is the hop the runtime actually replaces.
   Evidence: `ags-platform/adapters/skin.ts` (`watchSkin`, `SKIN_CSS_POINTER`) and
   `ags-platform/ports/skin.ts` watch `skinCssPath` / `skinJsonPath`; the runtime repoints
   `current/skins/<app>.css` in `dotfiles-runtime/src/runtime/adapters/seeder.py`
   (`repoint_current_symlinks`, `repoint_consumer_symlinks`). The palette comparison is
   `ags-platform/adapters/theme.ts` (`PALETTE_YAML = .../current/colors.yaml`).
2. **Refresh handlers only re-applied the palette.** Every app's `palette-refresh` handler calls
   `theme.apply()` and no skin apply.
   Evidence: `ags-apps/notifications/app.tsx:73-74`, `ags-apps/icme/app.tsx:32-38`,
   `ags-apps/wallpaper-selector/app.tsx:35-41`, `ags-apps/capture-tool/app.tsx:52-58`,
   `ags-apps/btop-theme-studio/app.tsx:31-40`, `ags-apps/hypr-pano/app.tsx:16-17`,
   `ags-apps/bar/app.tsx:141`.
3. **AGS apps were raw processes.** There was no systemd user unit owning the process group. A
   killed `ags run` parent could leave the gjs child owning the D-Bus name; the live investigation
   observed `org.freedesktop.Notifications` kept by the old child until
   `ags quit -i notifications`.
4. **v1 could not express the real stylesheets.** The global `border-w`/`hairline-w` pair cannot
   express per-role borders; hover/selected/disabled paints and small type/paddings lived as
   template literals; clipboard contrast was re-derived with color math; layout tokens were
   bar-only; and `paper` depended on guessing the palette mode instead of declaring explicit
   mode overrides.

## Generation

The runtime generates one immutable cache entry per appearance. The generation path is
`cache/appearance/<hash>/`, where `<hash>` is the `appearanceHash`:

```text
$XDG_STATE_HOME/dotfiles/cache/appearance/<appearanceHash>/
  colors.yaml          # palette.v1 roles selected for this appearance
  tokens.json          # resolved, mode-resolved v2 token document
  appearance.json      # version: 2 metadata (skin, mode, hashes, token ref)
  <configDir>.css      # one composed CSS file per target config dir
```

### `colors.yaml`

`colors.yaml` is the selected palette entry copied into the appearance generation. It carries the
existing `palette.v1` role vocabulary (50 Material roles plus `on_backdrop`); the appearance plane
does not invent, rename or alias roles.

### `tokens.json`

`tokens.json` is the **resolved** v2 token document and validates directly against
[`schemas/appearance-json.schema.json`](./schemas/appearance-json.schema.json):

```text
{"version": 2, "surface": {...}, "state": {...}, "type": {...}, "ink": {...}, "layout": {...}}
```

Mode overrides are already applied. The document has no `mode`, `skin` or palette fields; those
belong to `appearance.json`.

### `appearance.json`

`appearance.json` is metadata only and validates against
[`schemas/appearance-artifact.schema.json`](./schemas/appearance-artifact.schema.json):

| Field | Meaning |
| --- | --- |
| `version` | Exactly `2`. |
| `skin` | Selected skin name (`glass`, `flat`, `paper`, or another valid name). |
| `mode` | Selected palette mode, `dark` or `light`. |
| `paletteHash` | Content hash of the palette entry. |
| `skinHash` | Content hash of the skin entry. |
| `appearanceHash` | `sha256("appearance.v3" ‖ paletteHash ‖ skinHash ‖ mode ‖ hostHash)`; also the cache directory name. `hostHash` is `-` when no delegated value participated. |
| `generationHash` | Content hash of the generated `colors.yaml`, `tokens.json` and every composed `<configDir>.css`, excluding `appearance.json`. |
| `tokenRef` | Exactly `tokens.json`, the relative token document in this generation. |

The canonical appearance hash is:

```text
hostHash = sha256(canonical-json({
  "version": 1,
  "values": { <only the logical token paths that used the host> }
}))
# hostHash is "-" when no delegated value participated.

appearanceHash = sha256("appearance.v3\n" + paletteHash + "\n" + skinHash + "\n" + mode + "\n" + hostHash)
```

`hostHash` includes only the participating token paths and their resolved values. It excludes the
Hyprland instance signature, timestamps and the option `set` flag. A host change that does not
alter a participating value must not create a new generation. Host mapping version `1` is
`hyprland.paint.v1`; a mapping change bumps the version and therefore the hash. No-host
generations use the `-` placeholder, so the v3 formula is used for every new generation and
existing v2 generations remain valid without migration (one-time identity churn is expected).

The palette cache and the skin cache stay independent. An appearance generation is their
composition with a mode; it never mutates either cache entry. A palette-only change produces a new
`paletteHash`, a skin-only change produces a new `skinHash`, and both produce a new
`appearanceHash`.

### Composed CSS

Each target config directory gets one composed `<configDir>.css` containing, in order:

1. the palette `@define-color` block derived from `colors.yaml` (`@define-color <role> <hex>;` for
   every `palette.v1` role), and
2. the skin CSS expanded from the v2 templates.

The two are one sheet on purpose: a skin is not self-contained, and without the palette block role
references resolve to nothing and the UI paints near-black.

The target set is derived from the selected skin's `<configDir>` artifacts, never from a fixed app
list. A missing target is skipped at generation; it is not a partial appearance.

## Non-CSS appearance artifacts (v0.10.0)

The appearance contract has two target families. The families are separate on
purpose: widening the CSS family would break every AGS consumer.

- **CSS family — `appearance.targets` (frozen).** Each entry is
  `{configDir, path}` with `path` exactly `appearance/<configDir>.css`. AGS,
  wlogout, GTK3 and GTK4 use this family. GTK3/GTK4 are ordinary CSS consumers
  with the aliases `gtk3`/`gtk4`; provisioning maps them to the real
  `gtk-3.0`/`gtk-4.0` config dirs. This family is byte-identical to `v0.9.0`.
- **Non-CSS family — `appearance.artifacts` (optional).** Each entry is
  `{consumer, path, format}`. `consumer` uses the same safe lowercase segment
  as `configDir`, `format` is `rasi|conf|theme`, and `path` is exactly
  `appearance/<consumer>.<format>`. The runtime and verify enforce the
  path/consumer/format equality because JSON Schema draft-07 cannot compare
  properties; consumers that require strict schemas must re-pin this release.

The format extension must match the format and consumer in the same entry.
An unknown format, a CSS extension in `artifacts`, a non-CSS extension in
`targets`, a dot in `consumer`, or a duplicate consumer/path fails closed.
There is **no fake CSS** for non-CSS formats: a `.rasi`, `.conf` or `.theme`
consumer never receives a `.css` sheet. `rasi` ships first for rofi; `conf` and
`theme` are reserved even though no template ships yet. kitty (`.conf`) and
btop (`.theme`) stay palette-only in this phase because a skin may not emit
literal hex and the type/unit rules are unresolved.

**AGS compatibility.** AGS consumers ignore unknown keys on `appearance`: the
platform parser reads only `appearance.tokensPath`, `appearance.targets` and
`mode`, and returns a fresh object. Adding `appearance.artifacts` therefore
does not break an old AGS pin. The v0.9.0 strict JSON-Schema validators reject
the new key, so every in-tree validator must re-pin before an artifact-emitting
runtime ships. Evidence: `ags-platform/ports/appearance.ts:889-983`
(`parseGenerationManifest` reads the known keys and ignores the rest).

## One pointer, one hop

There is exactly **one** atomically repointed hop for an appearance:

```text
$XDG_STATE_HOME/dotfiles/current/appearance  ->  cache/appearance/<appearanceHash>/
```

Consumers get one stable convenience link per target config directory:

```text
{install}/config/<configDir>/appearance.css  ->  current/appearance/<configDir>.css
```

`current/appearance` is the only symlink the runtime replaces for an appearance change. The
consumer link is stable: its target text still names `current/appearance`, so it does not need to
be rewritten when the generation changes. The runtime writes the full generation, then repoints
the single hop atomically (write a temporary symlink and `rename`/`os.replace` it over
`current/appearance`). No file inside a published generation is ever rewritten.

### Consumers MUST watch `current/appearance`

A consumer MUST create **one** file monitor on the state pointer
`$XDG_STATE_HOME/dotfiles/current/appearance` and MUST read the config path
`$XDG_CONFIG_HOME/<configDir>/appearance.css` (or the equivalent install-spine path) after the
event. It MUST NOT watch `config/<configDir>/appearance.css` as the change signal.

**inotify rationale.** The v1 failure was caused by watching the wrong hop. A `Gio.FileMonitor`
created on the consumer link watches that link's own inode; when the runtime repoints a *lower*
symlink (`current/skins/<app>.css` in v1, or the directory link `current/appearance` in v2), the
consumer link's inode and target text do not change, so the monitor does not fire. The palette path
worked because `current/colors.yaml` itself was the replaced hop. v2 makes the appearance pointer
that same kind of hop: `current/appearance` is replaced, so a monitor on it receives the rename
event. The 50 ms debounce collapses the burst of events one atomic repoint emits. Reading the
config path (not a resolved generation path) after the event avoids a stale open handle.

## Token model v2

The nested vocabulary is closed. `additionalProperties: false` applies at every object level and
the token names below are the only legal names.

### `surface`

Five roles, each with its own paint and geometry. `border` is a colour expression and
`border-width` is the numeric width, so a role never has to share a global border token.

| Role | Tokens |
| --- | --- |
| `surface.panel` | `bg`, `border`, `border-width`, `radius`, `padding`, `shadow`, `blur` |
| `surface.card` | `bg`, `border`, `border-width`, `radius`, `padding` |
| `surface.cell` | `bg`, `border`, `border-width`, `radius`, `padding`, `hover-bg` |
| `surface.control` | `bg`, `border`, `border-width`, `radius`, `padding`, `font-size`, `font-weight` |
| `surface.pill` | `bg`, `border`, `border-width`, `radius`, `padding`, `font-size`, `letter-spacing` |

`surface.cell` is the row/tile surface. It may be borderless (`border: transparent`,
`border-width: 0`) and it owns its own `hover-bg`, so a hover paint is a token rather than a
template literal. `surface.control` owns the button/row-action type, and `surface.pill` owns the
badge/capsule type and tracking.

### `state`

Exactly four states. Their semantics are normative:

| State | `fill` | `ink` | `ring` |
| --- | --- | --- | --- |
| `hover` | the transient pointer background | the foreground that remains readable on `fill` | the hover outline/accent |
| `selected` | the selected surface fill | the foreground paired with `fill` | the selected outline/accent |
| `focus` | the focus background (often `transparent`) | the foreground while focused | the focus ring colour |
| `disabled` | the disabled background (often `transparent`) | the dimmed foreground | the disabled outline (often `transparent`) |

`fill`, `ink` and `ring` are palette role expressions, not literal colours. Selection is a role
pair (`selected.fill` + `selected.ink`), so apps do not re-derive contrast: the palette producer is
responsible for a readable container/on-container pair.

### `type`

`font-family`, `font-weight`, `letter-spacing`, `size-caption`, `size-meta`, `size-body`,
`size-title`, `size-display`.

The four named sizes replace ad-hoc small-font literals. `font-weight` is a unitless CSS weight;
`letter-spacing` is a unitless ratio rendered as `em`.

### `ink`

`ink`, `ink-dim`, `accent`, `accent-muted`, `ink-over`.

`ink-over` is derived and is exactly `auto`, meaning the palette's `on_backdrop` role for the
wallpaper band. `accent-muted` is the washed accent used for secondary emphasis; it removes the
per-app `alpha()` and color-mix literals.

### `layout.<app>`

Layout metrics are namespaced by app: `layout.bar.panel-width`, `layout.notifications.card-width`,
and so on. Every value is a **unitless number**. The app's TSX owns these values through
`skinValue()`; a template MUST NOT expand a layout token into CSS (`min-width`, `margin`,
`min-height`). This removes the v1 bar-only layout group and its dual ownership.

### `mode.dark` / `mode.light`

`mode.dark` and `mode.light` are optional overrides at the manifest root. Each override is a set of
complete, same-shape groups (`surface`, `state`, `type`, `ink`, `layout`); a provided group
**replaces** the base group as a whole. Omitted groups inherit the base. There is no deep merge,
because a partial nested merge is ambiguous and hard to validate.

Generation selects exactly one mode from the palette mode and applies that override before writing
`tokens.json` and before expanding templates. An appearance with no mode override uses the base
groups for both modes. An override that is present but incomplete is invalid.

### `host`

The optional root `[host]` policy is an explicit delegation allowlist. It is **not** a token
group and it does not make any token type dynamic: the authored manifest and the resolved
`tokens.json` keep concrete numbers and strings.

```toml
[host]
inherit = [
  "surface.panel.radius",
  "surface.panel.border-width",
  "surface.card.radius",
  "surface.control.radius",
  "surface.cell.radius",
]
fallback = "skin"          # "skin" (default) or "error"
```

Phase 1 supports exactly five logical paths: the **outer panel** and the **inner
card/control/cell rectangle radii**.

| Token path | Host source | Meaning |
| --- | --- | --- |
| `surface.panel.radius` | Hyprland `decoration:rounding` | outer panel/window corner |
| `surface.panel.border-width` | Hyprland `general:border_size` | outer panel/window frame width |
| `surface.card.radius` | Hyprland `decoration:rounding` | inner card rectangle corner |
| `surface.control.radius` | Hyprland `decoration:rounding` | inner control rectangle corner |
| `surface.cell.radius` | Hyprland `decoration:rounding` | inner cell rectangle corner |

`inherit` must be non-empty and unique. A token not named in `inherit` is always the skin's
explicit value. `surface.pill.radius` is **intentionally not delegable**: the pill is a capsule,
not a rectangle, and its capsule identity must not be flattened by the host rounding value. No
card/control/cell border width, padding, gap, type, paint, colour or `layout.<app>` path may be
inherited, and a host value is never a literal hex or structure. Host rounding maps only to the
listed rectangle radii; there is no border-width expansion beyond
`surface.panel.border-width`.

Resolution precedence, highest first: **mode override > host > skin fallback**.

1. a value supplied by the selected `mode.<mode>` group (the complete group is explicit; there is
   no deep merge);
2. the live host value for a token named in `inherit`;
3. the skin's selected concrete value (the headless/invalid-host fallback).

If the host is unavailable or a value is invalid, `fallback = "skin"` uses the skin value. With
`fallback = "error"` the generation fails closed before publishing; the previous generation
remains current. Host values are finite non-negative numbers in the supported ranges (radius
`0..64`, border `0..16`); booleans, strings, vectors, negatives, NaN/infinity and unknown options
are invalid. Reading effective values is a runtime concern; the contract only freezes the policy,
the allowlist, the precedence and the identity rule.

## Value types and units (normative)

The contract separates the **stored value** from its CSS rendering.

- **Lengths are unitless JSON numbers** in the manifest, in `tokens.json` and in any fixture:
  `border-width`, `radius`, `padding`, `font-size`, the four `type.size-*` values and every
  `layout.<app>` value. Store `18`, `1.5`, `380` — never `"18px"`, `"1.5px"` or `"380px"`.
  In a CSS length position the expander renders the number as `<number>px`.
- **`font-weight`** is a unitless number (`400`, `600`) and is rendered without a unit.
- **`letter-spacing`** is a unitless ratio (`0.05`) rendered as `<number>em` (`0.05em`). The unit is
  never stored; this is why the real stylesheet's `0.05em` becomes the number `0.05`.
- **Paints** (`surface.*.bg`, `surface.*.border`, `surface.cell.hover-bg`, `surface.panel.shadow`,
  `state.*.fill`, `state.*.ink`, `state.*.ring`, `ink.*`) are palette role expressions or CSS
  paint strings composed only from palette roles. The permitted atoms are `transparent`, `@<role>`,
  `alpha(@<role>, <0..1>)`, `color-mix(in srgb, @<role> <pct>%, transparent|@<role>)`, and
  gradients/shadows composed from them.
- **`surface.panel.blur`** is `none` or `blur(<n>px) [saturate(<n>)]`.
- **There is no literal hex anywhere** (`#...` is rejected). The palette owns colours.
- **There are no transitions** (a `transition` key or value is rejected). Motion is outside the
  appearance plane and would race a live CSS swap.
- **There is no `structure` or `variant`** (no keys named `structure`, `variant`, `order` or
  `presence`, and no `*variant*` token). Structure belongs to the app.

## Mode resolution and template expansion

Generation order is fixed:

1. read the selected skin manifest, the palette mode and the palette/skin entry hashes;
2. compute `appearanceHash` from those inputs;
3. resolve the base groups and, when the selected mode has an override, replace each provided
   group with its complete same-shape override;
4. write `tokens.json` (mode-resolved);
5. expand the v2 templates with the resolved values;
6. write the composed CSS and `appearance.json`, then repoint `current/appearance`.

**Mode is resolved before expansion.** The rule is: mode is resolved before expansion, so a
template never branches on mode, palette or skin. There are no conditionals in v2 templates: no
`{% if %}`, no `{{#if}}`, no expression evaluation. A template that contains conditional syntax is
invalid.

### Placeholder flattening

A v2 placeholder is the full nested token path, uppercased with every run of non-alphanumeric
characters replaced by `_`, prefixed with `SKIN` and wrapped in `{{...}}`:

| Token path | Placeholder |
| --- | --- |
| `surface.panel.bg` | `{{SKIN_SURFACE_PANEL_BG}}` |
| `surface.cell.hover-bg` | `{{SKIN_SURFACE_CELL_HOVER_BG}}` |
| `state.selected.ring` | `{{SKIN_STATE_SELECTED_RING}}` |
| `type.size-body` | `{{SKIN_TYPE_SIZE_BODY}}` |
| `ink.ink` | `{{SKIN_INK_INK}}` |

The template set remains one `<configDir>.gtk.css.j2` per target config directory and renders
`<configDir>.css`. An unknown placeholder, a `{{SKIN_` left unresolved after substitution, or a
layout token used in a template (`{{SKIN_LAYOUT_BAR_PANEL_WIDTH}}` and friends) is an error.
Expansion fails closed; it never passes a placeholder through.

## Composition and the one provider

Each app installs **one** `Gtk.CssProvider` whose sheet is the composed CSS (palette
`@define-color` block + skin CSS). The provider is added at
`GTK_STYLE_PROVIDER_PRIORITY_USER` = **800** and is **installed last** so it wins over the app
stylesheet and the GTK theme. The replacing sink adds the next provider before removing the
previous one, so no frame is skinless and there is never a second appearance provider.

A consumer has exactly **one monitor** (on `current/appearance`) and exactly **one apply** per
event: read the config path, validate, compose/install, notify widgets. It does not separately
apply a palette provider. Style and monitor objects are module-scoped, not local to a factory
callback; a local reference can be collected and the appearance stops tracking.

## Refresh contract

The runtime's existing **`palette-refresh`** request remains the transport. There is no new
protocol and no new D-Bus method. The app-side handler receives `["palette-refresh",
"<appearanceHash>"]` and MUST re-apply the **whole appearance** (palette + skin), not only
`theme.apply()`. In v2 the composed sheet already contains both, so the correct handler is one
appearance apply. Apps that keep the v1 `theme.apply()`-only handler are non-conformant.

The bar keeps the **restart lane**: it is a restart app, not a live `palette-refresh` app. All
other live apps answer `palette-refresh` in place.

### systemd user units

Every AGS app runs as a systemd **user unit**; there is no raw `ags run` process outside a unit.
The unit owns the whole process group. A stop or restart MUST terminate the group
(`KillMode=control-group`) so the gjs child cannot survive its `ags run` parent, and the stop path
MUST release the app's D-Bus name (`ags quit -i <instance>` or an equivalent graceful shutdown)
before the group is killed. The observed failure — `org.freedesktop.Notifications` still owned by
the old gjs child after its parent died, until `ags quit -i notifications` — is the reason this is
normative, not an implementation detail.

## v1 workarounds retired

| v1 workaround | v2 replacement |
| --- | --- |
| one global `border-w` / `hairline-w` | per-role `surface.*.border-width` |
| hover/selected/disabled paints as template literals | `state.hover|selected|focus|disabled.fill/ink/ring` |
| small type and paddings as template literals | `type.size-*`, `surface.*.font-size`, `surface.*.padding`, `surface.pill.letter-spacing` |
| clipboard contrast math | `selected.fill` + `selected.ink` role pairs |
| bar-only layout tokens | `layout.<app>.*` namespaces, TSX-owned |
| `paper` palette-mode guessing | explicit `mode.light` overrides |
| watching the stable consumer link while the runtime repointed the second hop | one repointed `current/appearance` hop |
| `palette-refresh` re-applying only the palette | handler re-applies the whole appearance |
| raw `ags run` processes with orphaned gjs children | systemd user units with `KillMode=control-group` |

## Fail closed

Missing or invalid inputs (palette entry, skin manifest, template, expanded CSS, `tokens.json`,
`appearance.json`, or a composed `<configDir>.css`) abort generation/publication. A consumer keeps
its previous appearance instead of painting an invalid one. A published generation is immutable;
only `current/appearance` moves.

Drift gates MUST assert a known ink (for example the resolved `on_surface`/`on_backdrop` colour of
a rendered probe), not merely that the app loaded. A missing palette block paints near-black, and a
stale appearance would otherwise pass a load-only check. Schema gates MUST assert the five groups,
the surface/state/type/ink vocabularies, the namespaced numeric layout, the mode-override shape,
the `version: 2` artifacts, and the forbidden constructs above.

## Built-in skins (v2)

- **`glass`** — the default and the app fallback parity target. Translucent panel/card paint,
  rounded corners, blur and a soft shadow. The v1 values are converted faithfully: panel
  `border-width` `1.5`, card/cell/control/pill hairlines `1`, panel `radius` `18`, card `14`,
  cell `10`, pill `20`, and the same paint/shadow strings.
- **`flat`** — zero radii, no blur, no shadow, solid role paint; all borders zero-width and
  transparent/outline-free. The v1 values are converted faithfully (radii `0`, `border-w` `0`,
  `hairline-w` `0`).
- **`paper`** — the role-based ink/palette axis with clean rules and light-weight borders. It uses
  explicit `mode.light` overrides for its light surface/state/ink groups instead of guessing from
  the palette. A light palette + `paper` reads light; a dark palette + `paper` keeps the base
  groups. The base groups are the v1 paper values converted faithfully; `mode.light` is authored,
  not derived.

## Migration

- v1 `skin.css`, `skin.json`, `current/skins/` and `current/skin.json` are retired by this
  contract. Consumers re-pin the `v0.7.0` tag; there is no dual-publish window and no `v1.1
  hotfix`.
- A consumer migrates by watching `current/appearance`, reading
  `$XDG_CONFIG_HOME/<configDir>/appearance.css`, and replacing its palette-only refresh handler
  with the whole-appearance apply.
- No runtime, platform, assets or app code is changed in this repo. Those repos adopt this tag and
  generate the artifacts described above.

## Verification

```bash
uv run pytest -q tests/test_appearance_contract.py
make test
make skin-test
make schema-test
```

The appearance tests validate all three schemas as draft-07, accept the `glass`/`flat`/`paper`
manifests and resolved token documents, reject literal hex, transition, structure/variant, an
unknown surface role, an incomplete mode override and unit-bearing numeric strings, and exercise
the v2 placeholder flattening: `surface.panel.bg` expands to `{{SKIN_SURFACE_PANEL_BG}}`, mode is
resolved before expansion, and a layout token in a template is rejected.
