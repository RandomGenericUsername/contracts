# container-adapter-env-contract Specification

> **Provenance.** Relocated from `dotfiles-v3/openspec/specs/container-adapter-env-contract/spec.md` during the
> cli-tools-repos split (slice **S0b**). Everything below the rule is the source spec,
> preserved verbatim; the CLI repos own the code these scenarios exercise. The
> `dotfiles-v3` copy is removed by the orchestrator after this repo's change is pushed.

---

## Purpose

This capability is the container/host environment seam for the two containerised CLIs: `csg`
and `weg` each hand the in-container process its whole configuration through a fixed
`_CONTAINER_ENV` env dict (`HOME`, the XDG dirs, the tool's config/effects paths, plus a
`...__RUNTIME__MODE=local` override) instead of re-passing `--config`/`--effects`/`--runtime`
flags into the container. It exists so the in-container run is configured identically to a host
run while those flags stay host-only, no new flag surface is added for it, and both tools carry
a test that pins the exact env dict the container runtime receives.

## Requirements
### Requirement: WEG defines and passes `_CONTAINER_ENV` on every container run

WEG's `container_processor.py` SHALL define a module-level constant `_CONTAINER_ENV` containing `HOME=/tmp`, `XDG_CONFIG_HOME=/tmp/.config`, `XDG_CACHE_HOME=/tmp/.cache`, `WALLPAPER_CONFIG_FILE_PATH=/weg-config/settings.toml`, `WALLPAPER_EFFECTS_CONFIG_FILE_PATH=/weg-effects/effects.yaml`, and `WALLPAPER__RUNTIME__MODE=local`. Every call to `self._get_engine().containers.run(run_config)` SHALL pass `environment=_CONTAINER_ENV` in the `RunConfig`.

#### Scenario: WEG container run receives the full env dict

- **WHEN** a WEG container processor executes a process/batch command and calls `containers.run(run_config)`
- **THEN** `run_config.environment` equals `_CONTAINER_ENV`
- **AND** the dict contains the `HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `WALLPAPER_CONFIG_FILE_PATH`, `WALLPAPER_EFFECTS_CONFIG_FILE_PATH`, and `WALLPAPER__RUNTIME__MODE` keys with the specified values

### Requirement: CSG extends `_CONTAINER_ENV` with the runtime-mode override

CSG's `_CONTAINER_ENV` in `color_scheme_generator/adapters/container_processor.py` SHALL include `COLORSCHEME__RUNTIME__MODE=local` in addition to the existing `HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `COLORSCHEME_CONFIG_FILE_PATH`, and `COLORSCHEME_TEMPLATES_TEMPLATES_DIR` keys.

#### Scenario: CSG container env contains the runtime override

- **WHEN** a CSG container processor runs in container mode
- **THEN** the environment passed to the container contains `COLORSCHEME__RUNTIME__MODE=local`
- **AND** the existing keys (`HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `COLORSCHEME_CONFIG_FILE_PATH`, `COLORSCHEME_TEMPLATES_TEMPLATES_DIR`) remain present

### Requirement: In-container argv uses no config/resource/runtime CLI flags

The in-container argv SHALL NOT contain WEG `--config`/`-c`/`--effects`/`-e` or CSG `--runtime`/`-r` at any scope. These flags remain valid on the host side unchanged.

#### Scenario: WEG in-container command carries no config/effects flags

- **WHEN** a WEG container processor builds the in-container command argv
- **THEN** the argv contains no `--config`, `-c`, `--effects`, or `-e` flag

#### Scenario: CSG in-container command carries no runtime flag

- **WHEN** a CSG container processor builds the in-container command argv
- **THEN** the argv contains no `--runtime` or `-r` flag

### Requirement: No new CLI flags are introduced

The env vars defined by this spec SHALL NOT create new CLI flags; they SHALL only reuse the env-var discovery mechanism that already exists in both tools' `config-assembler-engine` configuration.

#### Scenario: Flag surface is unchanged

- **WHEN** `csg --help` and `weg --help` are run
- **THEN** no new flags related to in-container environment configuration appear

### Requirement: Container environment contract is tested

Both tools SHALL have a test confirming the container runtime receives the exact `_CONTAINER_ENV` dict. WEG's test SHALL inspect `run_config.environment` from the call args. CSG's existing `test_passes_expected_environment` SHALL be updated to assert the new `COLORSCHEME__RUNTIME__MODE` key is present.

#### Scenario: WEG test asserts exact env dict

- **WHEN** the WEG container-processor test runs `test_passes_expected_environment`
- **THEN** the recorded `run_config.environment` equals `_CONTAINER_ENV`

#### Scenario: CSG test asserts the new runtime key

- **WHEN** the CSG container-processor test `test_passes_expected_environment` runs
- **THEN** it asserts `COLORSCHEME__RUNTIME__MODE` is present in the environment

