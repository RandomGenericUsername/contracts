.PHONY: help validate generate test

help:
	@echo "validate   Validate the event contract"
	@echo "generate   Regenerate bindings from the contract"
	@echo "test       Run the contract tests"

validate:
	@echo "TODO: validate event-contract.json/.xml"

generate:
	python3 gen/generate.py

test:
	python3 -m unittest discover -s gen -p 'test_*.py'
