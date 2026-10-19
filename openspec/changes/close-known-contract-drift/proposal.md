# close-known-contract-drift

## Why

AD-6 makes the canonical contract the single source and names this exact drift:
`wallpaper.state` is **ahead of the contract by `stage` and `reload_failures`**.
The runtime's embedded validator schema carries both fields, so the contract is
currently behind its own consumer — the opposite of the single-source rule.

Evidence: the runtime embedded validator schema declares both fields as
**optional** properties of `wallpaper.state`: `stage` is a string enum of seven
values (`setting_wallpaper`, `generating_palette`, `palette_generated`,
`preparing_appearance_assets`, `appearance_assets_ready`, `reconciling_consumers`,
`finished`) and `reload_failures` is `{"type": "array", "items": {"type":
"string"}}`; neither is in `required` (`required` is `["state",
"wallpaper_hash"]`). `emit_validation.py` lines 176–204.
Verify: `sed -n '176,204p' dotfiles-v3/src/runtime/src/runtime/adapters/emit_validation.py`.

Evidence: the canonical contract omits both. The `wallpaper.state` payload keys
are `['state', 'trigger', 'wallpaper_hash']` and `optional` is `['trigger']`.
Verify: `python3 -c "import json;d=json.load(open('event-contract.json'));t=d['topics']['wallpaper.state'];print(sorted(t['payload']), t.get('optional'))"` → `['state', 'trigger', 'wallpaper_hash'] ['trigger']`.

Evidence: spine `ARCHITECTURE-SPINE.md` AD-6 (lines 92–96) states the rule and
the observed drift verbatim: "already observed: `wallpaper.state` ahead of the
contract by `stage` and `reload_failures`" … "additive stays on `Events1`".
Verify: `sed -n '92,96p' <planning-repo>/architecture/architecture-ags-platform-2026-10-09/ARCHITECTURE-SPINE.md`.

Evidence: the symmetric drift gate already exists and is green (REQ-003); it
compares the contract against the generated artifacts in both directions, so an
unregenerated contract edit fails. `gen/check_symmetry.py` lines 204–295
(schema ↔ contract, both ways); `Makefile` `contracts-drift` target.
Verify: `make contracts-drift` → exit 0 on the current tree.

Evidence: `stage`/`reload_failures` are **additive optional** members, so by the
contract's own versioning rule they stay on `org.dotfiles.Events1` and are
non-breaking (`event-contract.json` `versioning.non_breaking`).
Verify: `python3 -c "import json;print(json.load(open('event-contract.json'))['versioning']['non_breaking'])"`.

## What Changes

- Add two **optional** members to `wallpaper.state` in `event-contract.json`:
  - `stage` (`s`, enum of the seven runtime stage values);
  - `reload_failures` (`as`, an array of strings).
  List both in the topic's `optional` array and add the `stage` enum.
- Update `event-contract.md`'s known-topics table row and the `wallpaper.state`
  notes to match.
- Regenerate `generated/{contract.py,contract.ts,events.schema.json}` with
  `python3 gen/generate.py` and commit the regenerated artifacts.

## Capabilities

- **Modified Capabilities:** `event-contract` — the `wallpaper.state` topic
  payload gains two optional fields; the capability's single-source guarantee is
  restored for this topic.

## Non-goals (out of scope)

- **Not** the dead `speedtest.finished` literal in
  `dotfiles-v3/src/gui-tools/hypr-pano/lib/event-bus-core.ts`. It lives in
  `dotfiles-v3`; REQ-004 (repoint) removes it. This change touches no file under
  `dotfiles-v3`.
- **Not** a new reverse drift check. REQ-003 already delivered the symmetric
  (schema ↔ contract, both directions) check and its negative test
  (`gen/test_symmetry.py` `test_c_extra_schema_key_reverse_check_fails`); this
  change closes the data drift that check would catch.
- **Not** the cross-repo runtime-tables leg of the gate — that is REQ-004
  (`gen/check_symmetry.py` `RUNTIME_TABLES_HOOK`).
- **Not** repointing consumers or deleting their embedded duplicates — REQ-004.
- **Not** a breaking change: both new fields are optional, so the interface
  stays `org.dotfiles.Events1` (no `Events2`).
- **Not** the structural `schemas/*.schema.json` state artifacts — only the event
  wire schema `generated/events.schema.json` is in scope.

## Impact

- Modified: `event-contract.json`, `event-contract.md`,
  `generated/contract.py`, `generated/contract.ts`,
  `generated/events.schema.json`.
- New: `openspec/changes/close-known-contract-drift/**`.
- No `dotfiles-v3` file, no `schemas/`, and no generator source is changed.
