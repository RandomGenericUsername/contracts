# event-contract (delta)

## ADDED Requirements

### Requirement: wallpaper.state pins the optional stage member

The canonical contract SHALL declare an optional `stage` member on the
`wallpaper.state` payload: a string enum of the seven runtime stage values,
matching the runtime's embedded validator schema.

Source: spine **AD-6** ("already observed: `wallpaper.state` ahead of the
contract by `stage`"); runtime `emit_validation.py`
`TOPIC_SCHEMAS["wallpaper.state"]` (lines 176–204); ticket REQ-005.

#### Scenario: contract matches the runtime stage enum

- **WHEN** the `wallpaper.state` payload is read from `event-contract.json`
- **THEN** `stage` is a string enum of `setting_wallpaper`,
  `generating_palette`, `palette_generated`, `preparing_appearance_assets`,
  `appearance_assets_ready`, `reconciling_consumers`, `finished`

### Requirement: wallpaper.state pins the optional reload_failures member

The canonical contract SHALL declare an optional `reload_failures` member on the
`wallpaper.state` payload: an array of strings, matching the runtime's embedded
validator schema.

Source: spine **AD-6** ("ahead of the contract by … `reload_failures`"); runtime
`emit_validation.py` `TOPIC_SCHEMAS["wallpaper.state"]`; ticket REQ-005.

#### Scenario: contract matches the runtime reload_failures shape

- **WHEN** the `wallpaper.state` payload is read from `event-contract.json`
- **THEN** `reload_failures` is declared as an array of strings

### Requirement: both new members are optional and non-breaking

Both `stage` and `reload_failures` SHALL be listed in the `wallpaper.state`
topic's `optional` array, so the change is additive and the interface stays
`org.dotfiles.Events1` (no `Events2`).

Source: spine **AD-6** ("additive … stays on `Events1`"); ticket REQ-005.

#### Scenario: neither member is required

- **WHEN** the `wallpaper.state` topic's `optional` array is read
- **THEN** it contains both `stage` and `reload_failures`

#### Scenario: symmetric gate agrees after regeneration

- **WHEN** `make contracts-drift` runs after the contract is updated and the
  bindings regenerated
- **THEN** the contract ↔ schema, contract ↔ `contract.py`, and contract ↔
  `contract.ts` legs all pass and the target exits 0

### Requirement: generated bindings carry the two optional members

The regenerated `generated/contract.py`, `generated/contract.ts`, and
`generated/events.schema.json` SHALL expose `stage` and `reload_failures` on the
`wallpaper.state` payload as optional members, with `stage` enum-constrained and
`reload_failures` typed as an array of strings.

Source: spine **AD-6** ("bindings are generated … the generated artifacts are
committed"); ticket REQ-005.

#### Scenario: Python binding is optional and enum-constrained

- **WHEN** `generated/contract.py`'s `WallpaperStatePayload` is inspected
- **THEN** `stage` is `NotRequired[Literal[...]]` with the seven values and
  `reload_failures` is `NotRequired[list[str]]`

#### Scenario: TypeScript binding is optional and enum-constrained

- **WHEN** `generated/contract.ts`'s `WallpaperStatePayload` interface is
  inspected
- **THEN** `stage?:` is the seven-value string union and `reload_failures?:` is
  `string[]`

#### Scenario: schema binding is optional and typed

- **WHEN** `generated/events.schema.json`'s `Topic_wallpaper_state` definition is
  inspected
- **THEN** `stage` and `reload_failures` are in `properties`, neither is in
  `required`, `stage` carries the seven-value enum, and `reload_failures` is
  `{"type": "array", "items": {"type": "string"}}`
