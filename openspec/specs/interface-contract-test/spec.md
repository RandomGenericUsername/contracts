# interface-contract-test Specification

> **Provenance.** Relocated from `dotfiles-v3/openspec/specs/interface-contract-test/spec.md` during the
> cli-tools-repos split (slice **S0b**). Everything below the rule is the source spec,
> preserved verbatim; the CLI repos own the code these scenarios exercise. The
> `dotfiles-v3` copy is removed by the orchestrator after this repo's change is pushed.

---

## Purpose

This capability is the adapter ↔ live-CLI interface check: `csg` and `weg` each build an
in-container argv from their adapters, and a test replays that argv through
`typer.testing.CliRunner` against the real Typer `app` (with processor resolution mocked) to
prove the CLI still accepts it. It exists so a flag that moves between scopes, gets renamed or
removed, or a changed positional order fails a test instead of surfacing as a runtime error in
the container, and so no flag the adapter emits is only "known" by the adapter itself.

## Requirements
### Requirement: WEG adapter argv is validated against the live CLI

WEG SHALL have an interface-contract test that constructs a `ProcessingRequest` with a synthetic input path, calls `_build_weg_command` to produce the in-container argv, strips the `"weg"` program name, passes the remaining argv through `typer.testing.CliRunner` against the live `app`, mocks processor resolution to short-circuit execution, and asserts `exit_code == 0`.

#### Scenario: WEG effect argv is accepted by the live CLI

- **WHEN** `processor._build_weg_command("effect", "blur", request, {"radius": "0x8"})` produces an argv like `["weg", "process", "effect", "blur", "/input/img.png", "-o", "/output", "--param", "radius=0x8"]`
- **AND** the argv (program name stripped) is invoked through `CliRunner` against the live `app` with `_resolve_processor`/`_resolve_context` mocked
- **THEN** the exit code is 0

#### Scenario: WEG composite argv is accepted by the live CLI

- **WHEN** `processor._build_weg_command("blur-resize", request, None)` produces an argv and it is invoked through `CliRunner` against the live `app`
- **THEN** the exit code is 0

#### Scenario: WEG preset argv is accepted by the live CLI

- **WHEN** `processor._build_weg_command("social", request, None)` produces an argv and it is invoked through `CliRunner` against the live `app`
- **THEN** the exit code is 0

### Requirement: CSG adapter argv is validated against the live CLI

CSG SHALL have an interface-contract test that captures the in-container argv from the container runtime's `call_args` (following the existing `test_inner_command_contains_runtime_local` pattern), strips the `"csg"` program name, patches `create_local_processor`/`create_container_processor` to short-circuit processor creation, and asserts `exit_code == 0` when the argv is invoked through `CliRunner` against the live `app`.

#### Scenario: CSG generate argv is accepted by the live CLI

- **WHEN** `process_generate` is run and the container runtime records the in-container command argv
- **AND** the argv (program name stripped) is invoked through `CliRunner` against the live `app` with processor factories patched
- **THEN** the exit code is 0

### Requirement: The interface contract guards against flag-scope drift

The tests SHALL fail (non-zero exit or `"No such option"`/`"Got unexpected extra argument"` in stderr) when a future change moves a CLI flag between scopes, renames a flag, removes a flag, or reorders positional arguments without updating the adapter argv.

#### Scenario: Flag moved between scopes is detected

- **WHEN** a flag the adapter emits is moved from sub-typer callback to root or vice versa without updating the adapter
- **THEN** the live CLI rejects the argv
- **AND** the interface-contract test reports a non-zero exit code

#### Scenario: Flag renamed is detected

- **WHEN** a flag the adapter emits is renamed without updating the adapter
- **THEN** the live CLI rejects the old name
- **AND** the interface-contract test reports a non-zero exit code

#### Scenario: Positional reordering is detected

- **WHEN** positional arguments are reordered without updating the adapter
- **THEN** the live CLI rejects wrong-arity or reports `"Got unexpected extra argument"`
- **AND** the interface-contract test reports a non-zero exit code

