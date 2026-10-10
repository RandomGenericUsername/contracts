# event-contract (delta)

## ADDED Requirements

### Requirement: Regenerate-and-diff gate

The repo SHALL expose a `make` target (`contracts-drift`, aliased as `drift`) that regenerates the bindings and then fails when `generated/` differs from a fresh generation. On a clean tree it SHALL exit 0.

Source: spine **AD-6** ("A regenerate-and-diff gate fails CI on drift"); ticket REQ-003 acceptance.

#### Scenario: clean tree passes

- **WHEN** `make contracts-drift` runs on a tree whose `generated/` matches a fresh generation
- **THEN** the generator runs and `git diff --exit-code generated/` exits 0

#### Scenario: unregenerated source change fails

- **WHEN** a topic or key is added to the canonical contract and `make contracts-drift` runs without the regenerated artifacts being committed
- **THEN** the gate exits non-zero

### Requirement: Symmetric schema check (contract ↔ schema)

The gate SHALL assert that `generated/events.schema.json` agrees with `event-contract.json` in **both** directions: every per-topic contract payload key, type, and enum is present in the schema, AND every schema topic/property is present in the contract; `required` equals the payload keys minus the declared `optional` keys; every enum is equal.

Source: spine **AD-6** ("it is symmetric … not one direction"); ticket REQ-003.

#### Scenario: extra schema key is rejected

- **WHEN** a property is hand-added to a topic definition in `generated/events.schema.json` that `event-contract.json` does not declare
- **THEN** the reverse check fails, naming the topic and the extra key

#### Scenario: dropped contract key is rejected

- **WHEN** a payload key exists in `event-contract.json` but not in the schema topic definition
- **THEN** the forward check fails, naming the topic and the missing key

#### Scenario: enum mismatch is rejected

- **WHEN** a schema enum differs from the contract enum (added, removed, or reordered value)
- **THEN** the check fails, naming the topic and field

### Requirement: Symmetric bindings check (contract ↔ contract.py / contract.ts)

The gate SHALL assert that the generated `contract.py` and `contract.ts` match the canonical contract: the identity/versioning/delivery/validation/job-lease constants, the topic→producer tables, the per-topic payload fields (names, optionality, types, enums), and the wire method/signal tables against `event-contract.xml`.

Source: spine **AD-6** ("the contract is checked against both the TS and the runtime tables").

#### Scenario: Python bindings agree with the contract

- **WHEN** the check runs
- **THEN** every constant, wire table, topic, and payload TypedDict in `generated/contract.py` equals the contract and XML, with no extra entry

#### Scenario: TypeScript bindings agree with the contract

- **WHEN** the check runs
- **THEN** every constant, wire table, topic, and payload interface in `generated/contract.ts` equals the contract and XML, with no extra entry

### Requirement: The gate can fail (negative-test coverage)

The change SHALL include negative tests proving the gate rejects drift; a gate that cannot fail is worthless.

Source: spine **AD-6**; ticket REQ-003 acceptance.

#### Scenario: hand-edited generated file fails

- **WHEN** a generated artifact is hand-edited and the gate runs
- **THEN** the gate exits non-zero

#### Scenario: extra schema key fails via the reverse check

- **WHEN** a schema topic gains a key absent from the contract
- **THEN** the reverse check reports it and the gate exits non-zero

### Requirement: Cross-repo runtime-tables leg is a named hook

The runtime wire-tables/validation-schema leg is cross-repo and SHALL be left as a clearly named hook owned by REQ-004; it SHALL NOT be faked.

Source: spine **AD-6**; ticket REQ-003 ("the runtime tables leg is cross-repo and belongs to REQ-004").

#### Scenario: hook is visible and skipped

- **WHEN** the checker runs in this repo
- **THEN** it reports the runtime-tables leg as skipped with a `TODO(REQ-004)` marker and does not assert a fake result

### Requirement: The gate runs in CI

CI SHALL run the gate on push and pull request.

Source: spine **AD-19**, **AD-23**.

#### Scenario: workflow invokes the gate

- **WHEN** a push or pull request triggers CI
- **THEN** a GitHub Actions workflow runs `make contracts-drift`
