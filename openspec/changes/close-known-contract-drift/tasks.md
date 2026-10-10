# Tasks

## 1. Pin the drift in the canonical contract (≤1h)

- [ ] 1.1 Add optional `stage` (`s`) and `reload_failures` (`as`) to the
  `wallpaper.state` payload in `event-contract.json`, list both in the topic's
  `optional` array, and add the `stage` enum (the seven runtime values).
  Verify: `python3 -c "import json;d=json.load(open('event-contract.json'));t=d['topics']['wallpaper.state'];print(t['payload'].get('stage'), t['payload'].get('reload_failures'), t.get('optional'))"`
  → `s as ['reload_failures', 'stage', 'trigger']`.
- [ ] 1.2 Update `event-contract.md`'s known-topics table row for
  `wallpaper.state` and its notes paragraph to include the two optional members.
  Verify: `grep -n 'stage' event-contract.md` → shows the row/notes mention.

## 2. Regenerate the committed bindings (≤1h)

- [ ] 2.1 Run `python3 gen/generate.py` and commit the regenerated
  `generated/{contract.py,contract.ts,events.schema.json}`.
  Verify: `git diff --stat generated/` → three files changed; the wallpaper
  payloads now carry `stage`/`reload_failures` as optional.
- [ ] 2.2 Confirm the symmetric drift gate is green after regeneration.
  Verify: `make contracts-drift` → exit 0, `[drift] symmetric: contract and
  generated/ agree`.

## 3. Verify the change (≤1h)

- [ ] 3.1 Confirm the generated Python/TS/schema expose the two fields as
  optional with the right shapes.
  Verify: `python3 -c "import json;s=json.load(open('generated/events.schema.json'));p=s['$defs']['Topic_wallpaper_state'];print(p['required'], sorted(p['properties']), p['properties']['stage']['enum'])"`
  → required excludes both; properties include both; enum has 7 values.
- [ ] 3.2 Run the contract test suite.
  Verify: `make test` → `OK`.
- [ ] 3.3 Confirm the tree is clean and the change validates.
  Verify: `git status --porcelain` → no output;
  `openspec validate close-known-contract-drift --type change` → valid.
