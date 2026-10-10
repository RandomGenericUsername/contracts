# event-contract (delta)

## ADDED Requirements

### Requirement: The contract is the single source of truth

The event contract SHALL live in this repo: `event-contract.xml` (the D-Bus wire source) and `event-contract.json` (methods/signals/topics/delivery), plus the structural `schemas/`. It SHALL be imported byte-identical to the `dotfiles-v3` source at the cut commit.

Source: spine **AD-6**.

#### Scenario: byte-identical import

- **WHEN** the import completes
- **THEN** every imported file is byte-identical to its `dotfiles-v3` source at the cut commit
- **AND** `diff -r` reports no differences

### Requirement: The cut commit is recorded

The commit of `dotfiles-v3` the contract was cut from SHALL be recorded, so the repointing step can diff consumers against a known baseline.

Source: spine **AD-6**; REQ-004.

#### Scenario: the baseline is known

- **WHEN** the repoint step starts
- **THEN** the recorded cut commit names the exact source baseline
