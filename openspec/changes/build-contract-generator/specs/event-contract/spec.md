# event-contract (delta)

## ADDED Requirements

### Requirement: Generator reads the canonical contract only

The generator SHALL read methods and signals from `event-contract.xml` (the D-Bus wire source) and topics, delivery, and versioning from `event-contract.json`. It SHALL NOT read a private or duplicate contract copy.

Source: spine **AD-6**.

#### Scenario: canonical sources are the only input

- **WHEN** the generator runs
- **THEN** it parses `event-contract.xml` for methods/signals and `event-contract.json` for topics/delivery/versioning
- **AND** no private `contract.json` is present in `gen/`

### Requirement: Python bindings are generated

The generator SHALL emit `generated/contract.py` containing the contract constants, TypedDicts, the wire method and signal tables, and a payload type per topic.

Source: spine **AD-6**.

#### Scenario: Python output covers the contract

- **WHEN** the generator runs
- **THEN** `generated/contract.py` names all 9 hub methods, 5 signals, the job interface, and all 6 topics

### Requirement: TypeScript bindings are generated

The generator SHALL emit `generated/contract.ts` containing the contract constants, types, and a payload interface per topic.

Source: spine **AD-6**.

#### Scenario: TypeScript output covers the contract

- **WHEN** the generator runs
- **THEN** `generated/contract.ts` names all 9 hub methods, 5 signals, the job interface, and all 6 topics

### Requirement: Generation is deterministic

The generator SHALL produce byte-identical output across runs: sorted keys and a trailing newline.

Source: spine **AD-6**; ticket REQ-002 acceptance.

#### Scenario: two runs are byte-identical

- **WHEN** the generator runs twice in a row
- **THEN** `git diff --exit-code generated/` exits 0

### Requirement: Generated output covers the full event surface

The generated bindings SHALL cover every topic (`icme.saved`, `capture.state`, `speedtest.state`, `clipboard.update`, `clipboard.state`, `wallpaper.state`), every hub method (9), every signal (5), and the job interface (`org.dotfiles.Job1`).

Source: spine **AD-6**; `event-contract.xml` / `event-contract.json`.

#### Scenario: coverage test passes

- **WHEN** the coverage test runs
- **THEN** it asserts all 6 topics, 9 hub methods, 5 signals, and the job interface are present
