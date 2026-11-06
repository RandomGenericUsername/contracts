# Appearance refresh protocol v3 — `appearance-refresh`

> **Status: frozen v3.** This is the generation-bound request/response protocol
> between `dotfiles-runtime` and a running **live** AGS app. It supersedes the
> v2 `palette-refresh` protocol in [`ags-app-refresh.md`](./ags-app-refresh.md)
> for provenance only; v3 apps implement `appearance-refresh`.
>
> The response schema is
> [`schemas/appearance-refresh-result.schema.json`](./schemas/appearance-refresh-result.schema.json).
> The generation identity and commit rules are
> [`generations.md`](./generations.md).

## Invocation

The runtime invokes each running live app after the generation is committed:

```sh
ags request appearance-refresh <genHash> -i <instance>
```

- `appearance-refresh` is the fixed command name (`argv[0]` in the handler).
- `<genHash>` is the only argument (`argv[1]`): a lowercase 64-character
  SHA-256 generation hash, never a path, an appearance hash, or a boolean
  version. The handler receives exactly
  `["appearance-refresh", "<genHash>"]`. Any other command or argument count is
  malformed and MUST NOT be treated as a successful refresh.
- `-i <instance>` selects the AGS instance; it is caller syntax, not a handler
  argument.
- Restart-lane apps do not implement this command; they are restarted after the
  commit. A failed live refresh never becomes a restart.

The request carries the generation because an ack without a generation is not
falsifiable. The app MUST apply the generation named in the request; it never acks
"whatever `current` is" at handler time.

## Transport

AGS 3.1.0's request transport is a string. The app registers a
`requestHandler(argv: string[], res: (response: string) => void)` and answers
by calling `res(JSON.stringify(...))`.

- Call `res` exactly once, after the apply has fully completed.
- The response is one JSON-encoded string on stdout, one line, with no other
  stdout output (AGS adds the trailing newline).
- A JSON object literal (`res({...})`) is forbidden: AGS prints the response
  with `cmd.print_literal(str + "\n")`, so a non-string becomes
  `[object Object]`.
- Progress logs, debug output and app-internal logging go to stderr or the
  app's log file, never to the request response.
- A missing handler produces the non-JSON string
  `instance "<name>" has no request handler implemented`; the runtime treats
  it as a malformed response (failure), not a skip.

## Response union

Exactly three response shapes are valid:

```text
{"applied":"<genHash>"}
{"deferred":"reason","genHash":"<genHash>"}
{"failed":"reason","retryable":true|false,"genHash":"<genHash>"}
```

| Meaning | Response string | Required fields |
| --- | --- | --- |
| Applied | `{"applied":"<genHash>"}` | `applied` is the exact requested lowercase 64-hex generation. |
| Deferred | `{"deferred":"reason","genHash":"<genHash>"}` | `deferred` is a non-empty reason; `genHash` is the requested generation. |
| Failed, retryable | `{"failed":"reason","retryable":true,"genHash":"<genHash>"}` | `failed` non-empty; `retryable` is `true`; `genHash` is the requested generation. |
| Failed, terminal | `{"failed":"reason","retryable":false,"genHash":"<genHash>"}` | `failed` non-empty; `retryable` is `false`; `genHash` is the requested generation. |

No other shape is valid. In particular:

- `{"ok":true}` (the v2 ack) is **invalid**: it cannot name a generation.
- A response without a generation hash is invalid.
- A `failed` response without `retryable` is invalid.
- Extra keys are invalid; do not copy v2 fields into a v3 response.
- A response whose `applied`/`genHash` differs from the request is invalid at
  the semantic layer even when the JSON schema accepts the shape. The caller
  MUST reject it; it MUST NOT record `applied`.

### The response hash MUST equal the request

For every response variant the generation the app reports MUST equal the
`genHash` that was requested. This is the difference between an observation and
an ack:

```text
request  ["appearance-refresh", "aaaaaaaa…"]
applied  {"applied":"aaaaaaaa…"}                 # valid
deferred {"deferred":"pointer moved","genHash":"aaaaaaaa…"}  # valid
failed   {"failed":"busy","retryable":true,"genHash":"aaaaaaaa…"}  # valid

applied  {"applied":"bbbbbbbb…"}                 # rejected: stale ack
deferred {"deferred":"x","genHash":"bbbbbbbb…"}  # rejected: wrong generation
{"ok":true}                                      # rejected: unbound ack
```

The runtime records `applied` only when the ack's generation equals the
requested generation **and** `current/manifest.json.generationHash` still
matches. A stale or mismatched ack is a deferred/retry, never success. The
ledger is keyed by `genHash`, not by a boolean.

## What the app must do

1. **Resolve the requested generation.** Verify
   `$XDG_STATE_HOME/dotfiles/current/manifest.json` has
   `version == 3` and `generationHash == <genHash>`, or read
   `$XDG_STATE_HOME/dotfiles/generations/<genHash>/...` directly. If `current`
   points at a different generation, return `deferred` (retryable) and apply
   nothing. Never apply a mix of the old and new generation.
2. **Read the immutable generation.** The sheet is
   `$XDG_STATE_HOME/dotfiles/generations/<genHash>/appearance/<configDir>.css`
   and the tokens are
   `$XDG_STATE_HOME/dotfiles/generations/<genHash>/appearance/tokens.json`. If
   it reads through `current` instead, it MUST verify the manifest again after
   reading and retry on a mismatch.
3. **Validate and install** the composed sheet: one provider at
   `GTK_STYLE_PROVIDER_PRIORITY_USER` = 800, installed last, then only
   app-owned derived work. It does not separately apply a palette provider.
4. **Answer** with the exact `genHash` it applied. A cached `applied` result is
   keyed by `genHash`, not by a boolean.

The app reads the state path directly:
`$XDG_STATE_HOME/dotfiles/current/appearance/<configDir>.css`. It MUST NOT read
the v2 `$XDG_CONFIG_HOME/<configDir>/appearance.css` convenience link as the
runtime path, and it MUST NOT read or write inside an app tag.

## Timeouts, failures and retry

- The runtime enforces a wall-clock timeout per live app. The timeout covers
  the transport and the handler's completion; a handler that cannot finish
  returns `deferred`/`busy` before the deadline.
- Malformed, empty or extra output, a JSON object literal, non-zero exit, a
  timeout, or a response without a matching generation is a failure for that
  app.
- One app's failure does not stop the other apps in the parallel live lane.
- There is no immediate retry within the operation and no restart fallback.
  The ledger records `deferred`/`failed` against the generation; the next
  trigger retries those apps.
- A terminal (`retryable:false`) failure is recorded as such and is not treated
  as applied.
- The runtime, not the app, emits the per-app result/log record. App-internal
  logs are separate.

## State preservation

`appearance-refresh` is non-destructive:

- Apps with `holdsUnsavedState: true` preserve pending edits. If applying the
  generation would discard or invalidate them, return `deferred` with the
  reason (or `busy` while a save/preview is in flight); never quit, restart or
  reset the app.
- Apps with an active transient surface (open dialog, draft preview, in-flight
  operation) preserve it, or return `deferred`/`busy`.
- Writable state lives under `$XDG_CONFIG_HOME/` or `$XDG_STATE_HOME/`, never
  inside an installed tag. A refresh updates the stable state path or in-memory
  state; it does not write into `<install>/apps/<installDir>/<tag>/`.
- `wallpaper.state` is the progress/UI event only. It is not the refresh
  trigger.

## Ledger and lane policy

- The runtime writes one ledger record per app per generation. `status` is
  `applied`, `deferred`, `failed` or `skipped`; `applied` requires the exact
  response hash and an unchanged `current`.
- A skipped app is already at that generation; it has no invocation.
- `live` apps use this protocol and are not restarted for a generation change.
  `restart` apps have no handler and are restarted only after the commit.
  `supervision` (`unit`/`launcher`) changes how the restart runs, not whether
  it runs. A failed live refresh never falls back to restart.
- A restart is downgraded to deferred when `current` moves during the restart;
  the ledger never records `applied` for a generation that was not verified.

## Provenance and supersession

The v2 [`ags-app-refresh.md`](./ags-app-refresh.md) describes
`palette-refresh <appearance-hash>` with `{"ok":true}` and the whole-appearance
re-apply. It remains in the repository as provenance for the released v2
contract, but v3 consumers MUST use `appearance-refresh <genHash>` and the
generation-bound response union above. The v2 appearance token vocabulary and
built-in skins are unchanged; only the refresh identity and apply path are
superseded.

## Evidence

- Frozen design: `dotfiles-v3/docs/107-generations-v3.md` §2.6 (request,
  response, resolve-before-apply) and §1.3 (the boolean ack defect).
- v2 boolean ack: `ags-app-refresh.md` "Permitted responses" table.
- AGS string transport, fixed command shape and one-JSON-string response:
  `/usr/share/ags/js/lib/gtk4/app.ts:272-296`; the v2 protocol records the same
  transport in `ags-app-refresh.md`.
- Generation layout and consumer paths: `generations.md` §1, §5 and §11.

Verify:

```sh
uv run pytest -q tests/test_generations_contract.py
make test
make skin-test
make appearance-test
make schema-test
```
