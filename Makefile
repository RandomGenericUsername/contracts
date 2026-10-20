.PHONY: help validate generate check-symmetry contracts-drift drift sync test build

help:
	@echo "validate          Validate the event contract"
	@echo "generate          Regenerate bindings from the contract"
	@echo "check-symmetry    Check generated/ against the contract, both directions"
	@echo "contracts-drift   Regenerate-and-diff gate (alias: drift)"
	@echo "sync              Install the cli-invocation-contract package + dev deps"
	@echo "test              Run the event-contract tests and the package tests"
	@echo "build             Build the cli-invocation-contract sdist + wheel"

validate:
	@echo "TODO: validate event-contract.json/.xml"

generate:
	python3 gen/generate.py

# Symmetric content check (spine AD-6): compares the COMMITTED generated
# artifacts against the canonical contract in BOTH directions.
check-symmetry:
	python3 gen/check_symmetry.py

# Regenerate-and-diff gate (spine AD-6). Three layers, in order:
#   1. the symmetric content check (prerequisite) runs against the committed
#      generated/ files, so a semantic hand-edit or a contract change is caught
#      before regeneration overwrites it;
#   2. a pre-regeneration `git diff` catches ANY uncommitted change to
#      generated/ — including a non-semantic hand-edit (whitespace) that the
#      content check cannot see and that regeneration would otherwise mask;
#   3. the generator runs in place, then `git diff --exit-code` catches a source
#      change committed without a regenerated generated/ (or a new untracked
#      file).
contracts-drift: check-symmetry
	@git diff --exit-code generated/ || \
		{ echo "generated/ has uncommitted changes — regenerate and commit them"; exit 1; }
	python3 gen/generate.py
	git diff --exit-code generated/
	@test -z "$$(git ls-files --others --exclude-standard generated/)" || \
		{ echo "untracked file(s) in generated/:"; \
		  git ls-files --others --exclude-standard generated/; exit 1; }

drift: contracts-drift

sync:
	uv sync

# Both legs are gates: a failure of either fails the target (no suppression).
test:
	python3 -m unittest discover -s gen -p 'test_*.py'
	uv run pytest -q

build:
	uv build
