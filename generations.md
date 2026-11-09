# Generations v3 (frozen)

> **Status: frozen v3.** This is the normative generation interface for the
> `dotfiles` state plane. It replaces the v2 **multi-pointer** and
> **two-pipeline** mechanics with one committed generation and one convergence
> function. It keeps the v2 appearance token vocabulary and the v2 artifact
> interface (composed palette + skin + mode, one provider, one watched hop).
>
> The machine-readable forms are
> [`schemas/generation-manifest.schema.json`](./schemas/generation-manifest.schema.json)
> and
> [`schemas/appearance-refresh-result.schema.json`](./schemas/appearance-refresh-result.schema.json).
> The generation-bound refresh protocol is
> [`appearance-refresh.md`](./appearance-refresh.md). The v2
> [`ags-app-refresh.md`](./ags-app-refresh.md) and the v2
> [`appearance.md`](./appearance.md) token model remain for provenance; where
> they describe pointers or restart mechanics, this document supersedes them.
>
> The frozen design record is `dotfiles-v3/docs/107-generations-v3.md`. This
> repo owns the contract only; the runtime, platform, provisioning and app
> implementations live elsewhere.

## 0. Non-negotiable decisions

1. **Generation is the unit.** A generation is a complete, immutable directory
   `state/generations/<genHash>/`. One pointer,
   `state/current -> generations/<genHash>`, is swapped with one atomic
   `rename`. Every consumer reads through `current/`.
2. **One convergence pipeline.** `converge(intent) -> generation` is the only
   mutation path for the daemon, the CLI and every skin/mode/wallpaper change.
   The daemon owns the serialized job queue; the CLI fallback runs the same
   function under the same exclusive kernel `flock`. There is no second
   pipeline and no publish-then-fail path.
3. **Generation-bound apply/ack.** A refresh request names a `genHash`; the app
   applies that exact generation and answers with that same `genHash`. A
   mismatch is deferred/retryable. The ledger records `applied` only on an exact
   match.
4. **Artifact locality.** Runtime writes live only under `state/`; never under
   `<install>/` or `<install>/apps/<tag>/`. The platform reads
   `$XDG_STATE_HOME/dotfiles/current/appearance/<configDir>.css` and watches
   `current` (one hop).
5. **No polling as correctness.** inotify for `desired.json` and `current`,
   D-Bus `NameOwnerChanged` for AGS registration, and systemd
   `JobRemoved`/`--wait` for restarts. A timeout aborts/reports; it never means
   "ready".
6. **Lane policy is explicit.** Every app declares `live` or `restart`; exactly
   one refresh path is enforced. Unit management changes *how* a restart
   happens, not *whether* it happens.
7. **Mode is a generation input.** `mode` is part of the intent and of
   generation identity. A mode change is an ordinary converge, not a
   `wallpaper set` side effect.
8. **No workarounds.** No second pointer, no second pipeline, no "apply
   whatever is current" ack, and no retry loop that hides a missing event.

## 1. State layout

Everything below is under the single runtime state root
`$XDG_STATE_HOME/dotfiles/`:

```text
state/
  cache/                                  # content-addressed layer entries
    palettes/<paletteHash>/...
    effects/<effectsHash>/...
    icons/<iconsHash>/...
    wallpapers/<wallpaperHash>/wallpaper.png
  generations/
    <genHash>/
      manifest.json                       # written last; the self-check
      palette -> ../../cache/palettes/<paletteHash>
      effects -> ../../cache/effects/<effectsHash>
      icons   -> ../../cache/icons/<iconsHash>
      wallpaper/
        wallpaper.png -> ../../../cache/wallpapers/<wallpaperHash>/wallpaper.png
      appearance/
        tokens.json                       # mode-resolved v2 tokens
        ags.css
        ags-notifications.css
        ...                               # one <configDir>.css per target
      # compatibility aliases INSIDE this generation (never pointers)
      colors.yaml -> palette/colors.yaml
      colors.gtk.css -> palette/colors.gtk.css
      colors.adw.css -> palette/colors.adw.css
      colors.conf -> palette/colors.conf
      colors.sequences -> palette/colors.sequences
      colors.rasi -> palette/colors.rasi
      colors.kitty -> palette/colors.kitty
      colors.btop.theme -> palette/colors.btop.theme
      wallpaper.png -> wallpaper/wallpaper.png
      wallpaper-<monitor>.png -> wallpaper/wallpaper.png
  current -> generations/<genHash>         # the ONE commit pointer
  appearance-ledger.json                   # per-app apply/ack state
  gc-pins.json                             # retention pins (metadata only)
  converge.lock                            # the one operation lock
  generations/.staging-<pid>-<uuid>/       # crash-recoverable staging only
```

- The directory basename **is** the generation hash. `current` targets exactly
  one generation directory; it is never a directory of independent family
  links.
- The compatibility aliases are **inside** the generation. Resolving
  `current/colors.yaml` and `current/appearance/ags.css` from the same
  `current` inode lands in the same generation, so they cannot skew.
- A generation references immutable content-addressed layer entries; it does
  not copy palette/icons/effects/wallpaper bytes. Only `appearance/*` and
  `manifest.json` are generation-specific real files.
- Staging is always a sibling of the target generation
  (`state/generations/.staging-<pid>-<uuid>/`) so the publish `rename` is on
  one filesystem. A cross-filesystem `state/staging/` directory is not a v3
  mechanism.
- `gc-pins.json` is retention metadata, not a read path and not a second
  pointer. No consumer resolves a generation through it.

## 2. Manifest

`manifest.json` is the generation self-check. A directory without a valid
manifest is never a generation. It validates against
[`schemas/generation-manifest.schema.json`](./schemas/generation-manifest.schema.json)
and is written last inside staging.

```json
{
  "version": 3,
  "generationHash": "<sha256>",
  "created": { "at": "2026-11-06T12:00:00Z", "by": "dotfiles-runtime 0.8.0" },
  "committed": { "at": "2026-11-06T12:00:01Z", "jobId": "converge-01J8Z3" },
  "layers": {
    "wallpaper": { "entryHash": "<wallpaperHash>", "path": "wallpaper" },
    "palette": { "entryHash": "<paletteHash>", "path": "palette" },
    "effects": { "entryHash": "<effectsHash>", "path": "effects" },
    "icons": { "entryHash": "<iconsHash>", "path": "icons" }
  },
  "skin": { "name": "glass", "entryHash": "<skinHash>", "mode": "dark" },
  "appearance": {
    "tokensPath": "appearance/tokens.json",
    "targets": [
      { "configDir": "ags", "path": "appearance/ags.css" },
      { "configDir": "ags-notifications", "path": "appearance/ags-notifications.css" }
    ]
  },
  "mode": "dark",
  "intent": {
    "wallpaper": "<wallpaperHash>",
    "palette": "<paletteHash>",
    "skin": "glass",
    "mode": "dark",
    "effects": "<effectsHash>",
    "icons": "<iconsHash>"
  },
  "source": {
    "kind": "daemon",
    "intentHash": "<desiredIntentHash>",
    "jobId": "converge-01J8Z3"
  }
}
```

### 2.1 Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `version` | yes | Exactly `3`. A v3 consumer rejects every other version. |
| `generationHash` | yes | Lowercase 64-hex canonical identity. Equals the directory basename and the `current` target basename. |
| `created` | yes | `at` (date-time) and optional `by`: when the complete generation directory was written in staging. |
| `committed` | yes | `at` (date-time) and optional `jobId`: when `current` was atomically swapped to this generation. |
| `layers` | yes | `wallpaper` and `palette` required; `effects` and `icons` optional. Each layer is `{entryHash, path}`. |
| `skin` | yes | `{name, entryHash, mode}`. `skin.mode` must equal the top-level `mode`. |
| `appearance` | yes | `{tokensPath, targets[]}`. `tokensPath` is exactly `appearance/tokens.json`; each target is `{configDir, path}` with `path` = `appearance/<configDir>.css`. |
| `mode` | yes | `dark` or `light`. A generation input and part of identity. |
| `host` | no | The resolved host snapshot, present only when at least one delegated token used the host: `{source, version, fingerprint, defaults}`. `defaults` records only the participating logical token paths. See §2.1.1. |
| `intent` | yes | The resolved intent snapshot: `wallpaper`, `palette`, `skin`, `mode`, plus optional `effects`/`icons` hashes and optional `host`. |
| `source` | yes | `{kind, intentHash, jobId?}`. `kind` is `daemon` or `cli`; `intentHash` is the `desired.json` snapshot hash; `jobId` is present for the daemon queue and absent for the CLI fallback. |

`additionalProperties: false` applies at every object level. Every property name
is checked against the forbidden structure vocabulary: keys named `structure`,
`order`, `presence`, any `*variant*` key, and the same substrings inside a
token-like name are rejected. The manifest carries no literal hex: hashes are
bare 64-hex digests, identities are lowercase path segments, and provenance
tokens do not accept `#`.

A layer `path` is a generation-local relative path: no leading slash, no empty
segment, no `.`/`..` segment and no `#`. A path that points back into
`cache/` or outside the generation is the v2 multi-pointer shape and is
invalid.

### 2.1.1 Optional host snapshot

A host block is present only when the selected skin's `[host]` policy actually used at least one
live host value in the selected mode. When no delegated value participated, omit `host` and
`intent.host` entirely; a no-host generation keeps the same manifest shape as before this slice.

```json
"host": {
  "source": "hyprland",
  "version": 1,
  "fingerprint": "<hostHash>",
  "defaults": {
    "surface.panel.radius": 0,
    "surface.panel.border-width": 1
  }
}
```

- `source` is `hyprland` in Phase 1. Other compositor sources require a later contract enum
  addition.
- `version` is the host mapping version; `1` is `hyprland.paint.v1`.
- `fingerprint` is the `hostHash` from `appearance.md`: canonical JSON of the mapping version and
  only the participating logical token paths/values. It excludes the instance signature,
  timestamps and `set` flags. A host change that does not alter a participating value is the same
  fingerprint.
- `defaults` is non-empty and closed. It may contain only `surface.panel.radius` (0..64) and
  `surface.panel.border-width` (0..16), and only when that token actually used the host.
- `intent.host` is required when `host` is present and must equal `host.fingerprint`. JSON Schema
  enforces presence; equality is enforced by runtime manifest validation and by the contract
  fixture gate, because draft-07 cannot compare two properties.
- A host block with an empty `defaults`, an unknown default, an unknown source, a bad version or a
  non-64-hex fingerprint is invalid.

### 2.2 Identity rules

- `generationHash` is the canonical hash of the intent, layer hashes, mode and
  the composed appearance artifact hash. It excludes timestamps.
- `generationHash` must equal the generation directory basename and the target
  basename of `current`.
- `skin.mode == mode`; `intent.mode == mode`; `intent.skin == skin.name`;
  `intent.wallpaper`/`intent.palette`/`intent.effects`/`intent.icons` equal the
  matching layer `entryHash` values when present.
- When `host` is present, `intent.host == host.fingerprint`; when it is absent,
  neither `host` nor `intent.host` is present. A host-participating generation
  includes the fingerprint in the `appearance.v3` identity, the generation
  intent hash and the generation hash. The queue key stays host-free: the host is read
  once inside `converge.lock`, so two requests with the same desired state can
  coalesce and the executing job resolves the current host.
- `appearance.targets` is the only app-list input. Config dirs are unique and
  the platform carries no separate app list.
- A manifest that fails any check fails closed: the consumer keeps its previous
  provider, reports the mismatch and retries on the next generation event.

## 3. Commit transaction

The commit is one lock scope and one visible rename:

1. **Acquire** `converge.lock` through the daemon job queue, or the CLI
   fallback. The lock is a blocking kernel `flock`; it has no bounded retry
   loop and is released by process death.
2. **Read intent** from `desired.json` and snapshot its identity (wallpaper
   bytes, skin manifest/templates, mode, effects/icons inputs). An invalid
   intent fails before any mutation.
3. **Derive/reuse layers** into content-addressed cache entries. Derivation may
   use cache staging; an orphaned entry is harmless and GC-able.
4. **Stage the generation** at
   `state/generations/.staging-<pid>-<uuid>/` on the same filesystem. Write
   layer links, composed appearance sheets and `tokens.json`; write
   `manifest.json` last; `fsync` files and directories.
5. **Publish the immutable generation:** `rename(staging,
   generations/<genHash>)`. If the target exists, validate it and discard the
   staging copy (content-addressed reuse).
6. **Commit the pointer:** create
   `current.tmp.<pid> -> generations/<genHash>` and `rename(current.tmp…,
   current)`, then `fsync` `state/`. This is the only visible transition;
   readers see the old generation or the new one, never a mix.
7. **Apply/ledger:** send generation-bound `appearance-refresh` requests to
   live apps, restart the restart lane, and write one ledger record per app
   against `generationHash`. The generation is already authoritative; an apply
   failure never repoints back to the previous generation.
8. **Release** the lock. The next job or trigger sees a complete generation, or
   the same complete generation (idempotent).

### 3.1 Daemon queue and CLI fallback

- The daemon owns a **converge job queue** over the existing
  `org.dotfiles.Events` job surface (`JobStarted`/`JobFinished`). The job
  carries the intent revision/hash and returns the committed `genHash` plus
  per-app status.
- The CLI preflights the well-known name once. If the daemon owns it, the CLI
  **subscribes to `JobFinished` before submitting**, submits one converge job,
  and waits for the matching `job_id`/`genHash`. It does not poll state files.
- The queue key stays host-free: the daemon queue key is the desired-state
  snapshot and does not include a host snapshot. The host is read once inside
  `converge.lock`; it participates in the generation identity, not in the
  pre-lock queue key. A queued job executes against the host snapshot it reads
  under the lock.
- An identical intent/generation is coalesced. The newest queued intent
  supersedes older queued (not running) intents. A running job is never
  cancelled mid-commit. A job is idempotent and safe to retry by intent hash.
- If the daemon is not on the bus, the CLI acquires the **same** `converge.lock`
  and calls the **same** `converge(intent)`. It does not start a daemon and
  does not run a second implementation.
- If the daemon disappears after a job was submitted, the CLI reports the
  typed failure and re-checks the commit; it does not run the fallback
  concurrently with a possibly-live job.
- There is no nested `.seed.lock` or appearance-operation lock. The daemon queue
  and the fallback share one lock path and one ordering.

## 4. Crash matrix

| Crash point | Visible state | Recovery |
| --- | --- | --- |
| before generation rename | old `current`; staging under `generations/.staging-*` | old generation stays; startup/converge removes stale staging older than grace |
| after generation rename, before `current` rename | old `current`; complete orphan `generations/<gen>` | old generation stays; GC may retain/remove the orphan; next converge reuses it by hash |
| during `current` rename | old or new `current` (rename is atomic) | no repair needed; manifest check validates the new target |
| after `current` rename, before ledger | new `current`; ledger names the old generation | next trigger sees `ledger.generation != current` and refreshes every app; no rollback |
| during apply/restart | new `current`; some apps old, some new | app event/retry converges to `current`; restart lane retries per policy; ledger records deferred, never `applied` |
| during GC | retained generations intact; object removal may be partial | sweep is journaled; only unreferenced objects older than grace are removed; next sweep completes |

A partially written generation is never visible because `current` points only
at a directory whose manifest was written last and whose rename completed. A
torn staging directory is never treated as a generation.

## 5. Consumer read and watch rules

A consumer MUST:

- Resolve the committed generation through `current`. It MUST verify
  `current/manifest.json` (`version: 3`, `generationHash`) before trusting
  target paths, or read `generations/<genHash>/...` directly after resolving
  the same `genHash`. If the pointer moves between resolve and read, it MUST
  answer deferred/retryable rather than paint a mix.
- Read the composed sheet and tokens from the state path:
  `$XDG_STATE_HOME/dotfiles/current/appearance/<configDir>.css` and
  `$XDG_STATE_HOME/dotfiles/current/appearance/tokens.json`. This is one hop
  from state to the generation.
- Take the target config dir list from `manifest.appearance.targets`; it MUST
  NOT carry a separate app list.
- Watch `$XDG_STATE_HOME/dotfiles/current` (or its parent, for the atomic
  `MOVED_TO` event) for a generation change. It MUST NOT watch an app tag, an
  install-spine convenience link, or `current/appearance` as a proxy for the
  generation commit.
- Read through `current` again after the event. It MUST NOT cache a resolved
  generation path across a commit without revalidating the manifest.
- Fail closed: an invalid/missing manifest, target, token document or sheet
  keeps the previous provider and reports the error; it never paints a
  partial generation.

A consumer MUST NOT:

- resolve a per-family link (`colors.yaml`, `effects`, `icons`, an app tag) and
  assume it belongs to the same generation as another family;
- read `$XDG_CONFIG_HOME/<configDir>/appearance.css` as the v3 runtime path;
- treat a boolean or an unbound "current" apply as success.

## 6. Artifact locality and immutability

Runtime-owned paths are exactly:

```text
state/cache/<kind>/<hash>/...
state/generations/<genHash>/...
state/generations/.staging-*...
state/current
state/appearance-ledger.json
state/gc-pins.json
state/converge.lock
```

The runtime never writes:

- `<install>/apps/<installDir>/<tag>/` (immutable app tag);
- `<install>/config/...` (install spine; provisioning owns its shape);
- `$XDG_CONFIG_HOME/<configDir>/appearance.css` (no runtime convenience link
  in v3).

All generation contents are immutable after publication. Only `current` moves.
Provisioning may create **writable stable links for non-runtime consumers**,
for example
`~/.config/gtk-4.0/colors.css -> $XDG_STATE_HOME/dotfiles/current/palette/colors.adw.css`.
Those links are provisioning-owned and stable; the runtime never repoints them.
App source links (`~/.config/<configDir> -> <install>/config/<configDir> ->
<install>/apps/<tag>`) remain for app code and static assets only.

`verify`/`deploy-coverage` MUST assert:

- no runtime artifact (`appearance.css`, `tokens.json`, `colors*`, a generation
  pointer) exists inside any `<install>/apps/<installDir>/<tag>/`;
- every non-runtime stable link resolves through `current/`, not through a
  generation-specific path;
- the state root contains no symlink into an app tag.

## 7. Lane policy

Each app declares three independent axes:

| Axis | Values | Owner | Meaning |
| --- | --- | --- | --- |
| `refresh` | `live` \| `restart` | app manifest and composition app list | exactly one apply path for a generation change |
| `supervision` | `unit` \| `launcher` | provisioning/app list | who owns the process lifecycle |
| `launch` | `always` \| `on-demand` | composition app list | whether login starts it |

Rules:

- `live` means the app has a generation-bound refresh handler and MUST NOT be
  restarted for an appearance change.
- `restart` means the app has no refresh handler and is restarted. A failed
  live refresh never falls back to restart. A restart failure is a retry, not a
  lane switch.
- Exactly one `refresh` value is enforced per app. A missing or contradictory
  declaration is invalid; there is no "both" or "try live then restart".
- `supervision: unit` changes only *how* a restart is performed
  (`systemctl --user restart`, `ExecStop=ags quit -i`,
  `Restart=on-failure`). `supervision: launcher` uses the serialized AGS
  quit/launch path. The `refresh` decision is made before supervision is
  consulted.
- `launch` is not a lane. An on-demand app can be `live`; an always-on app can
  be `restart`.
- A mode change is a normal generation change for every lane. There is no
  "mode-only" path and no wallpaper-set-only workaround.

## 8. Mode identity

`mode` is read from `desired.json`, resolved before appearance/template
generation, recorded in `manifest.mode` and `manifest.intent.mode`, and
included in `generationHash`. It must also equal `manifest.skin.mode`.

Consequences:

- changing only `mode` creates a different `generationHash`;
- `current/palette/colors.yaml` and `current/appearance/*` in one generation
  always describe the same mode;
- `doctor` compares `manifest.mode` with the resolved palette mode and reports
  divergence rather than guessing;
- a smart-mode projection is recorded once per converge; it cannot oscillate
  inside one generation.

## 9. Garbage collection and pins

GC is part of convergence, not a background timer.

### 9.1 Retention

Retain:

- the active generation (`current`);
- the newest `keep` generations (default 5);
- every pinned generation;
- every generation named by an `applied`/`deferred` ledger entry that may still
  be retried;
- any generation, staging manifest or layer referenced by the above.

Do not remove anything younger than `grace` (default 24 h) or newer than the
last successful commit.

### 9.2 Pin contract

`state/gc-pins.json` is runtime-owned retention metadata:

```json
{
  "version": 1,
  "generations": [
    { "generationHash": "<sha256>", "reason": "operator rollback target", "addedAt": "2026-11-06T12:00:00Z" }
  ]
}
```

A pin is **not** a pointer and is never resolved by a consumer. Pinning retains
a generation; unpinning only makes it eligible for the normal grace/keep sweep.
Pinned hashes are validated as lowercase 64-hex; an unknown pinned generation is
retained metadata and is reported, not silently dropped.

### 9.3 Mark-and-sweep

1. Enumerate retained generations and staging manifests; collect every
   referenced layer hash.
2. Remove unreferenced `cache/` entries older than grace. Never remove a
   referenced entry, even if old.
3. Prune generations only while holding `converge.lock`; remove generation
   directories before their now-unreferenced objects.
4. Remove stale `generations/.staging-*` older than grace at startup or at the
   next converge (never by a background timer).
5. A reader that already opened an old generation keeps working on POSIX; a
   reader that resolves a pruned path gets a retryable missing-generation
   result.
6. Never delete user files, app tags or install-spine links.

## 10. Event-driven rules (no polling)

| Wait | Required mechanism | Forbidden |
| --- | --- | --- |
| `desired.json` change | inotify watch on the intent file/parent | mtime polling |
| new generation | inotify `MOVED_TO` on `current` (or parent) | polling the `current` symlink |
| app registration | D-Bus `NameOwnerChanged` | repeated `ags list` |
| systemd restart | `systemctl --user restart --wait` or `JobRemoved` | sleep/name polls |
| lock acquisition | blocking kernel `flock` | bounded `flock` retry loop |
| watch overflow/lost event | one full rescan triggered by the overflow event | sleep-and-retry |

A timeout may exist only to abort/report (for example a D-Bus call deadline).
It must not decide that an app is ready, that a restart succeeded or that a
generation is committed.

## 11. Generation-bound refresh protocol

The request and response are frozen in
[`appearance-refresh.md`](./appearance-refresh.md) and
[`schemas/appearance-refresh-result.schema.json`](./schemas/appearance-refresh-result.schema.json):

```text
request:  ["appearance-refresh", "<genHash>"]
response: {"applied":"<genHash>"}
          | {"deferred":"reason","genHash":"<genHash>"}
          | {"failed":"reason","retryable":true|false,"genHash":"<genHash>"}
```

- `genHash` is a lowercase 64-hex generation identity, never a path.
- Every response names a generation. The response hash MUST equal the request
  hash; the caller rejects a mismatch instead of recording success.
- The app resolves the **requested** generation: it verifies
  `current/manifest.json.generationHash == genHash`, or reads
  `generations/<genHash>/appearance/<configDir>.css` and
  `appearance/tokens.json` directly. If `current` moved first, it answers
  deferred and applies nothing.
- After validating and installing the sheet (one provider,
  `GTK_STYLE_PROVIDER_PRIORITY_USER` = 800, installed last) it answers with the
  exact generation it applied.
- The runtime records `applied` only when the ack's generation equals the
  requested generation and `current` still matches. A stale ack is a
  deferred/retry, never success.
- A restart-lane app is restarted only after the generation is committed. If
  `current` moves during the restart, the per-app result is downgraded to
  deferred.
- The old v2 `palette-refresh` request and `{"ok":true}` ack are superseded.
  They remain in `ags-app-refresh.md` for provenance only; v3 apps implement
  `appearance-refresh`.

## 12. Evidence and verification

- Frozen design: `dotfiles-v3/docs/107-generations-v3.md` §0, §2.1–§2.10.
- Multi-pointer skew and two-pipeline evidence: the RFC §1.1–§1.6 cites
  `dotfiles-runtime/src/runtime/adapters/seeder.py:660-807`,
  `.../application/reconcile.py:308-326`,
  `.../adapters/invalidation.py:140-173`, `.../cli/main.py:2096-2240`,
  `.../adapters/appearance_ledger.py:58-94` and the live `state/current`
  listing.
- Unbound ack evidence: `ags-app-refresh.md:64-78` and RFC §1.3.
- Runtime writes into tags evidence: RFC §1.4 and the live
  `.../apps/notifications/v0.4.0/appearance.css` link.

Verify from the repo root:

```sh
make test
make skin-test
make appearance-test
make schema-test
make generations-test
```

The generation tests validate the manifest and refresh-result schemas as
draft-07, accept the positive fixtures, reject unknown/stale layers, wrong
hashes, a missing mode, extra keys, structure/variant and literal hex, reject
the old boolean ack, and reject any response hash that differs from the
request.
